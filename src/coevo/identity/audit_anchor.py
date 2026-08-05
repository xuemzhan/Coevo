"""Signed identity-audit heads with non-exportable per-generation freshness markers."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 身份审计锚点：签名审计头 + 每代不可导出新鲜度，防回滚/防篡改。

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import subprocess
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

ROOT = Path(__file__).resolve().parents[3]
SIGNING_SCRIPT = ROOT / "scripts" / "audit_signature.ps1"
FRESHNESS_SCRIPT = ROOT / "scripts" / "identity_freshness.ps1"
SIGNING_CONFIG = ROOT / "loop" / "audit-signing.json"


def _powershell_executable() -> str:
    exe = os.environ.get("COEVO_POWERSHELL_PATH")
    if exe and Path(exe).is_absolute():
        return exe
    fallback = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if fallback.is_file():
        return str(fallback)
    raise AuditAnchorError("Windows PowerShell is unavailable")


class AuditAnchorError(RuntimeError):
    pass


class Signer(Protocol):
    def sign(self, content: bytes) -> bytes: ...
    def verify(self, content: bytes, signature: bytes) -> None: ...


class FreshnessAuthority(Protocol):
    def create_marker(self, store_id: str, generation: int, binding: str) -> dict: ...
    def verify_marker(self, marker: dict) -> None: ...
    def delete_marker(self, marker: dict) -> None: ...
    def verify_retired(self, marker: dict) -> None: ...
    def sign(self, content: bytes, marker: dict) -> bytes: ...
    def verify_signature(self, content: bytes, signature: bytes, marker: dict) -> None: ...
    def store_retirement(self, tombstone: dict, main_signature: bytes, survivor_signature: bytes | None) -> None: ...
    def load_retirement(self, tombstone: dict) -> tuple[bytes, bytes, bytes | None]: ...


class WindowsCertificateSigner:
    def _run(self, action: str, content: bytes, signature: bytes | None = None) -> bytes:
        with tempfile.TemporaryDirectory(prefix="coevo-audit-sign-") as temporary:
            head = Path(temporary) / "head.json"
            signed = Path(temporary) / "head.p7s"
            head.write_bytes(content)
            if signature is not None:
                signed.write_bytes(signature)
            process = subprocess.run(
                [_powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SIGNING_SCRIPT), "-Action", action, "-HeadPath", str(head), "-SignaturePath", str(signed), "-ConfigPath", str(SIGNING_CONFIG)],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
            )
            if process.returncode:
                raise AuditAnchorError("identity audit signature operation failed")
            return signed.read_bytes() if action == "Sign" else b""

    def sign(self, content: bytes) -> bytes:
        return self._run("Sign", content)

    def verify(self, content: bytes, signature: bytes) -> None:
        self._run("Verify", content, signature)


class WindowsFreshnessAuthority:
    MARKER_FIELDS = {"store_id", "generation", "binding_sha256", "token", "key_id", "key_public_sha256", "transition_id"}

    def __init__(self, retirement_root: Path | None = None):
        local = os.environ.get("LOCALAPPDATA")
        if retirement_root is None and not local:
            raise AuditAnchorError("LOCALAPPDATA is unavailable for retirement tombstones")
        self.retirement_root = retirement_root or Path(local) / "Coevo" / "identity-retirements"

    @classmethod
    def _validate_marker(cls, marker: dict) -> None:
        if set(marker) != cls.MARKER_FIELDS:
            raise AuditAnchorError("identity freshness marker fields are invalid")
        try:
            uuid.UUID(marker["store_id"]); uuid.UUID(marker["transition_id"])
        except (ValueError, TypeError, AttributeError) as exc:
            raise AuditAnchorError("identity freshness marker identifier is invalid") from exc
        if type(marker["generation"]) is not int or marker["generation"] < 1:
            raise AuditAnchorError("identity freshness generation is invalid")
        if len(marker["binding_sha256"]) != 64 or any(c not in "0123456789abcdef" for c in marker["binding_sha256"]):
            raise AuditAnchorError("identity freshness binding is invalid")
        if len(marker["token"]) != 40 or any(c not in "0123456789ABCDEF" for c in marker["token"]):
            raise AuditAnchorError("identity freshness token is invalid")
        if not marker["key_id"].startswith("CoevoIdentityMarker-") or len(marker["key_id"]) != 52:
            raise AuditAnchorError("identity freshness key identifier is invalid")
        if len(marker["key_public_sha256"]) != 64 or any(c not in "0123456789abcdef" for c in marker["key_public_sha256"]):
            raise AuditAnchorError("identity freshness key public digest is invalid")

    def _arguments(self, action: str, marker: dict) -> list[str]:
        args = [
            _powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(FRESHNESS_SCRIPT),
            "-Action", action, "-StoreId", marker["store_id"], "-Generation", str(marker["generation"]),
            "-Binding", marker["binding_sha256"], "-TransitionId", marker["transition_id"],
            "-ConfigPath", str(SIGNING_CONFIG),
        ]
        if marker.get("token"):
            args += ["-Token", marker["token"]]
        if marker.get("key_id"):
            args += ["-KeyId", marker["key_id"], "-KeyPublicSha256", marker["key_public_sha256"]]
        return args

    def _run(self, arguments: list[str]) -> str:
        process = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=40)
        if process.returncode:
            raise AuditAnchorError("identity freshness operation failed")
        return process.stdout.strip()

    def _paths(self, marker: dict) -> tuple[Path, Path, Path]:
        self._validate_marker(marker)
        base = self.retirement_root / marker["store_id"] / f'{marker["generation"]}-{marker["transition_id"]}'
        return base.with_suffix(".json"), base.with_suffix(".main.p7s"), base.with_suffix(".survivor.p7s")

    def create_marker(self, store_id: str, generation: int, binding: str) -> dict:
        transition_id = str(uuid.uuid4())
        partial = {"store_id": store_id, "generation": generation, "binding_sha256": binding, "transition_id": transition_id}
        output = self._run(self._arguments("Create", partial))
        try:
            created = json.loads(output)
        except json.JSONDecodeError as exc:
            raise AuditAnchorError("identity freshness helper returned invalid JSON") from exc
        if not isinstance(created, dict) or set(created) != {"token", "key_id", "key_public_sha256"}:
            raise AuditAnchorError("identity freshness helper returned invalid marker data")
        marker = {**partial, "token": str(created["token"]).upper(), "key_id": created["key_id"], "key_public_sha256": created["key_public_sha256"]}
        self._validate_marker(marker)
        self.verify_marker(marker)
        return marker

    def verify_marker(self, marker: dict) -> None:
        self._validate_marker(marker)
        if self._paths(marker)[0].exists():
            raise AuditAnchorError("identity freshness marker is retired")
        self._run(self._arguments("VerifyMarker", marker))

    def delete_marker(self, marker: dict) -> None:
        self._validate_marker(marker)
        self._run(self._arguments("Delete", marker))

    def verify_retired(self, marker: dict) -> None:
        self._validate_marker(marker)
        self._run(self._arguments("VerifyRetired", marker))

    def _signature(self, action: str, content: bytes, marker: dict, signature: bytes | None = None) -> bytes:
        with tempfile.TemporaryDirectory(prefix="coevo-marker-sign-") as temporary:
            head = Path(temporary) / "head.json"
            signed = Path(temporary) / "head.p7s"
            head.write_bytes(content)
            if signature is not None:
                signed.write_bytes(signature)
            args = self._arguments(action, marker) + ["-ContentPath", str(head), "-SignaturePath", str(signed)]
            self._run(args)
            return signed.read_bytes() if action == "Sign" else b""

    def sign(self, content: bytes, marker: dict) -> bytes:
        self.verify_marker(marker)
        return self._signature("Sign", content, marker)

    def verify_signature(self, content: bytes, signature: bytes, marker: dict) -> None:
        self._validate_marker(marker)
        self._signature("VerifySignature", content, marker, signature)

    def store_retirement(self, tombstone: dict, main_signature: bytes, survivor_signature: bytes | None) -> None:
        target = tombstone["target_marker"]
        raw = canonical(tombstone)
        json_path, main_path, survivor_path = self._paths(target)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        expected_survivor = tombstone.get("survivor_marker") is not None
        if json_path.exists():
            loaded = self.load_retirement(tombstone)
            if loaded != (raw, main_signature, survivor_signature):
                raise AuditAnchorError("conflicting identity retirement tombstone")
            return
        # Signatures are staged first; the JSON file is the atomic commit marker.
        durable_write(main_path, main_signature)
        if expected_survivor and survivor_signature is not None:
            durable_write(survivor_path, survivor_signature)
        elif expected_survivor:
            raise AuditAnchorError("retirement survivor signature is missing")
        durable_write(json_path, raw)

    def load_retirement(self, tombstone: dict) -> tuple[bytes, bytes, bytes | None]:
        json_path, main_path, survivor_path = self._paths(tombstone["target_marker"])
        if not json_path.is_file() or not main_path.is_file():
            raise AuditAnchorError("identity retirement tombstone is incomplete")
        survivor = survivor_path.read_bytes() if tombstone.get("survivor_marker") is not None and survivor_path.is_file() else None
        if tombstone.get("survivor_marker") is not None and survivor is None:
            raise AuditAnchorError("identity retirement survivor proof is incomplete")
        return json_path.read_bytes(), main_path.read_bytes(), survivor


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def durable_write(path: Path, content: bytes) -> None:
    temporary = Path(str(path) + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(content); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


@contextlib.contextmanager
def exclusive_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"0"); stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


class SignedAuditAnchor:
    def __init__(self, database: Path, signer: Signer, freshness: FreshnessAuthority):
        base = Path(str(database) + ".identity-audit")
        self.head = Path(str(base) + "-head.json"); self.signature = Path(str(base) + "-head.p7s"); self.marker_signature = Path(str(base) + "-head.marker.p7s")
        self.pending_head = Path(str(base) + "-pending.json"); self.pending_signature = Path(str(base) + "-pending.p7s")
        self.pending_new_signature = Path(str(base) + "-pending.new-marker.p7s"); self.pending_old_signature = Path(str(base) + "-pending.old-marker.p7s")
        self.lock_path = Path(str(base) + ".lock"); self.signer = signer; self.freshness = freshness

    def locked(self):
        return exclusive_lock(self.lock_path)

    def artifacts(self) -> tuple[Path, ...]:
        return (self.head, self.signature, self.marker_signature, self.pending_head, self.pending_signature, self.pending_new_signature, self.pending_old_signature)

    def _decode_main(self, head: Path, signature: Path) -> tuple[bytes, dict]:
        if not head.is_file() or not signature.is_file():
            raise AuditAnchorError("identity audit anchor is incomplete")
        raw = head.read_bytes(); self.signer.verify(raw, signature.read_bytes())
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AuditAnchorError("identity audit anchor JSON is invalid") from exc
        if canonical(item) != raw or item.get("schema_version") != "3.0":
            raise AuditAnchorError("identity audit anchor is not canonical or supported")
        return raw, item

    def _read_official(self) -> tuple[bytes, dict]:
        raw, item = self._decode_main(self.head, self.signature); marker = item.get("marker")
        if not isinstance(marker, dict) or not self.marker_signature.is_file():
            raise AuditAnchorError("identity audit marker is missing")
        self.freshness.verify_signature(raw, self.marker_signature.read_bytes(), marker); self.freshness.verify_marker(marker)
        return raw, item

    def _read_pending(self, *, require_new_marker: bool = True) -> tuple[bytes, dict]:
        raw, item = self._decode_main(self.pending_head, self.pending_signature); marker = item.get("marker")
        if not isinstance(marker, dict) or not self.pending_new_signature.is_file():
            raise AuditAnchorError("pending new marker proof is incomplete")
        self.freshness.verify_signature(raw, self.pending_new_signature.read_bytes(), marker)
        if require_new_marker:
            self.freshness.verify_marker(marker)
        previous = item.get("previous_marker")
        if previous is None:
            if self.pending_old_signature.exists():
                raise AuditAnchorError("unexpected pending old marker proof")
        elif not isinstance(previous, dict) or not self.pending_old_signature.is_file():
            raise AuditAnchorError("pending old marker proof is incomplete")
        else:
            self.freshness.verify_signature(raw, self.pending_old_signature.read_bytes(), previous)
        return raw, item

    @staticmethod
    def _matches(item: dict, checkpoint: dict) -> bool:
        return item.get("checkpoint") == checkpoint

    def _tombstone(self, status: str, target: dict, survivor: dict | None, transition_head: bytes) -> dict:
        return {
            "schema_version": "1.0", "status": status, "store_id": target["store_id"],
            "target_marker": target, "survivor_marker": survivor,
            "transition_head_sha256": hashlib.sha256(transition_head).hexdigest(),
            "key_destroyed": True, "certificate_removed": True,
        }

    def _complete_retirement(self, tombstone: dict) -> None:
        target = tombstone.get("target_marker"); survivor = tombstone.get("survivor_marker")
        if not isinstance(target, dict) or (survivor is not None and not isinstance(survivor, dict)):
            raise AuditAnchorError("retirement tombstone marker is invalid")
        raw = canonical(tombstone)
        try:
            stored_raw, main_signature, survivor_signature = self.freshness.load_retirement(tombstone)
        except AuditAnchorError:
            self.freshness.delete_marker(target)
            self.freshness.verify_retired(target)
            main_signature = self.signer.sign(raw)
            survivor_signature = self.freshness.sign(raw, survivor) if survivor else None
            self.freshness.store_retirement(tombstone, main_signature, survivor_signature)
            stored_raw, main_signature, survivor_signature = self.freshness.load_retirement(tombstone)
        if stored_raw != raw:
            raise AuditAnchorError("identity retirement tombstone content mismatch")
        self.signer.verify(raw, main_signature)
        if survivor:
            if survivor_signature is None:
                raise AuditAnchorError("identity retirement survivor signature is missing")
            self.freshness.verify_signature(raw, survivor_signature, survivor)
        self.freshness.verify_retired(target)

    def verify(self, checkpoint: dict) -> bool:
        try:
            _, item = self._read_official()
            tombstone = item.get("retirement_tombstone")
            if tombstone is not None:
                self._complete_retirement(tombstone)
            return self._matches(item, checkpoint)
        except (AuditAnchorError, OSError, KeyError):
            return False

    def prepare(self, checkpoint: dict) -> None:
        if any(path.exists() for path in (self.pending_head, self.pending_signature, self.pending_new_signature, self.pending_old_signature)):
            raise AuditAnchorError("an identity audit anchor transaction is already pending")
        generation = 1; previous_hash = "0" * 64; previous_marker = None
        if self.head.exists() or self.signature.exists() or self.marker_signature.exists():
            previous_raw, previous = self._read_official(); generation = int(previous.get("generation", 0)) + 1
            previous_hash = hashlib.sha256(previous_raw).hexdigest(); previous_marker = previous["marker"]
        binding = hashlib.sha256(canonical(checkpoint)).hexdigest(); marker = self.freshness.create_marker(checkpoint["store_id"], generation, binding)
        item = {
            "schema_version": "3.0", "generation": generation, "previous_head_sha256": previous_hash,
            "signed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"), "checkpoint": checkpoint,
            "marker": marker, "previous_marker": previous_marker,
        }
        if previous_marker:
            provisional = canonical(item)
            item["retirement_tombstone"] = self._tombstone("promoted-retired", previous_marker, marker, provisional)
        raw = canonical(item)
        try:
            main_signature = self.signer.sign(raw); new_signature = self.freshness.sign(raw, marker)
            old_signature = self.freshness.sign(raw, previous_marker) if previous_marker else None
            self.signer.verify(raw, main_signature); self.freshness.verify_signature(raw, new_signature, marker)
            if previous_marker and old_signature:
                self.freshness.verify_signature(raw, old_signature, previous_marker)
            durable_write(self.pending_head, raw); durable_write(self.pending_signature, main_signature); durable_write(self.pending_new_signature, new_signature)
            if old_signature:
                durable_write(self.pending_old_signature, old_signature)
        except Exception:
            self.freshness.delete_marker(marker); self._unlink_pending(); raise

    def promote(self) -> None:
        raw, item = self._read_pending()
        durable_write(self.signature, self.pending_signature.read_bytes()); durable_write(self.marker_signature, self.pending_new_signature.read_bytes()); durable_write(self.head, raw)
        if self._read_official()[1] != item:
            raise AuditAnchorError("promoted identity audit anchor failed verification")
        tombstone = item.get("retirement_tombstone")
        if tombstone is not None:
            self._complete_retirement(tombstone)
        self._unlink_pending()

    def _unlink_pending(self) -> None:
        for path in (self.pending_head, self.pending_signature, self.pending_new_signature, self.pending_old_signature):
            path.unlink(missing_ok=True)

    def abort_pending(self) -> None:
        raw, item = self._read_pending(require_new_marker=False); target = item["marker"]; survivor = item.get("previous_marker")
        self._complete_retirement(self._tombstone("aborted-retired", target, survivor, raw)); self._unlink_pending()

    def recover(self, checkpoint: dict) -> None:
        pending_paths = (self.pending_head, self.pending_signature, self.pending_new_signature, self.pending_old_signature)
        if any(path.exists() for path in pending_paths):
            _, pending = self._read_pending()
            if self._matches(pending, checkpoint):
                self.promote(); return
            if self.verify(checkpoint):
                self.abort_pending(); return
            raise AuditAnchorError("identity database matches neither committed nor pending signed state")
        if not self.verify(checkpoint):
            raise AuditAnchorError("identity database does not match its signed freshness anchor")
