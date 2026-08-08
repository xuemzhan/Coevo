"""FRAMEWORK-OPTIMIZE-15: shared safe relative-path predicate + guards."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from src.coevo.relpath import is_safe_relative_path


ROOT = Path(__file__).resolve().parents[2]


class IsSafeRelativePathTests(unittest.TestCase):
    def test_accepts_plain_relative_path(self):
        self.assertTrue(is_safe_relative_path("a"))
        self.assertTrue(is_safe_relative_path("a/b/c.txt"))
        self.assertTrue(is_safe_relative_path("a b/c-d_e"))

    def test_rejects_absolute_and_drive_forms(self):
        self.assertFalse(is_safe_relative_path("/etc/passwd"))
        self.assertFalse(is_safe_relative_path("//server/share"))

    def test_drive_form_is_left_to_caller_containment(self):
        # "C:/x" is not a traversal/separator abuse; the shared predicate
        # accepts it and callers reject it via their filesystem containment
        # check (candidate.relative_to(root)) — same as the original copies.
        self.assertTrue(is_safe_relative_path("C:/x"))

    def test_rejects_backslash_and_nul(self):
        self.assertFalse(is_safe_relative_path("a\\..\\b"))
        self.assertFalse(is_safe_relative_path("a\x00b"))

    def test_rejects_traversal_and_dot_segments(self):
        self.assertFalse(is_safe_relative_path("a/../b"))
        self.assertFalse(is_safe_relative_path("../a"))
        self.assertFalse(is_safe_relative_path("a/./b"))
        self.assertFalse(is_safe_relative_path("a//b"))
        self.assertFalse(is_safe_relative_path("."))
        self.assertFalse(is_safe_relative_path(".."))

    def test_rejects_empty_and_non_string(self):
        self.assertFalse(is_safe_relative_path(""))
        self.assertFalse(is_safe_relative_path(None))
        self.assertFalse(is_safe_relative_path(123))
        self.assertFalse(is_safe_relative_path(b"a/b"))


class UnificationGuardTests(unittest.TestCase):
    """The three call sites must reference the shared leaf, not local copies."""

    LOCAL_PATTERN = re.compile(r'any\(part in \("", "\\.", "\\.\."\)')

    def test_modules_import_shared_predicate(self):
        for relative in (
            "src/coevo/progress_capture/watcher.py",
            "src/coevo/cockpit/static.py",
            "src/coevo/cockpit/wps.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                "is_safe_relative_path",
                text,
                f"{relative} must reference the shared predicate",
            )

    def test_no_local_part_segment_copies_remain(self):
        for relative in (
            "src/coevo/progress_capture/watcher.py",
            "src/coevo/cockpit/static.py",
            "src/coevo/cockpit/wps.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIsNone(
                self.LOCAL_PATTERN.search(text),
                f"{relative} must not keep a local part-segment check",
            )


if __name__ == "__main__":
    unittest.main()
