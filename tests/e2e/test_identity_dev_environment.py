from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "tests"))

from coevo.identity.models import Actor
from coevo.identity.audit_anchor import WindowsFreshnessAuthority
from coevo.identity.repository import IdentityRepository
from coevo.identity.service import IdentityService, StaticAuthorizer
from support_identity import identity_payload


class IdentityDevelopmentEnvironmentTests(unittest.TestCase):
    def test_windows_certificate_parser_and_generation_markers_work_end_to_end(self) -> None:
        marker = None; freshness = None
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "identity.sqlite3"
            freshness = WindowsFreshnessAuthority(Path(temporary) / "retirements")
            repository = IdentityRepository.create(database, freshness=freshness)
            try:
                service = IdentityService(repository, StaticAuthorizer({"dev-admin": frozenset({"identity:write"})}))
                result = service.register_identity_bundle(Actor("dev-admin"), "dev-environment-check", identity_payload())
                self.assertEqual(result.certificate_id, "cert-1"); self.assertTrue(repository.verify_audit_chain())
            finally: repository.close()
            reopened = IdentityRepository.open(database, freshness=freshness)
            try:
                self.assertTrue(reopened.verify_audit_chain()); marker = reopened.anchor._read_official()[1]["marker"]
                freshness = reopened.anchor.freshness
            finally: reopened.close()
            freshness.delete_marker(marker); freshness.verify_retired(marker)


if __name__ == "__main__": unittest.main()
