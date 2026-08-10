"""ARCH-REVIEW-3 (implementable subset): external-gates registry guards."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ExternalGatesTests(unittest.TestCase):
    def test_registry_lists_required_gates(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "external-gates.md"
        ).read_text(encoding="utf-8")
        self.assertIn("US-5-AC-2", text)
        self.assertIn("`BLOCKED`", text)
        self.assertIn("ARCH-REVIEW-3", text)
        self.assertIn("DECISION-RECORDED", text)
        self.assertIn("`REVIEW-REQUIRED`", text)
        self.assertIn("ARCH-REVIEW-4", text)
        self.assertIn("ARCH-REVIEW-5", text)
        self.assertIn("REVIEW2-10", text)

    def test_capability_status_references_external_gates(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "capability-status.md"
        ).read_text(encoding="utf-8")
        self.assertIn("external-gates", text)

    def test_backlog_item_remains_blocked_pending_decision(self) -> None:
        backlog = (ROOT / "loop" / "BACKLOG.yaml").read_text(encoding="utf-8")
        # ARCH-REVIEW-3 按 RECORDS-2 登记在队列注释（DECISIONS 完整清单）而非
        # BACKLOG 条目（避免多非 done 项违反单一在飞不变量）。
        self.assertIn("ARCH-REVIEW-3", backlog)
        self.assertIn("blocked 待用户裁决", backlog)
        self.assertNotIn("- id: ARCH-REVIEW-3", backlog)


if __name__ == "__main__":
    unittest.main()
