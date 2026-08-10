"""Project status handoff doc guard."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ProjectStatusTests(unittest.TestCase):
    def test_status_doc_covers_all_sections(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "project-status.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "一句话状态",
            "架构与能力",
            "质量与验证",
            "外部依赖与待批门",
            "需要业务负责人裁决",
            "external-gates",
            "capability-status",
            "DECISION-REQUIRED",
        ):
            self.assertIn(marker, text, marker)


if __name__ == "__main__":
    unittest.main()
