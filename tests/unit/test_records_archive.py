"""Unit tests for the records archiving policy helpers."""
from __future__ import annotations

import unittest

from src.coevo.records_archive import (
    archive_plan,
    split_audit_lines,
    split_decisions_sections,
    split_verification_sections,
)


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


if __name__ == "__main__":
    unittest.main()
