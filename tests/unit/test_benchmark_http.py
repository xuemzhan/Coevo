"""LOAD-1: cockpit HTTP concurrency/latency benchmark probe tests."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "benchmark_cli", ROOT / "scripts" / "benchmark.py"
)
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


class CockpitHttpProbeTests(unittest.TestCase):
    """Structural + SLA assertions over one shared probe result.

    The probe itself already warms up and takes the best of three measured
    rounds (see ``scripts/benchmark.py``), so a single class-level run gives
    deterministic assertions without multiplying the timing surface.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.result = benchmark._cockpit_http_probe()

    def test_probe_completes_with_zero_errors(self):
        result = self.result
        self.assertEqual("cockpit_http", result.name)
        self.assertEqual(128, result.samples)
        self.assertEqual("le", result.comparison)
        self.assertEqual(benchmark.COCKPIT_HTTP_P95_LIMIT_SEC, result.limit)
        self.assertTrue(result.ok, result.detail)
        self.assertIn("errors=0", result.detail)
        self.assertGreater(result.value, 0.0)

    def test_probe_reports_latency_bounds(self):
        result = self.result
        # Match the probe's own SLA comparison (``p95 <= limit``) so an
        # exact-boundary sample does not contradict ``result.ok``.
        self.assertLessEqual(result.value, result.limit)
        self.assertIn("p50=", result.detail)
        self.assertIn("max=", result.detail)

    def test_probe_round_contract_is_bounded(self):
        # The measurement contract stays fixed: 16 workers x 8 requests per
        # round, three measured rounds after a warm-up round.
        self.assertEqual(16, benchmark.COCKPIT_HTTP_WORKERS)
        self.assertEqual(8, benchmark.COCKPIT_HTTP_PER_WORKER)
        self.assertEqual(3, benchmark.COCKPIT_HTTP_PROBE_ROUNDS)


if __name__ == "__main__":
    unittest.main()
