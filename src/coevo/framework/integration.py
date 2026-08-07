"""FRAMEWORK-INTEGRATION-1: framework gates wired to the product orchestrator.

Bridges the framework layer to the existing ``src/coevo/orchestrator``:

* :func:`guard_registration` -- an agent may only be registered after the
  manifest-checker accepts its Agent Manifest;
* :func:`plan_to_chain` -- a validated framework Plan is compiled into the
  product ``OrchestrationChain`` (AGENT nodes resolve registered agents by
  capability; HUMAN_GATE becomes a confirmation step; TOOL nodes and
  framework-abstract capabilities are rejected because the current product
  orchestrator cannot execute them);
* :func:`guarded_dispatch` -- ``validate_plan`` is the mandatory precondition
  before the real ``Orchestrator.dispatch_event`` runs; the product report is
  mapped back to a framework :class:`OrchestrationOutcome`.

The module is additive (no changes to the existing orchestrator) and pure
except for the injected inner registration / dispatch calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from src.coevo.framework.capability import CapabilityKind, resolve_capability
from src.coevo.framework.manifest_checker import (
    AgentManifest,
    ManifestCheckInput,
    check,
)
from src.coevo.framework.orchestrator import (
    OrchestrationMode,
    OrchestrationOutcome,
    OrchestrationStatus,
)
from src.coevo.framework.plan import Plan, PlanNodeKind
from src.coevo.framework.policy import Policy
from src.coevo.framework.validation import (
    RbacChecker,
    ToolScopeChecker,
    validate_plan,
)
from src.coevo.orchestrator.models import (
    AgentRegistry,
    FailurePolicy,
    OrchestrationChain,
    OrchestrationOutcome as ProductOutcome,
    OrchestrationReport,
    OrchestrationStep,
    OrchestrationStepKind,
)
from src.coevo.orchestrator.service import Orchestrator

GUARD_PROJECTION_KEYS = frozenset(
    {"accepted", "manifest_accepted", "agent_id", "reason"}
)


class IntegrationError(Exception):
    """Raised when a Plan cannot be executed by the product orchestrator."""


@runtime_checkable
class InnerRegister(Protocol):
    def __call__(self, manifest: AgentManifest) -> None: ...


@dataclass(frozen=True)
class GuardResult:
    accepted: bool
    manifest_accepted: bool
    manifest: AgentManifest | None
    reason: str | None

    def to_audit_record(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "manifest_accepted": self.manifest_accepted,
            "agent_id": self.manifest.agent_id if self.manifest else None,
            "reason": self.reason,
        }


def guard_registration(
    manifest_input: ManifestCheckInput,
    *,
    policy_registry: Any,
    cert_resolver: Any,
    signature_verifier: Any,
    inner_register: InnerRegister,
) -> GuardResult:
    """Register an agent only after manifest-checker acceptance."""

    result = check(
        manifest_input,
        policy_registry=policy_registry,
        cert_resolver=cert_resolver,
        signature_verifier=signature_verifier,
    )
    if not result.accepted or result.validated_manifest is None:
        return GuardResult(
            accepted=False,
            manifest_accepted=False,
            manifest=None,
            reason=result.failure_reason,
        )
    try:
        inner_register(result.validated_manifest)
    except Exception as exc:  # noqa: BLE001 - inner registration fails closed
        return GuardResult(
            accepted=False,
            manifest_accepted=True,
            manifest=result.validated_manifest,
            reason=f"inner registration failed: {type(exc).__name__}",
        )
    return GuardResult(
        accepted=True,
        manifest_accepted=True,
        manifest=result.validated_manifest,
        reason=None,
    )


def plan_to_chain(
    plan: Plan,
    registry: AgentRegistry,
    *,
    chain_id: str = "framework.plan",
) -> OrchestrationChain:
    """Compile a framework Plan into the product OrchestrationChain."""

    steps: list[OrchestrationStep] = []
    for index, node in enumerate(plan.nodes):
        if node.kind is PlanNodeKind.HUMAN_GATE:
            steps.append(
                OrchestrationStep(
                    step_index=index,
                    kind=OrchestrationStepKind.HUMAN_CONFIRM,
                    requires_human_confirmation=True,
                    on_failure=FailurePolicy.ESCALATE_HUMAN,
                )
            )
            continue
        if node.kind is PlanNodeKind.TOOL:
            raise IntegrationError(
                f"TOOL node {node.node_id!r} cannot be executed by the "
                "product orchestrator (integration scope)"
            )
        entry = resolve_capability(node.agent_capability)
        if entry.kind is not CapabilityKind.MVP or entry.agent_capability is None:
            raise IntegrationError(
                f"AGENT node {node.node_id!r} uses non-MVP capability "
                f"{node.agent_capability!r}; not executable by the product "
                "orchestrator"
            )
        agents = registry.by_capability(entry.agent_capability)
        if not agents:
            raise IntegrationError(
                f"no registered agent for capability "
                f"{entry.agent_capability.name}"
            )
        steps.append(
            OrchestrationStep(
                step_index=index,
                kind=OrchestrationStepKind.AGENT_CALL,
                agent_id=agents[0].spec.agent_id,
                requires_human_confirmation=node.requires_human_confirmation,
                on_failure=FailurePolicy.ESCALATE_HUMAN,
            )
        )
    return OrchestrationChain(chain_id=chain_id, steps=tuple(steps))


def report_to_outcome(
    report: OrchestrationReport,
    plan_hash: str,
    validated_at: str,
    *,
    mode: OrchestrationMode = OrchestrationMode.HYBRID,
) -> OrchestrationOutcome:
    """Map the product dispatch report to a framework outcome."""

    mapping = {
        ProductOutcome.COMPLETED: OrchestrationStatus.COMPLETED,
        ProductOutcome.HELD_AT_CONFIRM: OrchestrationStatus.HELD,
        ProductOutcome.CONFIRMED_PENDING_PACKAGE: OrchestrationStatus.HELD,
        ProductOutcome.ESCALATED: OrchestrationStatus.ESCALATED,
        ProductOutcome.FAILED: OrchestrationStatus.ESCALATED,  # fail-closed
    }
    status = mapping.get(report.outcome, OrchestrationStatus.ESCALATED)
    return OrchestrationOutcome(
        accepted=True,
        mode=mode,
        status=status,
        plan_hash=plan_hash,
        validated_at=validated_at,
        failure_reason=None,
    )


def guarded_dispatch(
    plan: Plan,
    policy: Policy,
    *,
    event: Any,
    workspace: Any,
    now: str,
    registry: AgentRegistry,
    scope_checker: ToolScopeChecker,
    rbac_checker: RbacChecker,
    actor: str,
    validated_at: str,
    chain_id: str = "framework.plan",
    mode: OrchestrationMode = OrchestrationMode.HYBRID,
    dispatch_fn: Any = Orchestrator.dispatch_event,
) -> OrchestrationOutcome:
    """validate_plan-gated dispatch through the real product orchestrator."""

    validation = validate_plan(
        plan,
        policy,
        scope_checker=scope_checker,
        rbac_checker=rbac_checker,
        actor=actor,
        validated_at=validated_at,
    )
    if not validation.accepted:
        return OrchestrationOutcome(
            accepted=False,
            mode=mode,
            status=OrchestrationStatus.REJECTED,
            plan_hash=validation.plan_hash,
            validated_at=validated_at,
            failure_reason=validation.failure_reason,
        )
    try:
        chain = plan_to_chain(plan, registry, chain_id=chain_id)
        report = dispatch_fn(
            registry, chain, event, workspace=workspace, now=now
        )
    except Exception as exc:  # noqa: BLE001 - inner dispatch fails closed
        return OrchestrationOutcome(
            accepted=True,
            mode=mode,
            status=OrchestrationStatus.ESCALATED,
            plan_hash=validation.plan_hash,
            validated_at=validated_at,
            failure_reason=f"inner dispatch failed: {type(exc).__name__}",
        )
    return report_to_outcome(
        report,
        validation.plan_hash,
        validated_at,
        mode=mode,
    )
