"""Professional sub-agent manifest catalog (ARCH-REVIEW-4).

Design-time catalog of the seven professional sub-agents (system-
requirements §7.2): each entry declares its closed-set capability, the
service module that implements it, the model binding, the mandatory
human-confirmation points and the tool policy. Runtime registration still
goes through :func:`coevo.framework.integration.guard_registration`
(manifest-checker + production signer); this catalog is the *declared
contract* the registry must honour.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass

from src.coevo.framework.capability import (
    CapabilityKind,
    CapabilityValidationError,
    resolve_capability,
)
from src.coevo.ids import SAFE_ID
from src.coevo.orchestrator.models import AgentCapability


class AgentCatalogError(ValueError):
    """Raised when the catalog violates its contract (fail-closed)."""


@dataclass(frozen=True)
class AgentCatalogEntry:
    """One professional sub-agent manifest catalog row (ARCH-REVIEW-4)."""

    agent_id: str
    capability: AgentCapability
    service_module: str
    model_binding: str  # "rule" | "model" | "hybrid"
    human_confirmation_points: tuple[str, ...]
    tool_policy: str  # "read-only" | "none" | "guarded-write"


PROFESSIONAL_AGENT_CATALOG: tuple[AgentCatalogEntry, ...] = (
    AgentCatalogEntry(
        agent_id="agent.flow_understanding",
        capability=AgentCapability.TASK_FLOW_UNDERSTANDING,
        service_module="src.coevo.task_flow",
        model_binding="rule",
        human_confirmation_points=("flow_confirm",),
        tool_policy="read-only",
    ),
    AgentCatalogEntry(
        agent_id="agent.task_decomposition",
        capability=AgentCapability.TASK_DECOMPOSITION,
        service_module="src.coevo.task_decomposition",
        model_binding="hybrid",
        human_confirmation_points=("baseline_confirm",),
        tool_policy="read-only",
    ),
    AgentCatalogEntry(
        agent_id="agent.progress_capture",
        capability=AgentCapability.PROGRESS_CAPTURE,
        service_module="src.coevo.progress_capture",
        model_binding="rule",
        human_confirmation_points=("progress_accept",),
        tool_policy="guarded-write",
    ),
    AgentCatalogEntry(
        agent_id="agent.risk_analysis",
        capability=AgentCapability.RISK_ANALYSIS,
        service_module="src.coevo.risk",
        model_binding="hybrid",
        human_confirmation_points=("risk_release",),
        tool_policy="read-only",
    ),
    AgentCatalogEntry(
        agent_id="agent.supervision_meeting",
        capability=AgentCapability.SUPERVISION_MEETING,
        service_module="src.coevo.supervision",
        model_binding="rule",
        human_confirmation_points=("supervision_confirm",),
        tool_policy="read-only",
    ),
    AgentCatalogEntry(
        agent_id="agent.decision_brief",
        capability=AgentCapability.DECISION_BRIEF,
        service_module="src.coevo.decision_brief",
        model_binding="hybrid",
        human_confirmation_points=("brief_release",),
        tool_policy="guarded-write",
    ),
    AgentCatalogEntry(
        agent_id="agent.knowledge_ingest",
        capability=AgentCapability.KNOWLEDGE_INGEST,
        service_module="src.coevo.knowledge_base",
        model_binding="hybrid",
        human_confirmation_points=("knowledge_review",),
        tool_policy="guarded-write",
    ),
)


def validate_catalog() -> list[str]:
    """Validate the catalog, returning a list of violations (fail-closed)."""

    violations: list[str] = []
    seen_ids: set[str] = set()
    for entry in PROFESSIONAL_AGENT_CATALOG:
        if not isinstance(entry, AgentCatalogEntry):
            violations.append(f"non-catalog entry: {entry!r}")
            continue
        if not SAFE_ID.match(entry.agent_id):
            violations.append(f"{entry.agent_id}: agent_id must be safe-id")
        if entry.agent_id in seen_ids:
            violations.append(f"{entry.agent_id}: duplicate agent_id")
        seen_ids.add(entry.agent_id)
        try:
            resolved = resolve_capability(entry.capability.value)
            if resolved.kind is not CapabilityKind.MVP:
                violations.append(
                    f"{entry.agent_id}: capability {entry.capability.value!r} "
                    "is not MVP-executable"
                )
        except CapabilityValidationError as exc:
            violations.append(f"{entry.agent_id}: {exc}")
        try:
            importlib.import_module(entry.service_module)
        except Exception as exc:  # noqa: BLE001 - fail-closed on bad module
            violations.append(
                f"{entry.agent_id}: service module {entry.service_module!r} "
                f"unimportable: {type(exc).__name__}"
            )
        if entry.model_binding not in ("rule", "model", "hybrid"):
            violations.append(f"{entry.agent_id}: invalid model_binding")
        if not entry.human_confirmation_points:
            violations.append(f"{entry.agent_id}: no human confirmation point")
    if len(PROFESSIONAL_AGENT_CATALOG) != 7:
        violations.append(
            f"catalog must contain exactly 7 professional agents; "
            f"got {len(PROFESSIONAL_AGENT_CATALOG)}"
        )
    return violations


__all__ = [
    "AgentCatalogEntry",
    "AgentCatalogError",
    "PROFESSIONAL_AGENT_CATALOG",
    "validate_catalog",
]
