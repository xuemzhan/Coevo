"""US-16-AC-1: deployment-point manifest-checker (CTAF §5.3).

Validates an Agent Manifest at the deployment point before an agent may be
registered for orchestration.  The canonical wire form is **canonical JSON**
(the same rules as the ``.agent`` envelope, protocol §10): UTF-8 without BOM,
lexicographically sorted keys, compact separators, ASCII-safe escapes.  YAML
is an authoring format only; conversion to canonical JSON happens offline
before :func:`check`.

Design notes (CTAF v0.4.1 §19.6):

* ``capability`` must be a member of the existing ``AgentCapability`` closed
  set (single source of truth; the CTAF §5.2 extended names are reconciled in
  milestone M1b);
* ``spec_hash`` is the SHA-256 of the canonical manifest bytes **after**
  removing the self-referential fields ``metadata.spec_hash``,
  ``policy_ref.spec_hash`` and ``policy_ref.signature`` (F5; including
  ``policy_ref.spec_hash`` in the hashed bytes would make the hash
  self-referential and uncomputable in one pass);
* ``policy_ref`` three-part binding (F8): declared spec_hash, signer-certificate
  DER fingerprint, and an SM2 signature whose public key comes from the
  certificate chain (never from the manifest itself).  Real SM2 verification is
  delegated to an injected :class:`SignatureVerifier`;
* ``policy_profile`` must be bound to a ``policy_version`` that exists in the
  deployment-point policy registry (F7);
* the checker is a pure function: certificate resolution, signature
  verification and the policy registry are injected; registration is a separate
  side effect that refuses failed results (AC-1.9).

L15: standard library only, no third-party runtime dependency.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from src.coevo.crypto.contract import ProviderScope
from src.coevo.orchestrator.models import AgentCapability

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")
_HEX = frozenset("0123456789abcdefABCDEF")

AUDIT_PROJECTION_KEYS = frozenset(
    {
        "accepted",
        "spec_hash",
        "policy_profile",
        "policy_version",
        "signed_at",
        "failure_reason",
    }
)


class ManifestValidationError(Exception):
    """Raised when a manifest cannot be validated or registered."""


class _InvalidManifest(Exception):
    """Internal fail-closed signal used while parsing/validating."""


@dataclass(frozen=True)
class AgentManifest:
    """Validated, normalized view of an Agent Manifest."""

    agent_id: str
    display_name: str
    semantic_version: str
    capability: AgentCapability
    requires_human_confirmation: bool
    crypto_scope: ProviderScope
    redact_in_audit: tuple[str, ...]
    policy_profile: str
    policy_version: str
    spec_hash: str


@dataclass(frozen=True)
class ManifestCheckInput:
    """CTAF §5.3.1 check input."""

    manifest_bytes: bytes
    # ``site_policy`` is the deployment-point Policy; the full Policy type
    # lands with US-16-AC-2.  Kept as ``Any`` until then.
    site_policy: Any = None
    trusted_anchor_pubkey: bytes = b""
    now: str = ""


@dataclass(frozen=True)
class ManifestCheckResult:
    """CTAF §5.3.2 check result."""

    accepted: bool
    validated_manifest: AgentManifest | None
    spec_hash: str
    signed_at: str
    failure_reason: str | None

    def to_audit_record(self) -> dict[str, object]:
        manifest = self.validated_manifest
        return {
            "accepted": self.accepted,
            "spec_hash": self.spec_hash,
            "policy_profile": manifest.policy_profile if manifest else None,
            "policy_version": manifest.policy_version if manifest else None,
            "signed_at": self.signed_at,
            "failure_reason": self.failure_reason,
        }


@runtime_checkable
class PolicyRegistry(Protocol):
    """Deployment-point registry of (profile, policy_version) pairs."""

    def has_policy_version(self, profile: str, version: str) -> bool: ...


@runtime_checkable
class CertificateResolver(Protocol):
    """Resolves a signer certificate DER by its SHA-256 fingerprint."""

    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None: ...


@runtime_checkable
class SignatureVerifier(Protocol):
    """Verifies an SM2 signature with a certificate-derived public key."""

    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool: ...


@dataclass
class ManifestRegistry:
    """In-memory deployment registry; only accepted results may register."""

    _agents: dict[str, AgentManifest] = field(default_factory=dict)

    def register(self, result: ManifestCheckResult) -> None:
        """Register a validated manifest; refuse anything else (AC-1.9)."""
        if not result.accepted or result.validated_manifest is None:
            raise ManifestValidationError(
                "refusing to register a manifest that failed validation"
            )
        manifest = result.validated_manifest
        if manifest.agent_id in self._agents:
            raise ManifestValidationError(
                f"agent already registered: {manifest.agent_id}"
            )
        self._agents[manifest.agent_id] = manifest

    def get(self, agent_id: str) -> AgentManifest | None:
        return self._agents.get(agent_id)


def check(
    inp: ManifestCheckInput,
    *,
    policy_registry: PolicyRegistry,
    cert_resolver: CertificateResolver,
    signature_verifier: SignatureVerifier,
) -> ManifestCheckResult:
    """Validate an Agent Manifest (pure, fail-closed)."""
    parsed: dict[str, Any] | None = None
    try:
        parsed = _parse_manifest(inp.manifest_bytes)
        manifest = _validate(
            parsed,
            inp=inp,
            policy_registry=policy_registry,
            cert_resolver=cert_resolver,
            signature_verifier=signature_verifier,
        )
    except _InvalidManifest as exc:
        declared = _declared_spec_hash(parsed) if parsed is not None else ""
        return ManifestCheckResult(
            accepted=False,
            validated_manifest=None,
            spec_hash=declared,
            signed_at=inp.now,
            failure_reason=str(exc),
        )
    return ManifestCheckResult(
        accepted=True,
        validated_manifest=manifest,
        spec_hash=manifest.spec_hash,
        signed_at=inp.now,
        failure_reason=None,
    )


def _parse_manifest(data: bytes) -> dict[str, Any]:
    if not isinstance(data, bytes):
        raise _InvalidManifest("manifest_bytes must be bytes")
    if data.startswith(b"\xef\xbb\xbf"):
        raise _InvalidManifest("BOM is not allowed in canonical manifest bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _InvalidManifest(f"manifest is not valid UTF-8: {exc}") from exc
    try:
        parsed = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise _InvalidManifest(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise _InvalidManifest("manifest must be a JSON object")
    return parsed


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise _InvalidManifest(f"duplicate key in manifest: {key!r}")
        out[key] = value
    return out


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _strip_self_referential(parsed: dict[str, Any]) -> dict[str, Any]:
    """Deep copy without the three self-referential hash/signature fields."""

    stripped = copy.deepcopy(parsed)
    metadata = stripped.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("spec_hash", None)
    policy_ref = stripped.get("policy_ref")
    if isinstance(policy_ref, dict):
        policy_ref.pop("spec_hash", None)
        policy_ref.pop("signature", None)
    return stripped


def _declared_spec_hash(parsed: dict[str, Any]) -> str:
    metadata = parsed.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("spec_hash")
        if isinstance(value, str) and value:
            return value
    return ""


def _require_str(mapping: dict[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise _InvalidManifest(f"{label} must be a non-empty string")
    return value


def _is_hex(value: str) -> bool:
    return bool(value) and len(value) % 2 == 0 and all(c in _HEX for c in value)


def _validate(
    parsed: dict[str, Any],
    *,
    inp: ManifestCheckInput,
    policy_registry: PolicyRegistry,
    cert_resolver: CertificateResolver,
    signature_verifier: SignatureVerifier,
) -> AgentManifest:
    metadata = parsed.get("metadata")
    if not isinstance(metadata, dict):
        raise _InvalidManifest("metadata must be an object")
    agent_id = _require_str(metadata, "agent_id", "metadata.agent_id")
    if not _SAFE_ID.match(agent_id):
        raise _InvalidManifest("agent_id must be a safe-id")
    display_name = _require_str(metadata, "display_name", "metadata.display_name")
    semantic_version = _require_str(
        metadata, "semantic_version", "metadata.semantic_version"
    )

    spec = parsed.get("spec")
    if not isinstance(spec, dict):
        raise _InvalidManifest("spec must be an object")
    capability_raw = _require_str(spec, "capability", "spec.capability")
    try:
        capability = AgentCapability(capability_raw)
    except ValueError:
        raise _InvalidManifest(
            f"capability outside AgentCapability closed set: {capability_raw!r}"
        ) from None
    rhc = spec.get("requires_human_confirmation", True)
    if not isinstance(rhc, bool):
        raise _InvalidManifest("spec.requires_human_confirmation must be a bool")

    security = parsed.get("security")
    if not isinstance(security, dict):
        raise _InvalidManifest("security must be an object")
    scope_raw = _require_str(security, "crypto_scope", "security.crypto_scope")
    try:
        crypto_scope = ProviderScope(scope_raw)
    except ValueError:
        raise _InvalidManifest(
            f"crypto_scope outside ProviderScope closed set: {scope_raw!r}"
        ) from None

    audit = parsed.get("audit", {})
    if audit is None:
        audit = {}
    if not isinstance(audit, dict):
        raise _InvalidManifest("audit must be an object")
    redact_raw = audit.get("redact_in_audit", [])
    if not isinstance(redact_raw, list) or not all(
        isinstance(item, str) for item in redact_raw
    ):
        raise _InvalidManifest("audit.redact_in_audit must be a list of strings")
    outside = sorted(set(redact_raw) - set(AUDIT_PROJECTION_KEYS))
    if outside:
        raise _InvalidManifest(
            "redact_in_audit references fields outside the audit projection: "
            + ", ".join(outside)
        )
    redact = tuple(redact_raw)

    profile = _require_str(parsed, "policy_profile", "policy_profile")
    version = _require_str(parsed, "policy_version", "policy_version")
    if not policy_registry.has_policy_version(profile, version):
        raise _InvalidManifest(
            f"policy_profile {profile!r} version {version!r} "
            "not present in the deployment policy registry"
        )

    declared = _declared_spec_hash(parsed)
    computed = hashlib.sha256(
        _canonical_bytes(_strip_self_referential(parsed))
    ).hexdigest()
    if declared != computed:
        raise _InvalidManifest(
            "spec_hash does not match the canonical manifest bytes "
            "(excluding self-referential fields)"
        )

    policy_ref = parsed.get("policy_ref")
    if not isinstance(policy_ref, dict):
        raise _InvalidManifest("policy_ref must be an object")
    ref_spec_hash = _require_str(
        policy_ref, "spec_hash", "policy_ref.spec_hash"
    )
    cert_fp = _require_str(
        policy_ref, "signer_cert_fingerprint", "policy_ref.signer_cert_fingerprint"
    )
    signature_hex = _require_str(policy_ref, "signature", "policy_ref.signature")
    if ref_spec_hash != declared:
        raise _InvalidManifest("policy_ref.spec_hash does not match manifest spec_hash")
    if not _is_hex(signature_hex):
        raise _InvalidManifest("policy_ref.signature must be hex-encoded")

    cert_der = cert_resolver.resolve_by_fingerprint(cert_fp)
    if cert_der is None:
        raise _InvalidManifest("signer certificate not found in the certificate chain")
    if not isinstance(cert_der, bytes) or not cert_der:
        raise _InvalidManifest("signer certificate must be non-empty bytes")
    if hashlib.sha256(cert_der).hexdigest() != cert_fp:
        raise _InvalidManifest(
            "signer_cert_fingerprint does not match the resolved certificate"
        )
    binding = (ref_spec_hash + cert_fp).encode("ascii")
    signature = bytes.fromhex(signature_hex)
    if not signature_verifier.verify(cert_der, binding, signature):
        raise _InvalidManifest("policy_ref signature verification failed")

    if not isinstance(inp.trusted_anchor_pubkey, bytes) or not inp.trusted_anchor_pubkey:
        raise _InvalidManifest("trusted_anchor_pubkey must be non-empty bytes")

    return AgentManifest(
        agent_id=agent_id,
        display_name=display_name,
        semantic_version=semantic_version,
        capability=capability,
        requires_human_confirmation=rhc,
        crypto_scope=crypto_scope,
        redact_in_audit=redact,
        policy_profile=profile,
        policy_version=version,
        spec_hash=declared,
    )
