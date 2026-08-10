"""REVIEW2-2: two-phase quality gate guard tests.

Contract (docs/architecture/gate-phases.md):

* Phase A runs every stage without governance recording from the gate and
  writes a machine-readable results JSON under loop/runtime/gate-results/;
* Phase B (audit append, final seal, VERIFICATION write, records trim) runs
  only after all stages finished;
* each target has an independent stage timeout and progress is printed;
* a single stage fails closed on nonzero exit and on timeout (exit=13).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location(
    "quality_gate", ROOT / "scripts" / "quality_gate.py"
)
quality_gate = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / "scripts"))
assert spec.loader is not None
sys.modules[spec.name] = quality_gate
spec.loader.exec_module(quality_gate)


class TwoPhaseGateTests(unittest.TestCase):
    def test_phase_functions_and_constants_exist(self) -> None:
        for name in ("_run_stages", "_write_results_json", "_record_gate_result"):
            self.assertTrue(hasattr(quality_gate, name), name)
        for target in (
            "fast",
            "quality",
            "fmt",
            "lint",
            "test",
            "test-security",
            "test-e2e",
            "test-win7",
        ):
            self.assertGreater(quality_gate.STAGE_TIMEOUTS[target], 0, target)
        self.assertEqual(quality_gate.GATE_RESULTS_DIR.name, "gate-results")

    def test_phase_a_runs_before_phase_b(self) -> None:
        source = (ROOT / "scripts" / "quality_gate.py").read_text(encoding="utf-8")
        self.assertLess(
            source.index("_write_results_json("),
            source.index("_record_gate_result("),
        )

    def test_run_one_success_and_failure(self) -> None:
        ok = quality_gate._run_one([sys.executable, "-c", "pass"], timeout_sec=60)
        self.assertEqual(ok.exit_code, 0)
        bad = quality_gate._run_one(
            [sys.executable, "-c", "raise SystemExit(7)"], timeout_sec=60
        )
        self.assertEqual(bad.exit_code, 7)

    def test_run_one_timeout_fail_closed(self) -> None:
        slow = quality_gate._run_one(
            [sys.executable, "-c", "import time; time.sleep(5)"], timeout_sec=1
        )
        self.assertEqual(slow.exit_code, 13)
        self.assertIn("timed out", slow.output)

    def test_doc_exists(self) -> None:
        text = (ROOT / "docs" / "architecture" / "gate-phases.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Phase A", text)
        self.assertIn("Phase B", text)
        self.assertIn("STAGE_TIMEOUTS", text)


if __name__ == "__main__":
    unittest.main()
