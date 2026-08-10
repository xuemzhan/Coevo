"""REVIEW2-12: capability status matrix guard tests.

Contract (docs/architecture/capability-status.md):

* the level closed set is DESIGNED / MODELED / UNIT_VERIFIED /
  INTEGRATION_VERIFIED / E2E_VERIFIED / PROTOTYPE / PRODUCTION_READY /
  BLOCKED;
* every US-0..US-16 capability row is present;
* BACKLOG "done" means slice-level done only -- narrative must never
  claim "full gate green therefore system complete".
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LEVELS = (
    "DESIGNED",
    "MODELED",
    "UNIT_VERIFIED",
    "INTEGRATION_VERIFIED",
    "E2E_VERIFIED",
    "PROTOTYPE",
    "PRODUCTION_READY",
    "BLOCKED",
)


class CapabilityStatusTests(unittest.TestCase):
    def test_level_closed_set_is_documented(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "capability-status.md"
        ).read_text(encoding="utf-8")
        for level in LEVELS:
            self.assertIn(f"`{level}`", text, level)

    def test_every_user_story_has_a_row(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "capability-status.md"
        ).read_text(encoding="utf-8")
        for index in range(0, 17):
            self.assertIn(f"| US-{index}", text, f"US-{index}")

    def test_slice_done_semantics_is_explicit(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "capability-status.md"
        ).read_text(encoding="utf-8")
        self.assertIn("done", text)
        self.assertIn("切片", text)

    def test_readme_links_matrix_and_avoids_overclaim(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("capability-status", readme)
        self.assertNotIn("全量门禁全绿，因此系统完成", readme)
        self.assertNotIn("因此系统完成", readme)


if __name__ == "__main__":
    unittest.main()
