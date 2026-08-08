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

import hashlib
from dataclasses import dataclass, replace
from typing import Any, Protocol, runtime_checkable

from src.coevo.framework.capability import (
    CapabilityKind,
    CapabilityValidationError,
    resolve_capability,
)
from src.coevo.canon import canonical_json_bytes
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
    ValidationResult,
    is_iso_utc_z,
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
    require_production_verifier: bool = False,
) -> GuardResult:
    """Register an agent only after manifest-checker acceptance.

    ``require_production_verifier=True`` enforces the production boundary
    (FRAMEWORK-GAPS-7): the injected signature verifier MUST declare
    ``is_production is True`` (real SM2 verification bound to the certificate
    chain).  Demo adapters declare ``is_production=False`` and are rejected on
    production registration paths, fail-closed.
    """

    if (
        require_production_verifier
        and getattr(signature_verifier, "is_production", False) is not True
    ):
        return GuardResult(
            accepted=False,
            manifest_accepted=False,
            manifest=None,
            reason="production registration requires a production verifier "
            "(real SM2 bound to the certificate chain, is_production=True); "
            "demo adapters are rejected",
        )

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


def build_registration_manifest(
    agent_id: str,
    capability: str,
    *,
    display_name: str | None = None,
    semantic_version: str = "1.0.0",
    policy_profile: str = "INTERACTIVE",
    policy_version: str = "1.0",
    crypto_scope: str = "mvp-prototype",
    requires_human_confirmation: bool = True,
    signer_cert_fingerprint: str,
    signer: Any | None = None,
) -> bytes:
    """Build a canonical Agent Manifest for registration (pure).

    ``spec_hash`` excludes the self-referential fields
    (``metadata.spec_hash`` / ``policy_ref.spec_hash`` /
    ``policy_ref.signature``).  ``signer`` (optional) receives the
    ``spec_hash|fingerprint`` binding and returns the raw SM2 signature;
    production callers MUST inject a real signer backed by the certificate
    chain.
    """

    manifest: dict[str, Any] = {
        "apiVersion": "coevo.framework/v1",
        "kind": "Agent",
        "metadata": {
            "agent_id": agent_id,
            "display_name": display_name or capability,
            "semantic_version": semantic_version,
        },
        "spec": {
            "capability": capability,
            "requires_human_confirmation": requires_human_confirmation,
        },
        "policy_profile": policy_profile,
        "policy_version": policy_version,
        "policy_ref": {
            "signer_cert_fingerprint": signer_cert_fingerprint,
            "signature": "",
        },
        "security": {"crypto_scope": crypto_scope},
        "audit": {"redact_in_audit": ["policy_profile"]},
    }

    # FRAMEWORK-OPTIMIZE-1: structural copy that excludes the
    # self-referential fields -- no JSON round-trip needed. The canonical
    # bytes are identical to the previous implementation (sort_keys +
    # separators are unchanged), pinned by a byte-level regression test.
    stripped: dict[str, Any] = {
        "apiVersion": manifest["apiVersion"],
        "kind": manifest["kind"],
        "metadata": {
            key: value
            for key, value in manifest["metadata"].items()
            if key != "spec_hash"
        },
        "spec": manifest["spec"],
        "policy_profile": manifest["policy_profile"],
        "policy_version": manifest["policy_version"],
        "policy_ref": {
            key: value
            for key, value in manifest["policy_ref"].items()
            if key not in ("spec_hash", "signature")
        },
        "security": manifest["security"],
        "audit": manifest["audit"],
    }
    spec_hash = hashlib.sha256(canonical_json_bytes(stripped)).hexdigest()
    manifest["metadata"]["spec_hash"] = spec_hash
    manifest["policy_ref"]["spec_hash"] = spec_hash
    if signer is not None:
        binding = (spec_hash + signer_cert_fingerprint).encode("ascii")
        manifest["policy_ref"]["signature"] = signer(binding).hex()
    return canonical_json_bytes(manifest)


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
        try:
            entry = resolve_capability(node.agent_capability)
        except CapabilityValidationError as exc:
            raise IntegrationError(str(exc)) from exc
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


def chain_to_plan(
    chain: OrchestrationChain,
    registry: AgentRegistry,
    policy: Policy,
    *,
    plan_version: str = "1.0",
) -> Plan:
    """Lift an existing product OrchestrationChain into a framework Plan."""

    nodes: list[PlanNode] = []
    edges: list[PlanEdge] = []
    previous: str | None = None
    for index, step in enumerate(chain.steps):
        node_id = f"c{index}"
        if step.kind is OrchestrationStepKind.HUMAN_CONFIRM:
            node = PlanNode(
                node_id=node_id,
                kind=PlanNodeKind.HUMAN_GATE,
                human_gate_reason="product chain confirmation",
                requires_human_confirmation=True,
            )
        elif step.kind is OrchestrationStepKind.AGENT_CALL:
            registration = registry.get(step.agent_id)
            if registration is None:
                raise IntegrationError(
                    f"agent {step.agent_id!r} is not registered"
                )
            try:
                entry = resolve_capability(registration.spec.capability.value)
            except CapabilityValidationError as exc:
                raise IntegrationError(str(exc)) from exc
            if entry.kind is not CapabilityKind.MVP:
                raise IntegrationError(
                    f"agent {step.agent_id!r} has non-MVP capability "
                    f"{registration.spec.capability.value!r}; not liftable"
                )
            node = PlanNode(
                node_id=node_id,
                kind=PlanNodeKind.AGENT,
                agent_capability=registration.spec.capability.value,
                requires_human_confirmation=step.requires_human_confirmation,
            )
        else:
            raise IntegrationError(
                f"chain step kind {step.kind!r} cannot be lifted to a Plan"
            )
        nodes.append(node)
        if previous is not None:
            edges.append(PlanEdge(previous, node_id))
        previous = node_id
    plan = Plan(
        plan_id="0" * 64,
        plan_version=plan_version,
        policy_profile=policy.profile,
        policy_version=policy.policy_version,
        nodes=tuple(nodes),
        edges=tuple(edges),
    )
    # FRAMEWORK-OPTIMIZE-1: set the fingerprint in one pass instead of
    # rebuilding the whole Plan (nodes/edges are frozen and reused).
    return replace(plan, plan_id=plan_fingerprint(plan))


def validate_product_chain(
    chain: OrchestrationChain,
    registry: AgentRegistry,
    policy: Policy,
    *,
    scope_checker: ToolScopeChecker,
    rbac_checker: RbacChecker,
    actor: str,
    validated_at: str,
) -> ValidationResult:
    """Lift a product chain and run validate_plan (five invariants + L18 + L19)."""

    if not is_iso_utc_z(validated_at):
        return ValidationResult(
            accepted=False,
            plan_hash="",
            policy_profile=policy.profile,
            policy_version=policy.policy_version,
            validated_at=validated_at,
            failure_reason="validated_at must be ISO-8601 UTC with trailing Z (L7)",
        )
    try:
        plan = chain_to_plan(chain, registry, policy)
    except IntegrationError as exc:
        return ValidationResult(
            accepted=False,
            plan_hash="",
            policy_profile=policy.profile,
            policy_version=policy.policy_version,
            validated_at=validated_at,
            failure_reason=str(exc),
        )
    return validate_plan(
        plan,
        policy,
        scope_checker=scope_checker,
        rbac_checker=rbac_checker,
        actor=actor,
        validated_at=validated_at,
    )


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
