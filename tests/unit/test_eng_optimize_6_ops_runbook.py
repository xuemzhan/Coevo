"""ENG-OPTIMIZE-6: ops-runbook coverage guard tests."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class OpsRunbookTests(unittest.TestCase):
    def test_runbook_covers_new_ops_flows(self) -> None:
        text = (
            ROOT / "docs" / "operations" / "ops-runbook.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "8. 门禁与审计运维",
            "gate-results",
            "re-anchor",
            "recent_gate",
            "external-gates",
            "capability-status",
            "decision-records",
        ):
            self.assertIn(marker, text, marker)

    def test_release_section_lists_new_gates(self) -> None:
        text = (
            ROOT / "docs" / "operations" / "ops-runbook.md"
        ).read_text(encoding="utf-8")
        self.assertIn("delivery_artifacts", text)
        self.assertIn("recent_gate", text)
        self.assertIn("不发布", text)


if __name__ == "__main__":
    unittest.main()
