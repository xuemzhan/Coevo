"""FRAMEWORK-INTEGRATION-2: product-chain lifting and integration closure."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

from src.coevo.framework.integration import (
    IntegrationError,
    chain_to_plan,
    plan_to_chain,
    validate_product_chain,
)
from src.coevo.framework.plan import Plan, PlanNode, PlanNodeKind, plan_fingerprint
from src.coevo.framework.policy import get_default_profile
from src.coevo.orchestrator.models import (
    AgentCapability,
    AgentRegistration,
    AgentRegistry,
    AgentSpec,
    FailurePolicy,
    OrchestrationChain,
    OrchestrationStep,
    OrchestrationStepKind,
)

ROOT = Path(__file__).resolve().parents[2]


def make_registry(*, with_agent: bool = True) -> AgentRegistry:
    registry = AgentRegistry.empty()
    if with_agent:
        spec = AgentSpec(
            agent_id="agent.td",
            capability=AgentCapability.TASK_DECOMPOSITION,
            display_name="task decomposition",
            input_schema=(),
            output_schema=(),
        )
        registry = registry.register(AgentRegistration(spec=spec))
    return registry


def make_chain() -> OrchestrationChain:
    return OrchestrationChain(
        chain_id="demo.chain",
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


class _AllowAll:
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: Plan, actor: str) -> bool:
        return True


class _DenyRbac(_AllowAll):
    def authorized(self, plan: Plan, actor: str) -> bool:
        return False


class Integration2Tests(unittest.TestCase):
    def test_chain_to_plan_lifts_mixed_chain(self) -> None:
        plan = chain_to_plan(make_chain(), make_registry(), get_default_profile("INTERACTIVE"))
        self.assertEqual(len(plan.nodes), 2)
        self.assertEqual(plan.nodes[0].kind, PlanNodeKind.AGENT)
        self.assertEqual(plan.nodes[0].agent_capability, "task_decomposition")
        self.assertEqual(plan.nodes[1].kind, PlanNodeKind.HUMAN_GATE)
        self.assertEqual(plan.plan_id, plan_fingerprint(plan))

    def test_chain_to_plan_unknown_agent_rejected(self) -> None:
        with self.assertRaises(IntegrationError):
            chain_to_plan(make_chain(), make_registry(with_agent=False), get_default_profile("INTERACTIVE"))

    def test_chain_to_plan_conditional_rejected(self) -> None:
        chain = OrchestrationChain(
            chain_id="demo.conditional",
            steps=(
                OrchestrationStep(
                    step_index=0,
                    kind=OrchestrationStepKind.CONDITIONAL,
                    on_failure=FailurePolicy.ESCALATE_HUMAN,
                ),
            ),
        )
        with self.assertRaises(IntegrationError):
            chain_to_plan(chain, make_registry(), get_default_profile("INTERACTIVE"))

    def test_validate_product_chain(self) -> None:
        result = validate_product_chain(
            make_chain(),
            make_registry(),
            get_default_profile("INTERACTIVE"),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertTrue(result.accepted, result.failure_reason)
        denied = validate_product_chain(
            make_chain(),
            make_registry(),
            get_default_profile("INTERACTIVE"),
            scope_checker=_AllowAll(),
            rbac_checker=_DenyRbac(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertFalse(denied.accepted)

    def test_plan_to_chain_closed_set_error_is_integration_error(self) -> None:
        """INTEGRATION-1 Low closure: unknown capability → IntegrationError."""

        from src.coevo.framework.plan import PlanEdge

        policy = get_default_profile("INTERACTIVE")
        node = PlanNode(
            node_id="n1",
            kind=PlanNodeKind.AGENT,
            agent_capability="not_a_capability",
        )
        plan = Plan(
            plan_id="0" * 64,
            plan_version="1.0",
            policy_profile=policy.profile,
            policy_version=policy.policy_version,
            nodes=(node,),
            edges=(),
        )
        plan = Plan(
            plan_id=plan_fingerprint(plan),
            plan_version=plan.plan_version,
            policy_profile=plan.policy_profile,
            policy_version=plan.policy_version,
            nodes=plan.nodes,
            edges=plan.edges,
        )
        with self.assertRaises(IntegrationError):
            plan_to_chain(plan, make_registry())

    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "integration.py").read_text(
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
        self.assertEqual([], bad, "third-party imports found in integration.py")


if __name__ == "__main__":
    unittest.main()
