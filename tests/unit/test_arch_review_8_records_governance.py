"""ARCH-REVIEW-8: decision-records governance guard tests.

Contract (docs/architecture/decision-records.md):

* DECISIONS.md keeps ADR-style index summaries; long bodies go to the
  archive area via archive_records.py;
* every latest DECISIONS section must carry the governance marker
  (private-key-handle policy a+b) so it can never be dropped silently.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RecordsGovernanceTests(unittest.TestCase):
    def test_decision_records_doc_exists_and_defines_format(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "decision-records.md"
        ).read_text(encoding="utf-8")
        for marker in ("ADR", "Decision:", "Governance marker check", "归档"):
            self.assertIn(marker, text, marker)

    def test_latest_decisions_section_keeps_governance_marker(self) -> None:
        decisions = (ROOT / "loop" / "DECISIONS.md").read_text(encoding="utf-8")
        sections = re.split(r"(?m)^## ", decisions)
        latest = "## " + sections[-1]
        self.assertIn("Governance marker check", latest)
        self.assertIn("approved a+b", latest)
        self.assertIn("Decided by:", latest)

    def test_archive_policy_is_referenced(self) -> None:
        doc = (
            ROOT / "docs" / "architecture" / "decision-records.md"
        ).read_text(encoding="utf-8")
        self.assertIn("archive_records.py", doc)
        self.assertIn("loop/archive", doc)


if __name__ == "__main__":
    unittest.main()
