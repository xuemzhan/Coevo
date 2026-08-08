"""FRAMEWORK-OPTIMIZE-14: shared JSON duplicate-key rejection guard."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.jsonutil import reject_duplicate_pairs


ROOT = Path(__file__).resolve().parents[2]


class RejectDuplicatePairsTests(unittest.TestCase):
    def test_merges_unique_pairs(self) -> None:
        self.assertEqual(
            {"a": 1, "b": 2},
            reject_duplicate_pairs([("a", 1), ("b", 2)]),
        )
        self.assertEqual({}, reject_duplicate_pairs([]))

    def test_rejects_duplicate_keys_with_injected_factory(self) -> None:
        class CustomError(Exception):
            pass

        with self.assertRaises(CustomError) as ctx:
            reject_duplicate_pairs(
                [("a", 1), ("a", 2)], error_factory=CustomError
            )
        self.assertIn("duplicate key", str(ctx.exception))

    def test_default_factory_is_value_error(self) -> None:
        with self.assertRaises(ValueError):
            reject_duplicate_pairs([("x", 1), ("x", 2)])


class DuplicateKeyGuardConsolidationTests(unittest.TestCase):
    def test_modules_no_longer_define_local_guards(self) -> None:
        modules = (
            "src/coevo/protocol/agent_package.py",
            "src/coevo/framework/k8s_listing.py",
            "src/coevo/crypto/cng_handle.py",
            "src/coevo/cockpit/state_store.py",
            "src/coevo/framework/manifest_checker.py",
        )
        for relative in modules:
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(
                "def _reject_duplicate_keys", source, relative
            )
            self.assertNotIn(
                "def _reject_duplicate_pairs", source, relative
            )
            self.assertNotIn("def _unique_pairs", source, relative)
            self.assertIn("reject_duplicate_pairs", source, relative)


if __name__ == "__main__":
    unittest.main()
