"""US-16-AC-8: Hybrid Orchestrator core (CTAF §6.6 / §8 / M7).

Implements the orchestration contract with three modes sharing the same
hard gates:

* **StateMachine** -- a static chain (injected provider) is compiled into a
  canonical Plan and executed; failure or injected exceptions fail closed
  into ESCALATED with a RECOVER audit path (AC-8.2);
* **DynamicLLM** -- an injected LLM plan proposal is fully validated
  (five invariants + L18 + L19); invalid / missing / raising proposals fall
  back to the state-machine chain (AC-8.3);
* **Hybrid** -- LLM proposals may only cover non-HOLD nodes; any HOLD
  requirement comes from the static chain, otherwise the chain wins; the
  HELD human-confirmation gate is mandatory before further execution
  (AC-8.4).

``dispatch`` always calls :func:`validate_plan` first and refuses to execute
anything that fails (AC-8.1).  All LLM / chain / execution IO is injected;
the module is pure, stdlib-only and fully offline-testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from src.coevo.framework.lifecycle import (
    LifecycleState,
    validate_transition_path,
)
from src.coevo.framework.plan import (
    Plan,
    PlanEdge,
    PlanNode,
    PlanNodeKind,
    plan_fingerprint,
)
from src.coevo.framework.policy import Policy
from src.coevo.framework.validation import (
    RbacChecker,
    ToolScopeChecker,
    validate_plan,
)

ORCHESTRATION_PROJECTION_KEYS = frozenset(
    {"accepted", "mode", "status", "plan_hash", "failure_reason"}
)


class OrchestrationMode(Enum):
    STATE_MACHINE = "STATE_MACHINE"
    DYNAMIC_LLM = "DYNAMIC_LLM"
    HYBRID = "HYBRID"


class OrchestrationStatus(Enum):
    COMPLETED = "COMPLETED"
    ACTIVE = "ACTIVE"
    HELD = "HELD"
    RECOVERED = "RECOVERED"
    ESCALATED = "ESCALATED"
    REJECTED = "REJECTED"


class OrchestrationError(Exception):
    """Raised for programming errors in orchestrator usage."""


@dataclass(frozen=True)
class ChainStep:
    node_id: str
    capability: str
    requires_human_confirmation: bool = False


@dataclass(frozen=True)
class ExecutionResult:
    ok: bool
    held_node_id: str | None = None


@runtime_checkable
class StaticChainProvider(Protocol):
    def chain_for(self, task_id: str) -> tuple[ChainStep, ...]: ...


@runtime_checkable
class LlmPlanProvider(Protocol):
    def propose_plan(self, task_id: str, policy: Policy) -> Plan | None: ...


@runtime_checkable
class PlanExecutor(Protocol):
    def execute(self, plan: Plan, actor: str) -> ExecutionResult: ...


@dataclass(frozen=True)
class OrchestrationOutcome:
    accepted: bool
    mode: OrchestrationMode
    status: OrchestrationStatus
    plan_hash: str
    failure_reason: str | None

    def to_audit_record(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "mode": self.mode.value,
            "status": self.status.value,
            "plan_hash": self.plan_hash,
            "failure_reason": self.failure_reason,
        }


def chain_plan(
    task_id: str,
    steps: tuple[ChainStep, ...],
    policy: Policy,
) -> Plan:
    """Compile a static chain into a canonical Plan."""

    if not steps:
        raise OrchestrationError(f"static chain for {task_id!r} is empty")
    nodes = tuple(
        PlanNode(
            node_id=step.node_id,
            kind=PlanNodeKind.AGENT,
            agent_capability=step.capability,
            requires_human_confirmation=step.requires_human_confirmation,
        )
        for step in steps
    )
    edges = tuple(
        PlanEdge(nodes[index].node_id, nodes[index + 1].node_id)
        for index in range(len(nodes) - 1)
    )
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


def _has_hold(plan: Plan) -> bool:
    return any(node.requires_human_confirmation for node in plan.nodes)


def plan_for(
    mode: OrchestrationMode,
    task_id: str,
    policy: Policy,
    *,
    static_chain_provider: StaticChainProvider,
    llm_provider: LlmPlanProvider,
    scope_checker: ToolScopeChecker,
    rbac_checker: RbacChecker,
    actor: str,
    validated_at: str = "",
) -> Plan:
    """Choose the Plan for a mode; LLM proposals fall back to the chain."""

    if not isinstance(mode, OrchestrationMode):
        raise OrchestrationError("mode must be an OrchestrationMode member")
    fallback = chain_plan(task_id, static_chain_provider.chain_for(task_id), policy)
    if mode is OrchestrationMode.STATE_MACHINE:
        return fallback
    if mode is OrchestrationMode.HYBRID and _has_hold(fallback):
        # AC-8.4: the static chain is the ground truth for HOLD requirements.
        # When the chain mandates a human confirmation gate, the LLM proposal
        # must not bypass it -- fall back to the chain plan (dispatch -> HELD).
        return fallback
    try:
        proposal = llm_provider.propose_plan(task_id, policy)
    except Exception:  # noqa: BLE001 - injected LLM fails closed into fallback
        return fallback
    if proposal is None or not isinstance(proposal, Plan):
        return fallback
    if mode is OrchestrationMode.HYBRID and _has_hold(proposal):
        return fallback
    try:
        validation = validate_plan(
            proposal,
            policy,
            scope_checker=scope_checker,
            rbac_checker=rbac_checker,
            actor=actor,
            validated_at=validated_at,
        )
    except Exception:  # noqa: BLE001 - malformed proposal fails closed
        return fallback
    if not validation.accepted:
        return fallback
    return proposal


def dispatch(
    mode: OrchestrationMode,
    task_id: str,
    policy: Policy,
    *,
    plan: Plan,
    actor: str,
    scope_checker: ToolScopeChecker,
    rbac_checker: RbacChecker,
    plan_executor: PlanExecutor,
    transition_path: tuple[LifecycleState, ...] | None = None,
    validated_at: str = "",
) -> OrchestrationOutcome:
    """Dispatch with validate_plan as a mandatory precondition (AC-8.1)."""

    validation = validate_plan(
        plan,
        policy,
        scope_checker=scope_checker,
        rbac_checker=rbac_checker,
        actor=actor,
        transition_path=transition_path,
        validated_at=validated_at,
    )
    if not validation.accepted:
        return OrchestrationOutcome(
            accepted=False,
            mode=mode,
            status=OrchestrationStatus.REJECTED,
            plan_hash=validation.plan_hash,
            failure_reason=validation.failure_reason,
        )
    if _has_hold(plan):
        return OrchestrationOutcome(
            accepted=True,
            mode=mode,
            status=OrchestrationStatus.HELD,
            plan_hash=validation.plan_hash,
            failure_reason=None,
        )
    try:
        result = plan_executor.execute(plan, actor)
    except Exception as exc:  # noqa: BLE001 - injected executor fails closed
        return OrchestrationOutcome(
            accepted=True,
            mode=mode,
            status=OrchestrationStatus.ESCALATED,
            plan_hash=validation.plan_hash,
            failure_reason=f"execution failed: {type(exc).__name__}",
        )
    if not isinstance(result, ExecutionResult) or not result.ok:
        return OrchestrationOutcome(
            accepted=True,
            mode=mode,
            status=OrchestrationStatus.ESCALATED,
            plan_hash=validation.plan_hash,
            failure_reason="execution failed (audit RECOVER path)",
        )
    return OrchestrationOutcome(
        accepted=True,
        mode=mode,
        status=OrchestrationStatus.COMPLETED,
        plan_hash=validation.plan_hash,
        failure_reason=None,
    )


def transition(
    mode: OrchestrationMode,
    *,
    plan_hash: str,
    path: tuple[LifecycleState, ...],
) -> OrchestrationOutcome:
    """Validate an eight-state path (L19) and report the terminal status."""

    ok, reason = validate_transition_path(path)
    if not ok:
        return OrchestrationOutcome(
            accepted=False,
            mode=mode,
            status=OrchestrationStatus.REJECTED,
            plan_hash=plan_hash,
            failure_reason=reason,
        )
    terminal = path[-1]
    if terminal is LifecycleState.ACTIVE:
        status = OrchestrationStatus.ACTIVE
    elif terminal is LifecycleState.RECOVERED:
        status = OrchestrationStatus.RECOVERED
    elif terminal is LifecycleState.RETIRED:
        status = OrchestrationStatus.COMPLETED
    else:
        status = OrchestrationStatus.HELD
    return OrchestrationOutcome(
        accepted=True,
        mode=mode,
        status=status,
        plan_hash=plan_hash,
        failure_reason=None,
    )
