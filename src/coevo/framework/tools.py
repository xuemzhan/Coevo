"""US-16-AC-5: Tool abstraction and MCP schema path A (CTAF §6.3 / §7.2 / M4).

A :class:`Tool` is the framework's canonical tool declaration.  MCP path A
("schema alignment only", zero third-party dependencies) is implemented as a
deterministic bidirectional conversion between the framework ``Tool`` and an
MCP-style tool descriptor:

* standard MCP fields (``name`` / ``description`` / ``inputSchema`` /
  ``outputSchema``) are directly mapped;
* framework-only fields travel in an ``x-coevo`` extension block so a plain
  MCP consumer can read the shared subset while the framework round-trips the
  full declaration (AC-5.3);
* the JSON Schema subset is a strict white-list (type / properties / required
  / items / enum / description): unknown keywords, malformed structures and
  over-limit inputs are rejected, never silently dropped (AC-5.4).

L15: standard library only — no MCP SDK.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.coevo.crypto.contract import ProviderScope

from src.coevo.ids import SAFE_ID as _SAFE_ID
_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

SCHEMA_TYPES = frozenset({"string", "number", "integer", "boolean", "object", "array"})
SCHEMA_KEYS = frozenset({"type", "properties", "required", "items", "enum", "description"})
MCP_KEYS = frozenset({"name", "description", "inputSchema", "outputSchema", "x-coevo"})
X_COEVO_KEYS = frozenset(
    {
        "tool_version",
        "display_name",
        "side_effects",
        "requires_consent",
        "timeout_sec",
        "size_in_bytes_max",
        "crypto_scope",
        "audit_required",
    }
)

MAX_SCHEMA_BYTES = 16 * 1024
MAX_SCHEMA_DEPTH = 16
MAX_ENUM_ITEMS = 64
MAX_TOOL_ITEMS = 128


class ToolValidationError(Exception):
    """Raised when a Tool or schema violates the framework invariants."""


class ToolSideEffect(Enum):
    """CTAF §6.3 side-effect classification."""

    PURE = "pure"
    IDEMPOTENT = "idempotent"
    EXTERNAL = "external"


@dataclass(frozen=True)
class Tool:
    """Canonical tool declaration (CTAF §6.3)."""

    tool_id: str
    tool_version: str  # semver, P2 mandatory
    display_name: str
    description: str
    side_effects: ToolSideEffect
    requires_consent: bool
    timeout_sec: int
    size_in_bytes_max: int
    crypto_scope: ProviderScope
    audit_required: bool
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


@dataclass
class ToolRegistry:
    """In-memory tool registry; registration is validation-gated."""

    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        validate_tool(tool)  # validation and registration are separated
        if tool.tool_id in self._tools:
            raise ToolValidationError(f"tool already registered: {tool.tool_id}")
        if len(self._tools) >= MAX_TOOL_ITEMS:
            raise ToolValidationError(f"tool registry exceeds {MAX_TOOL_ITEMS} entries")
        self._tools[tool.tool_id] = tool

    def get(self, tool_id: str) -> Tool | None:
        return self._tools.get(tool_id)

    def list(self) -> tuple[Tool, ...]:
        return tuple(self._tools.values())


def validate_schema(schema: Any, *, depth: int = 0) -> None:
    """Validate the JSON Schema subset (pure, fail-closed)."""

    if not isinstance(schema, dict):
        raise ToolValidationError("schema must be a JSON object")
    if depth > MAX_SCHEMA_DEPTH:
        raise ToolValidationError(f"schema exceeds the {MAX_SCHEMA_DEPTH}-level depth limit")
    unknown = sorted(set(schema) - SCHEMA_KEYS)
    if unknown:
        raise ToolValidationError(
            "unsupported schema keywords: " + ", ".join(unknown)
        )
    schema_type = schema.get("type")
    if schema_type not in SCHEMA_TYPES:
        raise ToolValidationError(
            f"schema type must be one of {sorted(SCHEMA_TYPES)}; got {schema_type!r}"
        )
    if "description" in schema and not isinstance(schema["description"], str):
        raise ToolValidationError("schema description must be a string")
    if schema_type == "object":
        properties = schema.get("properties")
        if not isinstance(properties, dict):
            raise ToolValidationError("object schema requires a properties object")
        required = schema.get("required", [])
        if not isinstance(required, list) or not all(
            isinstance(item, str) for item in required
        ):
            raise ToolValidationError("required must be a list of strings")
        if not set(required) <= set(properties):
            raise ToolValidationError("required references a missing property")
        for property_schema in properties.values():
            validate_schema(property_schema, depth=depth + 1)
    elif schema_type == "array":
        if "items" not in schema:
            raise ToolValidationError("array schema requires items")
        validate_schema(schema["items"], depth=depth + 1)
    if "enum" in schema:
        enum = schema["enum"]
        if not isinstance(enum, list) or not 1 <= len(enum) <= MAX_ENUM_ITEMS:
            raise ToolValidationError(
                f"enum must be a non-empty list within {MAX_ENUM_ITEMS} items"
            )
    if len(canonical_schema_bytes(schema)) > MAX_SCHEMA_BYTES:
        raise ToolValidationError(f"schema exceeds the {MAX_SCHEMA_BYTES}-byte size limit")


def canonical_schema_bytes(schema: dict[str, Any]) -> bytes:
    return json.dumps(
        schema, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def validate_tool(tool: Tool) -> None:
    """Validate a Tool declaration (pure, fail-closed)."""

    if not isinstance(tool, Tool):
        raise ToolValidationError("tool must be a Tool instance")
    if not _SAFE_ID.match(tool.tool_id):
        raise ToolValidationError(f"tool_id must be a safe-id: {tool.tool_id!r}")
    if not _SEMVER.match(tool.tool_version):
        raise ToolValidationError(
            f"tool_version must be semver (P2): {tool.tool_version!r}"
        )
    if not tool.display_name:
        raise ToolValidationError("display_name is required")
    if not isinstance(tool.description, str):
        raise ToolValidationError("description must be a string")
    if not isinstance(tool.side_effects, ToolSideEffect):
        raise ToolValidationError("side_effects must be a ToolSideEffect member")
    if not isinstance(tool.requires_consent, bool):
        raise ToolValidationError("requires_consent must be bool")
    if type(tool.timeout_sec) is not int or tool.timeout_sec <= 0:
        raise ToolValidationError("timeout_sec must be a positive integer")
    if type(tool.size_in_bytes_max) is not int or tool.size_in_bytes_max < 0:
        raise ToolValidationError("size_in_bytes_max must be a non-negative integer")
    if not isinstance(tool.crypto_scope, ProviderScope):
        raise ToolValidationError("crypto_scope must be a ProviderScope member")
    if not isinstance(tool.audit_required, bool):
        raise ToolValidationError("audit_required must be bool")
    validate_schema(tool.input_schema)
    validate_schema(tool.output_schema)


def tool_to_mcp(tool: Tool) -> dict[str, Any]:
    """Framework Tool → MCP-style tool descriptor (path A)."""

    validate_tool(tool)
    return {
        "name": tool.tool_id,
        "description": tool.description,
        "inputSchema": tool.input_schema,
        "outputSchema": tool.output_schema,
        "x-coevo": {
            "tool_version": tool.tool_version,
            "display_name": tool.display_name,
            "side_effects": tool.side_effects.value,
            "requires_consent": tool.requires_consent,
            "timeout_sec": tool.timeout_sec,
            "size_in_bytes_max": tool.size_in_bytes_max,
            "crypto_scope": tool.crypto_scope.value,
            "audit_required": tool.audit_required,
        },
    }


def mcp_to_tool(descriptor: dict[str, Any]) -> Tool:
    """MCP-style tool descriptor → framework Tool (fail-closed)."""

    if not isinstance(descriptor, dict):
        raise ToolValidationError("MCP descriptor must be a JSON object")
    unknown = sorted(set(descriptor) - MCP_KEYS)
    if unknown:
        raise ToolValidationError(
            "unsupported MCP descriptor keys: " + ", ".join(unknown)
        )
    name = descriptor.get("name")
    if not isinstance(name, str) or not _SAFE_ID.match(name):
        raise ToolValidationError("MCP descriptor name must be a safe-id")
    description = descriptor.get("description", "")
    if not isinstance(description, str):
        raise ToolValidationError("MCP descriptor description must be a string")
    input_schema = descriptor.get("inputSchema")
    output_schema = descriptor.get("outputSchema")
    if not isinstance(input_schema, dict) or not isinstance(output_schema, dict):
        raise ToolValidationError("inputSchema and outputSchema must be objects")
    extension = descriptor.get("x-coevo")
    if not isinstance(extension, dict):
        raise ToolValidationError(
            "MCP descriptor requires the x-coevo extension block for full fidelity"
        )
    unknown_ext = sorted(set(extension) - X_COEVO_KEYS)
    if unknown_ext:
        raise ToolValidationError(
            "unsupported x-coevo keys: " + ", ".join(unknown_ext)
        )
    try:
        tool = Tool(
            tool_id=name,
            tool_version=extension["tool_version"],
            display_name=extension["display_name"],
            description=description,
            side_effects=ToolSideEffect(extension["side_effects"]),
            requires_consent=extension["requires_consent"],
            timeout_sec=extension["timeout_sec"],
            size_in_bytes_max=extension["size_in_bytes_max"],
            crypto_scope=ProviderScope(extension["crypto_scope"]),
            audit_required=extension["audit_required"],
            input_schema=input_schema,
            output_schema=output_schema,
        )
    except (KeyError, ValueError) as exc:
        raise ToolValidationError(f"malformed x-coevo extension: {exc}") from exc
    validate_tool(tool)
    return tool


def canonical_descriptor_bytes(descriptor: dict[str, Any]) -> bytes:
    return json.dumps(
        descriptor, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
