"""US-16-AC-9: K8s CRD paper listing generator tests (AC-9.1..9.5)."""

from __future__ import annotations

import ast
import json
import sys
import unittest
from pathlib import Path

from src.coevo.crypto.contract import ProviderScope
from src.coevo.framework.capability import CAPABILITY_CLOSED_SET
from src.coevo.framework.k8s_listing import (
    MAX_LISTING_BYTES,
    MAX_LISTING_DEPTH,
    ListingInput,
    ListingValidationError,
    generate_listing,
    listing_fingerprint,
    render_yaml,
    validate_listing_bytes,
)
from src.coevo.framework.plan import Plan, PlanEdge, PlanNode, PlanNodeKind, plan_fingerprint
from src.coevo.framework.policy import default_profiles
from src.coevo.framework.tools import Tool, ToolSideEffect

ROOT = Path(__file__).resolve().parents[2]


def make_tool() -> Tool:
    return Tool(
        tool_id="coevo.tools.cycle_check",
        tool_version="1.0.0",
        display_name="dependency cycle check",
        description="detect cycles",
        side_effects=ToolSideEffect.PURE,
        requires_consent=False,
        timeout_sec=5,
        size_in_bytes_max=4096,
        crypto_scope=ProviderScope.MVP_PROTOTYPE,
        audit_required=True,
        input_schema={"type": "object", "properties": {"nodes": {"type": "array", "items": {"type": "string"}}}},
        output_schema={"type": "object", "properties": {"cycle": {"type": "boolean"}}},
    )


def make_plan() -> Plan:
    nodes = (
        PlanNode(node_id="n1", kind=PlanNodeKind.AGENT, agent_capability="task_decomposition"),
        PlanNode(node_id="n2", kind=PlanNodeKind.HUMAN_GATE, human_gate_reason="approve", requires_human_confirmation=True),
    )
    plan = Plan(
        plan_id="0" * 64,
        plan_version="1.0",
        policy_profile="INTERACTIVE",
        policy_version="1.0",
        nodes=nodes,
        edges=(PlanEdge("n1", "n2"),),
    )
    return Plan(
        plan_id=plan_fingerprint(plan),
        plan_version=plan.plan_version,
        policy_profile=plan.policy_profile,
        policy_version=plan.policy_version,
        nodes=plan.nodes,
        edges=plan.edges,
    )


def make_input(**overrides) -> ListingInput:
    return ListingInput(
        capabilities=overrides.get("capabilities", CAPABILITY_CLOSED_SET[:3]),
        tools=overrides.get("tools", (make_tool(),)),
        policies=overrides.get("policies", default_profiles()[:1]),
        plans=overrides.get("plans", (make_plan(),)),
        generated_at=overrides.get("generated_at", "2026-08-08T08:00:00Z"),
    )


