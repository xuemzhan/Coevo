"""FRAMEWORK-OPTIMIZE-18: shared non-empty validator + SAFE_ID leftover guard."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from src.coevo.validate import non_empty_string


ROOT = Path(__file__).resolve().parents[2]


class NonEmptyStringTests(unittest.TestCase):
    def test_accepts_non_empty(self):
        non_empty_string("abc", error_factory=ValueError, field="name")
        non_empty_string("  abc  ", error_factory=ValueError, field="name")

    def test_rejects_empty_and_whitespace(self):
        for bad in ("", "   ", "\t\n"):
            with self.assertRaisesRegex(ValueError, "name must be a non-empty string"):
                non_empty_string(bad, error_factory=ValueError, field="name")

    def test_rejects_non_string(self):
        with self.assertRaisesRegex(ValueError, "name must be a non-empty string"):
            non_empty_string(123, error_factory=ValueError, field="name")
        with self.assertRaisesRegex(ValueError, "name must be a non-empty string"):
            non_empty_string(None, error_factory=ValueError, field="name")

    def test_error_factory_preserves_exception_class(self):
        with self.assertRaises(RuntimeError):
            non_empty_string("", error_factory=RuntimeError, field="x")


class UnificationGuardTests(unittest.TestCase):
    def test_knowledge_base_uses_shared_safe_id(self):
        text = (ROOT / "src/coevo/knowledge_base/models.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "from src.coevo.ids import SAFE_ID as _SAFE_ID", text
        )
        # No local safe-id regex copy remains.
        local = re.search(
            r"_SAFE_ID\s*=\s*re\.compile\(r\"\^\[a-zA-Z0-9_\].*", text
        )
        self.assertIsNone(local, "knowledge_base must not keep a local SAFE_ID regex")

    def test_risk_supervision_delegate_non_empty_to_shared_leaf(self):
        for relative in (
            "src/coevo/risk/models.py",
            "src/coevo/supervision/models.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                "non_empty_string", text, f"{relative} must use the shared validator"
            )
            self.assertNotIn(
                'raise ValueError(f"{field} must be a non-empty string")',
                text,
                f"{relative} must not keep a local _non_empty copy",
            )


if __name__ == "__main__":
    unittest.main()
