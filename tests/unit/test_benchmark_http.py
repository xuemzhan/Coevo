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
    def test_probe_completes_with_zero_errors(self):
        result = benchmark._cockpit_http_probe()
        self.assertEqual("cockpit_http", result.name)
        self.assertEqual(128, result.samples)
        self.assertEqual("le", result.comparison)
        self.assertEqual(benchmark.COCKPIT_HTTP_P95_LIMIT_SEC, result.limit)
        self.assertTrue(result.ok, result.detail)
        self.assertIn("errors=0", result.detail)
        self.assertGreater(result.value, 0.0)

    def test_probe_reports_latency_bounds(self):
        result = benchmark._cockpit_http_probe()
        self.assertLess(result.value, result.limit)
        self.assertIn("p50=", result.detail)
        self.assertIn("max=", result.detail)


if __name__ == "__main__":
    unittest.main()
