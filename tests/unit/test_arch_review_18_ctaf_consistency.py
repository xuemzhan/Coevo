"""ARCH-REVIEW-18: CTAF proposal consistency guard (pins F-1..F-5 fixes).

Prevents regression of the implementer pre-review corrections:
  F-1 cumulative review counts 60/53 (proposal §19.3/§19.4),
  F-2 threat matrix row count = 16 (proposal §13 / framework README),
  F-3 trace_id annotation = <sha256-64hex> (proposal §6.1),
  F-4 M1a/M2 marked delivered in framework README pending table,
  F-5 delivery-scope note present,
  plus F-2 ghost numbers (B12/A18) absent from §16.6/§17 bodies.
"""

from __future__ import annotations

import re
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
FRAMEWORK_README = (
    ROOT
    / "docs"
    / "plans"
    / "distributed-agent-framework"
    / "README.md"
)


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading))
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return "\n".join(lines[start:end])


class CtafProposalConsistencyTests(unittest.TestCase):
    def test_cumulative_review_counts_are_consistent(self) -> None:
        text = PROPOSAL.read_text(encoding="utf-8")
        self.assertIn("**60 条**（含迭代交叉）", text)
        self.assertIn("**53 条 net new**", text)
        self.assertNotIn("累计总条数 = 17 + 9 + 19 = 45", text)

    def test_threat_matrix_row_count_is_16(self) -> None:
        text = PROPOSAL.read_text(encoding="utf-8")
        section = _section(text, "## 13. ")
        rows = [
            line
            for line in section.splitlines()
            if line.startswith("|")
            and not re.match(r"^\|[\s\-|]+\|$", line)
            and "威胁 / 防御层" not in line
        ]
        self.assertEqual(len(rows), 16, "proposal threat matrix must have 16 rows")

    def test_framework_readme_threat_rows_matches(self) -> None:
        text = FRAMEWORK_README.read_text(encoding="utf-8")
        self.assertIn("**16 行**", text)
        self.assertNotIn("**15 行**", text)

    def test_trace_id_annotation_is_sha256(self) -> None:
        text = PROPOSAL.read_text(encoding="utf-8")
        self.assertIn("trace_id:         <sha256-64hex>", text)
        self.assertNotIn("trace_id:         <uuid>", text)

    def test_pending_docs_mark_m1a_m2_delivered(self) -> None:
        text = FRAMEWORK_README.read_text(encoding="utf-8")
        self.assertIn("M1a（已交付", text)
        self.assertIn("M2（已交付", text)
        self.assertIn("交付口径说明", text)

    def test_ghost_review_numbers_are_gone_from_body(self) -> None:
        text = PROPOSAL.read_text(encoding="utf-8")
        self.assertNotIn("B12", _section(text, "### 16.6 "))
        self.assertNotIn("A18", _section(text, "## 17. "))


if __name__ == "__main__":
    unittest.main()
