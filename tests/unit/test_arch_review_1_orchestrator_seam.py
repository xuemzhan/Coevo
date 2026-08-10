"""ARCH-REVIEW-1: orchestrator seam contract tests.

Ownership contract (docs/architecture/orchestrator-seam.md):

* framework layer = validation / policy gateway only (validate_plan,
  plan_to_chain / chain_to_plan / guarded_dispatch / validate_product_chain);
* product layer = sole executor of workflow instances (Orchestrator facade +
  real-chain store);
* no bypass: a composition root must pass the framework gate before any
  product dispatch entry; guarded_dispatch must never call the inner
  dispatch when validation fails; unknown product outcomes fail closed.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.framework.integration import (
    chain_to_plan,
    plan_to_chain,
    report_to_outcome,
)
from src.coevo.framework.orchestrator import OrchestrationStatus
from src.coevo.framework.plan import (
    Plan,
    PlanEdge,
    PlanNode,
    PlanNodeKind,
    plan_fingerprint,
)
from src.coevo.framework.policy import get_default_profile
from src.coevo.orchestrator.models import (
    AgentCapability,
    AgentRegistration,
    AgentRegistry,
    AgentSpec,
    FailurePolicy,
    OrchestrationChain,
    OrchestrationOutcome as ProductOutcome,
    OrchestrationStep,
    OrchestrationStepKind,
)

ROOT = Path(__file__).resolve().parents[2]


def make_plan(*, capability: str = "task_decomposition") -> Plan:
    nodes = (
        PlanNode(
            node_id="n1",
            kind=PlanNodeKind.AGENT,
            agent_capability=capability,
            requires_human_confirmation=False,
        ),
        PlanNode(
            node_id="n2",
            kind=PlanNodeKind.HUMAN_GATE,
            human_gate_reason="approve",
            requires_human_confirmation=True,
        ),
    )
    edges = (PlanEdge("n1", "n2"),)
    policy = get_default_profile("INTERACTIVE")
    plan = Plan(
        plan_id="0" * 64,
        plan_version="1.0",
        policy_profile=policy.profile,
        policy_version=policy.policy_version,
        nodes=nodes,
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


def make_registry() -> AgentRegistry:
    registry = AgentRegistry.empty()
    return registry.register(
        AgentRegistration(
            AgentSpec(
                agent_id="agent.td",
                capability=AgentCapability.TASK_DECOMPOSITION,
                display_name="task decomposition",
                input_schema=("input",),
                output_schema=("output",),
            )
        )
    )


def make_chain() -> OrchestrationChain:
    return OrchestrationChain(
        chain_id="seam.test",
        steps=(
            OrchestrationStep(
                step_index=0,
                kind=OrchestrationStepKind.AGENT_CALL,
                agent_id="agent.td",
                requires_human_confirmation=False,
                on_failure=FailurePolicy.ESCALATE_HUMAN,
            ),
            OrchestrationStep(
                step_index=1,
                kind=OrchestrationStepKind.HUMAN_CONFIRM,
                requires_human_confirmation=True,
                on_failure=FailurePolicy.ESCALATE_HUMAN,
            ),
        ),
    )


class _Report:
    def __init__(self, outcome: ProductOutcome) -> None:
        self.outcome = outcome


class SeamRoundTripTests(unittest.TestCase):
    """Plan <-> Chain conversion must be structurally stable."""

    def test_plan_to_chain_to_plan_preserves_shape(self) -> None:
        plan = make_plan()
        registry = make_registry()
        chain = plan_to_chain(plan, registry)
        lifted = chain_to_plan(chain, registry, get_default_profile("INTERACTIVE"))
        self.assertEqual(
            [node.kind for node in lifted.nodes],
            [node.kind for node in plan.nodes],
        )
        self.assertEqual(
            [
                node.agent_capability
                for node in lifted.nodes
                if node.kind is PlanNodeKind.AGENT
            ],
            [
                node.agent_capability
                for node in plan.nodes
                if node.kind is PlanNodeKind.AGENT
            ],
        )
        self.assertEqual(
            [node.requires_human_confirmation for node in lifted.nodes],
            [node.requires_human_confirmation for node in plan.nodes],
        )
        self.assertEqual(len(lifted.edges), len(plan.edges))

    def test_chain_to_plan_to_chain_preserves_steps(self) -> None:
        chain = make_chain()
        registry = make_registry()
        plan = chain_to_plan(chain, registry, get_default_profile("INTERACTIVE"))
        rebuilt = plan_to_chain(plan, registry, chain_id=chain.chain_id)
        self.assertEqual(
            [step.kind for step in rebuilt.steps],
            [step.kind for step in chain.steps],
        )
        self.assertEqual(
            [step.agent_id for step in rebuilt.steps],
            [step.agent_id for step in chain.steps],
        )
        self.assertEqual(
            [step.requires_human_confirmation for step in rebuilt.steps],
            [step.requires_human_confirmation for step in chain.steps],
        )
        self.assertEqual(rebuilt.chain_id, chain.chain_id)


class ReportMappingTests(unittest.TestCase):
    """Every product outcome maps to a framework status, fail-closed."""

    def test_all_product_outcomes_map(self) -> None:
        for product in ProductOutcome:
            outcome = report_to_outcome(
                _Report(product),
                "0" * 64,
                "2026-08-08T08:00:00Z",
            )
            self.assertTrue(outcome.accepted)
            self.assertIn(
                outcome.status,
                (
                    OrchestrationStatus.COMPLETED,
                    OrchestrationStatus.HELD,
                    OrchestrationStatus.ESCALATED,
                ),
            )

    def test_unknown_outcome_escalates(self) -> None:
        outcome = report_to_outcome(
            _Report("UNKNOWN_FUTURE_OUTCOME"),
            "0" * 64,
            "2026-08-08T08:00:00Z",
        )
        self.assertEqual(outcome.status, OrchestrationStatus.ESCALATED)


class CompositionRootGuardTests(unittest.TestCase):
    """The sanctioned composition root must gate before dispatching."""

    @staticmethod
    def _ordered_names(node: ast.AST):
        for child in ast.iter_child_nodes(node):
            yield from CompositionRootGuardTests._ordered_names(child)
        if isinstance(node, ast.Attribute):
            yield node.attr
        elif isinstance(node, ast.Name):
            yield node.id

    def test_pipeline_validate_gate_before_dispatch(self) -> None:
        source = (ROOT / "src" / "coevo" / "app" / "pipeline.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        func = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_demo_pipeline"
        )
        names = list(self._ordered_names(func))
        self.assertIn("validate_product_chain", names)
        self.assertIn("dispatch_event_with_real_facades", names)
        self.assertLess(
            names.index("validate_product_chain"),
            names.index("dispatch_event_with_real_facades"),
            "run_demo_pipeline must call validate_product_chain "
            "before any product dispatch entry",
        )
        # No other product dispatch entry is allowed in the composition root.
        self.assertEqual(
            [name for name in names if name.startswith("dispatch_")],
            ["dispatch_event_with_real_facades"],
        )

    def test_run_demo_cli_uses_only_the_pipeline(self) -> None:
        source = (ROOT / "scripts" / "run_demo.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = list(self._ordered_names(tree))
        self.assertNotIn("dispatch_event", names)
        self.assertNotIn("dispatch_event_with_real_facades", names)
        self.assertIn("run_demo_pipeline", names)


class SeamDocGuardTests(unittest.TestCase):
    """The seam contract document must exist and state ownership."""

    def test_seam_doc_states_ownership_and_no_bypass(self) -> None:
        doc = (ROOT / "docs" / "architecture" / "orchestrator-seam.md")
        text = doc.read_text(encoding="utf-8")
        self.assertIn("校验/策略网关", text)
        self.assertIn("唯一执行器", text)
        self.assertIn("无旁路", text)
        self.assertIn("任务下发链", text)
        self.assertIn("成果回传链", text)


if __name__ == "__main__":
    unittest.main()
