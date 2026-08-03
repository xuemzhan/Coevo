from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "tests"))

from coevo.identity.models import Actor
from coevo.identity.repository import ConflictError, IdentityRepository
from coevo.identity.service import IdentityService, StaticAuthorizer, UnauthorizedError
from coevo.identity.validation import ValidationError
from support_identity import TestFreshnessAuthority, TestSigner, identity_payload


class IdentityStoreIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(); self.database = Path(self.temp.name) / "identity.sqlite3"
        self.signer = TestSigner(); self.freshness = TestFreshnessAuthority()
        self.repo = IdentityRepository.create(self.database, self.signer, self.freshness)
        self.service = IdentityService(self.repo, StaticAuthorizer({"admin-1": frozenset({"identity:write"})})); self.writer = Actor("admin-1")

    def tearDown(self) -> None:
        self.repo.close(); self.temp.cleanup()

    def count(self, table: str) -> int:
        return self.repo.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_authorized_bundle_is_created_atomically_and_externally_anchored(self) -> None:
        result = self.service.register_identity_bundle(self.writer, "request-1", identity_payload(revoked=True))
        self.assertEqual((result.organization_id, result.user_id, result.client_id, result.certificate_id), ("org-1", "user-1", "client-1", "cert-1"))
        for table in ("organizations", "users", "clients", "trusted_certificates", "project_role_bindings", "identity_commands"):
            self.assertEqual(self.count(table), 1)
        certificate = self.repo.connection.execute("SELECT revoked,serial_number,public_key_algorithm_oid FROM trusted_certificates").fetchone()
        self.assertEqual(certificate["revoked"], 1); self.assertTrue(certificate["serial_number"])
        self.assertEqual(certificate["public_key_algorithm_oid"], "1.2.840.113549.1.1.1")
        self.assertTrue(self.repo.anchor.head.is_file()); self.assertTrue(self.repo.anchor.marker_signature.is_file())
        self.assertTrue(self.repo.verify_audit_chain())

    def test_same_request_is_idempotent_and_replay_is_audited(self) -> None:
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        replay = self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        self.assertTrue(replay.replayed); self.assertEqual(self.count("organizations"), 1)
        results = [row[0] for row in self.repo.connection.execute("SELECT result FROM identity_audit_events ORDER BY sequence_no")]
        self.assertEqual(results, ["success", "replayed"]); self.assertTrue(self.repo.verify_audit_chain())
        self.assertEqual(len(self.freshness.markers), 1)

    def test_changed_replay_conflicts_without_partial_business_writes(self) -> None:
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        changed = identity_payload(); changed["organization"]["name"] = "变更名称"
        with self.assertRaises(ConflictError): self.service.register_identity_bundle(self.writer, "request-1", changed)
        self.assertEqual(self.repo.connection.execute("SELECT name FROM organizations").fetchone()[0], "单位一")
        self.assertEqual(self.repo.connection.execute("SELECT result FROM identity_audit_events ORDER BY sequence_no DESC LIMIT 1").fetchone()[0], "conflict")
        self.assertTrue(self.repo.verify_audit_chain())

    def test_existing_identity_conflict_rolls_back_entire_new_bundle(self) -> None:
        self.service.register_identity_bundle(self.writer, "request-1", identity_payload())
        changed = copy.deepcopy(identity_payload()); changed["client"]["client_id"] = "client-2"
        changed["certificate"]["certificate_id"] = "cert-2"; changed["certificate"]["bound_client_id"] = "client-2"
        with self.assertRaises(ConflictError): self.service.register_identity_bundle(self.writer, "request-2", changed)
        self.assertEqual(self.count("clients"), 1); self.assertEqual(self.count("trusted_certificates"), 1)
        self.assertTrue(self.repo.verify_audit_chain())

    def test_authorization_comes_from_policy_and_invalid_envelope_is_audited(self) -> None:
        with self.assertRaises(UnauthorizedError): self.service.register_identity_bundle(Actor("viewer-1"), "request-1", identity_payload())
        with self.assertRaises(ValidationError): self.service.register_identity_bundle(Actor("bad actor"), "bad request", identity_payload())
        rows = self.repo.connection.execute("SELECT actor_id,request_id,result FROM identity_audit_events ORDER BY sequence_no").fetchall()
        self.assertEqual(rows[0]["result"], "unauthorized"); self.assertEqual(rows[1]["result"], "invalid_envelope")
        self.assertTrue(rows[1]["actor_id"].startswith("invalid:")); self.assertTrue(rows[1]["request_id"].startswith("invalid:"))
        self.assertEqual(self.count("organizations"), 0)


if __name__ == "__main__": unittest.main()
