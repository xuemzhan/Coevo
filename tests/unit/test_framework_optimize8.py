"""FRAMEWORK-OPTIMIZE-8: real-chain resume failure finish consolidation."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from src.coevo.orchestrator import (
    OrchestrationChain,
    OrchestrationEvent,
    OrchestrationEventKind,
    OrchestrationStep,
    OrchestrationStepKind,
)
from src.coevo.orchestrator._real_chain import (
    RealChainOutcome,
    _finish_resume_escalated,
)
from src.coevo.workspace.models import WorkspaceEntry


ROOT = Path(__file__).resolve().parents[2]


class FinishResumeEscalatedTests(unittest.TestCase):
    def test_helper_builds_escalated_result_and_finishes_store(self) -> None:
        chain = OrchestrationChain(
            "ch.1",
            (OrchestrationStep(0, OrchestrationStepKind.AGENT_CALL, "a.1"),),
        )
        event = OrchestrationEvent(
            "ev.1", OrchestrationEventKind.DISPATCH, "PRJ001", "t.1", {},
            "2026-08-08T02:00:00.000000Z",
        )
        workspace = WorkspaceEntry("PRJ001", "a.pm", "pkg.input", "PRJ001-R0001")
        store = mock.Mock()
        store.store_id = "s.1"
        confirmed = RealChainOutcome(
            chain_id="ch.1",
            event_id="ev.1",
            workspace_project_id="PRJ001",
            flow_understanding_summary=(),
            baseline_summary=(),
            recommendation_summary=(),
            package_summary=(),
            orch_report=None,
            event_digest="0" * 64,
            project_input_digest="1" * 64,
            confirmation_digest="2" * 64,
            package_preview=None,
            store_id="s.1",
        )
        traces: list[object] = []
        summaries = {"flow": [], "baseline": [], "talent": [], "package": []}
        result = _finish_resume_escalated(
            chain, event, workspace, traces, summaries, confirmed,
            "resume.digest", store, "2026-08-08T02:00:00.000000Z",
            chain.steps[0], "CRYPTO_CAPABILITY_UNAVAILABLE",
        )
        self.assertEqual("escalated", result.orch_report.outcome.value)
        self.assertEqual(1, len(result.orch_report.trace))
        self.assertEqual(
            "escalated", result.orch_report.trace[-1].result.value
        )
        store.finish_resume_failure.assert_called_once()
        args = store.finish_resume_failure.call_args.args
        self.assertEqual(
            ("ev.1", "0" * 64, "resume.digest"), args[:3]
        )
        self.assertEqual("CRYPTO_CAPABILITY_UNAVAILABLE", args[4])


class ConsolidationGuardTests(unittest.TestCase):
    def test_resume_failure_paths_are_consolidated(self) -> None:
        source = (
            ROOT / "src" / "coevo" / "orchestrator" / "_real_chain.py"
        ).read_text(encoding="utf-8")
        self.assertIn("def _finish_resume_escalated", source)
        for code in (
            "CRYPTO_PACKAGE_VERIFICATION_FAILED",
            "CRYPTO_CAPABILITY_UNAVAILABLE",
        ):
            self.assertEqual(
                1, source.count(code), f"code must appear once: {code}"
            )


if __name__ == "__main__":
    unittest.main()
