"""ARCH-REVIEW-14: CTAF design-proposal draft-status guard."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = (
    ROOT
    / "docs"
    / "plans"
    / "distributed-agent-framework"
    / "design-proposal.md"
)


class CtafDraftGuardTests(unittest.TestCase):
    def test_design_proposal_remains_draft(self) -> None:
        self.assertTrue(PROPOSAL.is_file(), "CTAF design proposal missing")
        text = PROPOSAL.read_text(encoding="utf-8")
        self.assertIn("产品级草案", text)
        self.assertIn("待独立复核后定稿", text)

    def test_independent_review_registered_as_external_gate(self) -> None:
        gates = (
            ROOT / "docs" / "architecture" / "external-gates.md"
        ).read_text(encoding="utf-8")
        self.assertIn("CTAF-PROPOSAL-REVIEW", gates)
        self.assertIn("`REVIEW-REQUIRED`", gates)
        self.assertIn("design-proposal.md", gates)

    def test_proposal_referenced_in_docs_index(self) -> None:
        index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("distributed-agent-framework", index)


if __name__ == "__main__":
    unittest.main()
