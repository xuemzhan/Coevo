"""FRAMEWORK-INTEGRATION-3: pipeline wiring precondition tests."""

from __future__ import annotations

import unittest

from src.coevo.framework.integration import validate_product_chain
from src.coevo.framework.policy import get_default_profile
from src.coevo.orchestrator.models import (
    MVP_FIXED_CHAIN,
    AgentCapability,
    AgentRegistration,
    AgentRegistry,
    AgentSpec,
)


class _AllowAll:
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: object, actor: str) -> bool:
        return True


def pipeline_registry() -> AgentRegistry:
    registry = AgentRegistry.empty()
    for agent_id, capability in (
        ("agent.task_flow_understanding", AgentCapability.TASK_FLOW_UNDERSTANDING),
        ("agent.task_decomposition", AgentCapability.TASK_DECOMPOSITION),
        ("agent.team_recommendation", AgentCapability.TEAM_RECOMMENDATION),
        ("agent.task_package_build", AgentCapability.TASK_PACKAGE_BUILD),
    ):
        registry = registry.register(
            AgentRegistration(
                AgentSpec(
                    agent_id,
                    capability,
                    capability.value,
                    ("input",),
                    ("output",),
                )
            )
        )
    return registry


class PipelineGateTests(unittest.TestCase):
    def test_mvp_fixed_chain_passes_framework_gate(self) -> None:
        """FRAMEWORK-INTEGRATION-3: the product fixed chain lifts and validates."""

        result = validate_product_chain(
            MVP_FIXED_CHAIN,
            pipeline_registry(),
            get_default_profile("INTERACTIVE"),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="demo.actor",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertTrue(result.accepted, result.failure_reason)

    def test_missing_agent_rejected(self) -> None:
        """A chain referencing an unregistered agent must fail the gate."""

        registry = pipeline_registry()
        registry = AgentRegistry(
            _by_id=tuple(
                r
                for r in registry._by_id  # noqa: SLF001 - test-only inspection
                if r.spec.agent_id != "agent.task_package_build"
            )
        )
        result = validate_product_chain(
            MVP_FIXED_CHAIN,
            registry,
            get_default_profile("INTERACTIVE"),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="demo.actor",
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertFalse(result.accepted)
        self.assertIn("not registered", result.failure_reason or "")


if __name__ == "__main__":
    unittest.main()
