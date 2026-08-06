"""Unit tests for the records archiving policy helpers."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from src.coevo.records_archive import (
    archive_plan,
    split_audit_lines,
    split_decisions_sections,
    split_verification_sections,
)


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class ArchiveScriptPolicyTests(unittest.TestCase):
    """REVIEW-FIX-3 (L-4): pin the lowered VERIFICATION archive threshold."""

    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location(
            "archive_records", SCRIPTS / "archive_records.py"
        )
        cls.script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.script)

    def test_verification_policy_keeps_file_readable(self):
        policy = self.script.POLICY["verification"]
        self.assertLessEqual(policy["keep_recent"], 30)
        self.assertLessEqual(policy["size"], 500_000)

    def test_other_policies_are_unchanged(self):
        self.assertEqual(20, self.script.POLICY["decisions"]["keep_recent"])
        self.assertEqual(2000, self.script.POLICY["audit"]["keep_recent"])


class SplitTests(unittest.TestCase):
    def test_verification_sections(self):
        text = (
            "## 2026-07-01T00:00:00Z \u2014 target=`quality`\n- exit 0\n"
            "## 2026-08-01T00:00:00Z \u2014 target=`quality`\n- exit 0\n"
        )
        sections = split_verification_sections(text)
        self.assertEqual(2, len(sections))
        self.assertEqual("2026-07-01T00:00:00Z", sections[0][0])

    def test_decisions_sections(self):
        text = "## 2026-07-01 -- one\nbody\n## 2026-08-01 -- two\nbody2\n"
        sections = split_decisions_sections(text)
        self.assertEqual(2, len(sections))
        self.assertEqual("2026-08-01", sections[1][0])

    def test_audit_lines(self):
        text = (
            '{"ts": "2026-07-01T00:00:00Z", "tool": "x"}\n'
            '{"ts": "2026-08-01T00:00:00Z", "tool": "y"}\n'
            "not json\n"
        )
        lines = split_audit_lines(text)
        self.assertEqual(2, len(lines))


class ArchivePlanTests(unittest.TestCase):
    def test_archives_old_keeps_recent(self):
        text = (
            "## 2026-07-01 -- old\nbody\n"
            "## 2026-07-15 -- old\nbody\n"
            "## 2026-08-01 -- recent\nbody\n"
        )
        plan = archive_plan(
            text,
            kind="decisions",
            now="2026-08-02T00:00:00Z",
            keep_recent=1,
            min_age_days=10,
            size_threshold_bytes=10_000_000,
        )
        self.assertEqual(2, plan["archived_sections"])
        self.assertIn("2026-08-01", plan["keep"])
        self.assertNotIn("2026-07-01", plan["keep"])

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            archive_plan("x", kind="bogus", now="2026-08-02T00:00:00Z",
                         keep_recent=1, min_age_days=1, size_threshold_bytes=1)

    def test_size_threshold_trims_oldest_kept_sections(self):
        text = (
            "## 2026-07-01 -- a\n" + "x" * 300 + "\n"
            "## 2026-07-02 -- b\n" + "y" * 300 + "\n"
            "## 2026-07-03 -- c\n" + "z" * 300 + "\n"
        )
        plan = archive_plan(
            text,
            kind="decisions",
            now="2026-08-02T00:00:00Z",
            keep_recent=3,
            min_age_days=1,
            size_threshold_bytes=400,
        )
        self.assertGreaterEqual(plan["archived_sections"], 1)
        self.assertNotIn("2026-07-01", plan["keep"])
        self.assertIn("2026-07-03", plan["keep"])
        self.assertIn("size-trimmed", plan["reason"])

    def test_size_threshold_never_empties_keep(self):
        text = "## 2026-08-01 -- only\n" + "x" * 5000 + "\n"
        plan = archive_plan(
            text,
            kind="decisions",
            now="2026-08-02T00:00:00Z",
            keep_recent=1,
            min_age_days=1,
            size_threshold_bytes=100,
        )
        self.assertEqual(1, len(split_decisions_sections(plan["keep"])))


if __name__ == "__main__":
    unittest.main()
