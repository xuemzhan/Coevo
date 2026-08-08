"""FRAMEWORK-GAPS-7: production registration verifier guard."""

from __future__ import annotations

import hashlib
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
from src.coevo.framework.manifest_checker import ManifestCheckInput


ROOT = Path(__file__).resolve().parents[2]


class _ProductionVerifier:
    """Test-only verifier that declares the production boundary."""

    is_production: bool = True

    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool:
        return True


class ProductionVerifierGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = DemoRegistrationResolver()
        self.signer = DemoRegistrationSigner()
        self.registry = DemoPolicyRegistry()
        self.fingerprint = hashlib.sha256(self.resolver.der).hexdigest()
        self.manifest = build_registration_manifest(
            "agent.task_decomposition",
            "task_decomposition",
            signer_cert_fingerprint=self.fingerprint,
            signer=self.signer.sign,
        )

    def run_guard(self, verifier, *, require_production: bool):
        calls: list[str] = []
        result = guard_registration(
            ManifestCheckInput(
                manifest_bytes=self.manifest,
                trusted_anchor_pubkey=b"DEMO-ANCHOR",
            ),
            policy_registry=self.registry,
            cert_resolver=self.resolver,
            signature_verifier=verifier,
            inner_register=lambda manifest: calls.append(manifest.agent_id),
            require_production_verifier=require_production,
        )
        return result, calls

    def test_demo_verifier_rejected_on_production_path(self) -> None:
        result, calls = self.run_guard(
            DemoRegistrationVerifier(), require_production=True
        )
        self.assertFalse(result.accepted)
        self.assertIn("production verifier", result.reason or "")
        self.assertEqual([], calls)

    def test_production_verifier_accepted_on_production_path(self) -> None:
        result, calls = self.run_guard(
            _ProductionVerifier(), require_production=True
        )
        self.assertTrue(result.accepted, result.reason)
        self.assertEqual(["agent.task_decomposition"], calls)

    def test_demo_path_unchanged_without_production_requirement(self) -> None:
        result, calls = self.run_guard(
            DemoRegistrationVerifier(), require_production=False
        )
        self.assertTrue(result.accepted, result.reason)
        self.assertEqual(["agent.task_decomposition"], calls)

    def test_demo_verifier_declares_non_production(self) -> None:
        self.assertIs(False, DemoRegistrationVerifier.is_production)

    def test_demo_support_guard_marker_is_pinned(self) -> None:
        source = (ROOT / "src" / "coevo" / "app" / "demo_support.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("is_production: bool = False", source)


if __name__ == "__main__":
    unittest.main()
