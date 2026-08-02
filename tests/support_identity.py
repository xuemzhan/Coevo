from __future__ import annotations

import hashlib
import hmac
import os
import uuid
from pathlib import Path

if __name__.startswith("tests."):
    # Unit/integration modules under the repository package import production
    # code through ``src.coevo``.
    from src.coevo.identity.audit_anchor import AuditAnchorError, canonical
else:
    # Security/e2e discovery adds ``src`` to sys.path and imports the installed
    # package shape directly as ``coevo``.
    from coevo.identity.audit_anchor import AuditAnchorError, canonical

ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE_DER = (ROOT / "loop" / "audit-signing-public.cer").read_bytes()


class TestSigner:
    __test__ = False

    def __init__(self) -> None:
        self.secret = os.urandom(32)

    def sign(self, content: bytes) -> bytes:
        return hmac.new(self.secret, content, hashlib.sha256).digest()

    def verify(self, content: bytes, signature: bytes) -> None:
        if not hmac.compare_digest(self.sign(content), signature):
            raise AuditAnchorError("test signature mismatch")


class TestFreshnessAuthority:
    __test__ = False

    def __init__(self) -> None:
        self.markers: dict[str, tuple[dict, bytes]] = {}
        self.known_markers: dict[str, tuple[dict, bytes]] = {}
        self.certificates: set[str] = set()
        self.keys: set[str] = set()
        self.retired: dict[str, bytes] = {}
        self.retirements: dict[str, tuple[bytes, bytes, bytes | None]] = {}
        self.fail_delete_after: str | None = None
        self.fail_retirement_store = False

    def create_marker(self, store_id: str, generation: int, binding: str) -> dict:
        token = os.urandom(20).hex().upper(); key_id = "CoevoIdentityMarker-" + os.urandom(16).hex()
        marker = {
            "store_id": store_id, "generation": generation, "binding_sha256": binding,
            "token": token, "key_id": key_id, "key_public_sha256": os.urandom(32).hex(), "transition_id": str(uuid.uuid4()),
        }
        stored = (dict(marker), os.urandom(32))
        self.markers[token] = stored; self.known_markers[token] = stored; self.certificates.add(token); self.keys.add(key_id)
        return marker

    def _stored(self, marker: dict) -> tuple[dict, bytes]:
        stored = self.known_markers.get(marker.get("token"))
        if stored is None or stored[0] != marker:
            raise AuditAnchorError("test freshness marker mismatch")
        return stored

    def verify_marker(self, marker: dict) -> None:
        self._stored(marker)
        if marker["token"] not in self.certificates or marker["key_id"] not in self.keys or marker["token"] in self.retirements:
            raise AuditAnchorError("test freshness marker is unavailable or retired")

    def delete_marker(self, marker: dict) -> None:
        stored = self._stored(marker)
        if marker["key_id"] in self.keys:
            self.keys.remove(marker["key_id"])
            if self.fail_delete_after == "key":
                self.fail_delete_after = None; raise OSError("injected after key destruction")
        if marker["token"] in self.certificates:
            self.certificates.remove(marker["token"])
            if self.fail_delete_after == "certificate":
                self.fail_delete_after = None; raise OSError("injected after certificate removal")
        self.retired[marker["token"]] = stored[1]
        self.markers.pop(marker["token"], None)

    def verify_retired(self, marker: dict) -> None:
        self._stored(marker)
        if marker["key_id"] in self.keys or marker["token"] in self.certificates:
            raise AuditAnchorError("test freshness marker retirement is incomplete")

    def sign(self, content: bytes, marker: dict) -> bytes:
        self.verify_marker(marker)
        return hmac.new(self.markers[marker["token"]][1], content, hashlib.sha256).digest()

    def verify_signature(self, content: bytes, signature: bytes, marker: dict) -> None:
        stored = self.known_markers.get(marker.get("token")); secret = stored[1] if stored is not None else self.retired.get(marker.get("token"))
        if secret is None or not hmac.compare_digest(hmac.new(secret, content, hashlib.sha256).digest(), signature):
            raise AuditAnchorError("test marker signature mismatch")

    def store_retirement(self, tombstone: dict, main_signature: bytes, survivor_signature: bytes | None) -> None:
        if self.fail_retirement_store:
            self.fail_retirement_store = False; raise OSError("injected retirement store failure")
        token = tombstone["target_marker"]["token"]; value = (canonical(tombstone), main_signature, survivor_signature)
        if token in self.retirements and self.retirements[token] != value:
            raise AuditAnchorError("conflicting test retirement tombstone")
        self.retirements[token] = value

    def load_retirement(self, tombstone: dict) -> tuple[bytes, bytes, bytes | None]:
        try:
            return self.retirements[tombstone["target_marker"]["token"]]
        except KeyError as exc:
            raise AuditAnchorError("test retirement tombstone is missing") from exc


def identity_payload(*, revoked: bool = False) -> dict:
    return {
        "organization": {"organization_id": "org-1", "code": "ORG1", "name": "单位一"},
        "user": {"user_id": "user-1", "organization_id": "org-1", "display_name": "用户一"},
        "client": {"client_id": "client-1", "organization_id": "org-1", "assigned_user_id": "user-1", "display_name": "终端一"},
        "certificate": {"certificate_id": "cert-1", "owner_user_id": "user-1", "bound_client_id": "client-1", "certificate_der": CERTIFICATE_DER, "revoked": revoked},
        "roles": [{"project_id": "project-1", "user_id": "user-1", "role_code": "project_owner"}],
    }
