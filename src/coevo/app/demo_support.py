"""app.demo_support - demo-only support: PKI profile bootstrap, in-memory demo signer/freshness stand-ins and sample inputs. Explicitly NOT production code."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 演示专用支撑（不进生产路径）：SM2 测试 PKI 引导、内存/文件模拟
# 签名与新鲜度权威（HMAC）、样例项目输入。关键不变量：不携带私钥字节，
# 仅测试环境使用。

from __future__ import annotations

import hashlib
import hmac
import os
import subprocess
import uuid
from pathlib import Path
from typing import Any
from src.coevo.identity.audit_anchor import AuditAnchorError, canonical
from src.coevo.timefmt import now_utc_iso_z

ROOT = Path(__file__).resolve().parents[3]

DEMO_PROFILE: str = "demo"

DEMO_REVISION: str = "PRJ001-R0001"

DEMO_ACTOR: str = "u.pm"

class _DemoAuditAnchorError(AuditAnchorError):
    pass

class DemoSigner:
    """Demo-only HMAC signer (production: WindowsCertificateSigner)."""

    def __init__(self) -> None:
        self.secret = os.urandom(32)

    def sign(self, content: bytes) -> bytes:
        return hmac.new(self.secret, content, hashlib.sha256).digest()

    def verify(self, content: bytes, signature: bytes) -> None:
        if not hmac.compare_digest(self.sign(content), signature):
            raise _DemoAuditAnchorError("demo signature mismatch")


class DemoRegistrationVerifier:
    """DEMO-ONLY registration signature verifier (explicitly NOT production).

    Returns ``True`` for any well-formed signature; the manifest-checker still
    enforces structure, capability closed set, crypto scope, spec_hash and
    policy_ref binding *format*.  Production MUST inject a real SM2 verifier
    backed by the certificate chain.
    """

    # FRAMEWORK-GAPS-7: explicit production-boundary marker. guard_registration
    # with require_production_verifier=True rejects this adapter fail-closed.
    is_production: bool = False

    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool:
        return True


class DemoRegistrationSigner:
    """DEMO-ONLY registration signer (explicitly NOT production).

    Produces a deterministic digest so the manifest's ``policy_ref.signature``
    satisfies the binding *format*; production MUST use a real SM2 signer
    whose public key is bound to the certificate chain.
    """

    def sign(self, data: bytes) -> bytes:
        return hashlib.sha256(data).digest()


class DemoRegistrationResolver:
    """DEMO-ONLY certificate resolver returning a fixed demo cert DER."""

    def __init__(self) -> None:
        self.der = b"DEMO-REGISTRATION-CERT-DER"

    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None:
        return (
            self.der
            if hashlib.sha256(self.der).hexdigest() == fingerprint_hex
            else None
        )


class DemoPolicyRegistry:
    """DEMO-ONLY policy registry (INTERACTIVE 1.0)."""

    def has_policy_version(self, profile: str, version: str) -> bool:
        return (profile, version) == ("INTERACTIVE", "1.0")


_DEMO_REGISTRATION_AGENTS: tuple[tuple[str, str], ...] = (
    ("agent.task_flow_understanding", "task_flow_understanding"),
    ("agent.task_decomposition", "task_decomposition"),
    ("agent.team_recommendation", "team_recommendation"),
    ("agent.task_package_build", "task_package_build"),
)


def register_demo_agents(
    registry: Any,
    registered: list[str] | None = None,
) -> tuple[Any, list[str]]:
    """DEMO-ONLY: register the four fixed demo agents through the framework gate.

    Each agent manifest is built with :func:`build_registration_manifest` and
    must pass :func:`guard_registration` (manifest-checker) before the agent
    enters the registry.  Explicitly NOT production: production MUST inject a
    real SM2 signer/verifier and a certificate-chain-backed resolver.

    Returns ``(registry, registered_agent_ids)``; ``registry`` is the
    immutable product registry extended with the four accepted agents.
    """

    from src.coevo.framework.integration import (
        build_registration_manifest,
        guard_registration,
    )
    from src.coevo.framework.manifest_checker import ManifestCheckInput
    from src.coevo.orchestrator.models import (
        AgentCapability,
        AgentRegistration,
        AgentSpec,
    )

    resolver = DemoRegistrationResolver()
    verifier = DemoRegistrationVerifier()
    signer = DemoRegistrationSigner()
    policy_registry = DemoPolicyRegistry()
    fingerprint = hashlib.sha256(resolver.der).hexdigest()
    registered = [] if registered is None else registered
    for agent_id, capability_name in _DEMO_REGISTRATION_AGENTS:
        capability = AgentCapability(capability_name)
        manifest_bytes = build_registration_manifest(
            agent_id,
            capability.value,
            display_name=capability.value,
            signer_cert_fingerprint=fingerprint,
            signer=signer.sign,
        )
        guard = guard_registration(
            ManifestCheckInput(
                manifest_bytes=manifest_bytes,
                trusted_anchor_pubkey=b"DEMO-ANCHOR",
            ),
            policy_registry=policy_registry,
            cert_resolver=resolver,
            signature_verifier=verifier,
            inner_register=lambda manifest: registered.append(manifest.agent_id),
        )
        if not guard.accepted:
            raise RuntimeError(
                f"framework registration gate rejected {agent_id}: {guard.reason}"
            )
        registry = registry.register(
            AgentRegistration(
                AgentSpec(
                    agent_id,
                    capability,
                    capability.value,
                    ("input",),
                    ("output",),
                )
            )
        )
    return registry, registered

class DemoFreshnessAuthority:
    """In-memory stand-in for the identity freshness authority."""

    def __init__(self) -> None:
        self._markers: dict[str, tuple[dict, bytes]] = {}
        self._known: dict[str, tuple[dict, bytes]] = {}
        self._certificates: set[str] = set()
        self._keys: set[str] = set()
        self._retired: dict[str, bytes] = {}
        self._retirements: dict[str, tuple[bytes, bytes, bytes | None]] = {}

    def create_marker(self, store_id: str, generation: int, binding: str) -> dict:
        """Create and persist a signed freshness marker."""
        token = os.urandom(20).hex().upper()
        key_id = "CoevoDemoMarker-" + os.urandom(16).hex()
        marker = {
            "store_id": store_id,
            "generation": generation,
            "binding_sha256": binding,
            "token": token,
            "key_id": key_id,
            "key_public_sha256": os.urandom(32).hex(),
            "transition_id": str(uuid.uuid4()),
        }
        stored = (dict(marker), os.urandom(32))
        self._markers[token] = stored
        self._known[token] = stored
        self._certificates.add(token)
        self._keys.add(key_id)
        return marker

    def _stored(self, marker: dict) -> tuple[dict, bytes]:
        stored = self._known.get(marker.get("token"))
        if stored is None or stored[0] != marker:
            raise _DemoAuditAnchorError("demo freshness marker mismatch")
        return stored

    def verify_marker(self, marker: dict) -> None:
        self._stored(marker)
        token = marker["token"]
        if token not in self._certificates or marker["key_id"] not in self._keys:
            raise _DemoAuditAnchorError("demo freshness marker is unavailable")

    def delete_marker(self, marker: dict) -> None:
        self._stored(marker)
        self._keys.discard(marker["key_id"])
        self._certificates.discard(marker["token"])
        self._retired[marker["token"]] = self._markers.pop(marker["token"], (None, b""))[1]

    def verify_retired(self, marker: dict) -> None:
        self._stored(marker)
        if marker["key_id"] in self._keys or marker["token"] in self._certificates:
            raise _DemoAuditAnchorError("demo retirement is incomplete")

    def sign(self, content: bytes, marker: dict) -> bytes:
        self.verify_marker(marker)
        return hmac.new(self._markers[marker["token"]][1], content, hashlib.sha256).digest()

    def verify_signature(self, content: bytes, signature: bytes, marker: dict) -> None:
        """Verify a signature against the demo authority."""
        stored = self._known.get(marker.get("token"))
        secret = stored[1] if stored is not None else self._retired.get(marker.get("token"))
        if secret is None or not hmac.compare_digest(
            hmac.new(secret, content, hashlib.sha256).digest(), signature
        ):
            raise _DemoAuditAnchorError("demo marker signature mismatch")

    def store_retirement(
        self,
        tombstone: dict,
        main_signature: bytes,
        survivor_signature: bytes | None,
    ) -> None:
        """Persist a retirement tombstone for a marker."""
        token = tombstone["target_marker"]["token"]
        value = (canonical(tombstone), main_signature, survivor_signature)
        if token in self._retirements and self._retirements[token] != value:
            raise _DemoAuditAnchorError("conflicting demo retirement tombstone")
        self._retirements[token] = value

    def load_retirement(self, tombstone: dict) -> tuple[bytes, bytes, bytes | None]:
        try:
            return self._retirements[tombstone["target_marker"]["token"]]
        except KeyError as exc:
            raise _DemoAuditAnchorError("demo retirement tombstone is missing") from exc

def sample_project_input() -> dict[str, Any]:
    """A valid cross-unit task input for the demo fixed chain."""
    return {
        "schema_version": "1.0",
        "base_revision": DEMO_REVISION,
        "project_id": "PRJ001",
        "task_id": "t.1",
        "title": "Ship offline MVP demo",
        "objective": "Prove the distributed task management loop offline",
        "plan_start": "2026-08-01T00:00:00Z",
        "plan_end": "2026-08-31T00:00:00Z",
        "responsible_units": ["unit_a"],
        "recipient_cert_id": "CERT-RECIPIENT",
        "sender_cert_id": "CERT-SENDER",
        "package_type": "TASK_ASSIGNMENT",
        "payload_digest": "b" * 64,
        "flow": {
            "unit_id": "unit_a",
            "title": "Offline MVP flow",
            "stages": [{
                "stage_id": "execution",
                "name": "execution",
                "nodes": [{
                    "node_id": "n1",
                    "title": "Implement demo",
                    "stage_hint": "execution",
                    "inputs": ["requirement"],
                    "outputs": ["result"],
                    "review_criteria": ["approved"],
                    "responsible_roles": ["tech:python"],
                }],
            }],
            "roles": [{
                "role_id": "tech.python",
                "name": "developer",
                "responsibility": "delivery",
            }],
        },
    }

def ensure_demo_profile() -> Path:
    """Ensure the locked demo PKI profile exists (generates it offline)."""
    profile_dir = ROOT / "loop" / "runtime" / "sm2-test-pki" / DEMO_PROFILE
    if (profile_dir / "receipt.json").is_file():
        return profile_dir
    profile_dir.parent.mkdir(parents=True, exist_ok=True)
    powershell = Path(os.environ.get("SystemRoot", r"C:\Windows")) / (
        "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    result = subprocess.run(
        [
            str(powershell), "-NoLogo", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-File",
            str(ROOT / "scripts" / "generate-sm2-test-pki.ps1"),
            "-ProfileName", DEMO_PROFILE,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"demo PKI generation failed: {result.stderr[-2000:]}")
    return profile_dir
