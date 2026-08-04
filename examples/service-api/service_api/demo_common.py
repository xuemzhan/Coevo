"""一致性 API 演示公共脚手架。

run_demo 与 run_demo_full 共享的启动/审计/清理逻辑收敛于此：

* :func:`build_audit_hook` —— 每次服务调用产生一条生产审计事件；
* :func:`build_framework` —— 服务注册表 + 共享上下文 + 权限策略装配；
* :func:`run_demo_server` —— 主线程顺序处理请求（共享 SQLite 同线程）+
  客户端线程驱动演示序列 + 上下文清理，返回演示退出码。

设计原因：服务端顺序处理请求（而非线程池），保证共享 SQLite 存储在同一
线程内使用，避免跨线程连接错误；演示为顺序调用，无需并发吞吐。
"""

from __future__ import annotations

import threading
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples" / "shared"))

from coevo_demo_utils import free_port  # noqa: E402
from src.coevo.audit_governance import (  # noqa: E402
    AuditEvent,
    AuditEventSource,
)

from .adapters import build_context, build_registry, close_context  # noqa: E402
from .framework import ServiceFramework  # noqa: E402
from .server import ServiceApiServer  # noqa: E402


DEFAULT_PERMISSIONS: dict[str, frozenset[str]] = {
    "u.pm": frozenset({"*"}),
    "u.auditor": frozenset({
        "identity.register",
        "audit.query",
        "audit.intercept",
    }),
}

_REJECTED_CODES = frozenset({
    "bad_request", "validation_error", "not_found", "conflict", "unauthorized",
})


def build_audit_hook(ctx: dict[str, Any], tool: str) -> Callable[..., None]:
    """返回服务调用审计钩子：每次调用写一条生产 AuditEvent。"""

    def audit_hook(request, response) -> None:
        result = (
            "ok"
            if response.ok
            else ("rejected" if response.code in _REJECTED_CODES else "failed")
        )
        record = {
            "ts": request.ts,
            "actor": request.actor,
            "action": f"{request.service}.{request.method}",
            "result": result,
            "project_id": "PRJ001",
            "task_id": "",
            "tool": tool,
        }
        event = AuditEvent.from_audit_record(
            record, source=AuditEventSource.STATE
        )
        ctx["audit_hub"].publish(event)
        ctx["audit_events"].append(event)

    return audit_hook


def build_framework(
    ctx: dict[str, Any],
    *,
    permissions: dict[str, frozenset[str]] | None = DEFAULT_PERMISSIONS,
    tool: str = "coevo.service-api",
) -> ServiceFramework:
    """装配统一服务框架：注册表 + 上下文 + 审计 + 权限治理。"""
    return ServiceFramework(
        build_registry(),
        ctx,
        audit=build_audit_hook(ctx, tool),
        permissions=permissions,
    )


def run_demo_server(
    run_dir: Path,
    *,
    sequence: Callable[[ServiceApiServer, dict[str, Any]], int],
    permissions: dict[str, frozenset[str]] | None = DEFAULT_PERMISSIONS,
    tool: str = "coevo.service-api",
    port: int = 0,
) -> int:
    """主线程顺序服务 + 客户端线程驱动 + 清理；返回演示退出码。"""
    ctx = build_context(run_dir)
    server = ServiceApiServer(build_framework(ctx, permissions=permissions, tool=tool), bind_port=port or free_port())
    exit_code: dict[str, int] = {"value": 1}

    def runner() -> None:
        try:
            exit_code["value"] = sequence(server, ctx)
        finally:
            server.shutdown()

    client = threading.Thread(target=runner, daemon=True)
    client.start()
    server.serve_forever()
    client.join(timeout=300)
    server.server_close()
    close_context(ctx)
    return exit_code["value"]


__all__ = [
    "DEFAULT_PERMISSIONS",
    "build_audit_hook",
    "build_framework",
    "run_demo_server",
]
