"""ARCH-REVIEW-4: professional sub-agent manifest catalog guard tests.

Contract (docs/architecture/agent-manifest-registry.md): the seven
professional sub-agents have a design-time manifest catalog whose
capabilities come from the framework closed set (MVP-executable), whose
service modules import, and whose human-confirmation points are non-empty.
Runtime registration still goes through guard_registration.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.framework.agent_catalog import (
    PROFESSIONAL_AGENT_CATALOG,
    validate_catalog,
)
from src.coevo.orchestrator.models import AgentCapability

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_CAPABILITIES = {
    AgentCapability.TASK_FLOW_UNDERSTANDING,
    AgentCapability.TASK_DECOMPOSITION,
    AgentCapability.PROGRESS_CAPTURE,
    AgentCapability.RISK_ANALYSIS,
    AgentCapability.SUPERVISION_MEETING,
    AgentCapability.DECISION_BRIEF,
    AgentCapability.KNOWLEDGE_INGEST,
}


class AgentManifestRegistryTests(unittest.TestCase):
    def test_catalog_has_exactly_seven_professional_agents(self) -> None:
        self.assertEqual(len(PROFESSIONAL_AGENT_CATALOG), 7)
        self.assertEqual(
            {entry.capability for entry in PROFESSIONAL_AGENT_CATALOG},
            EXPECTED_CAPABILITIES,
        )

    def test_catalog_validates_clean(self) -> None:
        violations = validate_catalog()
        self.assertEqual([], violations, violations)

    def test_each_entry_has_confirmation_and_binding(self) -> None:
        for entry in PROFESSIONAL_AGENT_CATALOG:
            self.assertTrue(entry.human_confirmation_points, entry.agent_id)
            self.assertIn(entry.model_binding, ("rule", "model", "hybrid"))
            self.assertIn(entry.tool_policy, ("read-only", "none", "guarded-write"))

    def test_doc_exists(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "agent-manifest-registry.md"
        ).read_text(encoding="utf-8")
        self.assertIn("guard_registration", text)
        self.assertIn("model_binding", text)
        self.assertIn("agent.flow_understanding", text)


if __name__ == "__main__":
    unittest.main()
