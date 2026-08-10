"""REVIEW2-1: unified offline test entry guard tests.

Contract: ``scripts/test.py`` is the single official test entry point,
discovering all suites with the correct per-suite file patterns, failing
closed (exit 3) when a suite discovers zero tests, and being used by every
quality-gate test stage (REVIEW2-1 / second-architect-review P1).
"""

from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location(
    "test_entry", ROOT / "scripts" / "test.py"
)
entry = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / "scripts"))
assert spec.loader is not None
spec.loader.exec_module(entry)

gate_spec = importlib.util.spec_from_file_location(
    "quality_gate", ROOT / "scripts" / "quality_gate.py"
)
quality_gate = importlib.util.module_from_spec(gate_spec)
assert gate_spec.loader is not None
gate_spec.loader.exec_module(quality_gate)


class TestEntryGuardTests(unittest.TestCase):
    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "scripts" / "test.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        allowed = set(sys.stdlib_module_names) | {"src"}
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] not in allowed:
                        bad.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    continue
                if node.module and node.module.split(".")[0] not in allowed:
                    bad.append(node.module)
        self.assertEqual([], bad, "third-party imports found in scripts/test.py")

    def test_zero_tests_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests" / "unit").mkdir(parents=True)
            summary = entry.run_suite(root, "unit")
            self.assertEqual(summary["discovered"], 0)
            self.assertEqual(summary["exit_code"], entry.NO_TESTS_EXIT)
            self.assertFalse(summary["ok"])

    def test_tiny_suite_runs_and_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            suite_dir = root / "tests" / "unit"
            suite_dir.mkdir(parents=True)
            (suite_dir / "test_mini.py").write_text(
                "import unittest\n"
                "class Mini(unittest.TestCase):\n"
                "    def test_ok(self): self.assertTrue(True)\n",
                encoding="utf-8",
            )
            summary = entry.run_suite(root, "unit")
            self.assertEqual(summary["discovered"], 1)
            self.assertEqual(summary["passed"], 1)
            self.assertEqual(summary["failed"], 0)
            self.assertEqual(summary["exit_code"], 0)
            self.assertTrue(summary["ok"])

    def test_cli_win7_suite_repo_exit_zero(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "test.py"), "--suite", "win7"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("discovered=", proc.stdout)
        self.assertIn("[win7]", proc.stdout)

    def test_all_gate_test_stages_use_unified_entry(self) -> None:
        test_argv = [sys.executable, str(ROOT / "scripts" / "test.py"), "--suite"]
        cases = {
            "unit": ("test", 0),
            "integration": ("test", 1),
            "security": ("test-security", 0),
            "e2e": ("test-e2e", 0),
            "win7": ("test-win7", 0),
        }
        for suite, (stage, index) in cases.items():
            command = quality_gate.TARGETS[stage][index]
            self.assertEqual(command[:3], test_argv)
            self.assertEqual(command[3], suite)


if __name__ == "__main__":
    unittest.main()
