"""ARCH-REVIEW-5: audit-signing key ceremony guard tests.

Contract (docs/architecture/audit-key-ceremony.md): the ceremony covers
rotation / offline backup / loss recovery / backup-signer evaluation; the
current signing configuration is a single prototype signer (F6DE, CNG
non-exportable); the operational runbook exists.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AuditKeyCeremonyTests(unittest.TestCase):
    def test_ceremony_doc_covers_all_sections(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "audit-key-ceremony.md"
        ).read_text(encoding="utf-8")
        for section in ("轮换", "备份", "恢复", "备份签名者"):
            self.assertIn(section, text, section)
        self.assertIn("security_review=true", text)

    def test_signing_config_is_single_prototype_signer(self) -> None:
        config = json.loads(
            (ROOT / "loop" / "audit-signing.json").read_text(encoding="utf-8")
        )
        self.assertTrue(config["prototype"])
        self.assertEqual(
            config["thumbprint"],
            "F6DE13A4ADF56B9D66902B8E3055DCCA8B702D86",
        )
        self.assertEqual(config["store"], "CurrentUser/My")

    def test_operational_runbook_exists(self) -> None:
        runbook = ROOT / "docs" / "operations" / "audit-key-runbook.md"
        self.assertTrue(runbook.is_file())
        text = runbook.read_text(encoding="utf-8")
        self.assertTrue(text.strip())


if __name__ == "__main__":
    unittest.main()
