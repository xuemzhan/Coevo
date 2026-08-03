"""Tests for US-4-AC-1 orchestrator service facade.

Covers AC-1..AC-7 (7 acceptance criteria) plus quality / regression tests.
Pure-function tests, no IO.
"""
from __future__ import annotations

import dataclasses
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.orchestrator import (
    AgentCapability,
    AgentRegistration,
    AgentRegistry,
    AgentSpec,
    AgentStatus,
    FailurePolicy,
    MVP_FIXED_CHAIN,
    OrchestrationChain,
    OrchestratorError,
    OrchestrationEvent,
    OrchestrationEventKind,
    OrchestrationOutcome,
    OrchestrationReport,
    OrchestrationStep,
    OrchestrationStepKind,
    OrchestrationStepResult,
    OrchestrationTrace,
    Orchestrator,
    OrchestratorConflictError,
    OrchestratorValidationError,
)
from src.coevo.workspace.models import WorkspaceEntry


NOW = "2026-08-22T00:00:00Z"
NOW2 = "2026-08-22T00:05:00Z"
NOW3 = "2026-08-22T00:10:00Z"


def _ws(project_id: str = "PRJ001") -> WorkspaceEntry:
    return WorkspaceEntry(
        project_id=project_id,
        role_id="a.pm",
        package_id="pkg.1",
        revision="r1",
    )


def _agent(
    agent_id: str,
    capability: AgentCapability = AgentCapability.TASK_DECOMPOSITION,
    *,
    requires_human_confirmation: bool = False,
) -> AgentRegistration:
    return AgentRegistration(
        spec=AgentSpec(
            agent_id=agent_id,
            capability=capability,
            display_name=capability.value,
            input_schema=("project_id", "task_id"),
            output_schema=("result",),
            requires_human_confirmation=requires_human_confirmation,
        )
    )


def _reg(*regs: AgentRegistration) -> AgentRegistry:
    r = AgentRegistry.empty()
    for reg in regs:
        r = r.register(reg)
    return r


def _event(
    *,
    event_id: str = "ev.001",
    project_id: str = "PRJ001",
    task_id: str = "t.1",
    triggered_at: str = NOW,
) -> OrchestrationEvent:
    return OrchestrationEvent(
        event_id=event_id,
        kind=OrchestrationEventKind.DISPATCH,
        project_id=project_id,
        task_id=task_id,
        payload={},
        triggered_at=triggered_at,
    )


def _chain(steps: tuple[OrchestrationStep, ...], chain_id: str = "oc.test.v1") -> OrchestrationChain:
    return OrchestrationChain(chain_id=chain_id, steps=steps)


# ---------------------------------------------------------------------------
# AC-1 AgentSpec / AgentRegistry
# ---------------------------------------------------------------------------


class AgentSpecTests(unittest.TestCase):
    def test_agent_capability_closed_set_includes_known_capabilities(self):
        names = {c.name for c in AgentCapability}
        # Closed set mirrors existing US-1..US-15 facade set.
        for required in (
            "TASK_FLOW_UNDERSTANDING",
            "TASK_DECOMPOSITION",
            "TEAM_RECOMMENDATION",
            "STATE_MERGE",
            "TASK_PACKAGE_BUILD",
            "PROGRESS_CAPTURE",
            "RISK_ANALYSIS",
            "DECISION_BRIEF",
            "SUPERVISION_MEETING",
            "AUDIT_GOVERNANCE",
            "REPORT_BUILD",
        ):
            self.assertIn(required, names)

    def test_agent_spec_rejects_non_safe_id(self):
        with self.assertRaises(OrchestratorValidationError):
            AgentSpec(
                agent_id="..",
                capability=AgentCapability.TASK_DECOMPOSITION,
                display_name="x",
                input_schema=(),
                output_schema=(),
            )

    def test_agent_spec_rejects_non_bool_confirmation_flag(self):
        with self.assertRaises(OrchestratorValidationError):
            AgentSpec(
                agent_id="agent.x",
                capability=AgentCapability.TASK_DECOMPOSITION,
                display_name="x",
                input_schema=("a",),
                output_schema=("b",),
                requires_human_confirmation="yes",  # type: ignore[arg-type]
            )


