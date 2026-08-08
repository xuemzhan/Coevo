"""FRAMEWORK-INTEGRATION-4: registration manifest builder + demo gate."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import unittest
from pathlib import Path

from src.coevo.app.demo_support import (
    DemoPolicyRegistry,
    DemoRegistrationResolver,
    DemoRegistrationSigner,
    DemoRegistrationVerifier,
)
from src.coevo.framework.integration import (
    build_registration_manifest,
    guard_registration,
)
from src.coevo.framework.manifest_checker import (
    ManifestCheckInput,
    manifest_spec_hash,
)

ROOT = Path(__file__).resolve().parents[2]


class RegistrationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = DemoRegistrationResolver()
        self.verifier = DemoRegistrationVerifier()
        self.signer = DemoRegistrationSigner()
        self.registry = DemoPolicyRegistry()
        self.fingerprint = hashlib.sha256(self.resolver.der).hexdigest()

    def run_guard(self, manifest_bytes: bytes):
        calls: list[str] = []
        result = guard_registration(
            ManifestCheckInput(
                manifest_bytes=manifest_bytes,
                trusted_anchor_pubkey=b"DEMO-ANCHOR",
            ),
            policy_registry=self.registry,
            cert_resolver=self.resolver,
            signature_verifier=self.verifier,
            inner_register=lambda manifest: calls.append(manifest.agent_id),
        )
        return result, calls

    def test_builder_produces_valid_manifest(self) -> None:
        manifest_bytes = build_registration_manifest(
            "agent.task_decomposition",
            "task_decomposition",
            display_name="task_decomposition",
            signer_cert_fingerprint=self.fingerprint,
            signer=self.signer.sign,
        )
        parsed = json.loads(manifest_bytes.decode("utf-8"))
        self.assertEqual(
            parsed["metadata"]["spec_hash"],
            manifest_spec_hash(manifest_bytes),
        )
        result, calls = self.run_guard(manifest_bytes)
        self.assertTrue(result.accepted, result.reason)
        self.assertEqual(calls, ["agent.task_decomposition"])

    def test_demo_pipeline_agents_all_accepted(self) -> None:
        agents = (
            ("agent.task_flow_understanding", "task_flow_understanding"),
            ("agent.task_decomposition", "task_decomposition"),
            ("agent.team_recommendation", "team_recommendation"),
            ("agent.task_package_build", "task_package_build"),
        )
        for agent_id, capability in agents:
            manifest_bytes = build_registration_manifest(
                agent_id,
                capability,
                display_name=capability,
                signer_cert_fingerprint=self.fingerprint,
                signer=self.signer.sign,
            )
            result, calls = self.run_guard(manifest_bytes)
            self.assertTrue(result.accepted, agent_id)
            self.assertEqual(calls, [agent_id])

    def test_tampered_capability_rejected(self) -> None:
        manifest_bytes = build_registration_manifest(
            "agent.task_decomposition",
            "task_decomposition",
            signer_cert_fingerprint=self.fingerprint,
            signer=self.signer.sign,
        )
        parsed = json.loads(manifest_bytes.decode("utf-8"))
        parsed["spec"]["capability"] = "not_a_capability"
        tampered = json.dumps(
            parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        result, calls = self.run_guard(tampered)
        self.assertFalse(result.accepted)
        self.assertEqual(calls, [])

    def test_unknown_capability_rejected(self) -> None:
        manifest_bytes = build_registration_manifest(
            "agent.bogus",
            "not_a_capability",
            signer_cert_fingerprint=self.fingerprint,
            signer=self.signer.sign,
        )
        result, calls = self.run_guard(manifest_bytes)
        self.assertFalse(result.accepted)
        self.assertEqual(calls, [])

    def test_missing_policy_version_rejected(self) -> None:
        manifest_bytes = build_registration_manifest(
            "agent.task_decomposition",
            "task_decomposition",
            policy_version="",
            signer_cert_fingerprint=self.fingerprint,
            signer=self.signer.sign,
        )
        result, calls = self.run_guard(manifest_bytes)
        self.assertFalse(result.accepted)
        self.assertEqual(calls, [])

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
