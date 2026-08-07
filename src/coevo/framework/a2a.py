"""US-16-AC-6: A2A wire 0.1 and policy_ref three-part binding (CTAF §7.3 / M5).

An :class:`A2aMessage` is a pure-data A2A envelope that rides on the
``.agent`` v1.0 encrypted package (wire stays byte-identical, T6-guarded).
The ``policy_ref`` three-part binding (spec_hash + signer-certificate
fingerprint + SM2 signature) is verified with the §7.3.3 five-step sequence;
the signer public key always comes from the certificate chain, never from
the message itself.  Business payloads larger than 64 KiB must be split into
``RESULT_SUBMISSION`` packages referenced by ``payload_ref`` (AC-6.4).

L15: standard library only, no third-party runtime dependency.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from src.coevo.framework.capability import CapabilityValidationError, resolve_capability
from src.coevo.framework.manifest_checker import _InvalidManifest, manifest_spec_hash

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX = frozenset("0123456789abcdefABCDEF")
_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

ENVELOPE_MAX_BYTES = 64 * 1024  # protocol §7.1 parity
# SM2 signatures are 64 bytes (128 hex chars); 1024 hex chars leaves generous
# headroom for future algorithms while keeping envelopes bounded (AC-6.1).
SIGNATURE_MAX_HEX_LEN = 1024
A2A_PROJECTION_KEYS = frozenset(
    {
        "accepted",
        "trace_id",
        "sender_cert_id",
        "purpose",
        "failure_reason",
    }
)


class A2aValidationError(Exception):
    """Raised when an A2A message or binding violates the invariants."""


@dataclass(frozen=True)
class PolicyRef:
    """§7.3.2 three-part policy reference."""

    spec_hash: str
    signer_cert_fingerprint: str
    signature: str  # hex


@dataclass(frozen=True)
class A2aMessage:
    """§7.3 A2A envelope carried by a `.agent` v1.0 package."""

    task_id: str
    trace_id: str
    sender_cert_id: str
    recipient_cert_id: str
    sequence_no: int
    business_correlation_key: str
    purpose: str
    policy_ref: PolicyRef
    payload_ref: str
    created_at: str

    def to_audit_record(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "sender_cert_id": self.sender_cert_id,
            "recipient_cert_id": self.recipient_cert_id,
            "sequence_no": self.sequence_no,
            "business_correlation_key": self.business_correlation_key,
            "purpose": self.purpose,
            "payload_ref": self.payload_ref,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class A2aVerificationResult:
    accepted: bool
    trace_id: str
    sender_cert_id: str
    purpose: str
    failure_reason: str | None

    def to_audit_record(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "trace_id": self.trace_id,
            "sender_cert_id": self.sender_cert_id,
            "purpose": self.purpose,
            "failure_reason": self.failure_reason,
        }


@runtime_checkable
class CertificateResolver(Protocol):
    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None: ...


@runtime_checkable
class SignatureVerifier(Protocol):
    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool: ...


def validate_a2a(message: A2aMessage) -> None:
    """Validate every A2A field (pure, fail-closed)."""

    if not isinstance(message, A2aMessage):
        raise A2aValidationError("message must be an A2aMessage instance")
    for label, value in (
        ("task_id", message.task_id),
        ("sender_cert_id", message.sender_cert_id),
        ("recipient_cert_id", message.recipient_cert_id),
        ("payload_ref", message.payload_ref),
    ):
        if not isinstance(value, str) or not _SAFE_ID.match(value):
            raise A2aValidationError(f"{label} must be a safe-id")
    if not _HEX64.match(message.trace_id):
        raise A2aValidationError("trace_id must be a 64-hex string")
    if type(message.sequence_no) is not int or message.sequence_no < 0:
        raise A2aValidationError("sequence_no must be a non-negative integer")
    if not isinstance(message.business_correlation_key, str) or not message.business_correlation_key:
        raise A2aValidationError("business_correlation_key is required")
    if not _ISO_UTC_Z.match(message.created_at):
        raise A2aValidationError(
            "created_at must be ISO-8601 UTC with trailing Z (L7)"
        )
    try:
        resolve_capability(message.purpose)
    except CapabilityValidationError as exc:
        raise A2aValidationError(str(exc)) from exc
    _validate_policy_ref(message.policy_ref)


def _validate_policy_ref(ref: PolicyRef) -> None:
    if not isinstance(ref, PolicyRef):
        raise A2aValidationError("policy_ref must be a PolicyRef instance")
    if not _HEX64.match(ref.spec_hash):
        raise A2aValidationError("policy_ref.spec_hash must be a 64-hex string")
    if not _HEX64.match(ref.signer_cert_fingerprint):
        raise A2aValidationError(
            "policy_ref.signer_cert_fingerprint must be a 64-hex string"
        )
    if not ref.signature or len(ref.signature) % 2 != 0:
        raise A2aValidationError("policy_ref.signature must be hex-encoded")
    if len(ref.signature) > SIGNATURE_MAX_HEX_LEN:
        raise A2aValidationError(
            f"policy_ref.signature exceeds {SIGNATURE_MAX_HEX_LEN} hex chars"
        )
    if not all(c in _HEX for c in ref.signature):
        raise A2aValidationError("policy_ref.signature must be hex-encoded")


def verify_policy_ref(
    message: A2aMessage,
    *,
    manifest_bytes: bytes,
    cert_resolver: CertificateResolver,
    signature_verifier: SignatureVerifier,
) -> A2aVerificationResult:
    """§7.3.3 five-step policy_ref verification (pure, fail-closed)."""

    def reject(reason: str) -> A2aVerificationResult:
        return A2aVerificationResult(
            accepted=False,
            trace_id=message.trace_id,
            sender_cert_id=message.sender_cert_id,
            purpose=message.purpose,
            failure_reason=reason,
        )

    try:
        validate_a2a(message)
        ref = message.policy_ref
        # Step 1/2: resolve the signer certificate from the chain and
        # confirm the fingerprint matches its DER digest.
        try:
            cert_der = cert_resolver.resolve_by_fingerprint(ref.signer_cert_fingerprint)
        except Exception as exc:  # noqa: BLE001 - injected resolver fails closed
            return reject(f"certificate resolution failed: {type(exc).__name__}")
        if cert_der is None:
            return reject("signer certificate not found in the certificate chain")
        if not isinstance(cert_der, bytes) or not cert_der:
            return reject("signer certificate must be non-empty bytes")
        if hashlib.sha256(cert_der).hexdigest() != ref.signer_cert_fingerprint:
            return reject("signer_cert_fingerprint does not match the resolved certificate")
        # Step 3: spec_hash must equal the canonical manifest hash
        # (excluding self-referential fields).
        try:
            computed = manifest_spec_hash(manifest_bytes)
        except _InvalidManifest as exc:
            return reject(f"manifest canonicalization failed: {exc}")
        except (RecursionError, MemoryError, ValueError) as exc:
            # Fail closed on pathological manifests (deep nesting / huge
            # integers) instead of leaking an exception out of the contract.
            return reject(
                f"manifest canonicalization failed: {type(exc).__name__}"
            )
        if computed != ref.spec_hash:
            return reject("policy_ref.spec_hash does not match the sender manifest")
        # Step 4: SM2 signature over (spec_hash | fingerprint) with the
        # certificate-derived public key.
        binding = (ref.spec_hash + ref.signer_cert_fingerprint).encode("ascii")
        signature = bytes.fromhex(ref.signature)
        try:
            signature_ok = signature_verifier.verify(cert_der, binding, signature)
        except Exception as exc:  # noqa: BLE001 - injected verifier fails closed
            return reject(f"signature verification failed: {type(exc).__name__}")
        if not signature_ok:
            return reject("policy_ref signature verification failed")
    except A2aValidationError as exc:
        return reject(str(exc))
    # Step 5: accepted.
    return A2aVerificationResult(
        accepted=True,
        trace_id=message.trace_id,
        sender_cert_id=message.sender_cert_id,
        purpose=message.purpose,
        failure_reason=None,
    )


def to_agent_fields(message: A2aMessage) -> dict[str, object]:
    """§7.3.1 A2A → `.agent` payload field mapping."""

    validate_a2a(message)
    return {
        "package_id": message.task_id,
        "trace_id": message.trace_id,
        "sender_cert_id": message.sender_cert_id,
        "recipient_cert_id": message.recipient_cert_id,
        "sequence_no": message.sequence_no,
        "business_correlation_key": message.business_correlation_key,
        "task_type": message.purpose,
        "policy_ref": {
            "spec_hash": message.policy_ref.spec_hash,
            "signer_cert_fingerprint": message.policy_ref.signer_cert_fingerprint,
            "signature": message.policy_ref.signature,
        },
        "payload_ref": message.payload_ref,
        "created_at": message.created_at,
    }


AGENT_FIELD_KEYS = frozenset(
    {
        "package_id",
        "trace_id",
        "sender_cert_id",
        "recipient_cert_id",
        "sequence_no",
        "business_correlation_key",
        "task_type",
        "policy_ref",
        "payload_ref",
        "created_at",
    }
)


def from_agent_fields(mapping: dict[str, object]) -> A2aMessage:
    """§7.3.1 `.agent` payload fields → A2A message (fail-closed)."""

    if not isinstance(mapping, dict):
        raise A2aValidationError("agent fields must be a JSON object")
    unknown = sorted(set(mapping) - AGENT_FIELD_KEYS)
    if unknown:
        raise A2aValidationError(
            "unsupported agent field keys: " + ", ".join(unknown)
        )
    ref = mapping.get("policy_ref")
    if not isinstance(ref, dict):
        raise A2aValidationError("policy_ref must be an object")
    try:
        message = A2aMessage(
            task_id=mapping["package_id"],
            trace_id=mapping["trace_id"],
            sender_cert_id=mapping["sender_cert_id"],
            recipient_cert_id=mapping["recipient_cert_id"],
            sequence_no=mapping["sequence_no"],
            business_correlation_key=mapping["business_correlation_key"],
            purpose=mapping["task_type"],
            policy_ref=PolicyRef(
                spec_hash=ref["spec_hash"],
                signer_cert_fingerprint=ref["signer_cert_fingerprint"],
                signature=ref["signature"],
            ),
            payload_ref=mapping["payload_ref"],
            created_at=mapping["created_at"],
        )
    except (KeyError, TypeError) as exc:
        raise A2aValidationError(f"malformed agent fields: {exc}") from exc
    validate_a2a(message)
    return message


def validate_payload_size(payload_len: int, *, payload_ref: str) -> None:
    """AC-6.4: business payload > 64 KiB must use RESULT_SUBMISSION split."""

    if type(payload_len) is not int or payload_len < 0:
        raise A2aValidationError("payload_len must be a non-negative integer")
    if payload_len > ENVELOPE_MAX_BYTES:
        if not isinstance(payload_ref, str) or not _SAFE_ID.match(payload_ref):
            raise A2aValidationError(
                f"payload exceeds {ENVELOPE_MAX_BYTES} bytes: must be split via "
                "RESULT_SUBMISSION with a valid payload_ref (raising the limit "
                "requires a protocol major-version bump)"
            )