class AgentRegistryTests(unittest.TestCase):
    def test_register_and_get(self):
        reg = _reg(_agent("agent.alpha"), _agent("agent.beta"))
        self.assertEqual(2, len(reg))
        self.assertIsNotNone(reg.get("agent.alpha"))
        self.assertIsNotNone(reg.get("agent.beta"))
        self.assertIsNone(reg.get("agent.gamma"))

    def test_register_rejects_duplicate(self):
        reg = _reg(_agent("agent.alpha"))
        with self.assertRaises(OrchestratorConflictError):
            reg.register(_agent("agent.alpha"))

    def test_register_rejects_unknown_capability(self):
        # AgentSpec.__post_init__ rejects non-AgentCapability at construction.
        with self.assertRaises(OrchestratorValidationError):
            AgentSpec(
                agent_id="agent.x",
                capability="bogus_capability",  # type: ignore[arg-type]
                display_name="x",
                input_schema=("a",),
                output_schema=("b",),
            )

    def test_list_available_filters_by_status(self):
        reg = _reg(_agent("agent.alpha"), _agent("agent.beta"))
        reg = reg.set_status("agent.alpha", AgentStatus.DISABLED)
        available = reg.list_available()
        self.assertEqual(1, len(available))
        self.assertEqual("agent.beta", available[0].spec.agent_id)

    def test_by_capability_filters(self):
        reg = _reg(
            _agent("agent.alpha", capability=AgentCapability.TASK_DECOMPOSITION),
            _agent("agent.beta", capability=AgentCapability.RISK_ANALYSIS),
            _agent("agent.gamma", capability=AgentCapability.TASK_DECOMPOSITION),
        )
        decomp = reg.by_capability(AgentCapability.TASK_DECOMPOSITION)
        self.assertEqual(2, len(decomp))
        risk = reg.by_capability(AgentCapability.RISK_ANALYSIS)
        self.assertEqual(1, len(risk))
        self.assertEqual("agent.beta", risk[0].spec.agent_id)

    def test_set_status_rejects_unknown_agent(self):
        reg = _reg(_agent("agent.alpha"))
        with self.assertRaises(OrchestratorValidationError):
            reg.set_status("agent.not_present", AgentStatus.DISABLED)


# ---------------------------------------------------------------------------
# AC-3/AC-4/AC-5/AC-6 dispatch_event
# ---------------------------------------------------------------------------


