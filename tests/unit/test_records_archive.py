"""Unit tests for the records archiving policy helpers."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from src.coevo.records_archive import (
    POLICY,
    archive_plan,
    over_policy_size,
    split_audit_lines,
    split_decisions_sections,
    split_verification_sections,
)


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class ArchivePolicyTests(unittest.TestCase):
    """RECORDS-ARCHIVE-2: policy lives in ``records_archive`` as one source."""

    def test_verification_policy_keeps_file_readable(self):
        policy = POLICY["verification"]
        self.assertLessEqual(policy["keep_recent"], 30)
        self.assertLessEqual(policy["size"], 500_000)

    def test_other_policies_are_unchanged(self):
        self.assertEqual(20, POLICY["decisions"]["keep_recent"])
        self.assertEqual(2000, POLICY["audit"]["keep_recent"])

    def test_script_imports_policy_from_module(self):
        spec = importlib.util.spec_from_file_location(
            "archive_records", SCRIPTS / "archive_records.py"
        )
        script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script)
        self.assertIs(script.POLICY, POLICY)


class OverPolicySizeTests(unittest.TestCase):
    def test_under_threshold_is_false(self):
        self.assertFalse(over_policy_size("verification", "x" * 10))

    def test_exact_threshold_is_false(self):
        text = "x" * POLICY["verification"]["size"]
        self.assertFalse(over_policy_size("verification", text))

    def test_over_threshold_is_true(self):
        text = "x" * (POLICY["verification"]["size"] + 1)
        self.assertTrue(over_policy_size("verification", text))

    def test_decisions_and_audit_kinds_use_their_own_caps(self):
        self.assertTrue(
            over_policy_size("decisions", "x" * (POLICY["decisions"]["size"] + 1))
        )
        self.assertFalse(over_policy_size("audit", "x" * 1000))

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            over_policy_size("bogus", "x")

    def test_non_string_text_is_rejected(self):
        with self.assertRaises(TypeError):
            over_policy_size("verification", 123)  # type: ignore[arg-type]


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

    def test_size_trim_leaves_headroom_below_threshold(self):
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
            size_tail_budget_bytes=50,
        )
        # The trim target is threshold - budget, so the kept tail fits with
        # headroom instead of landing exactly at the cap.
        self.assertLessEqual(len(plan["keep"].encode("utf-8")), 350)
        self.assertNotIn("2026-07-01", plan["keep"])

    def test_size_bytes_override_uses_true_file_size(self):
        text = (
            "## 2026-07-01 -- a\n" + "x" * 300 + "\n"
            "## 2026-07-02 -- b\n" + "y" * 300 + "\n"
        )
        plan = archive_plan(
            text,
            kind="decisions",
            now="2026-08-02T00:00:00Z",
            keep_recent=2,
            min_age_days=1,
            size_threshold_bytes=700,
            size_bytes=900,
            size_tail_budget_bytes=400,
        )
        self.assertGreaterEqual(plan["archived_sections"], 1)
        self.assertIn("900 > 700", plan["reason"])

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
