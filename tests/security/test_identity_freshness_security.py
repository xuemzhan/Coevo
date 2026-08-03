from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "tests"))

from coevo.identity.audit_anchor import AuditAnchorError
from coevo.identity.models import Actor
from coevo.identity.repository import IdentityRepository
from coevo.identity.service import IdentityService, StaticAuthorizer
from support_identity import TestFreshnessAuthority, TestSigner, identity_payload


class IdentityFreshnessSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(); self.database = Path(self.temp.name) / "identity.sqlite3"
        self.signer = TestSigner(); self.freshness = TestFreshnessAuthority()
        self.repo = IdentityRepository.create(self.database, self.signer, self.freshness)
        self.service = IdentityService(self.repo, StaticAuthorizer({"admin": frozenset({"identity:write"})}))

    def tearDown(self) -> None:
        try: self.repo.close()
        except Exception: pass
        self.temp.cleanup()

    def _snapshot(self, directory: Path) -> tuple[Path, ...]:
        files = (self.database, self.repo.anchor.head, self.repo.anchor.signature, self.repo.anchor.marker_signature)
        for source in files: shutil.copyfile(source, directory / source.name)
        return files

    def _recover_delete_crash(self, stage: str) -> None:
        old = self.repo.anchor._read_official()[1]["marker"]
        self.freshness.fail_delete_after = stage
        with self.assertRaises(OSError):
            self.service.register_identity_bundle(Actor("admin"), "request-1", identity_payload())
        self.assertTrue(self.repo.anchor.pending_head.is_file())
        self.assertNotIn(old["key_id"], self.freshness.keys)
        if stage == "key": self.assertIn(old["token"], self.freshness.certificates)
        if stage == "certificate": self.assertNotIn(old["token"], self.freshness.certificates)
        self.repo.close(); self.repo = IdentityRepository.open(self.database, self.signer, self.freshness)
        self.assertTrue(self.repo.verify_audit_chain()); self.assertFalse(self.repo.anchor.pending_head.exists())
        self.assertIn(old["token"], self.freshness.retirements); self.freshness.verify_retired(old)

    def test_key_destroyed_before_certificate_crash_recovers_idempotently(self) -> None:
        self._recover_delete_crash("key")

    def test_certificate_removed_before_tombstone_crash_recovers_idempotently(self) -> None:
        self._recover_delete_crash("certificate")

    def test_tombstone_store_failure_keeps_pending_and_recovers(self) -> None:
        old = self.repo.anchor._read_official()[1]["marker"]; self.freshness.fail_retirement_store = True
        with self.assertRaises(OSError): self.service.register_identity_bundle(Actor("admin"), "request-1", identity_payload())
        self.assertTrue(self.repo.anchor.pending_head.exists()); self.freshness.verify_retired(old)
        self.repo.close(); self.repo = IdentityRepository.open(self.database, self.signer, self.freshness)
        self.assertIn(old["token"], self.freshness.retirements); self.assertFalse(self.repo.anchor.pending_head.exists())

    def test_abort_retires_new_key_before_certificate_and_records_tombstone(self) -> None:
        self.repo.anchor.prepare(self.repo._checkpoint()); new_marker = self.repo.anchor._read_pending()[1]["marker"]
        self.freshness.fail_delete_after = "key"
        with self.assertRaises(OSError): self.repo.anchor.abort_pending()
        self.assertTrue(self.repo.anchor.pending_head.exists()); self.assertNotIn(new_marker["key_id"], self.freshness.keys)
        self.repo.anchor.abort_pending(); self.freshness.verify_retired(new_marker)
        self.assertIn(new_marker["token"], self.freshness.retirements); self.assertFalse(self.repo.anchor.pending_head.exists())

    def test_pre_removed_certificate_still_destroys_signed_key_id(self) -> None:
        old = self.repo.anchor._read_official()[1]["marker"]; original = self.freshness.delete_marker
        def remove_certificate_first(marker: dict) -> None:
            self.freshness.certificates.discard(marker["token"]); original(marker)
        self.freshness.delete_marker = remove_certificate_first
        self.service.register_identity_bundle(Actor("admin"), "request-1", identity_payload())
        self.freshness.delete_marker = original
        self.freshness.verify_retired(old); self.assertNotIn(old["key_id"], self.freshness.keys)

    def test_restored_old_certificate_cannot_reassociate_destroyed_key(self) -> None:
        self.service.register_identity_bundle(Actor("admin"), "request-1", identity_payload())
        snapshot = Path(self.temp.name) / "snapshot"; snapshot.mkdir(); files = self._snapshot(snapshot)
        old = self.repo.anchor._read_official()[1]["marker"]
        self.service.register_identity_bundle(Actor("admin"), "request-1", identity_payload())
        self.freshness.certificates.add(old["token"]); self.assertNotIn(old["key_id"], self.freshness.keys)
        self.repo.close()
        for destination in files: shutil.copyfile(snapshot / destination.name, destination)
        with self.assertRaises(AuditAnchorError): IdentityRepository.open(self.database, self.signer, self.freshness)

    def test_tombstone_content_tampering_is_rejected(self) -> None:
        old = self.repo.anchor._read_official()[1]["marker"]
        self.service.register_identity_bundle(Actor("admin"), "request-1", identity_payload())
        raw, main, survivor = self.freshness.retirements[old["token"]]
        self.freshness.retirements[old["token"]] = (raw + b" ", main, survivor)
        self.assertFalse(self.repo.verify_audit_chain())

    def test_official_marker_signature_tampering_is_rejected(self) -> None:
        data = bytearray(self.repo.anchor.marker_signature.read_bytes()); data[0] ^= 1
        self.repo.anchor.marker_signature.write_bytes(data); self.assertFalse(self.repo.verify_audit_chain())

    def test_tampered_dual_signed_pending_is_not_recovered(self) -> None:
        original = self.repo.anchor.promote; self.repo.anchor.promote = lambda: (_ for _ in ()).throw(OSError("injected after commit"))
        with self.assertRaises(OSError): self.service.register_identity_bundle(Actor("admin"), "request-1", identity_payload())
        self.repo.anchor.promote = original; data = bytearray(self.repo.anchor.pending_old_signature.read_bytes()); data[-1] ^= 1
        self.repo.anchor.pending_old_signature.write_bytes(data); self.repo.close()
        with self.assertRaises(AuditAnchorError): IdentityRepository.open(self.database, self.signer, self.freshness)

    def test_certificate_inspection_uses_stdin_without_candidate_temp_file(self) -> None:
        python_source = (ROOT / "src" / "coevo" / "identity" / "certificates.py").read_text(encoding="utf-8")
        helper_source = (ROOT / "scripts" / "inspect_certificate.ps1").read_text(encoding="utf-8")
        self.assertIn("input=request", python_source); self.assertNotIn("TemporaryDirectory", python_source)
        self.assertIn("[Console]::In.ReadToEnd()", helper_source); self.assertNotIn("CertificatePath", helper_source)


if __name__ == "__main__": unittest.main()