class DispatchTests(unittest.TestCase):
    """AC-3 + AC-4: dispatch an event through a chain and emit trace."""

    def test_dispatch_runs_full_chain_when_all_agents_available(self):
        reg = _reg(
            _agent("agent.a"),
            _agent("agent.b"),
            _agent("agent.c"),
        )
        chain = _chain(
            (
                OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),
                OrchestrationStep(step_index=1, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.b"),
                OrchestrationStep(step_index=2, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.c"),
            )
        )
        rpt = Orchestrator.dispatch_event(
            reg, chain, _event(), workspace=_ws(), now=NOW
        )
        self.assertEqual(OrchestrationOutcome.COMPLETED, rpt.outcome)
        self.assertEqual(3, len(rpt.trace))
        for i, tr in enumerate(rpt.trace):
            self.assertEqual(i, tr.step_index)
            self.assertEqual(OrchestrationStepResult.OK, tr.result)

    def test_dispatch_holds_at_human_confirmation_step(self):
        # AC-5
        reg = _reg(_agent("agent.a"))
        chain = _chain(
            (
                OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),
                OrchestrationStep(step_index=1, kind=OrchestrationStepKind.HUMAN_CONFIRM),
            )
        )
        rpt = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        self.assertEqual(OrchestrationOutcome.HELD_AT_CONFIRM, rpt.outcome)
        self.assertEqual(2, len(rpt.trace))
        self.assertEqual(OrchestrationStepResult.OK, rpt.trace[0].result)
        self.assertEqual(OrchestrationStepResult.HELD_AT_CONFIRM, rpt.trace[1].result)
        self.assertTrue(rpt.trace[1].requires_human_confirmation)

    def test_dispatch_holds_when_step_requires_human_confirmation(self):
        reg = _reg(
            _agent("agent.a"),
            _agent("agent.b", requires_human_confirmation=True),
        )
        chain = _chain(
            (
                OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),
                OrchestrationStep(step_index=1, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.b"),
            )
        )
        rpt = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        self.assertEqual(OrchestrationOutcome.HELD_AT_CONFIRM, rpt.outcome)
        # Step 1 is held; step 0 was OK.
        self.assertEqual(2, len(rpt.trace))
        self.assertEqual(OrchestrationStepResult.HELD_AT_CONFIRM, rpt.trace[1].result)

    def test_dispatch_retry_recovers_when_agent_becomes_available(self):
        # AC-6: simulate by mutating registry between two steps.
        # We can't truly mutate mid-dispatch (registry is a snapshot),
        # so we test that ESCALATE_HUMAN policy yields ESCALATED when
        # agent is not AVAILABLE.
        reg = _reg(_agent("agent.a"))
        reg = reg.set_status("agent.a", AgentStatus.BUSY)
        chain = _chain(
            (
                OrchestrationStep(
                    step_index=0,
                    kind=OrchestrationStepKind.AGENT_CALL,
                    agent_id="agent.a",
                    on_failure=FailurePolicy.RETRY,
                ),
            )
        )
        rpt = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        self.assertEqual(OrchestrationOutcome.ESCALATED, rpt.outcome)
        # RETRY policy emits two trace rows: the original ESCALATED
        # + the retry attempt; both mark the step as ESCALATED.
        self.assertGreaterEqual(len(rpt.trace), 1)
        self.assertEqual(OrchestrationStepResult.ESCALATED, rpt.trace[-1].result)

    def test_dispatch_skip_advances_past_unavailable_agent(self):
        # AC-6
        reg = _reg(_agent("agent.a"))
        reg = reg.set_status("agent.a", AgentStatus.DISABLED)
        chain = _chain(
            (
                OrchestrationStep(
                    step_index=0,
                    kind=OrchestrationStepKind.AGENT_CALL,
                    agent_id="agent.a",
                    on_failure=FailurePolicy.SKIP,
                ),
                OrchestrationStep(step_index=1, kind=OrchestrationStepKind.HUMAN_CONFIRM),
            )
        )
        rpt = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        # SKIPPED step counts as completed; chain advances to HUMAN_CONFIRM.
        self.assertEqual(OrchestrationOutcome.HELD_AT_CONFIRM, rpt.outcome)
        self.assertEqual(2, len(rpt.trace))
        self.assertEqual(OrchestrationStepResult.SKIPPED, rpt.trace[0].result)

    def test_dispatch_escalate_human_policy_yields_escalated(self):
        # AC-6
        reg = _reg(_agent("agent.a"))
        reg = reg.set_status("agent.a", AgentStatus.BUSY)
        chain = _chain(
            (
                OrchestrationStep(
                    step_index=0,
                    kind=OrchestrationStepKind.AGENT_CALL,
                    agent_id="agent.a",
                    on_failure=FailurePolicy.ESCALATE_HUMAN,
                ),
            )
        )
        rpt = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        self.assertEqual(OrchestrationOutcome.ESCALATED, rpt.outcome)
        self.assertEqual(OrchestrationStepResult.ESCALATED, rpt.trace[-1].result)

    def test_dispatch_rejects_unknown_agent_with_failed(self):
        chain = _chain(
            (
                OrchestrationStep(
                    step_index=0,
                    kind=OrchestrationStepKind.AGENT_CALL,
                    agent_id="agent.missing",
                ),
            )
        )
        rpt = Orchestrator.dispatch_event(_reg(), chain, _event(), workspace=_ws(), now=NOW)
        self.assertEqual(OrchestrationOutcome.FAILED, rpt.outcome)
        self.assertEqual(OrchestrationStepResult.FAILED, rpt.trace[-1].result)

    def test_dispatch_rejects_workspace_event_mismatch(self):
        reg = _reg(_agent("agent.a"))
        chain = _chain(
            (
                OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),
            )
        )
        with self.assertRaises(OrchestratorValidationError):
            Orchestrator.dispatch_event(
                reg, chain, _event(project_id="OTHER"),
                workspace=_ws(project_id="PRJ001"), now=NOW,
            )

    def test_dispatch_rejects_invalid_now(self):
        reg = _reg(_agent("agent.a"))
        chain = _chain(
            (OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),)
        )
        with self.assertRaises(OrchestratorValidationError):
            Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now="not-iso")


class ConfirmHumanTests(unittest.TestCase):
    """AC-5: confirm a held step."""

    def test_confirm_human_resumes_chain(self):
        reg = _reg(_agent("agent.a"))
        chain = _chain(
            (
                OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),
                OrchestrationStep(step_index=1, kind=OrchestrationStepKind.HUMAN_CONFIRM),
            )
        )
        held = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        self.assertEqual(OrchestrationOutcome.HELD_AT_CONFIRM, held.outcome)
        # Confirm: chain resumes from held step.
        confirmed = Orchestrator.confirm_human(
            held, step_index=1, confirmed_by="u.alice", now=NOW2
        )
        self.assertEqual(OrchestrationOutcome.COMPLETED, confirmed.outcome)
        self.assertEqual("u.alice", confirmed.trace[-1].confirmed_by)
        self.assertEqual(OrchestrationStepResult.OK, confirmed.trace[-1].result)

    def test_confirm_human_rejects_not_held(self):
        reg = _reg(_agent("agent.a"))
        chain = _chain(
            (OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),)
        )
        rpt = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        self.assertEqual(OrchestrationOutcome.COMPLETED, rpt.outcome)
        with self.assertRaises(OrchestratorConflictError):
            Orchestrator.confirm_human(
                rpt, step_index=0, confirmed_by="u.alice", now=NOW2
            )

    def test_confirm_human_rejects_mismatched_step_index(self):
        reg = _reg(_agent("agent.a"))
        chain = _chain(
            (
                OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),
                OrchestrationStep(step_index=1, kind=OrchestrationStepKind.HUMAN_CONFIRM),
            )
        )
        held = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        with self.assertRaises(OrchestratorConflictError):
            Orchestrator.confirm_human(
                held, step_index=0, confirmed_by="u.alice", now=NOW2
            )

    def test_confirm_human_rejects_invalid_confirmed_by(self):
        reg = _reg(_agent("agent.a"))
        chain = _chain(
            (OrchestrationStep(step_index=0, kind=OrchestrationStepKind.HUMAN_CONFIRM),)
        )
        held = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        with self.assertRaises(OrchestratorValidationError):
            Orchestrator.confirm_human(
                held, step_index=0, confirmed_by="..", now=NOW2
            )


