"""FRAMEWORK-OPTIMIZE-11: shared safe-id leaf (ids.py)."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.ids import SAFE_ID, is_safe_id


ROOT = Path(__file__).resolve().parents[2]


class SafeIdTests(unittest.TestCase):
    def test_shared_pattern_matches_repository_form(self) -> None:
        self.assertEqual(
            r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$", SAFE_ID.pattern
        )
        for value in ("a", "a.b_c-1", "_x", "x" * 64, "0start"):
            self.assertTrue(is_safe_id(value), value)

    def test_is_safe_id_fails_closed(self) -> None:
        for value in ("", ".lead", "-lead", "a" * 65, "has space", None, 123):
            self.assertFalse(is_safe_id(value), repr(value))


class SafeIdConsolidationGuardTests(unittest.TestCase):
    def test_modules_use_shared_safe_id(self) -> None:
        modules = (
            "src/coevo/workspace/paths.py",
            "src/coevo/cockpit/models.py",
            "src/coevo/report/models.py",
            "src/coevo/progress_capture/models.py",
            "src/coevo/audit_governance/stream.py",
            "src/coevo/orchestrator/models.py",
            "src/coevo/framework/tools.py",
        )
        for relative in modules:
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(
                're.compile(r"^[a-zA-Z0-9_]',
                source,
                f"{relative} must import SAFE_ID from src.coevo.ids",
            )
            self.assertIn(
                "from src.coevo.ids import SAFE_ID as _SAFE_ID",
                source,
                f"{relative} must alias the shared SAFE_ID",
            )

    def test_semantic_difference_modules_keep_their_own_pattern(self) -> None:
        # task_flow requires a letter/underscore first char (no leading digit);
        # talent validates with a hand-written check. Both intentionally differ.
        task_flow = (
            ROOT / "src" / "coevo" / "task_flow" / "parser.py"
        ).read_text(encoding="utf-8")
        self.assertIn('r"^[a-zA-Z_]', task_flow)
        talent = (
            ROOT / "src" / "coevo" / "talent" / "store.py"
        ).read_text(encoding="utf-8")
        self.assertIn("def _is_safe_id", talent)


if __name__ == "__main__":
    unittest.main()
