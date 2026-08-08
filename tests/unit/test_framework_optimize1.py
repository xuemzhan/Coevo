"""FRAMEWORK-OPTIMIZE-1: framework-driven optimization of the product code."""

from __future__ import annotations

import hashlib
import json
import unittest

from src.coevo.app.demo_support import (
    DemoRegistrationResolver,
    DemoRegistrationSigner,
    register_demo_agents,
)
from src.coevo.framework.integration import (
    build_registration_manifest,
    chain_to_plan,
)
from src.coevo.framework.manifest_checker import manifest_spec_hash
from src.coevo.framework.plan import Plan, plan_fingerprint
from src.coevo.framework.policy import get_default_profile
from src.coevo.orchestrator import MVP_FIXED_CHAIN, AgentRegistry
from src.coevo.orchestrator.models import (
    AgentCapability,
    AgentRegistration,
    AgentSpec,
)


def _registration(
    agent_id: str, capability: AgentCapability
) -> AgentRegistration:
    return AgentRegistration(
        AgentSpec(agent_id, capability, capability.value, ("input",), ("output",))
    )


class AgentRegistryIndexTests(unittest.TestCase):
    def test_by_capability_keeps_registration_order(self) -> None:
        registry = AgentRegistry.empty()
        flow = _registration("a.flow", AgentCapability.TASK_FLOW_UNDERSTANDING)
        decomp = _registration("a.decomp", AgentCapability.TASK_DECOMPOSITION)
        flow2 = _registration("a.flow2", AgentCapability.TASK_FLOW_UNDERSTANDING)
        registry = registry.register(flow).register(decomp).register(flow2)

        by_flow = registry.by_capability(AgentCapability.TASK_FLOW_UNDERSTANDING)
        self.assertEqual(("a.flow", "a.flow2"), tuple(r.spec.agent_id for r in by_flow))
        self.assertEqual(
            ("a.decomp",),
            tuple(r.spec.agent_id for r in registry.by_capability(AgentCapability.TASK_DECOMPOSITION)),
        )
        self.assertEqual((), registry.by_capability(AgentCapability.RISK_ANALYSIS))
        # Lazily built cache is populated after the first query.
        self.assertIsInstance(getattr(registry, "_capability_cache"), dict)
        self.assertEqual(
            getattr(registry, "_capability_cache")[AgentCapability.TASK_FLOW_UNDERSTANDING],
            by_flow,
        )

    def test_by_capability_cache_invalidates_on_mutation(self) -> None:
        registry = AgentRegistry.empty()
        registry = registry.register(
            _registration("a.flow", AgentCapability.TASK_FLOW_UNDERSTANDING)
        )
        registry.by_capability(AgentCapability.TASK_FLOW_UNDERSTANDING)
        extended = registry.register(
            _registration("a.flow2", AgentCapability.TASK_FLOW_UNDERSTANDING)
        )
        self.assertEqual(
            ("a.flow", "a.flow2"),
            tuple(r.spec.agent_id for r in extended.by_capability(AgentCapability.TASK_FLOW_UNDERSTANDING)),
        )
        # Immutability: the old instance still sees only its original entries.
        self.assertEqual(
            ("a.flow",),
            tuple(r.spec.agent_id for r in registry.by_capability(AgentCapability.TASK_FLOW_UNDERSTANDING)),
        )


class ManifestBuilderRegressionTests(unittest.TestCase):
    def test_manifest_bytes_are_byte_identical_to_baseline(self) -> None:
        resolver = DemoRegistrationResolver()
        signer = DemoRegistrationSigner()
        fingerprint = hashlib.sha256(resolver.der).hexdigest()
        manifest_bytes = build_registration_manifest(
            "agent.task_decomposition",
            "task_decomposition",
            display_name="task_decomposition",
            signer_cert_fingerprint=fingerprint,
            signer=signer.sign,
        )
        # Baseline captured before FRAMEWORK-OPTIMIZE-1 (wire bytes unchanged).
        self.assertEqual(
            "00ff9adadebe9b4271531012e244f5f825a19ba6c9e0e43521cac8e3bba52c52",
            hashlib.sha256(manifest_bytes).hexdigest(),
        )
        parsed = json.loads(manifest_bytes.decode("utf-8"))
        self.assertEqual(
            parsed["metadata"]["spec_hash"], manifest_spec_hash(manifest_bytes)
        )


class ChainToPlanTests(unittest.TestCase):
    def test_lifted_plan_fingerprint_and_structure(self) -> None:
        registry, _ = register_demo_agents(AgentRegistry.empty())
        policy = get_default_profile("INTERACTIVE")
        plan = chain_to_plan(MVP_FIXED_CHAIN, registry, policy)
        self.assertIsInstance(plan, Plan)
        self.assertEqual(plan.plan_id, plan_fingerprint(plan))
        self.assertEqual(len(plan.nodes), len(MVP_FIXED_CHAIN.steps))
        self.assertEqual(len(plan.edges), max(0, len(plan.nodes) - 1))
        for index, edge in enumerate(plan.edges):
            self.assertEqual(edge.predecessor_node_id, f"c{index}")
            self.assertEqual(edge.successor_node_id, f"c{index + 1}")


class DemoRegistrationAssemblyTests(unittest.TestCase):
    def test_register_demo_agents_registers_all_four(self) -> None:
        registry, registered = register_demo_agents(AgentRegistry.empty())
        self.assertEqual(4, len(registry))
        self.assertEqual(
            [
                "agent.task_flow_understanding",
                "agent.task_decomposition",
                "agent.team_recommendation",
                "agent.task_package_build",
            ],
            registered,
        )
        for agent_id, capability in (
            ("agent.task_flow_understanding", AgentCapability.TASK_FLOW_UNDERSTANDING),
            ("agent.task_decomposition", AgentCapability.TASK_DECOMPOSITION),
            ("agent.team_recommendation", AgentCapability.TEAM_RECOMMENDATION),
            ("agent.task_package_build", AgentCapability.TASK_PACKAGE_BUILD),
        ):
            self.assertEqual(
                agent_id, registry.get(agent_id).spec.agent_id  # type: ignore[union-attr]
            )
            self.assertEqual(
                (agent_id,),
                tuple(r.spec.agent_id for r in registry.by_capability(capability)),
            )


if __name__ == "__main__":
    unittest.main()
