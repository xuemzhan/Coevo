"""FRAMEWORK-INTEGRATION-1: guarded orchestration adapter tests."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import unittest
from pathlib import Path

from src.coevo.framework.integration import (
    GUARD_PROJECTION_KEYS,
    IntegrationError,
    guard_registration,
    guarded_dispatch,
    plan_to_chain,
)
from src.coevo.framework.manifest_checker import ManifestCheckInput
from src.coevo.framework.orchestrator import OrchestrationStatus
from src.coevo.framework.plan import (
    Plan,
    PlanEdge,
    PlanNode,
    PlanNodeKind,
    plan_fingerprint,
)
from src.coevo.framework.policy import get_default_profile
from src.coevo.orchestrator.models import (
    AgentCapability,
    AgentRegistration,
    AgentRegistry,
    AgentSpec,
    OrchestrationOutcome as ProductOutcome,
    OrchestrationStepKind,
)

ROOT = Path(__file__).resolve().parents[2]


def make_plan(
    *,
    capability: str = "task_decomposition",
    with_tool: bool = False,
    with_human_gate: bool = True,
) -> Plan:
    nodes = [
        PlanNode(
            node_id="n1",
            kind=PlanNodeKind.AGENT,
            agent_capability=capability,
            requires_human_confirmation=False,
        )
    ]
    edges: list[PlanEdge] = []
    if with_tool:
        nodes.append(
            PlanNode(
                node_id="n2",
                kind=PlanNodeKind.TOOL,
                tool_ref="coevo.tools.cycle_check",
            )
        )
        edges.append(PlanEdge("n1", "n2"))
    if with_human_gate:
        nodes.append(
            PlanNode(
                node_id="n3",
                kind=PlanNodeKind.HUMAN_GATE,
                human_gate_reason="approve",
                requires_human_confirmation=True,
            )
        )
        edges.append(PlanEdge(nodes[-2].node_id, "n3"))
    policy = get_default_profile("INTERACTIVE")
    plan = Plan(
        plan_id="0" * 64,
        plan_version="1.0",
        policy_profile=policy.profile,
        policy_version=policy.policy_version,
        nodes=tuple(nodes),
        edges=tuple(edges),
    )
    return Plan(
        plan_id=plan_fingerprint(plan),
        plan_version=plan.plan_version,
        policy_profile=plan.policy_profile,
        policy_version=plan.policy_version,
        nodes=plan.nodes,
        edges=plan.edges,
    )


def make_registry(*, with_agent: bool = True) -> AgentRegistry:
    registry = AgentRegistry()
    if with_agent:
        spec = AgentSpec(
            agent_id="agent.td",
            capability=AgentCapability.TASK_DECOMPOSITION,
            display_name="task decomposition",
            input_schema=(),
            output_schema=(),
        )
        registry = registry.register(AgentRegistration(spec=spec))
    return registry


class _AllowAll:
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: Plan, actor: str) -> bool:
        return True


class _FakeDispatch:
    def __init__(self, outcome: ProductOutcome) -> None:
        self.outcome = outcome
        self.calls: list[tuple] = []

    def __call__(self, registry, chain, event, *, workspace, now):
        self.calls.append((chain, event))
        return _Report(self.outcome)


class _RaisingDispatch:
    def __call__(self, registry, chain, event, *, workspace, now):
        raise RuntimeError("dispatch down")


class _Report:
    def __init__(self, outcome: ProductOutcome) -> None:
        self.outcome = outcome


def run_guarded(plan, dispatch, **kwargs):
    return guarded_dispatch(
        plan,
        get_default_profile("INTERACTIVE"),
        event=kwargs.pop("event", object()),
        workspace=kwargs.pop("workspace", object()),
        now=kwargs.pop("now", "2026-08-08T08:00:00Z"),
        registry=kwargs.pop("registry", make_registry()),
        scope_checker=kwargs.pop("scope", _AllowAll()),
        rbac_checker=kwargs.pop("rbac", _AllowAll()),
        actor=kwargs.pop("actor", "owner"),
        validated_at=kwargs.pop("validated_at", "2026-08-08T08:00:00Z"),
        dispatch_fn=dispatch,
    )


def make_manifest_bytes() -> bytes:
    cert_fp = hashlib.sha256(b"FAKE-CERT-DER").hexdigest()
    manifest = {
        "apiVersion": "coevo.framework/v1",
        "kind": "Agent",
        "metadata": {
            "agent_id": "task_decomposition.basic",
            "display_name": "task-decomposition agent",
            "semantic_version": "0.2.0",
        },
        "spec": {
            "capability": "task_decomposition",
            "requires_human_confirmation": True,
        },
        "policy_profile": "INTERACTIVE",
        "policy_version": "1.0",
        "policy_ref": {
            "signer_cert_fingerprint": cert_fp,
            "signature": "00" * 64,
        },
        "security": {"crypto_scope": "mvp-prototype"},
        "audit": {"redact_in_audit": ["policy_profile"]},
    }
    stripped = json.loads(json.dumps(manifest, ensure_ascii=True))
    stripped.get("metadata", {}).pop("spec_hash", None)
    stripped.get("policy_ref", {}).pop("spec_hash", None)
    stripped.get("policy_ref", {}).pop("signature", None)
    spec_hash = hashlib.sha256(
        json.dumps(stripped, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()
    manifest["metadata"]["spec_hash"] = spec_hash
    manifest["policy_ref"]["spec_hash"] = spec_hash
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


class _FakePolicyRegistry:
    def has_policy_version(self, profile: str, version: str) -> bool:
        return (profile, version) == ("INTERACTIVE", "1.0")


class _FakeResolver:
    def __init__(self) -> None:
        self.der = b"FAKE-CERT-DER"

    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None:
        return (
            self.der
            if hashlib.sha256(self.der).hexdigest() == fingerprint_hex
            else None
        )


class _FakeVerifier:
    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool:
        return True


class IntegrationTests(unittest.TestCase):
    def test_plan_to_chain_mixed_nodes(self) -> None:
        chain = plan_to_chain(make_plan(), make_registry())
        self.assertEqual(len(chain.steps), 2)
        self.assertEqual(chain.steps[0].kind, OrchestrationStepKind.AGENT_CALL)
        self.assertEqual(chain.steps[0].agent_id, "agent.td")
        self.assertEqual(chain.steps[1].kind, OrchestrationStepKind.HUMAN_CONFIRM)

    def test_plan_to_chain_tool_rejected(self) -> None:
        with self.assertRaises(IntegrationError):
            plan_to_chain(make_plan(with_tool=True), make_registry())

    def test_plan_to_chain_non_mvp_rejected(self) -> None:
        with self.assertRaises(IntegrationError):
            plan_to_chain(make_plan(capability="PLANNER"), make_registry())

    def test_plan_to_chain_no_agent_rejected(self) -> None:
        with self.assertRaises(IntegrationError):
            plan_to_chain(make_plan(), make_registry(with_agent=False))

    def test_guarded_dispatch_invalid_plan_rejected(self) -> None:
        cyclic = make_plan()
        cyclic = Plan(
            plan_id=cyclic.plan_id,
            plan_version=cyclic.plan_version,
            policy_profile=cyclic.policy_profile,
            policy_version=cyclic.policy_version,
            nodes=cyclic.nodes,
            edges=(PlanEdge("n1", "n3"), PlanEdge("n3", "n1")),
        )
        dispatch = _FakeDispatch(ProductOutcome.COMPLETED)
        outcome = run_guarded(cyclic, dispatch)
        self.assertEqual(outcome.status, OrchestrationStatus.REJECTED)
        self.assertEqual(dispatch.calls, [])

    def test_guarded_dispatch_maps_outcomes(self) -> None:
        plan = make_plan()
        for product, expected in (
            (ProductOutcome.COMPLETED, OrchestrationStatus.COMPLETED),
            (ProductOutcome.HELD_AT_CONFIRM, OrchestrationStatus.HELD),
            (ProductOutcome.ESCALATED, OrchestrationStatus.ESCALATED),
        ):
            dispatch = _FakeDispatch(product)
            outcome = run_guarded(plan, dispatch)
            self.assertEqual(outcome.status, expected)
            self.assertEqual(len(dispatch.calls), 1)

    def test_guarded_dispatch_inner_raises_fails_closed(self) -> None:
        outcome = run_guarded(make_plan(), _RaisingDispatch())
        self.assertEqual(outcome.status, OrchestrationStatus.ESCALATED)
        self.assertIn("inner dispatch failed", outcome.failure_reason or "")

    def test_guard_registration(self) -> None:
        calls: list = []

        def inner(manifest) -> None:
            calls.append(manifest)

        result = guard_registration(
            ManifestCheckInput(
                manifest_bytes=make_manifest_bytes(),
                trusted_anchor_pubkey=b"ANCHOR-PUBKEY",
            ),
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeResolver(),
            signature_verifier=_FakeVerifier(),
            inner_register=inner,
        )
        self.assertTrue(result.accepted, result.reason)
        self.assertEqual(len(calls), 1)
        record = result.to_audit_record()
        self.assertEqual(set(record), set(GUARD_PROJECTION_KEYS))

    def test_guard_registration_rejected_manifest(self) -> None:
        calls: list = []

        def inner(manifest) -> None:
            calls.append(manifest)

        bad = make_manifest_bytes().replace(b'"0.2.0"', b'"0.2"')
        result = guard_registration(
            ManifestCheckInput(
                manifest_bytes=bad,
                trusted_anchor_pubkey=b"ANCHOR-PUBKEY",
            ),
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeResolver(),
            signature_verifier=_FakeVerifier(),
            inner_register=inner,
        )
        self.assertFalse(result.accepted)
        self.assertEqual(calls, [])

    def test_guard_registration_inner_raises_fails_closed(self) -> None:
        def inner(manifest) -> None:
            raise RuntimeError("register down")

        result = guard_registration(
            ManifestCheckInput(
                manifest_bytes=make_manifest_bytes(),
                trusted_anchor_pubkey=b"ANCHOR-PUBKEY",
            ),
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeResolver(),
            signature_verifier=_FakeVerifier(),
            inner_register=inner,
        )
        self.assertFalse(result.accepted)
        self.assertIn("inner registration failed", result.reason or "")

    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "integration.py").read_text(
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
        self.assertEqual([], bad, "third-party imports found in integration.py")


if __name__ == "__main__":
    unittest.main()
