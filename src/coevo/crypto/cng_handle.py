"""HANDLE-1: CNG-protected SM2 key handle (KEK wrapping) layer.

The approved-product path requires a *protected, non-exportable key
handle*. Windows CNG does not natively host SM2 keys, so this layer
implements the industry-standard key-wrapping pattern instead: the
SM2 key's PKCS#8 encryption password is wrapped at rest under a
**non-exportable CNG RSA KEK** (``CngKekStore`` +
``scripts/cng-kek.ps1``); the key itself stays PKCS#8-encrypted in
the profile, and only the wrapped password blob plus metadata are
persisted (``CngWrappedKeyRegistry``). RSA-2048 OAEP-SHA256 cannot
carry the full encrypted key + DPAPI blob, so the KEK protects the
password that unlocks the key (HANDLE-2 unwraps it inside the
controlled crypto helper).

Key-security boundary (inherited from the repo-wide rule "Python never
receives private-key bytes"):

* the KEK lives only inside the Windows CNG KSP and is created with
  ``ExportPolicy=None`` (non-exportable by construction);
* ``Wrap`` accepts the key material once, at import time, over stdin
  and returns only ciphertext;
* ``UnwrapDigest`` returns **only the SHA-256 digest** of the unwrapped
  material -- raw SM2 key bytes never cross the process boundary to
  Python;
* the actual *use* of the unlocked key (SM2 sign / open) happens
  inside the controlled crypto helper (HANDLE-2 actions 6/7), which
  consumes the wrapped password blob and the KEK name directly and
  zeroizes the password and key in helper memory (see
  ``docs/dependencies/approved-crypto-provider-path.md``).
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# HANDLE-1：CNG 保护的 SM2 密钥句柄（KEK 包装）层，私钥字节不进入
# Python 进程；句柄/回滚/吊销由受控助手完成。
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final


KEK_PREFIX: Final[str] = "CoevoSm2Kek-"
KEK_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^CoevoSm2Kek-[0-9a-f]{32}$")
SM2_KEY_ALGORITHM_OID: Final[str] = "1.2.156.10197.1.301"
REGISTRY_SCHEMA: Final[str] = "1.0"
_HELPER_PATH: Final[Path] = Path(__file__).resolve().parents[3] / "scripts" / "cng-kek.ps1"
_HELPER_SIZE: Final[int] = 6118
_HELPER_SHA256: Final[str] = "f01e88716658e837c191ca15aa20c6a85423b557bb4efd0661ca350d3d1361ab"
_MAX_INPUT_BYTES: Final[int] = 64 * 1024
_ISO_RE: Final[re.Pattern[str]] = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)


class CngKekError(RuntimeError):
    """Base class for the CNG KEK handle layer (fail-closed)."""


class CngKekValidationError(CngKekError, ValueError):
    """A reference, name, or registry payload is malformed."""


class CngKekUnavailableError(CngKekError):
    """The CNG KEK does not exist (or has already been destroyed)."""


class CngKekHelperError(CngKekError):
    """The controlled CNG helper rejected an operation."""


def _now_utc_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validate_kek_name(name: str) -> str:
    if not isinstance(name, str) or not KEK_NAME_RE.fullmatch(name):
        raise CngKekValidationError(
            f"kek_name must match {KEK_PREFIX}<32-hex>; got {name!r}"
        )
    return name


@dataclass(frozen=True)
class CngKekReference:
    """Non-secret metadata reference to a CNG KEK (no key bytes)."""

    kek_name: str
    public_sha256: str
    created_at: str

    def __post_init__(self) -> None:
        _validate_kek_name(self.kek_name)
        if not isinstance(self.public_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", self.public_sha256
        ):
            raise CngKekValidationError("public_sha256 must be 64-char lowercase hex")
        if not isinstance(self.created_at, str) or not _ISO_RE.fullmatch(self.created_at):
            raise CngKekValidationError("created_at must be ISO-8601 UTC Z")

    def to_mapping(self) -> dict[str, str]:
        return {
            "kek_name": self.kek_name,
            "public_sha256": self.public_sha256,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class CngProtectedKeyHandle:
    """A non-secret protected-handle reference (implements ProtectedKeyHandle)."""

    handle_id: str
    certificate_id: str
    algorithm_oid: str = SM2_KEY_ALGORITHM_OID

    def __post_init__(self) -> None:
        if not isinstance(self.handle_id, str) or not self.handle_id:
            raise CngKekValidationError("handle_id must be a non-empty string")
        if not isinstance(self.certificate_id, str) or not self.certificate_id:
            raise CngKekValidationError("certificate_id must be a non-empty string")
        if not isinstance(self.algorithm_oid, str) or not re.fullmatch(
            r"[0-9.]+", self.algorithm_oid
        ):
            raise CngKekValidationError("algorithm_oid is malformed")


def _locked_powershell() -> str:
    root = Path(__file__).resolve().parents[3]
    try:
        lock = json.loads(
            (root / "docs" / "dependencies" / "toolchain-lock.json").read_text("utf-8")
        )
        expected = lock["tools"]["make_compatibility_shim"]["windows_powershell"]
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise CngKekHelperError("locked Windows PowerShell metadata is unavailable") from exc
    configured = os.environ.get("COEVO_POWERSHELL_PATH")
    candidate = Path(configured) if configured else (
        Path(os.environ.get("SystemRoot", r"C:\Windows"))
        / str(expected["windows_directory_relative_path"])
    )
    if not candidate.is_absolute():
        raise CngKekHelperError("Windows PowerShell path must be absolute")
    try:
        resolved = candidate.resolve(strict=True)
        stat = resolved.stat()
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    except OSError as exc:
        raise CngKekHelperError("Windows PowerShell is unavailable") from exc
    if stat.st_size != int(expected["size"]) or digest != expected["sha256"]:
        raise CngKekHelperError("Windows PowerShell failed the locked integrity check")
    return str(resolved)


class CngKekStore:
    """Create / inspect / use / destroy a non-exportable CNG KEK."""

    def __init__(self, helper_path: Path | None = None) -> None:
        candidate = Path(helper_path) if helper_path is not None else _HELPER_PATH
        try:
            self.helper_path = candidate.resolve(strict=True)
            controlled = _HELPER_PATH.resolve(strict=True)
        except OSError as exc:
            raise CngKekHelperError("controlled CNG KEK helper is unavailable") from exc
        if self.helper_path != controlled:
            raise CngKekHelperError("CNG KEK helper path is not controlled by the repository")
        helper_bytes = self.helper_path.read_bytes()
        canonical = helper_bytes.replace(b"\r\n", b"\n")
        if len(canonical) != _HELPER_SIZE or hashlib.sha256(canonical).hexdigest() != _HELPER_SHA256:
            raise CngKekHelperError("CNG KEK helper failed the locked integrity check")

    def _run(self, action: str, kek_name: str, *, input_base64: str | None = None) -> dict:
        body = json.dumps(
            {
                "action": action,
                "kek_name": kek_name,
                "input_base64": input_base64,
            },
            separators=(",", ":"),
        ).encode("utf-8")
        try:
            process = subprocess.run(
                [
                    _locked_powershell(),
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(self.helper_path),
                ],
                cwd=self.helper_path.parents[1],
                input=body,
                capture_output=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise CngKekHelperError("CNG KEK helper timed out") from exc
        if process.returncode:
            message = process.stderr.decode("utf-8", errors="replace").strip()
            raise CngKekHelperError(
                f"CNG KEK helper failed: action={action} exit={process.returncode} ({message[:200]})"
            )
        try:
            result = json.loads(process.stdout.decode("utf-8", errors="replace").strip())
        except json.JSONDecodeError as exc:
            raise CngKekHelperError("CNG KEK helper returned invalid JSON") from exc
        if not isinstance(result, dict) or result.get("schema_version") != "1.0":
            raise CngKekHelperError("CNG KEK helper output failed policy checks")
        return result.get("result", {})

    def create_kek(self, name: str | None = None) -> CngKekReference:
        kek_name = _validate_kek_name(name or f"{KEK_PREFIX}{uuid.uuid4().hex}")
        result = self._run("CreateKek", kek_name)
        return CngKekReference(
            kek_name=str(result["kek_name"]),
            public_sha256=str(result["public_sha256"]),
            created_at=_now_utc_iso(),
        )

    def status(self, ref: CngKekReference) -> dict:
        return self._run("Status", ref.kek_name)

    def wrap(self, ref: CngKekReference, plaintext: bytes) -> tuple[bytes, str]:
        if not isinstance(plaintext, bytes) or not plaintext:
            raise CngKekValidationError("wrap input must be non-empty bytes")
        if len(plaintext) > _MAX_INPUT_BYTES:
            raise CngKekValidationError("wrap input exceeds the size limit")
        result = self._run(
            "Wrap", ref.kek_name, input_base64=base64_b64encode(plaintext)
        )
        wrapped = base64_b64decode(str(result["wrapped_base64"]))
        return wrapped, str(result["wrapped_sha256"])

    def unwrap_digest(self, ref: CngKekReference, wrapped: bytes) -> tuple[str, int]:
        if not isinstance(wrapped, bytes) or not wrapped:
            raise CngKekValidationError("unwrap input must be non-empty bytes")
        result = self._run(
            "UnwrapDigest", ref.kek_name, input_base64=base64_b64encode(wrapped)
        )
        return str(result["plaintext_sha256"]), int(result["length"])

    def destroy(self, ref: CngKekReference) -> None:
        self._run("Destroy", ref.kek_name)


def base64_b64encode(data: bytes) -> str:
    """Return canonical ASCII base64 for ``data`` (helper framing)."""
    import base64
    return base64.b64encode(data).decode("ascii")


def base64_b64decode(value: str) -> bytes:
    """Strictly decode canonical base64; malformed input fails closed."""
    import base64
    import binascii
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise CngKekValidationError("helper returned invalid base64") from exc


class CngWrappedKeyRegistry:
    """Append-only, tamper-evident registry of CNG-wrapped SM2 keys.

    Persisted as JSON with a SHA-256 hash chain (each entry binds the
    previous entry hash). Explicit ``create`` / ``open``; corruption or
    tampering is rejected on open. Only wrapped blobs (ciphertext) and
    metadata are stored -- plaintext key bytes never touch this file.
    """

    _ALLOWED_ENTRY_FIELDS = frozenset({
        "entry_id", "handle_id", "kek_name", "wrapped_sha256", "role",
        "certificate_id", "action", "reason", "created_at",
        "prev_hash", "entry_hash",
    })

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path

    @classmethod
    def create(cls, path: Path) -> "CngWrappedKeyRegistry":
        if Path(path).exists():
            raise CngKekValidationError("refusing to create registry over existing state")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        registry = cls(path)
        registry._write({"schema_version": REGISTRY_SCHEMA, "entries": []})
        return registry

    @classmethod
    def open(cls, path: Path) -> "CngWrappedKeyRegistry":
        if not Path(path).is_file():
            raise CngKekValidationError("registry does not exist; explicit create is required")
        registry = cls(path)
        data = registry._read()
        if data.get("schema_version") != REGISTRY_SCHEMA:
            raise CngKekValidationError("registry schema_version mismatch")
        registry._verify_chain(data["entries"])
        return registry

    def register(
        self,
        *,
        handle_id: str,
        kek_name: str,
        wrapped_sha256: str,
        role: str,
        certificate_id: str,
        created_at: str | None = None,
    ) -> str:
        _validate_kek_name(kek_name)
        if role not in {"sender", "recipient"}:
            raise CngKekValidationError("role must be sender or recipient")
        if not isinstance(wrapped_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", wrapped_sha256
        ):
            raise CngKekValidationError("wrapped_sha256 must be 64-char lowercase hex")
        entry_id = uuid.uuid4().hex
        entry = {
            "entry_id": entry_id,
            "handle_id": handle_id,
            "kek_name": kek_name,
            "wrapped_sha256": wrapped_sha256,
            "role": role,
            "certificate_id": certificate_id,
            "action": "register",
            "reason": "",
            "created_at": created_at or _now_utc_iso(),
        }
        return self._append(entry)

    def revoke(self, handle_id: str, *, reason: str) -> str:
        if not isinstance(reason, str) or not reason.strip():
            raise CngKekValidationError("revocation reason is required")
        return self._append({
            "entry_id": uuid.uuid4().hex,
            "handle_id": handle_id,
            "kek_name": "",
            "wrapped_sha256": "",
            "role": "",
            "certificate_id": "",
            "action": "revoke",
            "reason": reason,
            "created_at": _now_utc_iso(),
        })

    def destroy(self, handle_id: str, *, reason: str) -> str:
        if not isinstance(reason, str) or not reason.strip():
            raise CngKekValidationError("destroy reason is required")
        return self._append({
            "entry_id": uuid.uuid4().hex,
            "handle_id": handle_id,
            "kek_name": "",
            "wrapped_sha256": "",
            "role": "",
            "certificate_id": "",
            "action": "destroy",
            "reason": reason,
            "created_at": _now_utc_iso(),
        })

    def snapshot(self) -> tuple[dict[str, Any], ...]:
        data = self._read()
        self._verify_chain(data["entries"])
        state: dict[str, dict[str, Any]] = {}
        for entry in data["entries"]:
            if entry["action"] == "register":
                state[entry["handle_id"]] = entry
            elif entry["action"] in {"revoke", "destroy"}:
                state.pop(entry["handle_id"], None)
        return tuple(state.values())

    def _append(self, entry: dict[str, Any]) -> str:
        data = self._read()
        self._verify_chain(data["entries"])
        previous = data["entries"][-1]["entry_hash"] if data["entries"] else "0" * 64
        entry["prev_hash"] = previous
        entry["entry_hash"] = _sha256_bytes(_canonical(entry))
        data["entries"].append(entry)
        self._write(data)
        return entry["entry_hash"]

    def _read(self) -> dict[str, Any]:
        try:
            raw = self._path.read_bytes()
        except OSError as exc:
            raise CngKekValidationError(f"registry is unreadable ({exc})") from exc
        if len(raw) > 4 * 1024 * 1024:
            raise CngKekValidationError("registry exceeds the size limit")
        try:
            data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CngKekValidationError("registry is not valid JSON") from exc
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
            raise CngKekValidationError("registry payload is malformed")
        return data

    def _write(self, data: dict[str, Any]) -> None:
        body = json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_name(f"{self._path.name}.{uuid.uuid4().hex}.tmp")
        try:
            with tmp.open("wb") as stream:
                stream.write(body)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, self._path)
        finally:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass

    def _verify_chain(self, entries: list[dict[str, Any]]) -> None:
        previous = "0" * 64
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != self._ALLOWED_ENTRY_FIELDS:
                raise CngKekValidationError("registry entry fields are invalid")
            probe = {key: value for key, value in entry.items() if key != "entry_hash"}
            entry_hash = _sha256_bytes(_canonical(probe))
            if entry["prev_hash"] != previous or entry["entry_hash"] != entry_hash:
                raise CngKekValidationError("registry hash chain is invalid (tampered?)")
            previous = entry["entry_hash"]


def _canonical(mapping: dict[str, Any]) -> bytes:
    return json.dumps(
        mapping, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CngKekValidationError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


__all__ = [
    "CngKekError",
    "CngKekHelperError",
    "CngKekReference",
    "CngKekStore",
    "CngKekUnavailableError",
    "CngKekValidationError",
    "CngProtectedKeyHandle",
    "CngWrappedKeyRegistry",
    "KEK_NAME_RE",
    "KEK_PREFIX",
    "SM2_KEY_ALGORITHM_OID",
]
