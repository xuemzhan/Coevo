"""Offline private-key storage interface for US-0-AC-2.

Design contract (binding across Coevo):

* :class:`PrivateKeyReference` carries **metadata only**: CNG key name
  (``key_id``), algorithm OID, public-key digest, validity range,
  bound certificate id, revocation flag, and a truncated handle token
  hint for debug logs. It MUST NOT carry, accept, or expose raw
  private-key bytes anywhere in the public surface (``__repr__``,
  ``__str__``, ``__bytes__``, ``__getstate__``, ``__safe_dict__``).

* :class:`PrivateKeyStore` is a ``typing.Protocol``.
  :class:`WindowsPrivateKeyStore` fulfils it by delegating to
  ``scripts/store_private_key.ps1`` (which in turn calls Windows CNG
  / Smart Card). Tests substitute ``InMemoryPrivateKeyStore`` (or
  their own fake) 闁?production code MUST never instantiate
  ``WindowsPrivateKeyStore`` from request data.

* :class:`PrivateKeyService` enforces policy: validity window,
  revocation, atomic destroy, hash-chained audit.

The privacy/integrity boundary is: the helper process performs the
cryptographic operation; only the **cryptographic result** (HMAC,
signature, SM2 public-key-encapsulation output, etc.) flows back to
Python. Private-key bytes NEVER leave Windows CNG.

Note on US-0 vs US-5 ordering: this AC defines the storage boundary.
The US-5 `.agent` envelope will read via this interface
(``PrivateKeyService.use``) but US-5 stays ``blocked`` until actual
CNG keys exist in ``Cert:\\CurrentUser\\My`` (next round, slice E).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Protocol

ROOT = Path(__file__).resolve().parents[3]
STORE_HELPER = ROOT / "scripts" / "store_private_key.ps1"

HANDLE_PREFIX = "CoevoPrivateKey-"
HANDLE_RE = re.compile(r"^CoevoPrivateKey-[0-9a-fA-F]{32}$")
PUBLIC_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
CREATION_AUDIT_ID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")
ALGORITHM_OID_RE = re.compile(r"^[0-9.]+$")

ALLOWED_PAYLOAD_FIELDS = frozenset({
    "certificate_id", "key_id", "algorithm_oid", "key_public_sha256",
    "valid_from", "valid_to", "creation_audit_id", "revoked",
})
PRIVATE_KEY_BYTES_HEURISTIC = ("PRIVATE KEY", "BEGIN ENCRYPTED", "BEGIN EC PRIVATE")


class PrivateKeyError(RuntimeError):
    """Base class for all errors raised by the private-key storage interface."""


class PrivateKeyValidationError(PrivateKeyError, ValueError):
    """A handle payload or :class:`PrivateKeyReference` is malformed."""


class PrivateKeyHandleError(PrivateKeyError):
    """The Windows CNG / Smart Card helper rejected a store or destroy operation."""


class PrivateKeyHandleUnavailableError(PrivateKeyHandleError):
    """The handle does not exist (or has already been destroyed)."""


class PrivateKeyRevokedError(PrivateKeyHandleError):
    """The handle exists but has been revoked."""


class PrivateKeyUsageError(PrivateKeyError):
    """A ``use`` call failed because of validity, revocation, or input policy."""


@dataclass(frozen=True)
class PrivateKeyReference:
    """Immutable, log-safe description of a private-key handle.

    Constructed once at store-time and reused. Mutating a field would
    defeat the tamper-evident audit chain, so ``frozen=True`` enforces
    immutability and callers that need to flip the revocation flag
    obtain a new instance via :func:`dataclasses.replace`.
    """

    key_id: str
    algorithm_oid: str
    key_public_sha256: str
    valid_from: datetime
    valid_to: datetime
    bound_certificate_id: str
    revoked: bool
    handle_token_hint: str

    def __post_init__(self) -> None:
        if not HANDLE_RE.match(self.key_id):
            raise PrivateKeyValidationError("private-key handle identifier is malformed")
        if not ALGORITHM_OID_RE.match(self.algorithm_oid):
            raise PrivateKeyValidationError("algorithm OID is malformed")
        if not PUBLIC_DIGEST_RE.match(self.key_public_sha256):
            raise PrivateKeyValidationError("public-key digest is malformed")
        if self.valid_from.tzinfo is None or self.valid_to.tzinfo is None:
            raise PrivateKeyValidationError("validity timestamps must include timezone")
        if self.valid_from >= self.valid_to:
            raise PrivateKeyValidationError("validity range is empty or inverted")
        if len(self.handle_token_hint) > 16:
            raise PrivateKeyValidationError("handle token hint must be truncated to <=16 chars")

    def __safe_dict__(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "algorithm_oid": self.algorithm_oid,
            "key_public_sha256": self.key_public_sha256,
            "valid_from": self.valid_from.isoformat().replace("+00:00", "Z"),
            "valid_to": self.valid_to.isoformat().replace("+00:00", "Z"),
            "bound_certificate_id": self.bound_certificate_id,
            "revoked": self.revoked,
            "handle_token_hint": self.handle_token_hint,
        }

    def __repr__(self) -> str:
        return (
            f"PrivateKeyReference(key_id={self.key_id}, "
            f"certificate_id={self.bound_certificate_id}, "
            f"public_sha256={self.key_public_sha256[:12]}..., "
            f"valid_until={self.valid_to.isoformat().replace('+00:00', 'Z')}, "
            f"revoked={self.revoked})"
        )


def format_handle(uuid_id: str) -> str:
    """Build a handle identifier from a UUID-shaped ``key_id``."""
    try:
        normalized = str(uuid.UUID(str(uuid_id))).replace("-", "").lower()
    except (ValueError, AttributeError, TypeError) as exc:
        raise PrivateKeyValidationError("private-key handle source is not a valid UUID") from exc
    return f"{HANDLE_PREFIX}{normalized}"


def validate_handle_payload(payload: Any) -> dict:
    """Strictly validate a ``store`` payload 闁?fail-closed for any unknown / sensitive field."""
    if not isinstance(payload, Mapping):
        raise PrivateKeyValidationError("private-key handle payload must be an object")
    unknown = set(payload) - ALLOWED_PAYLOAD_FIELDS
    if unknown:
        raise PrivateKeyValidationError(
            "unsupported private-key handle fields: " + ", ".join(sorted(map(str, unknown)))
        )
    missing = ALLOWED_PAYLOAD_FIELDS - set(payload)
    if missing:
        raise PrivateKeyValidationError(
            "missing private-key handle fields: " + ", ".join(sorted(missing))
        )
    for forbidden in PRIVATE_KEY_BYTES_HEURISTIC:
        for value in payload.values():
            if isinstance(value, str) and forbidden in value.upper():
                raise PrivateKeyValidationError("private-key material must not appear in handle payload")
            if isinstance(value, (bytes, bytearray)) and forbidden in bytes(value).upper():
                raise PrivateKeyValidationError("private-key material must not appear in handle payload")
    if not isinstance(payload["certificate_id"], str) or not payload["certificate_id"].strip():
        raise PrivateKeyValidationError("certificate_id is required")
    try:
        handle = format_handle(payload["key_id"])
    except PrivateKeyValidationError as exc:
        raise PrivateKeyValidationError(str(exc)) from exc
    if not ALGORITHM_OID_RE.match(str(payload["algorithm_oid"])):
        raise PrivateKeyValidationError("algorithm_oid is malformed")
    digest = str(payload["key_public_sha256"])
    # Allow empty string: callers may have a pre-claim digest that the
    # Windows CNG / Smart Card helper must verify or overwrite. Reject
    # everything else that doesn't match the strict 64-hex format.
    if digest and not PUBLIC_DIGEST_RE.match(digest):
        raise PrivateKeyValidationError("key_public_sha256 is malformed")
    if not CREATION_AUDIT_ID_RE.match(str(payload["creation_audit_id"])):
        raise PrivateKeyValidationError("creation_audit_id must be a UUID")
    if not isinstance(payload["revoked"], bool):
        raise PrivateKeyValidationError("revoked flag must be a boolean")
    for instant_field in ("valid_from", "valid_to"):
        raw = payload[instant_field]
        if not isinstance(raw, str):
            raise PrivateKeyValidationError(f"{instant_field} must be ISO-8601")
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise PrivateKeyValidationError(f"{instant_field} is not ISO-8601") from exc
        if parsed.tzinfo is None:
            raise PrivateKeyValidationError(f"{instant_field} must include timezone")
    result = dict(payload)
    result["key_id"] = handle
    return result


class PrivateKeyStore(Protocol):
    """Storage abstraction for non-exportable private keys.

    Implementations MUST keep key material inside Windows CNG / a
    Smart Card. Only the cryptographic output (signature / decrypted
    session key) returns from ``use``. ``verify_handle`` MUST be a
    metadata-only round trip (no key-usage event recorded).
    """

    def store(self, certificate_id: str, payload: Mapping[str, Any], *, parent_pinned_thumbprint: str | None = None) -> PrivateKeyReference:
        ...

    def use(self, reference: PrivateKeyReference, payload: bytes) -> bytes:
        ...

    def destroy(self, reference: PrivateKeyReference) -> None:
        ...

    def verify_handle(self, reference: PrivateKeyReference) -> None:
        ...


def _powershell_executable() -> str:
    exe = os.environ.get("COEVO_POWERSHELL_PATH")
    if exe and Path(exe).is_absolute():
        return exe
    fallback = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if fallback.is_file():
        return str(fallback)
    raise PrivateKeyHandleError("Windows PowerShell is unavailable")


class WindowsPrivateKeyStore:
    """Delegate all key operations to ``scripts/store_private_key.ps1``.

    The PowerShell helper performs the actual CNG / Smart Card work
    (``CngKey.Create`` with ``ExportPolicy=None`` for private signing
    material; ``CngKey.Open`` + ``CngKey.Delete`` for revocation /
    retirement; etc.). Helper output is a JSON envelope describing
    either the freshly stored reference or the cryptographic result;
    private-key bytes NEVER cross the process boundary.
    """

    def __init__(self, helper_path: Path | None = None) -> None:
        self.helper_path = Path(helper_path) if helper_path is not None else STORE_HELPER
        if not self.helper_path.is_file():
            raise PrivateKeyHandleError("controlled private-key helper is unavailable")

    def _run(self, action: str, **arguments: Any) -> dict:
        body = json.dumps({"action": action, "arguments": arguments}, separators=(",", ":"))
        process = subprocess.run(
            [
                _powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", str(self.helper_path),
            ],
            cwd=ROOT, input=body.encode("utf-8"), capture_output=True,
            timeout=30,
        )
        if process.returncode:
            raise PrivateKeyHandleError(
                f"private-key helper failed: action={action} exit={process.returncode} "
                f"stderr={process.stderr.decode('utf-8', errors='replace').strip()[:400]}"
            )
        try:
            text = process.stdout.decode("utf-8", errors="replace").strip()
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            raise PrivateKeyHandleError(
                f"private-key helper returned invalid JSON: stdout={process.stdout.decode('utf-8', errors='replace').strip()[:200]}"
            ) from exc
        if not isinstance(result, dict) or result.get("schema_version") != "1.0":
            raise PrivateKeyHandleError("private-key helper output failed policy checks")
        return result

    def store(self, certificate_id: str, payload: Mapping[str, Any], *, parent_pinned_thumbprint: str | None = None) -> PrivateKeyReference:
        sanitized = validate_handle_payload(dict(payload))
        sanitized["certificate_id"] = certificate_id
        result = self._run("Store", payload=sanitized, parent_pinned_thumbprint=parent_pinned_thumbprint)
        return _reference_from_helper(result, certificate_id)

    def use(self, reference: PrivateKeyReference, payload: bytes) -> bytes:
        if not isinstance(payload, (bytes, bytearray)):
            raise PrivateKeyUsageError("private-key usage payload must be bytes")
        try:
            with tempfile.TemporaryDirectory(prefix="coevo-pkcs8-use-") as tmp:
                payload_path = Path(tmp) / "payload.bin"
                payload_path.write_bytes(bytes(payload))
                result = self._run(
                    "Use",
                    handle=reference.key_id,
                    public_digest=reference.key_public_sha256,
                    algorithm_oid=reference.algorithm_oid,
                    payload_path=str(payload_path),
                )
                signature_b64 = result.get("result", {}).get("signature_base64")
                if not signature_b64:
                    raise PrivateKeyHandleError("private-key helper returned no signature")
                return base64.b64decode(signature_b64, validate=True)
        except subprocess.TimeoutExpired as exc:
            raise PrivateKeyHandleError("private-key helper timed out") from exc

    def destroy(self, reference: PrivateKeyReference) -> None:
        try:
            self._run("Destroy", handle=reference.key_id, public_digest=reference.key_public_sha256)
        except PrivateKeyHandleError as exc:
            if "missing" in str(exc).lower():
                raise PrivateKeyHandleUnavailableError(str(exc)) from exc
            raise

    def verify_handle(self, reference: PrivateKeyReference) -> None:
        self._run("VerifyHandle", handle=reference.key_id, public_digest=reference.key_public_sha256)


def _reference_from_helper(result: dict, certificate_id: str) -> PrivateKeyReference:
    reference = result.get("reference")
    if not isinstance(reference, dict):
        raise PrivateKeyHandleError("private-key helper did not return a reference")
    return PrivateKeyReference(
        key_id=str(reference["key_id"]),
        algorithm_oid=str(reference["algorithm_oid"]),
        key_public_sha256=str(reference["key_public_sha256"]),
        valid_from=datetime.fromisoformat(str(reference["valid_from"]).replace("Z", "+00:00")).astimezone(UTC),
        valid_to=datetime.fromisoformat(str(reference["valid_to"]).replace("Z", "+00:00")).astimezone(UTC),
        bound_certificate_id=certificate_id,
        revoked=bool(reference.get("revoked", False)),
        handle_token_hint=str(reference.get("handle_token_hint", ""))[:16],
    )


class PrivateKeyService:
    """Policy layer on top of a :class:`PrivateKeyStore`.

    NOTE: the underlying backend is exposed as ``_backend`` (private)
    so the public ``store``/``use``/``destroy``/``revoke`` methods do
    not shadow the backend attribute.
    """

    def __init__(self, store: PrivateKeyStore) -> None:
        self._backend = store
        self.audit_trail: list[dict[str, Any]] = []
        self._previous_hash = "0" * 64

    def _record(self, *, action: str, actor_id: str, reference: PrivateKeyReference | None,
                request_id: str | None, result: str, **extra: Any) -> None:
        event: dict[str, Any] = {
            "action": action,
            "actor_id": actor_id,
            "request_id": request_id or "-",
            "result": result,
            "key_id": reference.key_id if reference else "-",
            "certificate_id": reference.bound_certificate_id if reference else "-",
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
        event.update(extra)
        serialized = json.dumps(event, sort_keys=True, separators=(",", ":"))
        event["event_hash"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        event["previous_hash"] = self._previous_hash
        self._previous_hash = event["event_hash"]
        self.audit_trail.append(event)

    def store(self, certificate_id: str, payload: Mapping[str, Any], *,
              actor_id: str = "system", request_id: str | None = None) -> PrivateKeyReference:
        self._require_actor(actor_id)
        try:
            reference = self._backend.store(certificate_id, payload)
        except PrivateKeyHandleError as exc:
            self._record(action="private_key_store", actor_id=actor_id,
                         request_id=request_id, reference=None,
                         result="rejected", reason=str(exc))
            raise
        self._record(action="private_key_store", actor_id=actor_id,
                     request_id=request_id, reference=reference, result="success")
        return reference

    def use(self, reference: PrivateKeyReference, payload: bytes, *,
            trusted_time: datetime, actor_id: str = "system",
            request_id: str | None = None) -> bytes:
        self._require_actor(actor_id)
        if trusted_time.tzinfo is None:
            raise PrivateKeyUsageError("trusted_time must include timezone information")
        current = trusted_time.astimezone(UTC)
        if current < reference.valid_from or current >= reference.valid_to:
            self._record(action="private_key_use", actor_id=actor_id,
                         request_id=request_id, reference=reference,
                         result="rejected", reason="outside_validity_window")
            raise PrivateKeyUsageError("trusted time is outside the private-key validity window")
        if reference.revoked:
            self._record(action="private_key_use", actor_id=actor_id,
                         request_id=request_id, reference=reference,
                         result="rejected", reason="revoked")
            raise PrivateKeyUsageError("private-key reference has been revoked")
        try:
            result = self._backend.use(reference, payload)
        except PrivateKeyHandleUnavailableError:
            self._record(action="private_key_use", actor_id=actor_id,
                         request_id=request_id, reference=reference,
                         result="rejected", reason="handle_unavailable")
            raise
        except PrivateKeyRevokedError:
            self._record(action="private_key_use", actor_id=actor_id,
                         request_id=request_id, reference=reference,
                         result="rejected", reason="store_reported_revoked")
            raise PrivateKeyUsageError("private-key store reports the handle is revoked") from None
        if not isinstance(result, (bytes, bytearray)) or not result:
            raise PrivateKeyUsageError("private-key store returned an empty or invalid result")
        self._record(action="private_key_use", actor_id=actor_id,
                     request_id=request_id, reference=reference,
                     result="success",
                     result_digest=hashlib.sha256(bytes(result)).hexdigest())
        return bytes(result)

    def revoke(self, reference: PrivateKeyReference, *, actor_id: str,
               reason: str = "") -> PrivateKeyReference:
        """Return a new :class:`PrivateKeyReference` flagged as revoked.

        Because the reference is frozen, callers MUST adopt the new
        instance. The Store layer is also informed via
        :func:`PrivateKeyStore.verify_handle` (next round, when US-5
        wires in revocation propagation through the helper).
        """
        self._require_actor(actor_id)
        if not reason:
            raise PrivateKeyValidationError("revocation reason is required")
        revoked = replace(reference, revoked=True)
        self._record(action="private_key_revoke", actor_id=actor_id,
                     request_id=None, reference=revoked,
                     result="success", reason=reason)
        return revoked

    def destroy(self, reference: PrivateKeyReference, *, actor_id: str) -> None:
        self._require_actor(actor_id)
        try:
            self._backend.destroy(reference)
        except PrivateKeyHandleError:
            self._record(action="private_key_destroy", actor_id=actor_id,
                         request_id=None, reference=reference,
                         result="rejected")
            raise
        self._record(action="private_key_destroy", actor_id=actor_id,
                     request_id=None, reference=reference,
                     result="success")

    @staticmethod
    def _require_actor(actor_id: str) -> None:
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise PrivateKeyValidationError("actor_id is required and must be a non-empty string")

    def verify_audit_chain(self) -> bool:
        previous = "0" * 64
        for event in self.audit_trail:
            snapshot = {key: event[key] for key in event if key not in {"event_hash", "previous_hash"}}
            expected = hashlib.sha256(
                json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            if event["previous_hash"] != previous or event["event_hash"] != expected:
                return False
            previous = event["event_hash"]
        return True


__all__ = [
    "PrivateKeyError",
    "PrivateKeyHandleError",
    "PrivateKeyHandleUnavailableError",
    "PrivateKeyRevokedError",
    "PrivateKeyUsageError",
    "PrivateKeyValidationError",
    "PrivateKeyReference",
    "PrivateKeyStore",
    "PrivateKeyService",
    "WindowsPrivateKeyStore",
    "format_handle",
    "validate_handle_payload",
]
