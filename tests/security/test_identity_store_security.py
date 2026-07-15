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
from coevo.identity.validation import SensitiveInputError, ValidationError
from support_identity import TestFreshnessAuthority, TestSigner, identity_payload


class IdentityStoreSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(); self.database = Path(self.temp.name) / "identity.sqlite3"
        self.signer = TestSigner(); self.freshness = TestFreshnessAuthority()
        self.repo = IdentityRepository.create(self.database, self.signer, self.freshness)
        self.service = IdentityService(self.repo, StaticAuthorizer({"admin-1": frozenset({"identity:write"})})); self.writer = Actor("admin-1")

    def tearDown(self) -> None:
        try: self.repo.close()
        except Exception: pass
        self.temp.cleanup()

    def test_private_key_fields_and_binary_pkcs8_are_rejected_and_redacted(self) -> None:
        secret = "DO-NOT-PERSIST-PRIVATE-KEY"; value = identity_payload(); value["certificate"]["private_key_path"] = secret
        with self.assertRaises(SensitiveInputError): self.service.register_identity_bundle(self.writer, "request-1", value)
        self.assertNotIn(secret.encode(), self.database.read_bytes())
        event = self.repo.connection.execute("SELECT result,target_summary,payload_digest FROM identity_audit_events").fetchone()
        self.assertEqual((event["result"], event["target_summary"], event["payload_digest"]), ("sensitive_input_rejected", "{}", None))
        value = identity_payload(); value["certificate"]["certificate_der"] = bytes.fromhex("3016020100300d06092a864886f70d010101050004023000")
        with self.assertRaises(ValidationError): self.service.register_identity_bundle(self.writer, "request-2", value)
        self.assertEqual(self.repo.connection.execute("SELECT COUNT(*) FROM trusted_certificates").fetchone()[0], 0)
        self.assertTrue(self.repo.verify_audit_chain())

    def test_cyclic_and_oversized_inputs_are_rejected_with_audit(self) -> None:
        cyclic: dict = {}; cyclic["child"] = cyclic
        with self.assertRaises(ValidationError): self.service.register_identity_bundle(self.writer, "request-1", cyclic)
        with self.assertRaises(ValidationError): self.service.register_identity_bundle(self.writer, "request-2", {"data": b"x" * (2 * 1024 * 1024 + 1)})
        self.assertEqual(self.repo.connection.execute("SELECT COUNT(*) FROM identity_audit_events").fetchone()[0], 2)
        self.assertTrue(self.repo.verify_audit_chain())

    def test_signed_anchor_detects_audit_tail_and_all_event_deletion(self) -> None:
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload()); self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        self.repo.connection.execute("DELETE FROM identity_audit_events WHERE sequence_no=(SELECT MAX(sequence_no) FROM identity_audit_events)")
        self.assertFalse(self.repo.verify_audit_chain()); self.repo.connection.execute("DELETE FROM identity_audit_events")
        self.assertFalse(self.repo.verify_audit_chain())

    def test_signed_anchor_detects_business_and_command_tampering(self) -> None:
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        self.repo.connection.execute("UPDATE organizations SET name='forged'"); self.assertFalse(self.repo.verify_audit_chain())
        self.repo.connection.execute("UPDATE identity_commands SET payload_digest=?", ("0" * 64,)); self.assertFalse(self.repo.verify_audit_chain())

    def test_complete_old_snapshot_rollback_is_rejected_by_destroyed_marker(self) -> None:
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        snapshot = Path(self.temp.name) / "snapshot"; snapshot.mkdir()
        files = (self.database, self.repo.anchor.head, self.repo.anchor.signature, self.repo.anchor.marker_signature)
        for source in files: shutil.copyfile(source, snapshot / source.name)
        old_token = self.repo.anchor._read_official()[1]["marker"]["token"]
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        self.assertNotIn(old_token, self.freshness.markers)
        self.repo.close()
        for destination in files: shutil.copyfile(snapshot / destination.name, destination)
        with self.assertRaises(AuditAnchorError): IdentityRepository.open(self.database, self.signer, self.freshness)

    def test_missing_store_never_silently_initializes(self) -> None:
        missing = Path(self.temp.name) / "missing.sqlite3"
        with self.assertRaises(AuditAnchorError): IdentityRepository.open(missing, self.signer, self.freshness)
        self.assertFalse(missing.exists())
        other = Path(self.temp.name) / "explicit.sqlite3"
        created = IdentityRepository.create(other, self.signer, self.freshness); created.close()
        with self.assertRaises(AuditAnchorError): IdentityRepository.create(other, self.signer, self.freshness)
        other.unlink()
        for path in created.anchor.artifacts(): path.unlink(missing_ok=True)
        with self.assertRaises(AuditAnchorError): IdentityRepository.open(other, self.signer, self.freshness)

    def test_anchor_from_another_database_is_rejected(self) -> None:
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        other_database = Path(self.temp.name) / "other.sqlite3"; other = IdentityRepository.create(other_database, self.signer, self.freshness)
        try:
            other_service = IdentityService(other, StaticAuthorizer({"admin-1": frozenset({"identity:write"})})); value = identity_payload()
            value["organization"]["organization_id"] = "org-2"; value["organization"]["code"] = "ORG2"
            value["user"]["organization_id"] = "org-2"; value["client"]["organization_id"] = "org-2"
            other_service.register_identity_bundle(self.writer, "request-2", value)
            shutil.copyfile(other.anchor.head, self.repo.anchor.head); shutil.copyfile(other.anchor.signature, self.repo.anchor.signature)
            shutil.copyfile(other.anchor.marker_signature, self.repo.anchor.marker_signature)
            self.assertFalse(self.repo.verify_audit_chain())
        finally: other.close()

    def test_committed_pending_state_recovers_and_retires_old_marker(self) -> None:
        old_token = self.repo.anchor._read_official()[1]["marker"]["token"]
        original_promote = self.repo.anchor.promote
        self.repo.anchor.promote = lambda: (_ for _ in ()).throw(OSError("injected promotion failure"))
        with self.assertRaises(OSError): self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        self.repo.anchor.promote = original_promote; self.assertTrue(self.repo.anchor.pending_head.exists()); self.repo.close()
        recovered = IdentityRepository.open(self.database, self.signer, self.freshness)
        try:
            self.assertTrue(recovered.verify_audit_chain()); self.assertFalse(recovered.anchor.pending_head.exists())
            self.assertNotIn(old_token, self.freshness.markers)
            service = IdentityService(recovered, StaticAuthorizer({"admin-1": frozenset({"identity:write"})}))
            self.assertTrue(service.register_identity_bundle(self.writer, "request-1", identity_payload()).replayed)
        finally: recovered.close()

    def test_signature_and_marker_loss_are_detected(self) -> None:
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        data = bytearray(self.repo.anchor.signature.read_bytes()); data[len(data) // 2] ^= 1; self.repo.anchor.signature.write_bytes(data)
        self.assertFalse(self.repo.verify_audit_chain())
        # A fresh store proves that removal of the active non-exportable marker is independently detected.
        other = Path(self.temp.name) / "marker-loss.sqlite3"; repo = IdentityRepository.create(other, self.signer, self.freshness)
        try:
            marker = repo.anchor._read_official()[1]["marker"]; self.freshness.delete_marker(marker)
            self.assertFalse(repo.verify_audit_chain())
        finally: repo.close()


if __name__ == "__main__": unittest.main()
