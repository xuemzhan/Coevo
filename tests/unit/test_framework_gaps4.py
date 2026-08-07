"""FRAMEWORK-GAPS-4: shared L7 validator + exception-branch coverage."""

from __future__ import annotations

import unittest

from src.coevo.framework.integration import validate_product_chain
from src.coevo.framework.policy import get_default_profile
from src.coevo.framework.validation import is_iso_utc_z
from src.coevo.orchestrator.models import (
    MVP_FIXED_CHAIN,
    AgentCapability,
    AgentRegistration,
    AgentRegistry,
    AgentSpec,
    FailurePolicy,
    OrchestrationChain,
    OrchestrationStep,
    OrchestrationStepKind,
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
                AgentSpec(agent_id, capability, capability.value, ("input",), ("output",))
            )
        )
    return registry


def broken_chain() -> OrchestrationChain:
    return OrchestrationChain(
        chain_id="demo.broken",
        steps=(
            OrchestrationStep(
                step_index=0,
                kind=OrchestrationStepKind.AGENT_CALL,
                agent_id="agent.missing",
                on_failure=FailurePolicy.ESCALATE_HUMAN,
            ),
        ),
    )


class SharedIsoTests(unittest.TestCase):
    def test_is_iso_utc_z_shared(self) -> None:
        """FRAMEWORK-GAPS-4: one canonical L7 validator."""

        for ok in (
            "2026-08-08T08:00:00Z",
            "2026-08-08T08:00:00.123456Z",
        ):
            self.assertTrue(is_iso_utc_z(ok), ok)
        for bad in (
            "",
            "2026-08-08 08:00:00Z",
            "2026-99-99T99:99:99Z",
            "2026-02-30T00:00:00Z",
            "2026-08-08T08:00:00",
            "2026-08-08T08:00:00Z\n",
        ):
            self.assertFalse(is_iso_utc_z(bad), bad)

    def test_validate_product_chain_non_iso_rejected_everywhere(self) -> None:
        """INTEGRATION-3 Low closure: L7 applies on every returned result."""

        for chain, registry in (
            (MVP_FIXED_CHAIN, pipeline_registry()),
            (broken_chain(), pipeline_registry()),  # lift would fail too
        ):
            result = validate_product_chain(
                chain,
                registry,
                get_default_profile("INTERACTIVE"),
                scope_checker=_AllowAll(),
                rbac_checker=_AllowAll(),
                actor="demo.actor",
                validated_at="2026-08-08 08:00:00Z",  # not strict ISO
            )
            self.assertFalse(result.accepted)
            self.assertIn("validated_at", result.failure_reason or "")


if __name__ == "__main__":
    unittest.main()
