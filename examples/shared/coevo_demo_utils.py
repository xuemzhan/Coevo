"""Coevo 示例共享工具（examples/shared/）。

把 tool-dev-project 与 service-api 两个示例重复使用的演示助手收敛到这里，
避免同一逻辑在多处漂移：

* 时间与 JSON 助手：``ts`` / ``json_dump`` / ``jsonable``
* 文档与加密：``write_docx`` / ``sm3_hex``
* 加密任务包构建/回读校验：``build_and_verify_package`` /
  ``encrypt_and_verify``
* 编排容错：``with_recovery`` / ``_store_factory`` / ``run_chain_guarded``
* 端口：``free_port``

本模块只依赖 `src/coevo` 的生产门面，不修改任何领域逻辑。
"""

from __future__ import annotations

import datetime as _dt
import json
import socket
import sys
import uuid
import zipfile
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.app.demo_support import (  # noqa: E402
    DEMO_PROFILE,
    DemoFreshnessAuthority,
    DemoSigner,
)
from src.coevo.crypto import GmsslPrototypeProvider  # noqa: E402
from src.coevo.orchestrator import (  # noqa: E402
    RealChainStore,
    RealChainStoreRecoveryRequired,
)
from src.coevo.protocol import (  # noqa: E402
    build_encrypted_package,
    build_envelope_template,
    open_encrypted_package,
    parse_package_bytes,
)


def ts(day: int, hour: int) -> str:
    """演示时间线固定于 2026-08（便于结果可复现）。"""
    return f"2026-08-{day:02d}T{hour:02d}:00:00Z"


def json_dump(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )


def jsonable(value: Any) -> Any:
    """把 MISSING 哨兵与枚举转换为可 JSON 序列化的值。"""
    from src.coevo.merge import MISSING

    if value is MISSING:
        return None
    if isinstance(value, _dt.datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [jsonable(v) for v in value]
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    if hasattr(value, "value") and isinstance(value.value, (str, int, float, bool)):
        return value.value
    return value


def write_docx(path: Path) -> None:
    """生成一个最小、无宏的 DOCX（与仓库测试同构）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>',
        )


def sm3_hex(provider: GmsslPrototypeProvider, data: bytes) -> str:
    return provider.sm3(data).hex()


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def encrypt_and_verify(
    *,
    envelope: Any,
    manifest: dict[str, Any],
    content: bytes,
    provider: GmsslPrototypeProvider,
    sender_cert: str,
    recipient_cert: str,
    signed_at: str,
) -> tuple[Any, bytes]:
    """使用调用方预置的信封加密并回读校验（真实 SM2/SM4）。"""
    package = build_encrypted_package(
        envelope=envelope,
        manifest=manifest,
        content=content,
        provider=provider,
        sender_handle=provider.sender_handle(DEMO_PROFILE, sender_cert),
        recipient_handle=provider.recipient_handle(DEMO_PROFILE, recipient_cert),
        signed_at=signed_at,
    )
    wire = package.to_bytes()
    parsed = parse_package_bytes(wire)
    opened = open_encrypted_package(
        parsed,
        provider=provider,
        recipient_handle=provider.recipient_handle(DEMO_PROFILE, recipient_cert),
        sender_handle=provider.sender_handle(DEMO_PROFILE, sender_cert),
    )
    if opened.content != content:
        raise RuntimeError("package round-trip verification failed")
    return package, wire


def build_and_verify_package(
    *,
    provider: GmsslPrototypeProvider,
    sender_cert: str,
    recipient_cert: str,
    package_type: str,
    project_id: str,
    task_id: str,
    base_revision: str,
    sequence_no: int,
    manifest: dict[str, Any],
    content: bytes,
    signed_at: str,
    expires_at: str,
) -> tuple[Any, bytes]:
    """构建真实加密任务包并立即解密、验签回读（失败即抛错）。"""
    envelope = build_envelope_template(
        sender_cert_id=sender_cert,
        recipient_cert_id=recipient_cert,
        project_id=project_id,
        package_type=package_type,
        sequence_no=sequence_no,
        payload_length=0,
        created_at=signed_at,
        expires_at=expires_at,
    )
    return encrypt_and_verify(
        envelope=envelope,
        manifest=manifest,
        content=content,
        provider=provider,
        sender_cert=sender_cert,
        recipient_cert=recipient_cert,
        signed_at=signed_at,
    )


def with_recovery(
    store: RealChainStore,
    operation: Callable[[], Any],
) -> Any:
    """RealChainStore 审计锚点提升偶发失败时，按官方 recover() 修复并重试一次。"""
    try:
        return operation()
    except RealChainStoreRecoveryRequired:
        store.recover()
        return operation()


def _store_factory(path: Path) -> Callable[[], RealChainStore]:
    """每次调用生成独立文件的 RealChainStore 工厂（重试时换新库）。"""

    def factory() -> RealChainStore:
        unique = path.parent / f"{path.stem}-{uuid.uuid4().hex[:8]}{path.suffix}"
        return RealChainStore.create(
            unique,
            signer=DemoSigner(),
            freshness=DemoFreshnessAuthority(),
        )

    return factory


def run_chain_guarded(
    store_factory: Callable[[], RealChainStore],
    run_fn: Callable[[RealChainStore], Any],
) -> tuple[RealChainStore, Any]:
    """编排调用容错：审计锚点/恢复类失败时换新存储整链重跑一次。"""
    recovery_hints = ("recovery", "in progress", "anchor", "checkpoint")
    store = store_factory()
    try:
        return store, run_fn(store)
    except Exception as exc:
        if not any(hint in str(exc).lower() for hint in recovery_hints):
            raise
        store.close()
        store = store_factory()
        return store, run_fn(store)


__all__ = [
    "_store_factory",
    "build_and_verify_package",
    "encrypt_and_verify",
    "free_port",
    "json_dump",
    "jsonable",
    "run_chain_guarded",
    "sm3_hex",
    "ts",
    "with_recovery",
    "write_docx",
]
