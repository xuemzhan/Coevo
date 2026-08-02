"""app.demo_support - demo-only support: PKI profile bootstrap, in-memory demo signer/freshness stand-ins and sample inputs. Explicitly NOT production code."""

from __future__ import annotations

import hashlib
import hmac
import os
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from src.coevo.identity.audit_anchor import AuditAnchorError, canonical

ROOT = Path(__file__).resolve().parents[3]

DEMO_PROFILE: str = "demo"

DEMO_REVISION: str = "PRJ001-R0001"

DEMO_ACTOR: str = "u.pm"

def now_utc_iso_z() -> str:
    """Return the current UTC time as an ISO-8601 ``Z`` string."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")

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
