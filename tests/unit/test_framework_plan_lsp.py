"""US-16-AC-7: Plan serialization (Plan-LSP) tests (AC-7.1..7.5)."""

from __future__ import annotations

import ast
import json
import sys
import unittest
from pathlib import Path

from src.coevo.framework.plan import (
    MAX_PLAN_JSON_BYTES,
    Plan,
    PlanEdge,
    PlanNode,
    PlanNodeKind,
    PlanValidationError,
    json_to_plan,
    parse_plan_json_bytes,
    plan_fingerprint,
    plan_to_json,
)
from src.coevo.framework.policy import get_default_profile
from src.coevo.framework.validation import validate_plan_json

ROOT = Path(__file__).resolve().parents[2]


class _AllowAll:
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: Plan, actor: str) -> bool:
        return True


def make_plan() -> Plan:
    nodes = (
        PlanNode(
            node_id="n1",
            kind=PlanNodeKind.AGENT,
            agent_capability="task_decomposition",
            requires_human_confirmation=True,
        ),
        PlanNode(
            node_id="n2",
            kind=PlanNodeKind.TOOL,
            tool_ref="coevo.tools.cycle_check",
            tool_args=(("max_nodes", 100),),
        ),
        PlanNode(
            node_id="n3",
            kind=PlanNodeKind.HUMAN_GATE,
            human_gate_reason="approve result",
            requires_human_confirmation=True,
            confirmation_role="project_owner",
        ),
    )
    edges = (PlanEdge("n1", "n2"), PlanEdge("n2", "n3"))
    plan = Plan(
        plan_id="0" * 64,
        plan_version="1.0",
        policy_profile="INTERACTIVE",
        policy_version="1.0",
        nodes=nodes,
        edges=edges,
    )
    return Plan(
        plan_id=plan_fingerprint(plan),
        plan_version=plan.plan_version,
        policy_profile=plan.policy_profile,
        policy_version=plan.policy_version,
        nodes=plan.nodes,
        edges=plan.edges,
    )


def plan_json_bytes(plan: Plan) -> bytes:
    return json.dumps(
        plan_to_json(plan), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


class PlanLspTests(unittest.TestCase):
    def test_plan_json_round_trip_identity(self) -> None:
        """AC-7.1: Plan ↔ JSON round-trips with byte identity."""

        plan = make_plan()
        restored = json_to_plan(plan_to_json(plan))
        self.assertEqual(restored, plan)
        self.assertEqual(
            plan_json_bytes(restored),
            plan_json_bytes(plan),
        )
        parsed = parse_plan_json_bytes(plan_json_bytes(plan))
        self.assertEqual(parsed, plan)

    def test_fingerprint_consistency(self) -> None:
        """AC-7.2: serialization shares plan_fingerprint's canonical rule."""

        plan = make_plan()
        self.assertEqual(json_to_plan(plan_to_json(plan)).plan_id, plan.plan_id)
        self.assertEqual(plan_fingerprint(plan), plan.plan_id)

    def test_duplicate_keys_rejected(self) -> None:
        payload = b'{"plan_id":"0","nodes":[],"nodes":[]}'
        with self.assertRaises(PlanValidationError):
            parse_plan_json_bytes(payload)

    def test_unknown_fields_rejected(self) -> None:
        mapping = plan_to_json(make_plan())
        mapping["bogus"] = 1
        with self.assertRaises(PlanValidationError):
            json_to_plan(mapping)
        nodes = mapping["nodes"]
        assert isinstance(nodes, list)
        nodes[0]["bogus"] = 1
        with self.assertRaises(PlanValidationError):
            json_to_plan(mapping)

    def test_bad_kind_rejected(self) -> None:
        mapping = plan_to_json(make_plan())
        nodes = mapping["nodes"]
        assert isinstance(nodes, list)
        nodes[0]["kind"] = "BOGUS"
        with self.assertRaises(PlanValidationError):
            json_to_plan(mapping)

    def test_bad_tool_args_shape_rejected(self) -> None:
        mapping = plan_to_json(make_plan())
        nodes = mapping["nodes"]
        assert isinstance(nodes, list)
        nodes[1]["tool_args"] = [["max_nodes"]]  # not a [key, value] pair
        with self.assertRaises(PlanValidationError):
            json_to_plan(mapping)

    def test_bom_rejected(self) -> None:
        with self.assertRaises(PlanValidationError):
            parse_plan_json_bytes(b"\xef\xbb\xbf" + plan_json_bytes(make_plan()))

    def test_size_limit_rejected(self) -> None:
        mapping = plan_to_json(make_plan())
        nodes = mapping["nodes"]
        assert isinstance(nodes, list)
        nodes[1]["tool_args"] = [["padding", "x" * (MAX_PLAN_JSON_BYTES + 1)]]
        payload = json.dumps(
            mapping, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        self.assertGreater(len(payload), MAX_PLAN_JSON_BYTES)
        with self.assertRaises(PlanValidationError):
            parse_plan_json_bytes(payload)

    def test_validate_plan_json_entry(self) -> None:
        """AC-7.3: serialized entry validates five invariants + L18 + L19."""

        result = validate_plan_json(
            plan_json_bytes(make_plan()),
            get_default_profile("INTERACTIVE"),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertTrue(result.accepted, result.failure_reason)
        # Cycle via JSON is rejected (rebuild with a valid fingerprint so the
        # cycle check is the failure, not the hash check).
        base = make_plan()
        cyclic = Plan(
            plan_id="0" * 64,
            plan_version=base.plan_version,
            policy_profile=base.policy_profile,
            policy_version=base.policy_version,
            nodes=base.nodes,
            edges=(PlanEdge("n1", "n2"), PlanEdge("n2", "n1")),
        )
        cyclic = Plan(
            plan_id=plan_fingerprint(cyclic),
            plan_version=cyclic.plan_version,
            policy_profile=cyclic.policy_profile,
            policy_version=cyclic.policy_version,
            nodes=cyclic.nodes,
            edges=cyclic.edges,
        )
        payload = plan_json_bytes(cyclic)
        result = validate_plan_json(
            payload,
            get_default_profile("INTERACTIVE"),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertFalse(result.accepted)
        self.assertIn("cycle", result.failure_reason or "")
        # Malformed JSON bytes → REJECTED result (not an exception).
        result = validate_plan_json(
            b"{bad json",
            get_default_profile("INTERACTIVE"),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
        )
        self.assertFalse(result.accepted)

    def test_l18_key_in_serialized_tool_args_rejected(self) -> None:
        mapping = plan_to_json(make_plan())
        nodes = mapping["nodes"]
        assert isinstance(nodes, list)
        nodes[1]["tool_args"] = [["max_recover_attempts", 5]]
        with self.assertRaises(PlanValidationError):
            json_to_plan(mapping)

    def test_module_imports_stdlib_only(self) -> None:
        for name in ("plan.py", "validation.py"):
            source = (ROOT / "src" / "coevo" / "framework" / name).read_text(
                encoding="utf-8"
            )
            tree = ast.parse(source)
            allowed = set(sys.stdlib_module_names) | {"src"}
            bad: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".")[0] not in allowed:
                            bad.append(f"{name}: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.level > 0:
                        continue
                    if node.module and node.module.split(".")[0] not in allowed:
                        bad.append(f"{name}: {node.module}")
            self.assertEqual([], bad, f"third-party imports found in {name}")


if __name__ == "__main__":
    unittest.main()
