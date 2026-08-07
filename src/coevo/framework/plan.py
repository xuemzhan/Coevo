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
MAX_PLAN_JSON_BYTES = 64 * 1024

PLAN_JSON_KEYS = frozenset(
    {"plan_id", "plan_version", "policy_profile", "policy_version", "nodes", "edges"}
)
NODE_JSON_KEYS = frozenset(
    {
        "node_id",
        "kind",
        "agent_capability",
        "tool_ref",
        "tool_args",
        "human_gate_reason",
        "requires_human_confirmation",
        "confirmation_role",
    }
)
EDGE_JSON_KEYS = frozenset({"predecessor_node_id", "successor_node_id"})

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


def plan_to_json(plan: Plan) -> dict[str, object]:
    """Canonical Plan → JSON object (Plan-LSP serialization)."""

    validate_plan_structure(plan)
    return {
        "plan_id": plan.plan_id,
        "plan_version": plan.plan_version,
        "policy_profile": plan.policy_profile,
        "policy_version": plan.policy_version,
        "nodes": [
            {
                "node_id": node.node_id,
                "kind": node.kind.value,
                "agent_capability": node.agent_capability,
                "tool_ref": node.tool_ref,
                "tool_args": [list(pair) for pair in node.tool_args],
                "human_gate_reason": node.human_gate_reason,
                "requires_human_confirmation": node.requires_human_confirmation,
                "confirmation_role": node.confirmation_role,
            }
            for node in plan.nodes
        ],
        "edges": [
            {
                "predecessor_node_id": edge.predecessor_node_id,
                "successor_node_id": edge.successor_node_id,
            }
            for edge in plan.edges
        ],
    }


def json_to_plan(mapping: object) -> Plan:
    """Strict JSON object → Plan (unknown keys, bad shapes rejected)."""

    if not isinstance(mapping, dict):
        raise PlanValidationError("plan JSON must be an object")
    unknown = sorted(set(mapping) - PLAN_JSON_KEYS)
    if unknown:
        raise PlanValidationError("unsupported plan JSON keys: " + ", ".join(unknown))
    plan_id = mapping.get("plan_id")
    plan_version = mapping.get("plan_version")
    policy_profile = mapping.get("policy_profile")
    policy_version = mapping.get("policy_version")
    if not isinstance(plan_id, str) or not _HEX64.match(plan_id):
        raise PlanValidationError("plan_id must be a 64-hex string")
    if not isinstance(plan_version, str) or not plan_version:
        raise PlanValidationError("plan_version is required")
    if not isinstance(policy_profile, str) or not isinstance(policy_version, str):
        raise PlanValidationError("policy_profile and policy_version must be strings")
    nodes_raw = mapping.get("nodes")
    edges_raw = mapping.get("edges", [])
    if not isinstance(nodes_raw, list) or not nodes_raw:
        raise PlanValidationError("nodes must be a non-empty list")
    if not isinstance(edges_raw, list):
        raise PlanValidationError("edges must be a list")
    nodes = tuple(_node_from_json(item) for item in nodes_raw)
    edges = tuple(_edge_from_json(item) for item in edges_raw)
    plan = Plan(
        plan_id=plan_id,
        plan_version=plan_version,
        policy_profile=policy_profile,
        policy_version=policy_version,
        nodes=nodes,
        edges=edges,
    )
    validate_plan_structure(plan)
    return plan


def parse_plan_json_bytes(data: bytes) -> Plan:
    """Strict canonical-JSON bytes → Plan (BOM/duplicate keys/size caps)."""

    if not isinstance(data, bytes):
        raise PlanValidationError("plan JSON must be bytes")
    if len(data) > MAX_PLAN_JSON_BYTES:
        raise PlanValidationError(
            f"plan JSON exceeds the {MAX_PLAN_JSON_BYTES}-byte size limit"
        )
    if data.startswith(b"\xef\xbb\xbf"):
        raise PlanValidationError("BOM is not allowed in canonical plan JSON")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PlanValidationError(f"plan JSON is not valid UTF-8: {exc}") from exc
    try:
        mapping = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        raise PlanValidationError(f"plan JSON is not valid JSON: {exc}") from exc
    return json_to_plan(mapping)


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in pairs:
        if key in out:
            raise PlanValidationError(f"duplicate key in plan JSON: {key!r}")
        out[key] = value
    return out


def _node_from_json(item: object) -> PlanNode:
    if not isinstance(item, dict):
        raise PlanValidationError("each node must be an object")
    unknown = sorted(set(item) - NODE_JSON_KEYS)
    if unknown:
        raise PlanValidationError(
            "unsupported plan node keys: " + ", ".join(unknown)
        )
    node_id = item.get("node_id")
    kind_raw = item.get("kind")
    if not isinstance(node_id, str) or not _SAFE_ID.match(node_id):
        raise PlanValidationError("node_id must be a safe-id")
    try:
        kind = PlanNodeKind(kind_raw)
    except ValueError:
        raise PlanValidationError(
            f"node kind must be one of {[k.value for k in PlanNodeKind]}; got {kind_raw!r}"
        ) from None
    tool_args_raw = item.get("tool_args", [])
    if not isinstance(tool_args_raw, list):
        raise PlanValidationError("tool_args must be a list of [key, value] pairs")
    tool_args: list[tuple[str, object]] = []
    for pair in tool_args_raw:
        if (
            not isinstance(pair, list)
            or len(pair) != 2
            or not isinstance(pair[0], str)
        ):
            raise PlanValidationError(
                "tool_args entries must be [key, value] pairs with string keys"
            )
        tool_args.append((pair[0], pair[1]))
    rhc = item.get("requires_human_confirmation", False)
    if not isinstance(rhc, bool):
        raise PlanValidationError("requires_human_confirmation must be bool")
    for field in ("agent_capability", "tool_ref", "human_gate_reason", "confirmation_role"):
        value = item.get(field)
        if value is not None and not isinstance(value, str):
            raise PlanValidationError(f"{field} must be a string")
    return PlanNode(
        node_id=node_id,
        kind=kind,
        agent_capability=item.get("agent_capability", ""),
        tool_ref=item.get("tool_ref", ""),
        tool_args=tuple(tool_args),
        human_gate_reason=item.get("human_gate_reason", ""),
        requires_human_confirmation=rhc,
        confirmation_role=item.get("confirmation_role", ""),
    )


def _edge_from_json(item: object) -> PlanEdge:
    if not isinstance(item, dict):
        raise PlanValidationError("each edge must be an object")
    unknown = sorted(set(item) - EDGE_JSON_KEYS)
    if unknown:
        raise PlanValidationError(
            "unsupported plan edge keys: " + ", ".join(unknown)
        )
    predecessor = item.get("predecessor_node_id")
    successor = item.get("successor_node_id")
    if not isinstance(predecessor, str) or not _SAFE_ID.match(predecessor):
        raise PlanValidationError("predecessor_node_id must be a safe-id")
    if not isinstance(successor, str) or not _SAFE_ID.match(successor):
        raise PlanValidationError("successor_node_id must be a safe-id")
    return PlanEdge(predecessor, successor)


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
