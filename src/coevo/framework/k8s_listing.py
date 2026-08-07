"""US-16-AC-9: K8s CRD paper listing generator (CTAF §14.2 / §16.4 / M9).

Exports the framework declarations (capabilities / tools / policies / plans)
as a deterministic, hashable *paper listing* (canonical JSON plus a safe YAML
rendering subset) for documentation and compliance use.  Per §16.4 this is
**paper only**: no reconcile loop, no Kubernetes coupling, no IO.  The
generator is a pure function; ``listing_fingerprint`` pins the exact bytes for
audit / version comparison.

L15: standard library only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from src.coevo.framework.capability import CapabilityEntry
from src.coevo.framework.plan import Plan
from src.coevo.framework.policy import Policy
from src.coevo.framework.tools import Tool

LISTING_KEYS = frozenset({"apiVersion", "kind", "metadata", "spec"})
METADATA_KEYS = frozenset({"schema_version", "generated_at"})
SPEC_KEYS = frozenset({"capabilities", "tools", "policies", "plans"})
MAX_LISTING_BYTES = 64 * 1024
MAX_LISTING_DEPTH = 64


class ListingValidationError(Exception):
    """Raised when listing bytes are not canonical or malformed."""


@dataclass(frozen=True)
class ListingInput:
    """Read-only declaration set for the paper listing."""

    capabilities: tuple[CapabilityEntry, ...] = ()
    tools: tuple[Tool, ...] = ()
    policies: tuple[Policy, ...] = ()
    plans: tuple[Plan, ...] = ()
    generated_at: str = ""

    def to_audit_record(self) -> dict[str, object]:
        """Audit projection (AC-9.5): fixed-key summary, no spec details."""

        return {
            "kind": "DeclarativeListing",
            "schema_version": "1.0",
            "generated_at": self.generated_at,
            "capability_count": len(self.capabilities),
            "tool_count": len(self.tools),
            "policy_count": len(self.policies),
            "plan_count": len(self.plans),
            "listing_fingerprint": listing_fingerprint(self),
        }


def generate_listing_json(inp: ListingInput) -> dict[str, Any]:
    """Build the canonical listing structure (pure, deterministic)."""

    capabilities = [
        {
            "name": entry.canonical_name,
            "kind": entry.kind.value,
            "agent_capability": entry.agent_capability.name
            if entry.agent_capability is not None
            else None,
            "requires_approved_product": entry.requires_approved_product,
        }
        for entry in inp.capabilities
    ]
    tools = [
        {
            "tool_id": tool.tool_id,
            "tool_version": tool.tool_version,
            "display_name": tool.display_name,
            "description": tool.description,
            "side_effects": tool.side_effects.value,
            "requires_consent": tool.requires_consent,
            "timeout_sec": tool.timeout_sec,
            "size_in_bytes_max": tool.size_in_bytes_max,
            "crypto_scope": tool.crypto_scope.value,
            "audit_required": tool.audit_required,
        }
        for tool in inp.tools
    ]
    policies = [
        {
            "policy_id": policy.policy_id,
            "policy_version": policy.policy_version,
            "profile": policy.profile,
            "max_recover_attempts": policy.retry_profile.max_recover_attempts,
            "dispatch_timeout_sec": policy.timeout_profile.dispatch_timeout_sec,
            "plan_total_timeout_sec": policy.timeout_profile.plan_total_timeout_sec,
        }
        for policy in inp.policies
    ]
    plans = [
        {
            "plan_id": plan.plan_id,
            "plan_version": plan.plan_version,
            "policy_profile": plan.policy_profile,
            "policy_version": plan.policy_version,
            "node_count": len(plan.nodes),
            "edge_count": len(plan.edges),
        }
        for plan in inp.plans
    ]
    return {
        "apiVersion": "coevo.framework/v1",
        "kind": "DeclarativeListing",
        "metadata": {
            "schema_version": "1.0",
            "generated_at": inp.generated_at,
        },
        "spec": {
            "capabilities": capabilities,
            "tools": tools,
            "policies": policies,
            "plans": plans,
        },
    }


def generate_listing(inp: ListingInput) -> bytes:
    """Canonical JSON bytes of the paper listing."""

    return json.dumps(
        generate_listing_json(inp),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def listing_fingerprint(inp: ListingInput) -> str:
    """SHA-256 of the canonical listing bytes (AC-9.2)."""

    return hashlib.sha256(generate_listing(inp)).hexdigest()


def validate_listing_bytes(data: bytes) -> dict[str, Any]:
    """Strict parse: BOM / duplicate keys / unknown fields / size cap (AC-9.4)."""

    if not isinstance(data, bytes):
        raise ListingValidationError("listing must be bytes")
    if len(data) > MAX_LISTING_BYTES:
        raise ListingValidationError(
            f"listing exceeds the {MAX_LISTING_BYTES}-byte size limit"
        )
    if data.startswith(b"\xef\xbb\xbf"):
        raise ListingValidationError("BOM is not allowed in canonical listing bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ListingValidationError(f"listing is not valid UTF-8: {exc}") from exc
    try:
        parsed = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        raise ListingValidationError(f"listing is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ListingValidationError("listing must be a JSON object")
    _check_keys(parsed, LISTING_KEYS, "listing")
    _check_depth(parsed)
    metadata = parsed.get("metadata")
    if not isinstance(metadata, dict):
        raise ListingValidationError("metadata must be an object")
    _check_keys(metadata, METADATA_KEYS, "metadata")
    spec = parsed.get("spec")
    if not isinstance(spec, dict):
        raise ListingValidationError("spec must be an object")
    _check_keys(spec, SPEC_KEYS, "spec")
    for section in ("capabilities", "tools", "policies", "plans"):
        if not isinstance(spec.get(section), list):
            raise ListingValidationError(f"spec.{section} must be a list")
    return parsed


def _check_depth(root: Any) -> None:
    """Iterative nesting-depth guard (AC-9.4 over-limit fail-closed).

    Uses an explicit stack so the guard itself cannot blow the interpreter
    stack on adversarial deep input; the walk is bounded by the 64 KiB
    size cap already enforced above.
    """

    stack: list[tuple[Any, int]] = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        if depth > MAX_LISTING_DEPTH:
            raise ListingValidationError(
                f"listing nesting exceeds depth limit {MAX_LISTING_DEPTH}"
            )
        if isinstance(node, dict):
            stack.extend((value, depth + 1) for value in node.values())
        elif isinstance(node, list):
            stack.extend((value, depth + 1) for value in node)


def _check_keys(mapping: dict[str, Any], allowed: frozenset[str], label: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ListingValidationError(
            f"unsupported {label} keys: " + ", ".join(unknown)
        )


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ListingValidationError(f"duplicate key in listing: {key!r}")
        out[key] = value
    return out


def render_yaml(listing_bytes: bytes) -> str:
    """Safe YAML subset rendering of the canonical listing (deterministic)."""

    parsed = validate_listing_bytes(listing_bytes)
    return _render(parsed, 0) + "\n"


def _render(value: Any, indent: int) -> str:
    pad = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.append(_render(item, indent + 1))
            else:
                lines.append(f"{pad}{key}: {_yaml_scalar(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_render(item, indent + 1))
            else:
                lines.append(f"{pad}- {_yaml_scalar(item)}")
        return "\n".join(lines)
    return pad + _yaml_scalar(value)


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    # Double-quoted JSON string is valid YAML; escapes embedded quotes safely.
    return json.dumps(str(value), ensure_ascii=False)
