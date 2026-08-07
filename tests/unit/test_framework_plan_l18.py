"""US-16-AC-2: Plan model and L18 white-list tests (AC-2.4/2.5)."""

from __future__ import annotations

import unittest

from src.coevo.framework.plan import (
    Plan,
    PlanEdge,
    PlanNode,
    PlanNodeKind,
    PlanValidationError,
    plan_fingerprint,
    validate_plan_structure,
)


def make_plan(
    *,
    tool_args: tuple[tuple[str, object], ...] = (),
    plan_id: str | None = None,
    nodes: tuple[PlanNode, ...] | None = None,
    edges: tuple[PlanEdge, ...] | None = None,
) -> Plan:
    nodes = nodes or (
        PlanNode(
            node_id="n1",
            kind=PlanNodeKind.AGENT,
            agent_capability="task_decomposition",
            requires_human_confirmation=True,
        ),
        PlanNode(
            node_id="n2",
            kind=PlanNodeKind.TOOL,
            tool_ref="coevo.tools.cycle_check",
            tool_args=tool_args,
        ),
        PlanNode(
            node_id="n3",
            kind=PlanNodeKind.HUMAN_GATE,
            human_gate_reason="approve result",
            requires_human_confirmation=True,
            confirmation_role="project_owner",
        ),
    )
    edges = edges or (
        PlanEdge("n1", "n2"),
        PlanEdge("n2", "n3"),
    )
    plan = Plan(
        plan_id="0" * 64,
        plan_version="1.0",
        policy_profile="INTERACTIVE",
        policy_version="1.0",
        nodes=nodes,
        edges=edges,
    )
    if plan_id is None:
        plan = Plan(
            plan_id=plan_fingerprint(plan),
            plan_version=plan.plan_version,
            policy_profile=plan.policy_profile,
            policy_version=plan.policy_version,
            nodes=plan.nodes,
            edges=plan.edges,
        )
    else:
        plan = Plan(
            plan_id=plan_id,
            plan_version=plan.plan_version,
            policy_profile=plan.policy_profile,
            policy_version=plan.policy_version,
            nodes=plan.nodes,
            edges=plan.edges,
        )
    return plan


class PlanL18Tests(unittest.TestCase):
    def test_valid_plan_structure_passes(self) -> None:
        validate_plan_structure(make_plan())  # must not raise

    def test_l18_policy_key_in_tool_args_rejected(self) -> None:
        plan = make_plan(tool_args=(("max_recover_attempts", 5),))
        with self.assertRaises(PlanValidationError) as ctx:
            validate_plan_structure(plan)
        self.assertIn("L18", str(ctx.exception))

    def test_l18_timeout_key_in_tool_args_rejected(self) -> None:
        plan = make_plan(tool_args=(("dispatch_timeout_sec", 30),))
        with self.assertRaises(PlanValidationError):
            validate_plan_structure(plan)

    def test_tool_args_ordinary_numeric_allowed(self) -> None:
        """AC-2.5 (F6): numeric tool data is allowed per schema."""

        validate_plan_structure(make_plan(tool_args=(("max_nodes", 100),)))
        validate_plan_structure(make_plan(tool_args=(("top_k", 3), ("verbose", True))))

    def test_tool_args_duplicate_key_rejected(self) -> None:
        """security-review Low: duplicate keys break hash/execution consistency."""

        plan = make_plan(
            tool_args=(("max_nodes", 100), ("max_nodes", 200))
        )
        with self.assertRaises(PlanValidationError):
            validate_plan_structure(plan)

    def test_node_count_limit_rejected(self) -> None:
        nodes = tuple(
            PlanNode(
                node_id=f"n{i}",
                kind=PlanNodeKind.TOOL,
                tool_ref=f"coevo.tools.t{i}",
            )
            for i in range(65)
        )
        with self.assertRaises(PlanValidationError):
            validate_plan_structure(make_plan(nodes=nodes, edges=()))

    def test_tool_args_count_limit_rejected(self) -> None:
        args = tuple((f"k{i}", i) for i in range(33))
        with self.assertRaises(PlanValidationError):
            validate_plan_structure(make_plan(tool_args=args))

    def test_plan_id_must_match_fingerprint(self) -> None:
        with self.assertRaises(PlanValidationError):
            validate_plan_structure(make_plan(plan_id="a" * 64))

    def test_duplicate_node_id_rejected(self) -> None:
        nodes = (
            PlanNode(node_id="n1", kind=PlanNodeKind.AGENT, agent_capability="task_decomposition"),
            PlanNode(node_id="n1", kind=PlanNodeKind.TOOL, tool_ref="coevo.tools.cycle_check"),
        )
        with self.assertRaises(PlanValidationError):
            validate_plan_structure(make_plan(nodes=nodes, edges=()))

    def test_dangling_edge_rejected(self) -> None:
        with self.assertRaises(PlanValidationError):
            validate_plan_structure(
                make_plan(edges=(PlanEdge("n1", "missing"),))
            )

    def test_human_gate_requires_confirmation(self) -> None:
        nodes = (
            PlanNode(node_id="n1", kind=PlanNodeKind.AGENT, agent_capability="task_decomposition"),
            PlanNode(
                node_id="n2",
                kind=PlanNodeKind.HUMAN_GATE,
                human_gate_reason="approve",
                requires_human_confirmation=False,
            ),
        )
        with self.assertRaises(PlanValidationError):
            validate_plan_structure(make_plan(nodes=nodes, edges=()))


if __name__ == "__main__":
    unittest.main()
