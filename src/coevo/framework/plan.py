"""US-16-AC-2: Plan model and L18 white-list rule (CTAF §6.4 / M2).

A Plan is pure structure: DAG nodes/edges plus a ``(policy_profile,
policy_version)`` reference.  Every numeric execution boundary lives in the
referenced Policy (L18).  ``POLICY_OWNED_NUMERIC_KEYS`` is the white-list of
keys a Plan may never carry — including inside ``tool_args``; ordinary
tool data (e.g. ``max_nodes``) is allowed per schema (F6).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")

MAX_PLAN_NODES = 64
MAX_PLAN_EDGES = 128
MAX_TOOL_ARGS = 32
MAX_TEXT_LENGTH = 256

# L18 white-list: policy-owned numeric/consent keys never appear in a Plan.
POLICY_OWNED_NUMERIC_KEYS = frozenset(
    {
        "max_plan_depth",
        "max_runtime_sec",
        "max_recover_attempts",
        "max_router_retries",
        "dispatch_timeout_sec",
        "plan_total_timeout_sec",
        "consent_timeout_sec",
        "recover_backoff_sec",
        "post_hoc_confirm_window_sec",
    }
)


class PlanValidationError(Exception):
    """Raised when a Plan violates the framework invariants."""


class PlanNodeKind(Enum):
    """§6.4.1 invariant 2: closed node-type set."""

    AGENT = "AGENT"
    TOOL = "TOOL"
    HUMAN_GATE = "HUMAN_GATE"


@dataclass(frozen=True)
class PlanNode:
    node_id: str
    kind: PlanNodeKind
    agent_capability: str = ""
    tool_ref: str = ""
    tool_args: tuple[tuple[str, object], ...] = ()
    human_gate_reason: str = ""
    requires_human_confirmation: bool = False
    confirmation_role: str = ""


@dataclass(frozen=True)
class PlanEdge:
    predecessor_node_id: str
    successor_node_id: str


@dataclass(frozen=True)
class Plan:
    plan_id: str
    plan_version: str
    policy_profile: str
    policy_version: str
    nodes: tuple[PlanNode, ...]
    edges: tuple[PlanEdge, ...]


def canonical_plan_bytes(plan: Plan) -> bytes:
    """Canonical JSON of the Plan structure excluding the self-referential
    ``plan_id`` (same canonicalization rules as the `.agent` envelope)."""

    payload = dataclasses.asdict(plan)
    payload.pop("plan_id", None)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=_json_default,
    ).encode("utf-8")


def _json_default(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def plan_fingerprint(plan: Plan) -> str:
    """SHA-256 fingerprint of the Plan structure (invariant 3: hashability)."""

    return hashlib.sha256(canonical_plan_bytes(plan)).hexdigest()


def validate_plan_structure(plan: Plan) -> None:
    """Structural checks shared by :func:`validate_plan` (pure, fail-closed)."""

    if not isinstance(plan, Plan):
        raise PlanValidationError("plan must be a Plan instance")
    if not _HEX64.match(plan.plan_id):
        raise PlanValidationError("plan_id must be a 64-hex fingerprint")
    if plan.plan_id != plan_fingerprint(plan):
        raise PlanValidationError("plan_id does not match the plan fingerprint")
    if not plan.plan_version:
        raise PlanValidationError("plan_version is required")
    if not plan.policy_profile or not plan.policy_version:
        raise PlanValidationError(
            "policy_profile and policy_version are required (F7)"
        )
    if not plan.nodes:
        raise PlanValidationError("plan must contain at least one node")
    if len(plan.nodes) > MAX_PLAN_NODES:
        raise PlanValidationError(
            f"plan exceeds the {MAX_PLAN_NODES}-node limit"
        )
    if len(plan.edges) > MAX_PLAN_EDGES:
        raise PlanValidationError(
            f"plan exceeds the {MAX_PLAN_EDGES}-edge limit"
        )
    node_ids = [node.node_id for node in plan.nodes]
    if len(set(node_ids)) != len(node_ids):
        raise PlanValidationError("duplicate node_id in plan")
    node_set = set(node_ids)
    for node in plan.nodes:
        _validate_node(node)
        _validate_l18_keys(node)
    for edge in plan.edges:
        if edge.predecessor_node_id not in node_set:
            raise PlanValidationError(
                f"edge references unknown predecessor {edge.predecessor_node_id!r}"
            )
        if edge.successor_node_id not in node_set:
            raise PlanValidationError(
                f"edge references unknown successor {edge.successor_node_id!r}"
            )


def _validate_node(node: PlanNode) -> None:
    if not isinstance(node.kind, PlanNodeKind):
        raise PlanValidationError("node kind must be a PlanNodeKind member")
    if not _SAFE_ID.match(node.node_id):
        raise PlanValidationError(f"node_id must be a safe-id: {node.node_id!r}")
    for label, value in (
        ("agent_capability", node.agent_capability),
        ("tool_ref", node.tool_ref),
        ("human_gate_reason", node.human_gate_reason),
        ("confirmation_role", node.confirmation_role),
    ):
        if len(value) > MAX_TEXT_LENGTH:
            raise PlanValidationError(f"{label} exceeds {MAX_TEXT_LENGTH} chars")
    if node.kind is PlanNodeKind.AGENT:
        if not node.agent_capability:
            raise PlanValidationError("AGENT node requires agent_capability")
    elif node.kind is PlanNodeKind.TOOL:
        if not node.tool_ref or not _SAFE_ID.match(node.tool_ref):
            raise PlanValidationError("TOOL node requires a safe-id tool_ref")
    elif node.kind is PlanNodeKind.HUMAN_GATE:
        if not node.human_gate_reason:
            raise PlanValidationError("HUMAN_GATE node requires a reason")
        if not node.requires_human_confirmation:
            raise PlanValidationError("HUMAN_GATE node must require confirmation")
    else:
        raise PlanValidationError(f"unknown node kind: {node.kind!r}")


def _validate_l18_keys(node: PlanNode) -> None:
    """L18: policy-owned numeric keys must not appear anywhere in the Plan."""

    if len(node.tool_args) > MAX_TOOL_ARGS:
        raise PlanValidationError(
            f"node {node.node_id!r} exceeds the {MAX_TOOL_ARGS}-entry tool_args limit"
        )
    seen: set[str] = set()
    for key, _value in node.tool_args:
        if key in POLICY_OWNED_NUMERIC_KEYS:
            raise PlanValidationError(
                f"L18: policy-owned key {key!r} is not allowed inside tool_args"
            )
        if key in seen:
            raise PlanValidationError(
                f"duplicate tool_args key {key!r} on node {node.node_id!r}"
            )
        seen.add(key)


def tool_args_mapping(node: PlanNode) -> dict[str, object]:
    return dict(node.tool_args)
