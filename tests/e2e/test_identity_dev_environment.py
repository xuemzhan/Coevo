from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "tests"))

from coevo.identity.models import Actor
from coevo.identity.repository import IdentityRepository
from coevo.identity.service import IdentityService, StaticAuthorizer
from support_identity import identity_payload


class IdentityDevelopmentEnvironmentTests(unittest.TestCase):
    def test_windows_certificate_parser_and_generation_markers_work_end_to_end(self) -> None:
        marker = None; freshness = None
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "identity.sqlite3"; repository = IdentityRepository.create(database)
            try:
                service = IdentityService(repository, StaticAuthorizer({"dev-admin": frozenset({"identity:write"})}))
                result = service.register_identity_bundle(Actor("dev-admin"), "dev-environment-check", identity_payload())
                self.assertEqual(result.certificate_id, "cert-1"); self.assertTrue(repository.verify_audit_chain())
            finally: repository.close()
            reopened = IdentityRepository.open(database)
            try:
                self.assertTrue(reopened.verify_audit_chain()); marker = reopened.anchor._read_official()[1]["marker"]
                freshness = reopened.anchor.freshness
            finally: reopened.close()
            freshness.delete_marker(marker); freshness.verify_retired(marker)
        # The E2E store no longer exists, so remove only its externally anchored test tombstones.
        retirement_directory = freshness.retirement_root / marker["store_id"]
        if retirement_directory.exists(): shutil.rmtree(retirement_directory)


if __name__ == "__main__": unittest.main()
