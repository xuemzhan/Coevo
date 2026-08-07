"""OPTIMIZE-17: static safety guards for the destructive loop/runtime cleaners.

`force-remove-loop-runtime*.ps1` permanently delete `loop/runtime`. These
tests pin the safety rails so an edit cannot silently redirect the delete to
another path or drop the confirmation/reparse-point guards.
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_LITERAL = str(ROOT / "loop" / "runtime")  # e.g. E:\Workspace\Coevo\loop\runtime


class ForceRemoveSafetyTests(unittest.TestCase):
    def test_main_variant_targets_repo_runtime_only(self):
        text = (
            ROOT / "scripts" / "force-remove-loop-runtime.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn(RUNTIME_LITERAL, text)
        self.assertIn("Equals($Target, $Expected", text)
        self.assertIn("ReparsePoint", text)
        self.assertIn("/XJ", text)
        self.assertIn("Type DELETE", text)
        self.assertIn("Post-delete verification", text)

    def test_win32_variant_targets_repo_runtime_and_guards(self):
        text = (
            ROOT / "scripts" / "force-remove-loop-runtime-win32.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn(RUNTIME_LITERAL, text)
        self.assertIn("Type DELETE", text)
        self.assertIn("FILE_ATTRIBUTE_REPARSE_POINT", text)
        self.assertIn("Deletion incomplete", text)


if __name__ == "__main__":
    unittest.main()
