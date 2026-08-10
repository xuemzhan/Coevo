"""ARCH-REVIEW-15: architecture risk ledger guard tests."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs" / "architecture" / "architecture-risk-ledger.md"


class RiskLedgerTests(unittest.TestCase):
    def test_ledger_exists_and_lists_all_known_risks(self) -> None:
        self.assertTrue(LEDGER.is_file(), "architecture risk ledger missing")
        text = LEDGER.read_text(encoding="utf-8")
        for risk in (
            "P0-1",
            "P0-2",
            "P1-1",
            "P1-2",
            "P1-3",
            "P2-1",
            "P2-2",
            "EXT-1",
            "EXT-2",
            "EXT-3",
        ):
            self.assertIn(risk, text, risk)

    def test_fixed_risks_reference_guard_evidence(self) -> None:
        text = LEDGER.read_text(encoding="utf-8")
        for marker in (
            "go-python-parity.md",
            "state-persistence.md",
            "file-size-budget.md",
            "online-mode-scope.md",
        ):
            self.assertIn(marker, text, marker)

    def test_external_risks_reference_registries(self) -> None:
        text = LEDGER.read_text(encoding="utf-8")
        self.assertIn("external-gates.md", text)
        self.assertIn("known-limitations.md", text)
        self.assertIn("REVIEW-REQUIRED", text)
        self.assertIn("BLOCKED", text)

    def test_registered_in_docs_index(self) -> None:
        index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("architecture-risk-ledger.md", index)
        self.assertIn("架构风险台账", index)


if __name__ == "__main__":
    unittest.main()
