"""Unit tests for the offline benchmark harness."""
from __future__ import annotations

import time
import unittest

from src.coevo.benchmarks import (
    SCALABILITY_PROBES,
    SLA_TARGETS,
    BenchmarkResult,
    measure,
    report,
)


class SlaTableTests(unittest.TestCase):
    def test_targets_cover_reference_architecture(self):
        names = {target.name for target in SLA_TARGETS}
        self.assertEqual(
            {"page_open", "task_query", "package_check", "dir_discovery", "package_generation"},
            names,
        )
        page = next(target for target in SLA_TARGETS if target.name == "page_open")
        self.assertEqual(3.0, page.limit_value)
        generation = next(target for target in SLA_TARGETS if target.name == "package_generation")
        self.assertEqual("ge", generation.comparison)


class ScalabilityProbeTableTests(unittest.TestCase):
    """The 2026-08-02 optimization probes are additive to the SLA table."""

    def test_probe_table_has_expected_scenarios(self):
        names = {target.name for target in SCALABILITY_PROBES}
        self.assertEqual(
            {
                "dag_toposort",
                "graph_lookup",
                "watcher_rescan",
                "talent_recommend",
                "registry_lookup",
                "flow_json_group",
                "audit_stream_append",
            },
            names,
        )

    def test_probes_are_le_comparisons_with_positive_limits(self):
        for target in SCALABILITY_PROBES:
            self.assertEqual("le", target.comparison)
            self.assertGreater(target.limit_value, 0.0)

    def test_probes_do_not_overlap_reference_sla_targets(self):
        sla_names = {target.name for target in SLA_TARGETS}
        probe_names = {target.name for target in SCALABILITY_PROBES}
        self.assertTrue(sla_names.isdisjoint(probe_names))


class MeasureTests(unittest.TestCase):
    def test_fast_function_passes_le_limit(self):
        result = measure(
            "x",
            "quick",
            lambda: None,
            limit=1.0,
            unit="seconds",
            samples=10,
        )
        self.assertTrue(result.ok)
        self.assertEqual(10, result.samples)

    def test_slow_function_fails_le_limit(self):
        def slow() -> None:
            time.sleep(0.05)

        result = measure("x", "slow", slow, limit=0.01, unit="seconds", samples=1)
        self.assertFalse(result.ok)

    def test_ge_comparison_uses_returned_value(self):
        result = measure(
            "success",
            "rate",
            lambda: 97.0,
            limit=95.0,
            unit="percent",
            comparison="ge",
        )
        self.assertTrue(result.ok)
        self.assertEqual(97.0, result.value)

    def test_invalid_arguments_are_rejected(self):
        with self.assertRaises(TypeError):
            measure("x", "m", "not callable", limit=1.0, unit="s")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            measure("x", "m", lambda: None, limit=0, unit="s")
        with self.assertRaises(ValueError):
            measure("x", "m", lambda: None, limit=1.0, unit="s", samples=0)
        with self.assertRaises(ValueError):
            measure("x", "m", lambda: None, limit=1.0, unit="s", comparison="bad")


class ReportTests(unittest.TestCase):
    def test_report_is_json_safe(self):
        import json

        result = measure("x", "quick", lambda: None, limit=1.0, unit="seconds")
        data = report((result,))
        self.assertTrue(data["all_ok"])
        self.assertEqual("1.0", data["schema_version"])
        json.dumps(data)

    def test_report_requires_results(self):
        with self.assertRaises(ValueError):
            report(())

    def test_result_mapping_shape(self):
        result = BenchmarkResult(
            "x", "m", 0.1, "seconds", 1.0, "le", True, 5, detail="d"
        )
        mapping = result.to_mapping()
        self.assertEqual("x", mapping["name"])
        self.assertEqual(5, mapping["samples"])
        self.assertEqual("d", mapping["detail"])


if __name__ == "__main__":
    unittest.main()