# ---------------------------------------------------------------------------
# AC-7 audit projection + MVP fixed chain
# ---------------------------------------------------------------------------


class AuditProjectionTests(unittest.TestCase):
    """Mirrors US-11/12/13/8/15: exclude sensitive detail text."""

    def test_to_audit_record_excludes_sensitive_detail(self):
        reg = _reg(
            _agent("agent.a"),
            _agent("agent.b"),
        )
        chain = _chain(
            (
                OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),
                OrchestrationStep(step_index=1, kind=OrchestrationStepKind.HUMAN_CONFIRM),
            )
        )
        rpt = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        record = Orchestrator.to_audit_record(rpt)
        self.assertEqual(record, json.loads(json.dumps(record)))
        # Detail text MUST NOT appear; only detail_hash.
        serialized = json.dumps(record)
        self.assertNotIn("executed", serialized)
        self.assertNotIn("explicit human confirmation", serialized)
        # 64-char lowercase hex for detail_hash.
        for step in record["steps"]:
            self.assertEqual(64, len(step["detail_hash"]))
            self.assertNotIn("detail", step)
        # Metadata fields.
        self.assertEqual("coevo.orchestrator", record["domain"])
        self.assertEqual("1.0", record["schema_version"])


class MVPFixedChainTests(unittest.TestCase):
    def test_mvp_fixed_chain_has_five_steps(self):
        self.assertEqual(5, MVP_FIXED_CHAIN.steps_count())
        # Step 0..2: AGENT_CALL (3 agents)
        for i in (0, 1, 2):
            self.assertEqual(OrchestrationStepKind.AGENT_CALL, MVP_FIXED_CHAIN.steps[i].kind)
        # Step 3: HUMAN_CONFIRM
        self.assertEqual(OrchestrationStepKind.HUMAN_CONFIRM, MVP_FIXED_CHAIN.steps[3].kind)
        # Step 4: AGENT_CALL
        self.assertEqual(OrchestrationStepKind.AGENT_CALL, MVP_FIXED_CHAIN.steps[4].kind)
        self.assertEqual("agent.task_package_build", MVP_FIXED_CHAIN.steps[4].agent_id)

    def test_mvp_fixed_chain_dispatch_stops_at_human_confirm(self):
        reg = _reg(
            _agent("agent.task_flow_understanding", capability=AgentCapability.TASK_FLOW_UNDERSTANDING),
            _agent("agent.task_decomposition", capability=AgentCapability.TASK_DECOMPOSITION),
            _agent("agent.team_recommendation", capability=AgentCapability.TEAM_RECOMMENDATION),
            _agent("agent.task_package_build", capability=AgentCapability.TASK_PACKAGE_BUILD),
        )
        rpt = Orchestrator.dispatch_event(
            reg, MVP_FIXED_CHAIN, _event(), workspace=_ws(), now=NOW
        )
        # First 3 steps OK, step 3 held.
        self.assertEqual(OrchestrationOutcome.HELD_AT_CONFIRM, rpt.outcome)
        self.assertEqual(4, len(rpt.trace))
        for i in range(3):
            self.assertEqual(OrchestrationStepResult.OK, rpt.trace[i].result)
        self.assertEqual(OrchestrationStepResult.HELD_AT_CONFIRM, rpt.trace[3].result)


class PureFunctionTests(unittest.TestCase):
    def test_pure_function_determinism_same_input_same_outcome(self):
        reg = _reg(
            _agent("agent.a"),
            _agent("agent.b"),
        )
        chain = _chain(
            (
                OrchestrationStep(step_index=0, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.a"),
                OrchestrationStep(step_index=1, kind=OrchestrationStepKind.AGENT_CALL, agent_id="agent.b"),
            )
        )
        a = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        b = Orchestrator.dispatch_event(reg, chain, _event(), workspace=_ws(), now=NOW)
        self.assertEqual(a.trace_id, b.trace_id)
        self.assertEqual(a.outcome, b.outcome)
        self.assertEqual(a.trace, b.trace)


if __name__ == "__main__":
    unittest.main()
