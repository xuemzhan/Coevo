"""FRAMEWORK-OPTIMIZE-19: _util extraction + models delegation guards."""
from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.decision_brief import models
from src.coevo.decision_brief._util import (
    _digest,
    _encode_json,
    _safe_string,
    _stat_is_reparse,
    _parse_utc,
)


ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "src/coevo/decision_brief/models.py"
UTIL = ROOT / "src/coevo/decision_brief/_util.py"


class UtilBehaviorTests(unittest.TestCase):
    def test_digest_validates_lowercase_sha256(self):
        _digest("a" * 64, field="d", error_factory=ValueError)
        with self.assertRaisesRegex(ValueError, "lowercase SHA-256"):
            _digest("A" * 64, field="d", error_factory=ValueError)
        with self.assertRaisesRegex(ValueError, "lowercase SHA-256"):
            _digest("a" * 63, field="d", error_factory=ValueError)

    def test_encode_json_bounded(self):
        payload = _encode_json({"a": 1}, max_bytes=1000, error_factory=ValueError)
        self.assertEqual(b'{"a":1}', payload)
        with self.assertRaisesRegex(ValueError, "byte limit"):
            _encode_json({"a": "x" * 2000}, max_bytes=100, error_factory=ValueError)

    def test_safe_string_and_reparse_helpers(self):
        _safe_string("ok", field="f", max_bytes=8, error_factory=ValueError)
        with self.assertRaises(ValueError):
            _safe_string("", field="f", max_bytes=8, error_factory=ValueError)

        class _Info:
            st_file_attributes = 0

        self.assertFalse(_stat_is_reparse(_Info()))

    def test_parse_utc_delegates_to_timefmt(self):
        parsed = _parse_utc(
            "2026-08-08T12:00:00Z",
            field="ts",
            error_factory=ValueError,
            not_utc_message="nz",
            invalid_message="inv",
        )
        self.assertEqual(12, parsed.hour)


class ExtractionGuardTests(unittest.TestCase):
    def test_models_imports_util_leaf(self):
        text = MODELS.read_text(encoding="utf-8")
        self.assertIn("from ._util import", text)

    def test_models_keeps_export_surface(self):
        # The historical private import surface stays importable from models.
        for name in (
            "_ZERO_DIGEST",
            "_safe_string",
            "_digest",
            "_encode_json",
            "_stat_is_reparse",
            "_is_link_or_reparse",
            "_parse_utc",
        ):
            self.assertTrue(hasattr(models, name), f"models.{name} must be re-exported")

    def test_util_has_no_domain_import(self):
        text = UTIL.read_text(encoding="utf-8")
        self.assertNotIn("from .models import", text)
        self.assertNotIn("from src.coevo.decision_brief.models", text)

    def test_no_local_logic_copies_in_models(self):
        text = MODELS.read_text(encoding="utf-8")
        for marker in (
            'st_file_attributes',
            'lowercase SHA-256',
            'value is not canonical JSON',
        ):
            self.assertNotIn(marker, text, f"models.py must not keep util logic: {marker}")


if __name__ == "__main__":
    unittest.main()
