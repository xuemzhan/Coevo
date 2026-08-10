"""ENG-OPTIMIZE-2: VERIFICATION derived from the Phase A results JSON."""

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


def _sample_results_json(path: Path) -> None:
    payload = {
        "schema_version": "1.0",
        "target": "fast",
        "fingerprint": "a" * 16,
        "exit_code": 0,
        "ok": True,
        "started_at": "2026-08-10T00:00:00Z",
        "duration_ms": 1000,
        "stages": [
            {
                "argv": ["python", "test.py", "--suite", "win7"],
                "exit_code": 0,
                "duration_ms": 100,
                "output_tail": "discovered=4 passed=4 failed=0 skipped=0\n",
                "discovered": 4,
                "passed": 4,
                "failed": 0,
                "skipped": 0,
            }
        ],
        "totals": {"discovered": 4, "passed": 4, "failed": 0, "skipped": 0},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


class VerificationFromJsonTests(unittest.TestCase):
    def test_body_from_json_contains_argv_counts_and_totals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp) / "results.json"
            _sample_results_json(results)
            body = quality_gate._verification_body_from_json(results)
        self.assertIn("$ python test.py --suite win7", body)
        self.assertIn("discovered=4 passed=4 failed=0 skipped=0", body)
        self.assertIn("totals", body)
        self.assertIn('"discovered": 4', body)

    def test_record_gate_result_writes_json_derived_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / "results.json"
            verification = root / "VERIFICATION.md"
            _sample_results_json(results)
            with (
                mock.patch.object(quality_gate, "append_record"),
                mock.patch.object(quality_gate, "seal"),
                mock.patch.object(
                    quality_gate, "verify_seal", return_value="fully-sealed"
                ),
                mock.patch.object(
                    quality_gate, "_trim_records_to_policy", return_value=""
                ),
            ):
                rc = quality_gate._record_gate_result(
                    "fast",
                    "a" * 16,
                    0,
                    [],
                    "2026-08-10T00:00:00Z",
                    results_json=results,
                    verification=verification,
                )
            text = verification.read_text(encoding="utf-8")
        self.assertEqual(rc, 0)
        self.assertIn("target=`fast`", text)
        self.assertIn("audit seal: fully-sealed", text)
        self.assertIn("discovered=4 passed=4 failed=0 skipped=0", text)

    def test_record_gate_result_falls_back_to_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            verification = Path(tmp) / "VERIFICATION.md"
            with (
                mock.patch.object(quality_gate, "append_record"),
                mock.patch.object(quality_gate, "seal"),
                mock.patch.object(
                    quality_gate, "verify_seal", return_value="fully-sealed"
                ),
                mock.patch.object(
                    quality_gate, "_trim_records_to_policy", return_value=""
                ),
            ):
                rc = quality_gate._record_gate_result(
                    "fast",
                    "a" * 16,
                    0,
                    ["stage output line\n"],
                    "2026-08-10T00:00:00Z",
                    results_json=None,
                    verification=verification,
                )
            text = verification.read_text(encoding="utf-8")
        self.assertEqual(rc, 0)
        self.assertIn("stage output line", text)


if __name__ == "__main__":
    unittest.main()
