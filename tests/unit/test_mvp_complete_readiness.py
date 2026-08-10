"""MVP-complete readiness doc guard (ARCH-REVIEW-3 decision support)."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class MvpReadinessTests(unittest.TestCase):
    def test_readiness_doc_covers_all_conditions(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "mvp-complete-readiness.md"
        ).read_text(encoding="utf-8")
        for index in range(1, 12):
            self.assertIn(f"| {index} |", text, f"condition {index}")
        self.assertIn("双签", text)
        self.assertIn("external-gates", text)


if __name__ == "__main__":
    unittest.main()
