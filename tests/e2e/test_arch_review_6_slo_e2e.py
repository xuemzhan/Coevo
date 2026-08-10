"""ARCH-REVIEW-6 e2e: the real demo pipeline drives SLO metrics.

Runs the offline composition root once and feeds its actual outputs
(orchestration outcome, audit events, package round-trip) into the SLO
aggregators; any threshold violation fails the gate.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.app import run_demo_pipeline  # noqa: E402
from src.coevo.slo import (  # noqa: E402
    assert_slo_thresholds,
    audit_coverage,
    dispatch_success_rate,
    package_round_trip_rate,
)


class SloE2ETests(unittest.TestCase):
    def test_real_pipeline_meets_slo_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_demo_pipeline(Path(tmp))
            observed_actions = tuple(
                event.action for event in result.hub.recent_events()
            )
            metrics = {
                "dispatch_success": dispatch_success_rate((result.outcome,)),
                "audit_coverage": audit_coverage(
                    observed_actions,
                    (
                        "chain.completed",
                        "package.exported",
                        "knowledge.stored",
                    ),
                ),
                "package_round_trip": package_round_trip_rate(
                    1 if result.package_wire_sha256 else 0, 1
                ),
            }
            violations = assert_slo_thresholds(metrics)
            self.assertEqual([], violations, violations)
            if result.store is not None and hasattr(result.store, "close"):
                result.store.close()


if __name__ == "__main__":
    unittest.main()
