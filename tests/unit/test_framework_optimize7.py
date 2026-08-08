"""FRAMEWORK-OPTIMIZE-7: real-chain failure finish path consolidation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.coevo.orchestrator import (
    OrchestrationChain,
    OrchestrationEvent,
    OrchestrationEventKind,
    OrchestrationStep,
    OrchestrationStepKind,
    RealChainStore,
)
from src.coevo.orchestrator._real_chain import _escalate_and_finish
from src.coevo.app.demo_support import DemoFreshnessAuthority, DemoSigner
from src.coevo.workspace.models import WorkspaceEntry


ROOT = Path(__file__).resolve().parents[2]


class EscalateFinishTests(unittest.TestCase):
    def test_escalate_and_finish_returns_escalated_outcome(self) -> None:
        chain = OrchestrationChain(
            "ch.1",
            (OrchestrationStep(0, OrchestrationStepKind.AGENT_CALL, "a.1"),),
        )
        event = OrchestrationEvent(
            "ev.1", OrchestrationEventKind.DISPATCH, "PRJ001", "t.1", {},
            "2026-08-08T02:00:00.000000Z",
        )
        workspace = WorkspaceEntry("PRJ001", "a.pm", "pkg.input", "PRJ001-R0001")
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        store = RealChainStore.create(
            Path(temporary.name) / "rc.db",
            signer=DemoSigner(),
            freshness=DemoFreshnessAuthority(),
        )
        try:
            traces: list[object] = []
            summaries = {"flow": [], "baseline": [], "talent": [], "package": []}
            store.begin_dispatch(
                event.event_id, "0" * 64, "PRJ001",
                "2026-08-08T02:00:00.000000Z",
            )
            result = _escalate_and_finish(
                chain, event, workspace, traces, summaries,
                "0" * 64, "0" * 64, None, store,
                "2026-08-08T02:00:00.000000Z",
                chain.steps[0],
                "agent unavailable; human escalation required",
            )
            self.assertEqual("escalated", result.orch_report.outcome.value)
            self.assertEqual(1, len(result.orch_report.trace))
            self.assertEqual(
                "escalated", result.orch_report.trace[-1].result.value
            )
        finally:
            store.close()
            del store
            import gc
            gc.collect()


class ConsolidationGuardTests(unittest.TestCase):
    def test_failure_paths_are_consolidated_into_one_helper(self) -> None:
        source = (
            ROOT / "src" / "coevo" / "orchestrator" / "_real_chain.py"
        ).read_text(encoding="utf-8")
        self.assertIn("def _escalate_and_finish", source)
        for detail in (
            "agent unavailable; human escalation required",
            "facade failed; human escalation required",
            "facade retry failed; human escalation required",
        ):
            self.assertEqual(
                1, source.count(detail), f"detail must appear once: {detail}"
            )


if __name__ == "__main__":
    unittest.main()
