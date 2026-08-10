"""ARCH-REVIEW-6: SLO metric aggregator guard tests.

Contract (docs/architecture/slo-metrics.md): the gateable subset of
system-requirements §20 acceptance metrics is computed as deterministic
offline ratios; empty denominators fail closed (0.0); unknown metric names
are violations.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.slo import (
    SLO_DEFAULTS,
    SloValidationError,
    assert_slo_thresholds,
    audit_coverage,
    dispatch_success_rate,
    interception_rate,
    package_round_trip_rate,
    replay_rejection_rate,
)

ROOT = Path(__file__).resolve().parents[2]


class SloMetricsTests(unittest.TestCase):
    def test_dispatch_success_rate(self) -> None:
        self.assertEqual(
            dispatch_success_rate(("completed", "completed", "held")),
            2 / 3,
        )
        self.assertEqual(dispatch_success_rate(()), 0.0)  # no evidence

    def test_replay_and_interception_require_full_rejection(self) -> None:
        self.assertEqual(replay_rejection_rate(3, 3), 1.0)
        self.assertEqual(replay_rejection_rate(2, 3), 2 / 3)
        self.assertEqual(interception_rate(0, 0), 0.0)
        self.assertEqual(interception_rate(5, 5), 1.0)

    def test_audit_coverage(self) -> None:
        self.assertEqual(
            audit_coverage(
                ("chain.completed", "package.exported", "knowledge.stored"),
                ("chain.completed", "package.exported", "knowledge.stored"),
            ),
            1.0,
        )
        self.assertEqual(
            audit_coverage(("chain.completed",), ("chain.completed", "merge")),
            0.5,
        )
        self.assertEqual(audit_coverage((), ("merge",)), 0.0)
        self.assertEqual(audit_coverage((), ()), 1.0)

    def test_package_round_trip(self) -> None:
        self.assertEqual(package_round_trip_rate(1, 1), 1.0)
        self.assertEqual(package_round_trip_rate(0, 1), 0.0)

    def test_threshold_assertions_fail_closed(self) -> None:
        self.assertEqual(
            assert_slo_thresholds(
                {"dispatch_success": 0.96, "audit_coverage": 1.0}
            ),
            [],
        )
        violations = assert_slo_thresholds(
            {"dispatch_success": 0.90, "audit_coverage": 1.0}
        )
        self.assertEqual(len(violations), 1)
        self.assertIn("dispatch_success", violations[0])
        self.assertEqual(
            assert_slo_thresholds({"bogus_metric": 1.0}),
            ["unknown SLO metric: 'bogus_metric'"],
        )

    def test_input_validation(self) -> None:
        with self.assertRaises(SloValidationError):
            dispatch_success_rate("completed")
        with self.assertRaises(SloValidationError):
            replay_rejection_rate(4, 3)

    def test_defaults_are_documented_thresholds(self) -> None:
        self.assertEqual(SLO_DEFAULTS["dispatch_success"], 0.95)
        self.assertEqual(SLO_DEFAULTS["replay_rejection"], 1.0)
        self.assertEqual(SLO_DEFAULTS["interception"], 1.0)
        self.assertEqual(SLO_DEFAULTS["audit_coverage"], 1.0)
        self.assertEqual(SLO_DEFAULTS["package_round_trip"], 1.0)

    def test_docs_exist(self) -> None:
        arch = (ROOT / "docs" / "architecture" / "slo-metrics.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("dispatch_success", arch)
        self.assertIn("试点", arch)
        module = (ROOT / "docs" / "modules" / "slo.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("metrics.py", module)


if __name__ == "__main__":
    unittest.main()
