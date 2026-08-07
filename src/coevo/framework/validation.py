"""US-16-AC-2: ``validate_plan`` dispatch precondition (CTAF §6.6 / §8.4).

``validate_plan`` runs the five §6.4.1 invariants (acyclic, closed node kinds,
hashability, L4 tool scope, four-layer RBAC) plus L18 (no policy-owned numeric
keys) and L19 (ESCALATED→ACTIVE must pass through HELD).  L4 scope and RBAC
are delegated to injected protocols so the checker stays pure and stdlib-only;
any injected exception is treated as a rejection (fail-closed).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from src.coevo.framework.lifecycle import (
    LifecycleState,
    validate_transition_path,
)
from src.coevo.framework.plan import (
    Plan,
    PlanNodeKind,
    PlanValidationError,
    plan_fingerprint,
    validate_plan_structure,
)
from src.coevo.framework.policy import Policy, PolicyValidationError
from src.coevo.orchestrator.models import AgentCapability

VALIDATION_PROJECTION_KEYS = frozenset(
    {
        "accepted",
        "plan_hash",
        "policy_profile",
        "policy_version",
        "validated_at",
        "failure_reason",
    }
)


@runtime_checkable
class ToolScopeChecker(Protocol):
    """L4 scope decision for a TOOL node under a policy profile."""

    def within_scope(self, tool_ref: str, policy_profile: str) -> bool: ...


@runtime_checkable
class RbacChecker(Protocol):
    """Four-layer RBAC decision for the whole Plan."""

    def authorized(self, plan: Plan, actor: str) -> bool: ...


@dataclass(frozen=True)
class ValidationResult:
    """CTAF §8.4 validation result."""

    accepted: bool
    plan_hash: str
    policy_profile: str
    policy_version: str
    validated_at: str
    failure_reason: str | None

    def to_audit_record(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "plan_hash": self.plan_hash,
            "policy_profile": self.policy_profile,
            "policy_version": self.policy_version,
            "validated_at": self.validated_at,
            "failure_reason": self.failure_reason,
        }


def validate_plan(
    plan: Plan,
    policy: Policy,
    *,
    scope_checker: ToolScopeChecker,
    rbac_checker: RbacChecker,
    actor: str,
    transition_path: tuple[LifecycleState, ...] | None = None,
    validated_at: str = "",
) -> ValidationResult:
    """Validate a Plan before dispatch (pure, fail-closed)."""

    def reject(reason: str) -> ValidationResult:
        return ValidationResult(
            accepted=False,
            plan_hash=plan.plan_id if isinstance(plan, Plan) else "",
            policy_profile=policy.profile,
            policy_version=policy.policy_version,
            validated_at=validated_at,
            failure_reason=reason,
        )

    if not validated_at:
        return reject("validated_at is required for audit metadata")
    try:
        validate_plan_structure(plan)
        if plan.policy_profile != policy.profile:
            return reject(
                f"plan.policy_profile {plan.policy_profile!r} does not match "
                f"policy.profile {policy.profile!r}"
            )
        if plan.policy_version != policy.policy_version:
            return reject(
                f"plan.policy_version {plan.policy_version!r} does not match "
                f"policy.policy_version {policy.policy_version!r} (F7)"
            )
        _validate_agent_capabilities(plan)
        _validate_tool_scopes(plan, policy.profile, scope_checker)
        _validate_acyclic(plan)
        if not rbac_checker.authorized(plan, actor):
            return reject("four-layer RBAC authorization failed")
        if transition_path is not None:
            path_ok, path_reason = validate_transition_path(transition_path)
            if not path_ok:
                return reject(f"L19: {path_reason}")
    except (PlanValidationError, PolicyValidationError) as exc:
        return reject(str(exc))
    except Exception as exc:  # noqa: BLE001 - injected checkers must fail closed
        return reject(f"plan validation failed: {type(exc).__name__}")
    return ValidationResult(
        accepted=True,
        plan_hash=plan_fingerprint(plan),
        policy_profile=policy.profile,
        policy_version=policy.policy_version,
        validated_at=validated_at,
        failure_reason=None,
    )


def _validate_agent_capabilities(plan: Plan) -> None:
    for node in plan.nodes:
        if node.kind is PlanNodeKind.AGENT:
            try:
                AgentCapability(node.agent_capability)
            except ValueError:
                raise PlanValidationError(
                    f"AGENT node capability outside the closed set: "
                    f"{node.agent_capability!r}"
                ) from None


def _validate_tool_scopes(
    plan: Plan,
    policy_profile: str,
    scope_checker: ToolScopeChecker,
) -> None:
    for node in plan.nodes:
        if node.kind is PlanNodeKind.TOOL:
            if not scope_checker.within_scope(node.tool_ref, policy_profile):
                raise PlanValidationError(
                    f"TOOL node {node.node_id!r} (tool_ref {node.tool_ref!r}) "
                    f"is outside the L4 scope of profile {policy_profile!r}"
                )


def _validate_acyclic(plan: Plan) -> None:
    """Iterative DFS cycle detection (invariant 1)."""

    adjacency: dict[str, list[str]] = {node.node_id: [] for node in plan.nodes}
    for edge in plan.edges:
        adjacency[edge.predecessor_node_id].append(edge.successor_node_id)
    color: dict[str, int] = {}  # 0 = white, 1 = gray, 2 = black
    for start in adjacency:
        if color.get(start, 0) != 0:
            continue
        stack: list[tuple[str, int]] = [(start, 0)]
        while stack:
            node_id, pointer = stack.pop()
            if pointer == 0:
                if color.get(node_id, 0) == 1:
                    raise PlanValidationError("plan DAG contains a cycle")
                if color.get(node_id, 0) == 2:
                    continue
                color[node_id] = 1
                stack.append((node_id, 1))
                for successor in adjacency.get(node_id, []):
                    if color.get(successor, 0) == 0:
                        stack.append((successor, 0))
                    elif color.get(successor, 0) == 1:
                        raise PlanValidationError("plan DAG contains a cycle")
            else:
                color[node_id] = 2
