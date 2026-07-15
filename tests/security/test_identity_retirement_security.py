from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "tests"))

from coevo.identity.audit_anchor import WindowsFreshnessAuthority


class IdentityRetirementSecurityTests(unittest.TestCase):
    def test_production_delete_is_key_first_and_verifies_both_resources_absent(self) -> None:
        source = (ROOT / "scripts" / "identity_freshness.ps1").read_text(encoding="utf-8")
        delete = source[source.index("if($Action-eq'Delete')"):source.index("if($Action-eq'VerifyRetired')")]
        self.assertLess(delete.index("$key.Delete()"), delete.index("$store.Remove($certificate)"))
        self.assertIn("Freshness private key destruction could not be verified", delete)
        self.assertIn("Freshness certificate still exists after retirement", delete)

    def test_marker_schema_binds_transition_key_id_and_public_digest(self) -> None:
        self.assertEqual(
            WindowsFreshnessAuthority.MARKER_FIELDS,
            {"store_id", "generation", "binding_sha256", "token", "key_id", "key_public_sha256", "transition_id"},
        )
        source = (ROOT / "scripts" / "identity_freshness.ps1").read_text(encoding="utf-8")
        self.assertIn("$TransitionId|$Id|$KeyPublicSha256", source)
        self.assertIn("Key-PublicDigest $key", source)


if __name__ == "__main__": unittest.main()
