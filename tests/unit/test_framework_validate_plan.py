"""US-16-AC-2: validate_plan tests (AC-2.6 + L19 integration)."""

from __future__ import annotations

import unittest

from src.coevo.framework.lifecycle import LifecycleState
from src.coevo.framework.plan import PlanEdge, PlanNode, PlanNodeKind, plan_fingerprint
from src.coevo.framework.policy import get_default_profile
from src.coevo.framework.validation import (
    VALIDATION_PROJECTION_KEYS,
    validate_plan,
)
from src.coevo.framework.plan import Plan


def make_plan(
    *,
    edges: tuple[PlanEdge, ...] | None = None,
    capability: str = "task_decomposition",
    tool_ref: str = "coevo.tools.cycle_check",
    policy_profile: str = "INTERACTIVE",
    policy_version: str = "1.0",
    human_gate: bool = True,
) -> Plan:
    nodes = [
        PlanNode(
            node_id="n1",
            kind=PlanNodeKind.AGENT,
            agent_capability=capability,
            requires_human_confirmation=True,
        ),
        PlanNode(
            node_id="n2",
            kind=PlanNodeKind.TOOL,
            tool_ref=tool_ref,
            tool_args=(("max_nodes", 100),),
        ),
    ]
    if human_gate:
        nodes.append(
            PlanNode(
                node_id="n3",
                kind=PlanNodeKind.HUMAN_GATE,
                human_gate_reason="approve result",
                requires_human_confirmation=True,
                confirmation_role="project_owner",
            )
        )
    edges = edges or (
        (PlanEdge("n1", "n2"), PlanEdge("n2", "n3"))
        if human_gate
        else (PlanEdge("n1", "n2"),)
    )
    plan = Plan(
        plan_id="0" * 64,
        plan_version="1.0",
        policy_profile=policy_profile,
        policy_version=policy_version,
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


class _AllowAll:
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: Plan, actor: str) -> bool:
        return True


class _DenyScope(_AllowAll):
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return False


class _DenyRbac(_AllowAll):
    def authorized(self, plan: Plan, actor: str) -> bool:
        return False


class _BoomRbac(_AllowAll):
    def authorized(self, plan: Plan, actor: str) -> bool:
        raise RuntimeError("rbac unavailable")


def run_validate(plan: Plan, **kwargs):
    return validate_plan(
        plan,
        get_default_profile("INTERACTIVE"),
        scope_checker=kwargs.pop("scope", _AllowAll()),
        rbac_checker=kwargs.pop("rbac", _AllowAll()),
        actor=kwargs.pop("actor", "owner"),
        transition_path=kwargs.pop("transition_path", None),
        validated_at=kwargs.pop("validated_at", "2026-08-07T09:00:00Z"),
    )


class ValidatePlanTests(unittest.TestCase):
    def test_valid_plan_accepted(self) -> None:
        result = run_validate(make_plan())
        self.assertTrue(result.accepted, result.failure_reason)
        self.assertEqual(result.plan_hash, plan_fingerprint(make_plan()))
        self.assertEqual(result.policy_profile, "INTERACTIVE")
        self.assertEqual(result.policy_version, "1.0")

    def test_cycle_rejected(self) -> None:
        plan = make_plan(edges=(PlanEdge("n1", "n2"), PlanEdge("n2", "n1")))
        result = run_validate(plan)
        self.assertFalse(result.accepted)
        self.assertIn("cycle", result.failure_reason or "")

    def test_self_loop_rejected(self) -> None:
        plan = make_plan(edges=(PlanEdge("n1", "n1"),))
        self.assertFalse(run_validate(plan).accepted)

    def test_policy_profile_mismatch_rejected(self) -> None:
        plan = make_plan(policy_profile="BATCH")
        self.assertFalse(run_validate(plan).accepted)

    def test_policy_version_mismatch_rejected(self) -> None:
        plan = make_plan(policy_version="2.0")
        self.assertFalse(run_validate(plan).accepted)

    def test_agent_capability_closed_set_rejected(self) -> None:
        plan = make_plan(capability="not_a_capability")
        self.assertFalse(run_validate(plan).accepted)

    def test_tool_scope_outside_rejected(self) -> None:
        result = run_validate(make_plan(), scope=_DenyScope())
        self.assertFalse(result.accepted)
        self.assertIn("L4 scope", result.failure_reason or "")

    def test_rbac_denied_rejected(self) -> None:
        result = run_validate(make_plan(), rbac=_DenyRbac())
        self.assertFalse(result.accepted)
        self.assertIn("RBAC", result.failure_reason or "")

    def test_l19_path_violation_rejected(self) -> None:
        result = run_validate(
            make_plan(),
            transition_path=(LifecycleState.ESCALATED, LifecycleState.ACTIVE),
        )
        self.assertFalse(result.accepted)
        self.assertIn("L19", result.failure_reason or "")

    def test_l19_path_held_accepted(self) -> None:
        result = run_validate(
            make_plan(),
            transition_path=(
                LifecycleState.ESCALATED,
                LifecycleState.HELD,
                LifecycleState.ACTIVE,
            ),
        )
        self.assertTrue(result.accepted, result.failure_reason)

    def test_injected_checker_exception_fails_closed(self) -> None:
        result = run_validate(make_plan(), rbac=_BoomRbac())
        self.assertFalse(result.accepted)
        self.assertIn("plan validation failed", result.failure_reason or "")

    def test_audit_projection_keys(self) -> None:
        record = run_validate(make_plan()).to_audit_record()
        self.assertEqual(set(record), set(VALIDATION_PROJECTION_KEYS))


if __name__ == "__main__":
    unittest.main()
