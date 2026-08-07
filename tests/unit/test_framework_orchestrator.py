"""US-16-AC-8: Hybrid Orchestrator core tests (AC-8.1..8.5)."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

from src.coevo.framework.lifecycle import LifecycleState
from src.coevo.framework.orchestrator import (
    ORCHESTRATION_PROJECTION_KEYS,
    ChainStep,
    ExecutionResult,
    OrchestrationMode,
    OrchestrationOutcome,
    OrchestrationStatus,
    chain_plan,
    dispatch,
    plan_for,
    transition,
)
from src.coevo.framework.plan import (
    Plan,
    PlanEdge,
    PlanNode,
    PlanNodeKind,
    plan_fingerprint,
)
from src.coevo.framework.policy import get_default_profile
from src.coevo.framework.policy import Policy

ROOT = Path(__file__).resolve().parents[2]


class _AllowAll:
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: Plan, actor: str) -> bool:
        return True


class _DenyRbac(_AllowAll):
    def authorized(self, plan: Plan, actor: str) -> bool:
        return False


class _Chain:
    def __init__(self, steps: tuple[ChainStep, ...]) -> None:
        self.steps = steps

    def chain_for(self, task_id: str) -> tuple[ChainStep, ...]:
        return self.steps


class _Llm:
    def __init__(self, proposal: Plan | None = None, raises: bool = False) -> None:
        self.proposal = proposal
        self.raises = raises

    def propose_plan(self, task_id: str, policy) -> Plan | None:
        if self.raises:
            raise RuntimeError("llm down")
        return self.proposal


class _Executor:
    def __init__(self, ok: bool = True, raises: bool = False) -> None:
        self.ok = ok
        self.raises = raises
        self.calls: list[Plan] = []

    def execute(self, plan: Plan, actor: str) -> ExecutionResult:
        self.calls.append(plan)
        if self.raises:
            raise RuntimeError("executor down")
        return ExecutionResult(ok=self.ok)


def chain_steps() -> tuple[ChainStep, ...]:
    return (
        ChainStep("s1", "task_flow_understanding"),
        ChainStep("s2", "task_decomposition"),
        ChainStep("s3", "team_recommendation"),
    )


def proposal_plan(*, with_hold: bool = False) -> Plan:
    nodes = [
        PlanNode(
            node_id="p1",
            kind=PlanNodeKind.AGENT,
            agent_capability="risk_analysis",
            requires_human_confirmation=False,
        ),
        PlanNode(
            node_id="p2",
            kind=PlanNodeKind.AGENT,
            agent_capability="decision_brief",
            requires_human_confirmation=with_hold,
        ),
    ]
    edges = (PlanEdge("p1", "p2"),)
    policy = get_default_profile("INTERACTIVE")
    plan = Plan(
        plan_id="0" * 64,
        plan_version="1.0",
        policy_profile=policy.profile,
        policy_version=policy.policy_version,
        nodes=tuple(nodes),
        edges=edges,
    )
    return Plan(
        plan_id=plan_fingerprint(plan),
        plan_version=plan.plan_version,
        policy_profile=plan.policy_profile,
        policy_version=plan.policy_version,
        nodes=plan.nodes,
        edges=plan.edges,
    )


def policy() -> Policy:
    return get_default_profile("INTERACTIVE")


def run_dispatch(mode, *, plan, executor, **kwargs):
    return dispatch(
        mode,
        "task-0001",
        policy(),
        plan=plan,
        actor=kwargs.pop("actor", "owner"),
        scope_checker=kwargs.pop("scope", _AllowAll()),
        rbac_checker=kwargs.pop("rbac", _AllowAll()),
        plan_executor=executor,
        validated_at=kwargs.pop("validated_at", "2026-08-08T08:00:00Z"),
    )


class OrchestratorTests(unittest.TestCase):
    def test_dispatch_requires_valid_plan(self) -> None:
        """AC-8.1: validate_plan is a mandatory dispatch precondition."""

        cyclic = proposal_plan()
        cyclic = Plan(
            plan_id=cyclic.plan_id,
            plan_version=cyclic.plan_version,
            policy_profile=cyclic.policy_profile,
            policy_version=cyclic.policy_version,
            nodes=cyclic.nodes,
            edges=(PlanEdge("p1", "p2"), PlanEdge("p2", "p1")),
        )
        executor = _Executor()
        outcome = run_dispatch(
            OrchestrationMode.STATE_MACHINE,
            plan=cyclic,
            executor=executor,
        )
        self.assertFalse(outcome.accepted)
        self.assertEqual(outcome.status, OrchestrationStatus.REJECTED)
        self.assertEqual(executor.calls, [])

    def test_dispatch_rbac_denied_rejected(self) -> None:
        executor = _Executor()
        outcome = run_dispatch(
            OrchestrationMode.STATE_MACHINE,
            plan=chain_plan("task-0001", chain_steps(), policy()),
            executor=executor,
            rbac=_DenyRbac(),
        )
        self.assertEqual(outcome.status, OrchestrationStatus.REJECTED)
        self.assertEqual(executor.calls, [])

    def test_state_machine_mode(self) -> None:
        """AC-8.2: static chain compiles and executes; failure escalates."""

        plan = plan_for(
            OrchestrationMode.STATE_MACHINE,
            "task-0001",
            policy(),
            static_chain_provider=_Chain(chain_steps()),
            llm_provider=_Llm(),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        executor = _Executor()
        outcome = run_dispatch(OrchestrationMode.STATE_MACHINE, plan=plan, executor=executor)
        self.assertTrue(outcome.accepted)
        self.assertEqual(outcome.status, OrchestrationStatus.COMPLETED)
        self.assertEqual(len(executor.calls), 1)

        executor = _Executor(ok=False)
        outcome = run_dispatch(OrchestrationMode.STATE_MACHINE, plan=plan, executor=executor)
        self.assertEqual(outcome.status, OrchestrationStatus.ESCALATED)
        self.assertIn("RECOVER", outcome.failure_reason or "")

        executor = _Executor(raises=True)
        outcome = run_dispatch(OrchestrationMode.STATE_MACHINE, plan=plan, executor=executor)
        self.assertEqual(outcome.status, OrchestrationStatus.ESCALATED)

    def test_dynamic_llm_fallback(self) -> None:
        """AC-8.3: valid proposal executes; missing/invalid/raising falls back."""

        good = proposal_plan()
        plan = plan_for(
            OrchestrationMode.DYNAMIC_LLM,
            "task-0001",
            policy(),
            static_chain_provider=_Chain(chain_steps()),
            llm_provider=_Llm(proposal=good),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertEqual(plan, good)
        # Missing proposal → chain fallback.
        plan = plan_for(
            OrchestrationMode.DYNAMIC_LLM,
            "task-0001",
            policy(),
            static_chain_provider=_Chain(chain_steps()),
            llm_provider=_Llm(proposal=None),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertNotEqual(plan, good)
        self.assertEqual(len(plan.nodes), 3)
        # Raising proposal → chain fallback.
        plan = plan_for(
            OrchestrationMode.DYNAMIC_LLM,
            "task-0001",
            policy(),
            static_chain_provider=_Chain(chain_steps()),
            llm_provider=_Llm(raises=True),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertEqual(len(plan.nodes), 3)

    def test_dynamic_llm_invalid_proposal_falls_back(self) -> None:
        cyclic = proposal_plan()
        cyclic = Plan(
            plan_id=cyclic.plan_id,
            plan_version=cyclic.plan_version,
            policy_profile=cyclic.policy_profile,
            policy_version=cyclic.policy_version,
            nodes=cyclic.nodes,
            edges=(PlanEdge("p1", "p2"), PlanEdge("p2", "p1")),
        )
        plan = plan_for(
            OrchestrationMode.DYNAMIC_LLM,
            "task-0001",
            policy(),
            static_chain_provider=_Chain(chain_steps()),
            llm_provider=_Llm(proposal=cyclic),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertEqual(len(plan.nodes), 3)  # chain fallback, not the cyclic proposal

    def test_hybrid_hold_gate(self) -> None:
        """AC-8.4: LLM may only cover non-HOLD nodes; chain HOLD → HELD."""

        good = proposal_plan(with_hold=False)
        plan = plan_for(
            OrchestrationMode.HYBRID,
            "task-0001",
            policy(),
            static_chain_provider=_Chain(chain_steps()),
            llm_provider=_Llm(proposal=good),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertEqual(plan, good)
        # Proposal with a HOLD node → chain fallback.
        with_hold = proposal_plan(with_hold=True)
        plan = plan_for(
            OrchestrationMode.HYBRID,
            "task-0001",
            policy(),
            static_chain_provider=_Chain(chain_steps()),
            llm_provider=_Llm(proposal=with_hold),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertEqual(len(plan.nodes), 3)
        # Chain with HOLD → HELD, executor not called.
        hold_chain = _Chain(
            (
                ChainStep("h1", "task_flow_understanding", requires_human_confirmation=True),
                ChainStep("h2", "task_decomposition"),
            )
        )
        plan = plan_for(
            OrchestrationMode.HYBRID,
            "task-0001",
            policy(),
            static_chain_provider=hold_chain,
            llm_provider=_Llm(proposal=None),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        executor = _Executor()
        outcome = run_dispatch(OrchestrationMode.HYBRID, plan=plan, executor=executor)
        self.assertEqual(outcome.status, OrchestrationStatus.HELD)
        self.assertEqual(executor.calls, [])

    def test_hybrid_chain_hold_not_bypassed_by_llm(self) -> None:
        """security-review: chain-mandated HOLD cannot be bypassed by a valid
        non-HOLD LLM proposal in HYBRID mode (AC-8.4 HELD gate is mandatory)."""

        hold_chain = _Chain(
            (
                ChainStep("h1", "task_flow_understanding", requires_human_confirmation=True),
                ChainStep("h2", "task_decomposition"),
            )
        )
        expected = chain_plan("task-0001", hold_chain.steps, policy())
        plan = plan_for(
            OrchestrationMode.HYBRID,
            "task-0001",
            policy(),
            static_chain_provider=hold_chain,
            llm_provider=_Llm(proposal=proposal_plan(with_hold=False)),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertEqual(plan, expected)
        executor = _Executor()
        outcome = run_dispatch(OrchestrationMode.HYBRID, plan=plan, executor=executor)
        self.assertEqual(outcome.status, OrchestrationStatus.HELD)
        self.assertEqual(executor.calls, [])

    def test_lifecycle_integration(self) -> None:
        """AC-8.5: L19 paths enforced via transition()."""

        plan = chain_plan("task-0001", chain_steps(), policy())
        outcome = transition(
            OrchestrationMode.STATE_MACHINE,
            plan_hash=plan.plan_id,
            path=(LifecycleState.ESCALATED, LifecycleState.ACTIVE),
        )
        self.assertEqual(outcome.status, OrchestrationStatus.REJECTED)
        self.assertIn("L19", outcome.failure_reason or "")
        outcome = transition(
            OrchestrationMode.STATE_MACHINE,
            plan_hash=plan.plan_id,
            path=(LifecycleState.ESCALATED, LifecycleState.HELD, LifecycleState.ACTIVE),
        )
        self.assertTrue(outcome.accepted)
        self.assertEqual(outcome.status, OrchestrationStatus.ACTIVE)
        record = outcome.to_audit_record()
        self.assertEqual(set(record), set(ORCHESTRATION_PROJECTION_KEYS))

    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "orchestrator.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        allowed = set(sys.stdlib_module_names) | {"src"}
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] not in allowed:
                        bad.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    continue
                if node.module and node.module.split(".")[0] not in allowed:
                    bad.append(node.module)
        self.assertEqual([], bad, "third-party imports found in orchestrator.py")


if __name__ == "__main__":
    unittest.main()
