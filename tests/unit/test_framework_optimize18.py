"""FRAMEWORK-OPTIMIZE-17: shared ISO-UTC parser + unification guards."""
from __future__ import annotations

import datetime as dt
import unittest
from pathlib import Path

from src.coevo.timefmt import parse_iso_utc


ROOT = Path(__file__).resolve().parents[2]


class ParseIsoUtcTests(unittest.TestCase):
    def test_valid_utc_z_parses(self):
        parsed = parse_iso_utc(
            "2026-08-08T12:00:00Z",
            error_factory=ValueError,
            not_utc_message="nz",
            invalid_message="inv",
        )
        self.assertEqual(dt.datetime(2026, 8, 8, 12, 0, 0, tzinfo=dt.timezone.utc), parsed)

    def test_valid_with_fractional_seconds(self):
        parsed = parse_iso_utc(
            "2026-08-08T12:00:00.123456Z",
            error_factory=ValueError,
            not_utc_message="nz",
            invalid_message="inv",
        )
        self.assertEqual(123456, parsed.microsecond)

    def test_missing_z_raises_not_utc_message(self):
        with self.assertRaisesRegex(RuntimeError, "NOT_UTC"):
            parse_iso_utc(
                "2026-08-08T12:00:00",
                error_factory=RuntimeError,
                not_utc_message="NOT_UTC",
                invalid_message="INVALID",
            )

    def test_malformed_raises_invalid_message(self):
        with self.assertRaisesRegex(ValueError, "INVALID"):
            parse_iso_utc(
                "2026-13-99T99:99:99Z",
                error_factory=ValueError,
                not_utc_message="NOT_UTC",
                invalid_message="INVALID",
            )

    def test_non_string_raises_not_utc(self):
        with self.assertRaisesRegex(ValueError, "NOT_UTC"):
            parse_iso_utc(
                123,
                error_factory=ValueError,
                not_utc_message="NOT_UTC",
                invalid_message="INVALID",
            )

    def test_error_factory_preserves_exception_class(self):
        with self.assertRaises(ValueError):
            parse_iso_utc(
                "x",
                error_factory=ValueError,
                not_utc_message="nz",
                invalid_message="inv",
            )


class UnificationGuardTests(unittest.TestCase):
    def test_modules_delegate_to_shared_parser(self):
        for relative in (
            "src/coevo/decision_brief/models.py",
            "src/coevo/merge/receipt.py",
            "src/coevo/risk/models.py",
            "src/coevo/supervision/models.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                "parse_iso_utc", text, f"{relative} must use the shared parser"
            )

    def test_no_local_fromisoformat_parse_copies(self):
        for relative in (
            "src/coevo/decision_brief/models.py",
            "src/coevo/merge/receipt.py",
            "src/coevo/risk/models.py",
            "src/coevo/supervision/models.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(
                'fromisoformat(value[:-1] + "+00:00")',
                text,
                f"{relative} must not keep a local ISO-UTC parser copy",
            )


if __name__ == "__main__":
    unittest.main()
