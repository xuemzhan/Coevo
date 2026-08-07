"""OPTIMIZE-15: behavioral tests for the locked control-archive entry point."""
from __future__ import annotations

import importlib.util
import runpy
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "control_main", ROOT / "scripts" / "control_main.py"
)

EXPECTED_MODULES = {
    "check_loop_stop",
    "audit_log",
    "audit_seal",
    "traceability_check",
    "quality_gate",
    "validate_opencode",
}


def _load(argv: list[str], runpy_mock: mock.Mock):
    module = importlib.util.module_from_spec(SPEC)
    with mock.patch.object(sys, "argv", argv), mock.patch.object(
        runpy, "run_module", runpy_mock
    ):
        SPEC.loader.exec_module(module)
    return module


class ControlMainTests(unittest.TestCase):
    def test_missing_arg_exits_with_usage(self):
        with self.assertRaises(SystemExit) as ctx:
            _load(["control_main.py"], mock.Mock())
        self.assertIn("usage:", str(ctx.exception.code))

    def test_unknown_module_exits_with_usage(self):
        with self.assertRaises(SystemExit) as ctx:
            _load(["control_main.py", "bogus"], mock.Mock())
        self.assertIn("usage:", str(ctx.exception.code))

    def test_dispatch_calls_runpy_for_valid_module(self):
        argv = ["control_main.py", "traceability_check"]
        runpy = mock.Mock()
        _load(argv, runpy)
        runpy.assert_called_once_with(
            "traceability_check", run_name="__main__", alter_sys=True
        )
        # argv[0] is rewritten to the module name; the module arg is consumed.
        self.assertEqual("traceability_check", argv[0])
        self.assertEqual(1, len(argv))

    def test_modules_contains_expected_set(self):
        module = _load(["control_main.py", "audit_log"], mock.Mock())
        self.assertEqual(EXPECTED_MODULES, set(module.MODULES))


if __name__ == "__main__":
    unittest.main()