class K8sListingTests(unittest.TestCase):
    def test_listing_generation_and_yaml(self) -> None:
        """AC-9.1: deterministic listing JSON + safe YAML rendering."""

        listing = generate_listing(make_input())
        parsed = validate_listing_bytes(listing)
        self.assertEqual(parsed["kind"], "DeclarativeListing")
        self.assertEqual(parsed["apiVersion"], "coevo.framework/v1")
        spec = parsed["spec"]
        self.assertEqual(len(spec["capabilities"]), 3)
        self.assertEqual(len(spec["tools"]), 1)
        self.assertEqual(len(spec["policies"]), 1)
        self.assertEqual(len(spec["plans"]), 1)
        yaml_text = render_yaml(listing)
        self.assertIn("apiVersion: \"coevo.framework/v1\"", yaml_text)
        self.assertIn("kind: \"DeclarativeListing\"", yaml_text)
        self.assertIn('name: "TASK_FLOW_UNDERSTANDING"', yaml_text)
        # Deterministic rendering.
        self.assertEqual(render_yaml(listing), render_yaml(generate_listing(make_input())))

    def test_listing_deterministic_hash(self) -> None:
        """AC-9.2: same input → same bytes/fingerprint; change → different."""

        inp = make_input()
        self.assertEqual(generate_listing(inp), generate_listing(inp))
        self.assertEqual(listing_fingerprint(inp), listing_fingerprint(inp))
        changed = make_input(generated_at="2026-08-08T09:00:00Z")
        self.assertNotEqual(listing_fingerprint(inp), listing_fingerprint(changed))

    def test_listing_empty_input(self) -> None:
        listing = generate_listing(make_input(capabilities=(), tools=(), policies=(), plans=()))
        parsed = validate_listing_bytes(listing)
        self.assertEqual(parsed["spec"]["capabilities"], [])

    def test_audit_projection(self) -> None:
        """AC-9.5: audit projection is fixed-key and excludes spec details."""

        inp = make_input()
        rec = inp.to_audit_record()
        self.assertEqual(rec["kind"], "DeclarativeListing")
        self.assertEqual(rec["schema_version"], "1.0")
        self.assertEqual(rec["generated_at"], "2026-08-08T08:00:00Z")
        self.assertEqual(rec["capability_count"], 3)
        self.assertEqual(rec["tool_count"], 1)
        self.assertEqual(rec["policy_count"], 1)
        self.assertEqual(rec["plan_count"], 1)
        self.assertEqual(rec["listing_fingerprint"], listing_fingerprint(inp))
        for section in ("capabilities", "tools", "policies", "plans"):
            self.assertNotIn(section, rec)

    def test_listing_validation(self) -> None:
        """AC-9.4: duplicate keys / unknown fields / BOM / size cap rejected."""

        listing = generate_listing(make_input())
        with self.assertRaises(ListingValidationError):
            validate_listing_bytes(b"\xef\xbb\xbf" + listing)
        with self.assertRaises(ListingValidationError):
            validate_listing_bytes(b'{"apiVersion":"x","kind":"y","metadata":{},"spec":{},"extra":1}')
        with self.assertRaises(ListingValidationError):
            validate_listing_bytes(b'{"apiVersion":"x","kind":"y","metadata":{},"spec":{"bogus":[]}}')
        with self.assertRaises(ListingValidationError):
            validate_listing_bytes(b'{"apiVersion":"x","apiVersion":"z","kind":"y","metadata":{},"spec":{}}')
        with self.assertRaises(ListingValidationError):
            validate_listing_bytes(b" " * (MAX_LISTING_BYTES + 1))
        with self.assertRaises(ListingValidationError):
            validate_listing_bytes(b"not json")

    def test_listing_deep_nesting_rejected(self) -> None:
        """AC-9.4: over-depth nesting fails closed instead of crashing render."""

        base = {
            "apiVersion": "a",
            "kind": "b",
            "metadata": {"schema_version": "1.0", "generated_at": "x"},
            "spec": {"capabilities": [0], "tools": [], "policies": [], "plans": []},
        }
        deep = 0
        for _ in range(MAX_LISTING_DEPTH + 50):
            deep = {"x": deep}
        payload = json.dumps(base, separators=(",", ":")).replace(
            "[0]", "[" + json.dumps(deep, separators=(",", ":")) + "]"
        ).encode("utf-8")
        self.assertLess(len(payload), MAX_LISTING_BYTES)
        with self.assertRaises(ListingValidationError):
            validate_listing_bytes(payload)

    def test_yaml_quotes_safely(self) -> None:
        """Strings with special characters stay safely quoted in YAML."""

        tool = make_tool()
        tool = Tool(
            tool_id=tool.tool_id,
            tool_version=tool.tool_version,
            display_name=tool.display_name,
            description='quote " and colon : and # hash',
            side_effects=tool.side_effects,
            requires_consent=tool.requires_consent,
            timeout_sec=tool.timeout_sec,
            size_in_bytes_max=tool.size_in_bytes_max,
            crypto_scope=tool.crypto_scope,
            audit_required=tool.audit_required,
            input_schema=tool.input_schema,
            output_schema=tool.output_schema,
        )
        yaml_text = render_yaml(generate_listing(make_input(tools=(tool,))))
        self.assertIn('\\"', yaml_text)

    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "k8s_listing.py").read_text(
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
        self.assertEqual([], bad, "third-party imports found in k8s_listing.py")

    def test_listing_no_io_side_effects(self) -> None:
        """AC-9.3: generator has zero IO imports (pure function, offline)."""

        source = (ROOT / "src" / "coevo" / "framework" / "k8s_listing.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        io_modules = {
            "os",
            "io",
            "sys",
            "subprocess",
            "socket",
            "urllib",
            "http",
            "shutil",
            "tempfile",
            "pathlib",
            "ctypes",
            "select",
            "signal",
            "threading",
            "multiprocessing",
            "mmap",
        }
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    continue
                if node.module:
                    imported.add(node.module.split(".")[0])
        self.assertEqual(
            set(),
            imported & io_modules,
            "IO-capable imports found in k8s_listing.py",
        )


if __name__ == "__main__":
    unittest.main()
