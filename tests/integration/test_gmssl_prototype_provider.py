"""Real GmSSL MVP provider and encrypted .agent round-trip tests."""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path

from src.coevo.crypto import GmsslPrototypeError, GmsslPrototypeProvider, SealedPayload
from src.coevo.protocol import (
    AgentPackageError,
    build_encrypted_package,
    build_envelope_template,
    open_encrypted_package,
    parse_package_bytes,
)
from src.coevo.identity.models import Actor
from src.coevo.identity.service import StaticAuthorizer
from src.coevo.orchestrator import OrchestrationOutcome, Orchestrator, RealChainStore
from tests.integration import test_orchestrator_real_facade_chain as chain_fixture
from tests.support_identity import TestFreshnessAuthority, TestSigner

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == "nt", "locked Win64 GmSSL provider requires Windows")
class GmsslPrototypeProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = "crypto-" + uuid.uuid4().hex[:16]
        cls.output = ROOT / "loop" / "runtime" / "sm2-test-pki" / cls.profile
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(ROOT / "scripts" / "generate-sm2-test-pki.ps1"),
             "-ProfileName", cls.profile],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        cls.provider = GmsslPrototypeProvider(ROOT)
        cls.sender = cls.provider.sender_handle(cls.profile, "CERT-SENDER")
        cls.recipient = cls.provider.recipient_handle(cls.profile, "CERT-RECIPIENT")

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.output, ignore_errors=True)

    def envelope(self):
        return build_envelope_template(
            sender_cert_id="CERT-SENDER", recipient_cert_id="CERT-RECIPIENT",
            project_id="PRJ001", package_type="TASK_ASSIGNMENT", sequence_no=1,
            payload_length=0, created_at="2026-08-02T00:00:00Z",
            expires_at="2027-08-02T00:00:00Z",
        )

    def test_lock_matches_helper_launcher_and_explicit_prototype_scope(self) -> None:
        lock = json.loads((ROOT / "docs/dependencies/toolchain-lock.json").read_text("utf-8"))
        tool = lock["tools"]["gmssl_prototype_provider"]
        helper = tool["helper"]
        self.assertEqual("3.2.0", tool["version"])
        self.assertIn("business-approved 2026-08-03", tool["scope"])
        self.assertIn("not a nationally certified module", tool["scope"])
        self.assertEqual("COEVOCRYPTO/1", helper["protocol"])
        for field, name in (("source", "source_sha256"),):
            path = ROOT / helper[field]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), helper[name])
        launcher = ROOT / helper["launcher"]["path"]
        self.assertEqual(hashlib.sha256(launcher.read_bytes()).hexdigest(), helper["launcher"]["sha256"])
        self.assertIn("No secrets in argv", helper["secret_transport"])

    def test_helper_compile_cache_is_verified_and_self_heals(self) -> None:
        """PERF-HELPER-1: cached helper + sidecar are hash-verified; corruption self-heals."""
        lock = json.loads((ROOT / "docs/dependencies/toolchain-lock.json").read_text("utf-8"))
        source_sha = lock["tools"]["gmssl_prototype_provider"]["helper"]["source_sha256"]
        cache_dir = ROOT / ".tools" / "runtime" / "gmssl-crypto-helper" / "cache"
        cache_exe = cache_dir / f"helper-{source_sha}.exe"
        sidecar = cache_dir / f"helper-{source_sha}.exe.sha256"
        # A real crypto operation populates the cache on the first helper
        # launch (cache miss -> compile -> best-effort install).
        signature = self.provider.sign(self.sender, b"cache-probe")
        self.assertTrue(signature)
        self.assertTrue(cache_exe.is_file(), "cached helper should exist after provider use")
        self.assertTrue(sidecar.is_file(), "cache sidecar should exist")
        self.assertEqual(
            hashlib.sha256(cache_exe.read_bytes()).hexdigest(),
            sidecar.read_text(encoding="utf-8").strip(),
            "sidecar must record the cached helper hash",
        )
        # Corrupt the sidecar: the next call must fail closed and self-heal by
        # recompiling, and the sidecar must be re-recorded.
        sidecar.write_text("0" * 64, encoding="utf-8")
        signature2 = self.provider.sign(self.sender, b"cache-probe-2")
        self.assertTrue(signature2)
        self.assertEqual(
            hashlib.sha256(cache_exe.read_bytes()).hexdigest(),
            sidecar.read_text(encoding="utf-8").strip(),
            "sidecar must be re-recorded after a self-heal recompile",
        )

    def test_official_sm3_vector_and_sm2_signature_tamper(self) -> None:
        self.assertEqual(
            "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0",
            self.provider.sm3(b"abc").hex(),
        )
        signature = self.provider.sign(self.sender, b"manifest")
        self.assertTrue(self.provider.verify(self.sender, b"manifest", signature))
        self.assertFalse(self.provider.verify(self.sender, b"tampered", signature))
        self.assertNotIn("PRIVATE", repr(self.sender).upper())

    def test_sm2_sm4_gcm_roundtrip_and_all_authentication_fields(self) -> None:
        sealed = self.provider.seal(self.recipient, b"secret payload", associated_data=b"envelope")
        self.assertEqual(b"secret payload", self.provider.open(self.recipient, sealed, associated_data=b"envelope"))
        mutations = (
            (dataclasses.replace(sealed, nonce=bytes([sealed.nonce[0] ^ 1]) + sealed.nonce[1:]), b"envelope"),
            (dataclasses.replace(sealed, ciphertext=bytes([sealed.ciphertext[0] ^ 1]) + sealed.ciphertext[1:]), b"envelope"),
            (dataclasses.replace(sealed, tag=bytes([sealed.tag[0] ^ 1]) + sealed.tag[1:]), b"envelope"),
            (sealed, b"tampered-envelope"),
        )
        for candidate, aad in mutations:
            with self.subTest(aad=aad), self.assertRaises(GmsslPrototypeError):
                self.provider.open(self.recipient, candidate, associated_data=aad)

    def test_real_agent_wire_roundtrip_inner_signature_and_tamper(self) -> None:
        package = build_encrypted_package(
            envelope=self.envelope(), manifest={"project_id": "PRJ001", "task_id": "TASK-1"},
            content=b"offline assignment", provider=self.provider,
            sender_handle=self.sender, recipient_handle=self.recipient,
            signed_at="2026-08-02T00:00:00Z",
        )
        wire = package.to_bytes()
        self.assertNotIn(b"offline assignment", wire)
        self.assertNotIn(b"PRIVATE KEY", wire)
        parsed = parse_package_bytes(wire)
        opened = open_encrypted_package(
            parsed, provider=self.provider, recipient_handle=self.recipient,
            sender_handle=self.sender,
        )
        self.assertEqual(b"offline assignment", opened.content)
        self.assertEqual("TASK-1", opened.manifest["task_id"])
        self.assertTrue(opened.signature.signature)
        wrong = self.provider.recipient_handle(self.profile, "CERT-WRONG")
        with self.assertRaises(AgentPackageError):
            open_encrypted_package(parsed, provider=self.provider, recipient_handle=wrong, sender_handle=self.sender)
        corrupted = dataclasses.replace(
            parsed,
            payload_block=dataclasses.replace(
                parsed.payload_block,
                tag=bytes([parsed.payload_block.tag[0] ^ 1]) + parsed.payload_block.tag[1:],
            ),
        )
        with self.assertRaises(GmsslPrototypeError):
            open_encrypted_package(
                corrupted, provider=self.provider, recipient_handle=self.recipient,
                sender_handle=self.sender,
            )

    def test_orchestrator_completes_only_after_real_package_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = RealChainStore.create(
                Path(temp) / "chain.db", signer=TestSigner(),
                freshness=TestFreshnessAuthority(),
            )
            try:
                data = chain_fixture.project_input()
                held = Orchestrator.dispatch_event_with_real_facades(
                    chain_fixture.registry(), chain_fixture.MVP_FIXED_CHAIN,
                    chain_fixture.event(data), workspace=chain_fixture.workspace(),
                    executor=chain_fixture.executor(), project_input=data,
                    store=store, now=chain_fixture.NOW,
                )
                confirmed = Orchestrator.confirm_real_chain(
                    held, preview=held.package_preview, actor=Actor("owner.1"),
                    authorizer=StaticAuthorizer({"owner.1": frozenset({
                        "orchestrator:confirm-package:PRJ001"
                    })}), store=store, now=chain_fixture.NOW,
                )
                result = Orchestrator.resume_real_chain(
                    confirmed, registry=chain_fixture.registry(),
                    chain=chain_fixture.MVP_FIXED_CHAIN,
                    event=chain_fixture.event(data), workspace=chain_fixture.workspace(),
                    executor=chain_fixture.executor(), store=store, now=chain_fixture.NOW,
                    crypto_provider=self.provider, sender_handle=self.sender,
                    recipient_handle=self.recipient,
                )
                self.assertEqual(OrchestrationOutcome.COMPLETED, result.orch_report.outcome)
                self.assertEqual(1, len(result.package_summary))
                self.assertIn(("package", "completed"),
                              [(row.action, row.result) for row in store.audit_entries])
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
