"""ENG-OPTIMIZE-1: gate results JSON per-stage test counts guard tests."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location(
    "quality_gate", ROOT / "scripts" / "quality_gate.py"
)
quality_gate = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / "scripts"))
assert spec.loader is not None
sys.modules[spec.name] = quality_gate
spec.loader.exec_module(quality_gate)


class GateCountsTests(unittest.TestCase):
    def test_parse_test_counts(self) -> None:
        sample = (
            "[split] pkg: models=2\n"
            "discovered=1399 passed=1396 failed=0 skipped=3 duration_ms=65067\n"
        )
        self.assertEqual(
            quality_gate._parse_test_counts(sample), (1399, 1396, 0, 3)
        )
        self.assertIsNone(quality_gate._parse_test_counts("no summary here"))

    def test_run_one_populates_counts_from_unified_entry(self) -> None:
        result = quality_gate._run_one(
            [sys.executable, str(ROOT / "scripts" / "test.py"), "--suite", "win7"],
            timeout_sec=120,
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIsNotNone(result.discovered)
        self.assertEqual(result.discovered, 4)
        self.assertEqual(result.failed, 0)

    def test_results_artifact_contains_counts_and_totals(self) -> None:
        stage = quality_gate.StageResult(
            argv=("python", "test.py", "--suite", "win7"),
            exit_code=0,
            duration_ms=100,
            output="discovered=4 passed=4 failed=0 skipped=0 duration_ms=100\n",
            discovered=4,
            passed=4,
            failed=0,
            skipped=0,
        )
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                quality_gate, "GATE_RESULTS_DIR", Path(tmp)
            ):
                path = quality_gate._write_results_json(
                    "test-win7", "a" * 16, 0, [stage], "2026-08-10T00:00:00Z", 100
                )
            artifact = json.loads(Path(path).read_text(encoding="utf-8"))
        self.assertEqual(artifact["stages"][0]["discovered"], 4)
        self.assertEqual(artifact["totals"]["passed"], 4)
        self.assertEqual(artifact["totals"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()
