"""OPTIMIZE-11: exit-code decision tests for the locked loop-stop script."""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "check_loop_stop", ROOT / "scripts" / "check_loop_stop.py"
)
check_loop_stop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_loop_stop)


class CheckLoopStopTests(unittest.TestCase):
    def _run_with_state(self, payload: object | None) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "loop"
            state_path.mkdir()
            if payload is not None:
                (state_path / "STATE.json").write_text(
                    json.dumps(payload), encoding="utf-8"
                )
            previous = os.getcwd()
            try:
                os.chdir(tmp)
                return check_loop_stop.main()
            finally:
                os.chdir(previous)

    def test_missing_state_file_blocks(self):
        self.assertEqual(20, self._run_with_state(None))

    def test_mvp_complete_returns_zero(self):
        self.assertEqual(0, self._run_with_state({"status": "mvp-complete"}))

    def test_done_and_ready_return_continue(self):
        for status in ("done", "in-progress", "ready"):
            with self.subTest(status=status):
                self.assertEqual(10, self._run_with_state({"status": status}))

    def test_blocked_states_return_20(self):
        for status in ("blocked", "security-blocked", "decision-required"):
            with self.subTest(status=status):
                self.assertEqual(20, self._run_with_state({"status": status}))

    def test_malformed_json_blocks_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "loop"
            state_path.mkdir()
            (state_path / "STATE.json").write_text("{not json", encoding="utf-8")
            previous = os.getcwd()
            try:
                os.chdir(tmp)
                self.assertEqual(20, check_loop_stop.main())
            finally:
                os.chdir(previous)

    def test_non_object_state_blocks(self):
        self.assertEqual(20, self._run_with_state([1, 2, 3]))


if __name__ == "__main__":
    unittest.main()
