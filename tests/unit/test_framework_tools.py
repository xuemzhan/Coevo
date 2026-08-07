"""US-16-AC-5: Tool abstraction and MCP schema path A tests (AC-5.1..5.5)."""

from __future__ import annotations

import ast
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from src.coevo.crypto.contract import ProviderScope
from src.coevo.framework.tools import (
    MAX_ENUM_ITEMS,
    MAX_SCHEMA_DEPTH,
    Tool,
    ToolRegistry,
    ToolSideEffect,
    ToolValidationError,
    canonical_descriptor_bytes,
    canonical_schema_bytes,
    mcp_to_tool,
    tool_to_mcp,
    validate_schema,
    validate_tool,
)

ROOT = Path(__file__).resolve().parents[2]


def make_tool(**overrides) -> Tool:
    base = Tool(
        tool_id="coevo.tools.cycle_check",
        tool_version="1.0.0",
        display_name="dependency cycle check",
        description="detect cycles in a dependency graph",
        side_effects=ToolSideEffect.PURE,
        requires_consent=False,
        timeout_sec=5,
        size_in_bytes_max=4096,
        crypto_scope=ProviderScope.MVP_PROTOTYPE,
        audit_required=True,
        input_schema={
            "type": "object",
            "properties": {
                "nodes": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["nodes"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "cycle": {"type": "boolean"},
            },
            "required": ["cycle"],
        },
    )
    return replace(base, **overrides)


class ToolTests(unittest.TestCase):
    def test_tool_model_and_version_required(self) -> None:
        """AC-5.1: Tool model; version is mandatory semver (P2)."""

        validate_tool(make_tool())
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(tool_version=""))
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(tool_version="1.0"))
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(tool_id="../escape"))
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(side_effects="pure"))  # type: ignore[arg-type]
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(timeout_sec=0))
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(timeout_sec=True))  # type: ignore[arg-type]
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(size_in_bytes_max=-1))
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(size_in_bytes_max=True))  # type: ignore[arg-type]
        with self.assertRaises(ToolValidationError):
            validate_tool(make_tool(crypto_scope="mvp-prototype"))  # type: ignore[arg-type]

    def test_registry_duplicate_and_fail_closed(self) -> None:
        """AC-5.2: duplicate rejected; validation gates registration."""

        registry = ToolRegistry()
        registry.register(make_tool())
        with self.assertRaises(ToolValidationError):
            registry.register(make_tool())
        self.assertEqual(len(registry.list()), 1)
        self.assertIsNotNone(registry.get("coevo.tools.cycle_check"))

        registry = ToolRegistry()
        with self.assertRaises(ToolValidationError):
            registry.register(make_tool(tool_version="bad"))
        self.assertEqual(registry.list(), ())

    def test_mcp_round_trip_identity(self) -> None:
        """AC-5.3: Tool ↔ MCP descriptor round-trips byte-identically."""

        tool = make_tool()
        descriptor = tool_to_mcp(tool)
        restored = mcp_to_tool(descriptor)
        self.assertEqual(restored, tool)
        self.assertEqual(
            canonical_descriptor_bytes(tool_to_mcp(restored)),
            canonical_descriptor_bytes(descriptor),
        )

    def test_mcp_missing_extension_rejected(self) -> None:
        descriptor = tool_to_mcp(make_tool())
        descriptor.pop("x-coevo")
        with self.assertRaises(ToolValidationError):
            mcp_to_tool(descriptor)

    def test_mcp_unknown_keys_rejected(self) -> None:
        descriptor = tool_to_mcp(make_tool())
        descriptor["bogus"] = 1
        with self.assertRaises(ToolValidationError):
            mcp_to_tool(descriptor)
        extension = descriptor["x-coevo"]
        assert isinstance(extension, dict)
        extension["bogus"] = 1
        with self.assertRaises(ToolValidationError):
            mcp_to_tool(descriptor)

    def test_schema_subset_validation(self) -> None:
        """AC-5.4: white-list subset; unknown/malformed/over-limit rejected."""

        validate_schema({"type": "string"})
        validate_schema(
            {
                "type": "object",
                "properties": {"a": {"type": "string"}},
                "required": ["a"],
            }
        )
        validate_schema(
            {"type": "array", "items": {"type": "integer"}, "description": "ids"}
        )
        validate_schema({"type": "string", "enum": ["a", "b"]})
        with self.assertRaises(ToolValidationError):
            validate_schema({"type": "unknown"})
        with self.assertRaises(ToolValidationError):
            validate_schema({})
        with self.assertRaises(ToolValidationError):
            validate_schema({"type": "string", "pattern": ".*"})
        with self.assertRaises(ToolValidationError):
            validate_schema({"type": "object"})
        with self.assertRaises(ToolValidationError):
            validate_schema(
                {
                    "type": "object",
                    "properties": {"a": {"type": "string"}},
                    "required": ["missing"],
                }
            )
        with self.assertRaises(ToolValidationError):
            validate_schema({"type": "array"})
        with self.assertRaises(ToolValidationError):
            validate_schema({"type": "string", "enum": []})
        with self.assertRaises(ToolValidationError):
            validate_schema({"type": "string", "enum": list(range(MAX_ENUM_ITEMS + 1))})

    def test_schema_depth_limit_rejected(self) -> None:
        schema: dict[str, object] = {"type": "string"}
        for _ in range(MAX_SCHEMA_DEPTH + 2):
            schema = {"type": "array", "items": schema}
        with self.assertRaises(ToolValidationError):
            validate_schema(schema)

    def test_schema_size_limit_rejected(self) -> None:
        schema = {"type": "string", "description": "x" * (MAX_ENUM_ITEMS * 300)}
        with self.assertRaises(ToolValidationError):
            validate_schema(schema)

    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "tools.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        allowed = set(sys.stdlib_module_names) | {"src"}
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] not in allowed:
                        bad.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    continue
                if node.module and node.module.split(".")[0] not in allowed:
                    bad.append(node.module)
        self.assertEqual([], bad, "third-party imports found in tools.py")


if __name__ == "__main__":
    unittest.main()
