"""US-16-AC-3: framework capability closed-set convergence (CTAF §5.2 / M1b).

Reconciles the CTAF §5.2 capability closed set with the existing
``AgentCapability`` enum (the orchestrator's single source of truth):

* every CTAF §5.2 name is registered with an explicit kind;
* MVP capabilities map to an ``AgentCapability`` member (dual-name
  resolution accepts both the enum value and the CTAF name);
* ``CRYPTO_PROXY`` is a distinct kind that requires the
  ``APPROVED_PRODUCT`` crypto scope;
* PLANNER / ROUTER / AGGREGATOR / EVALUATOR / OPTIMIZER / HUMAN_GATE are
  framework-abstract capabilities usable at Plan level.

The registry is fail-closed: unknown names and case variants are rejected.
L15: standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.coevo.orchestrator.models import AgentCapability


class CapabilityKind(Enum):
    """How a capability is used within the framework."""

    MVP = "MVP"
    FRAMEWORK_ABSTRACT = "FRAMEWORK_ABSTRACT"
    CRYPTO_PROXY = "CRYPTO_PROXY"


class CapabilityValidationError(Exception):
    """Raised when a capability name is outside the closed set."""


@dataclass(frozen=True)
class CapabilityEntry:
    """One entry of the framework capability closed set."""

    canonical_name: str
    kind: CapabilityKind
    agent_capability: AgentCapability | None = None
    aliases: tuple[str, ...] = ()
    description: str = ""
    requires_approved_product: bool = False


def _entry(
    canonical_name: str,
    kind: CapabilityKind,
    agent_capability: AgentCapability | None = None,
    aliases: tuple[str, ...] = (),
    description: str = "",
    requires_approved_product: bool = False,
) -> CapabilityEntry:
    return CapabilityEntry(
        canonical_name=canonical_name,
        kind=kind,
        agent_capability=agent_capability,
        aliases=aliases,
        description=description,
        requires_approved_product=requires_approved_product,
    )


def _mvp(
    ctaf_name: str,
    capability: AgentCapability,
    description: str = "",
) -> CapabilityEntry:
    return _entry(
        canonical_name=ctaf_name,
        kind=CapabilityKind.MVP,
        agent_capability=capability,
        aliases=(capability.value, capability.name),
        description=description,
    )


CAPABILITY_CLOSED_SET: tuple[CapabilityEntry, ...] = (
    _mvp(
        "TASK_FLOW_UNDERSTANDING",
        AgentCapability.TASK_FLOW_UNDERSTANDING,
        "US-1 task-flow understanding",
    ),
    _mvp(
        "TASK_DECOMPOSITION",
        AgentCapability.TASK_DECOMPOSITION,
        "US-2 task decomposition",
    ),
    _mvp(
        "TEAM_RECOMMENDATION",
        AgentCapability.TEAM_RECOMMENDATION,
        "US-3 team recommendation",
    ),
    _mvp(
        "KNOWLEDGE_INGEST",
        AgentCapability.KNOWLEDGE_INGEST,
        "US-14 knowledge ingestion (registered in M1b)",
    ),
    _mvp(
        "TASK_PACKAGE_BUILD",
        AgentCapability.TASK_PACKAGE_BUILD,
        "US-5 task package build",
    ),
    _mvp(
        "PROGRESS_CAPTURE",
        AgentCapability.PROGRESS_CAPTURE,
        "US-8 progress capture",
    ),
    _mvp(
        "RISK_ANALYSIS",
        AgentCapability.RISK_ANALYSIS,
        "US-11 risk analysis",
    ),
    _mvp(
        "DECISION_BRIEF",
        AgentCapability.DECISION_BRIEF,
        "US-13 decision brief",
    ),
    _mvp(
        "SUPERVISION",
        AgentCapability.SUPERVISION_MEETING,
        "US-12 supervision meeting",
    ),
    _mvp(
        "AUDIT_INTERCEPT",
        AgentCapability.AUDIT_GOVERNANCE,
        "US-15 audit interception",
    ),
    _mvp(
        "REPORT_BUILD",
        AgentCapability.REPORT_BUILD,
        "US-9 report build",
    ),
    _mvp(
        "MERGE_ENGINE",
        AgentCapability.STATE_MERGE,
        "US-10 state merge",
    ),
    _entry(
        "CRYPTO_PROXY",
        CapabilityKind.CRYPTO_PROXY,
        description="crypto proxy; approved product scope only",
        requires_approved_product=True,
    ),
    _entry("PLANNER", CapabilityKind.FRAMEWORK_ABSTRACT, description="framework abstract"),
    _entry("ROUTER", CapabilityKind.FRAMEWORK_ABSTRACT, description="framework abstract"),
    _entry("AGGREGATOR", CapabilityKind.FRAMEWORK_ABSTRACT, description="framework abstract"),
    _entry("EVALUATOR", CapabilityKind.FRAMEWORK_ABSTRACT, description="framework abstract"),
    _entry("OPTIMIZER", CapabilityKind.FRAMEWORK_ABSTRACT, description="framework abstract"),
    _entry("HUMAN_GATE", CapabilityKind.FRAMEWORK_ABSTRACT, description="framework abstract"),
)

_BY_NAME: dict[str, CapabilityEntry] = {}
for _item in CAPABILITY_CLOSED_SET:
    _BY_NAME[_item.canonical_name] = _item
    for _alias in _item.aliases:
        _BY_NAME[_alias] = _item


def capability_entry(name: str) -> CapabilityEntry | None:
    """Resolve a capability name (canonical CTAF name or alias) or None."""

    if not isinstance(name, str):
        return None
    return _BY_NAME.get(name)


def resolve_capability(name: str) -> CapabilityEntry:
    """Resolve a capability name; fail-closed on unknown/case-variant names."""

    entry = capability_entry(name)
    if entry is None:
        raise CapabilityValidationError(
            f"capability outside the framework closed set: {name!r}"
        )
    return entry


def manifest_capability_allowed(entry: CapabilityEntry) -> bool:
    """MVP entries must be mapped to an AgentCapability to be registrable."""

    if entry.kind is CapabilityKind.MVP:
        return entry.agent_capability is not None
    return True


def orphan_agent_capabilities() -> list[str]:
    """AgentCapability members missing from the registry (should be empty)."""

    mapped = {
        item.agent_capability.name
        for item in CAPABILITY_CLOSED_SET
        if item.agent_capability is not None
    }
    return sorted(c.name for c in AgentCapability if c.name not in mapped)


def unmapped_mvp_capabilities() -> list[str]:
    """MVP entries without an AgentCapability mapping (should be empty)."""

    return sorted(
        item.canonical_name
        for item in CAPABILITY_CLOSED_SET
        if item.kind is CapabilityKind.MVP and item.agent_capability is None
    )


def consistency_report() -> dict[str, list[str]]:
    return {
        "orphan_agent_capabilities": orphan_agent_capabilities(),
        "unmapped_mvp_capabilities": unmapped_mvp_capabilities(),
    }


def check_consistency() -> None:
    """Raise when the registry and AgentCapability drift apart (AC-3.4)."""

    report = consistency_report()
    if report["orphan_agent_capabilities"]:
        raise CapabilityValidationError(
            "AgentCapability members missing from the framework registry: "
            + ", ".join(report["orphan_agent_capabilities"])
        )
    if report["unmapped_mvp_capabilities"]:
        raise CapabilityValidationError(
            "MVP capabilities without an AgentCapability mapping: "
            + ", ".join(report["unmapped_mvp_capabilities"])
        )
