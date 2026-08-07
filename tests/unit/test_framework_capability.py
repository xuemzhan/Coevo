"""US-16-AC-3: framework capability closed-set convergence tests (M1b)."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

from src.coevo.framework.capability import (
    CAPABILITY_CLOSED_SET,
    CapabilityKind,
    CapabilityValidationError,
    capability_entry,
    check_consistency,
    consistency_report,
    orphan_agent_capabilities,
    resolve_capability,
    unmapped_mvp_capabilities,
)
from src.coevo.orchestrator.models import AgentCapability

ROOT = Path(__file__).resolve().parents[2]

CTAF_NAMES = {
    "TASK_FLOW_UNDERSTANDING",
    "TASK_DECOMPOSITION",
    "TEAM_RECOMMENDATION",
    "TASK_PACKAGE_BUILD",
    "RISK_ANALYSIS",
    "DECISION_BRIEF",
    "KNOWLEDGE_INGEST",
    "SUPERVISION",
    "AUDIT_INTERCEPT",
    "PROGRESS_CAPTURE",
    "REPORT_BUILD",
    "MERGE_ENGINE",
    "CRYPTO_PROXY",
    "PLANNER",
    "ROUTER",
    "AGGREGATOR",
    "EVALUATOR",
    "OPTIMIZER",
    "HUMAN_GATE",
}


class CapabilityClosedSetTests(unittest.TestCase):
    def test_registry_covers_ctaf_closed_set(self) -> None:
        names = {item.canonical_name for item in CAPABILITY_CLOSED_SET}
        self.assertEqual(names, CTAF_NAMES)

    def test_mvp_entries_map_to_agent_capability(self) -> None:
        expected = {
            "TASK_FLOW_UNDERSTANDING": AgentCapability.TASK_FLOW_UNDERSTANDING,
            "TASK_DECOMPOSITION": AgentCapability.TASK_DECOMPOSITION,
            "TEAM_RECOMMENDATION": AgentCapability.TEAM_RECOMMENDATION,
            "KNOWLEDGE_INGEST": AgentCapability.KNOWLEDGE_INGEST,
            "TASK_PACKAGE_BUILD": AgentCapability.TASK_PACKAGE_BUILD,
            "PROGRESS_CAPTURE": AgentCapability.PROGRESS_CAPTURE,
            "RISK_ANALYSIS": AgentCapability.RISK_ANALYSIS,
            "DECISION_BRIEF": AgentCapability.DECISION_BRIEF,
            "SUPERVISION": AgentCapability.SUPERVISION_MEETING,
            "AUDIT_INTERCEPT": AgentCapability.AUDIT_GOVERNANCE,
            "REPORT_BUILD": AgentCapability.REPORT_BUILD,
            "MERGE_ENGINE": AgentCapability.STATE_MERGE,
        }
        for name, capability in expected.items():
            entry = resolve_capability(name)
            self.assertEqual(entry.agent_capability, capability, name)

    def test_dual_name_resolution(self) -> None:
        by_value = resolve_capability("task_decomposition")
        by_ctaf = resolve_capability("TASK_DECOMPOSITION")
        self.assertIs(by_value, by_ctaf)
        self.assertEqual(by_value.canonical_name, "TASK_DECOMPOSITION")
        # Enum member name also resolves (dual-name).
        self.assertIs(resolve_capability("STATE_MERGE"), resolve_capability("MERGE_ENGINE"))
        self.assertIs(
            resolve_capability("SUPERVISION_MEETING"),
            resolve_capability("SUPERVISION"),
        )

    def test_unknown_and_case_variant_rejected(self) -> None:
        for bad in ("not_a_capability", "Task_Decomposition", "task_decomposition ", ""):
            with self.assertRaises(CapabilityValidationError):
                resolve_capability(bad)
        self.assertIsNone(capability_entry("not_a_capability"))
        self.assertIsNone(capability_entry(None))  # type: ignore[arg-type]

    def test_framework_abstracts_registered(self) -> None:
        for name in ("PLANNER", "ROUTER", "AGGREGATOR", "EVALUATOR", "OPTIMIZER", "HUMAN_GATE"):
            entry = resolve_capability(name)
            self.assertEqual(entry.kind, CapabilityKind.FRAMEWORK_ABSTRACT, name)
            self.assertIsNone(entry.agent_capability)

    def test_crypto_proxy_requires_approved_product(self) -> None:
        entry = resolve_capability("CRYPTO_PROXY")
        self.assertEqual(entry.kind, CapabilityKind.CRYPTO_PROXY)
        self.assertTrue(entry.requires_approved_product)

    def test_bidirectional_consistency(self) -> None:
        """AC-3.4: no orphans, no unmapped MVP names."""

        self.assertEqual(orphan_agent_capabilities(), [])
        self.assertEqual(unmapped_mvp_capabilities(), [])
        report = consistency_report()
        self.assertEqual(report["orphan_agent_capabilities"], [])
        self.assertEqual(report["unmapped_mvp_capabilities"], [])
        check_consistency()  # must not raise
        for capability in AgentCapability:
            self.assertIsNotNone(capability_entry(capability.value))

    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "capability.py").read_text(
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
        self.assertEqual([], bad, "third-party imports found in capability.py")


if __name__ == "__main__":
    unittest.main()
