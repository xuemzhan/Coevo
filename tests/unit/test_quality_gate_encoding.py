"""QUALITY-GATE-ENCODING-1: quality gate child-process UTF-8 capture tests."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "quality_gate", SCRIPTS / "quality_gate.py"
)
quality_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quality_gate)


class QualityGateEncodingTests(unittest.TestCase):
    def test_gate_env_forces_utf8_and_does_not_mutate_parent(self):
        before = dict(os.environ)
        env = quality_gate.gate_env()
        self.assertEqual("utf-8", env["PYTHONIOENCODING"])
        self.assertEqual("1", env["PYTHONUTF8"])
        # The helper must copy, not mutate, the parent environment.
        self.assertEqual(before, dict(os.environ))

    def test_gate_env_captures_child_chinese_without_replacement_chars(self):
        payload = "注册门接入与 Manifest 构建器"
        result = subprocess.run(
            [sys.executable, "-c", f"print('{payload}')"],
            env=quality_gate.gate_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, result.returncode)
        self.assertIn(payload, result.stdout)
        self.assertNotIn("\ufffd", result.stdout)

    def test_every_gate_subprocess_run_uses_gate_env(self):
        source = (SCRIPTS / "quality_gate.py").read_text(encoding="utf-8")
        self.assertNotIn("env=None", source)
        self.assertGreaterEqual(source.count("env=gate_env()"), 2)


if __name__ == "__main__":
    unittest.main()
