"""HANDLE-1: real CNG non-exportable KEK integration tests."""
from __future__ import annotations

import dataclasses
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path

from src.coevo.crypto import (
    CngKekStore,
    CngKekUnavailableError,
    CngProtectedKeyHandle,
    CngWrappedKeyRegistry,
    GmsslProtectedProvider,
    GmsslPrototypeProvider,
)


ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == "nt", "CNG KEK tests require Windows CNG")
class CngKekIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = CngKekStore()
        self.kek_name = "CoevoSm2Kek-" + uuid.uuid4().hex

    def tearDown(self) -> None:
        try:
            ref = self.store.create_kek(self.kek_name)
            self.store.destroy(ref)
        except Exception:
            pass

    def test_create_status_wrap_unwrap_digest_destroy(self):
        ref = self.store.create_kek(self.kek_name)
        status = self.store.status(ref)
        self.assertTrue(status["exists"])
        self.assertFalse(status["exportable"])
        self.assertEqual(2048, status["key_size"])

        secret = b"SM2-PRIVATE-KEY-MATERIAL-" + os.urandom(32)
        wrapped, wrapped_sha = self.store.wrap(ref, secret)
        self.assertEqual(hashlib.sha256(wrapped).hexdigest(), wrapped_sha)
        digest, length = self.store.unwrap_digest(ref, wrapped)
        self.assertEqual(hashlib.sha256(secret).hexdigest(), digest)
        self.assertEqual(len(secret), length)

        self.store.destroy(ref)
        with self.assertRaises(Exception):
            self.store.status(ref)

    def test_wrap_roundtrip_under_reopened_handle(self):
        ref = self.store.create_kek(self.kek_name)
        secret = b"second-material-" + os.urandom(16)
        wrapped, _ = self.store.wrap(ref, secret)
        # A fresh store instance reopens the same non-exportable key.
        other = CngKekStore()
        digest, length = other.unwrap_digest(ref, wrapped)
        self.assertEqual(hashlib.sha256(secret).hexdigest(), digest)
        self.assertEqual(len(secret), length)


class RegistryPersistenceIntegrationTests(unittest.TestCase):
    def test_registry_survives_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrapped.json"
            registry = CngWrappedKeyRegistry.create(path)
            registry.register(
                handle_id="h.1",
                kek_name="CoevoSm2Kek-" + "a" * 32,
                wrapped_sha256="c" * 64,
                role="sender",
                certificate_id="CERT-SENDER",
            )
            reopened = CngWrappedKeyRegistry.open(path)
            self.assertEqual(1, len(reopened.snapshot()))
            self.assertEqual("h.1", reopened.snapshot()[0]["handle_id"])


@unittest.skipUnless(os.name == "nt", "CNG protected SM2 round-trip requires Windows")
class ProtectedSm2RoundTripTests(unittest.TestCase):
    """HANDLE-2: sign/open via a CNG KEK-wrapped SM2 key (helper-side unwrap)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = "handle2-" + uuid.uuid4().hex[:16]
        cls.output = ROOT / "loop" / "runtime" / "sm2-test-pki" / cls.profile
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(ROOT / "scripts" / "generate-sm2-test-pki.ps1"),
             "-ProfileName", cls.profile],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        cls.engine = GmsslPrototypeProvider(ROOT)
        cls.store = CngKekStore()
        cls.kek_ref = cls.store.create_kek("CoevoSm2Kek-" + uuid.uuid4().hex)
        cls.sender_handle = cls.engine.sender_handle(cls.profile, "CERT-SENDER")
        cls.recipient_handle = cls.engine.recipient_handle(cls.profile, "CERT-RECIPIENT")
        cls.sender_wrapped = cls.engine.protect_key(
            cls.kek_ref.kek_name, "sender", profile=cls.profile
        )
        cls.recipient_wrapped = cls.engine.protect_key(
            cls.kek_ref.kek_name, "recipient", profile=cls.profile
        )

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.store.destroy(cls.kek_ref)
        except Exception:
            pass
        shutil.rmtree(cls.output, ignore_errors=True)

    def _provider(
        self, wrapped: bytes, handle: CngProtectedKeyHandle, role: str
    ) -> GmsslProtectedProvider:
        return GmsslProtectedProvider(
            self.engine, self.store, handle, wrapped, self.kek_ref, self.profile, role
        )

    def test_protected_sign_verifies_with_public_cert(self):
        provider = self._provider(
            self.sender_wrapped, CngProtectedKeyHandle("h.s", "CERT-SENDER"), "sender"
        )
        signature = provider.sign(None, b"canonical manifest")
        self.assertTrue(
            self.engine.verify(self.sender_handle, b"canonical manifest", signature)
        )
        self.assertFalse(self.engine.verify(self.sender_handle, b"tampered", signature))

    def test_protected_open_roundtrip_and_tamper(self):
        sealed = self.engine.seal(
            self.recipient_handle, b"secret payload", associated_data=b"envelope"
        )
        provider = self._provider(
            self.recipient_wrapped,
            CngProtectedKeyHandle("h.r", "CERT-RECIPIENT"),
            "recipient",
        )
        self.assertEqual(
            b"secret payload",
            provider.open(None, sealed, associated_data=b"envelope"),
        )
        tampered = dataclasses.replace(
            sealed, tag=bytes([sealed.tag[0] ^ 1]) + sealed.tag[1:]
        )
        with self.assertRaises(Exception):
            provider.open(None, tampered, associated_data=b"envelope")

    def test_wrong_kek_fails_closed(self):
        other = self.store.create_kek("CoevoSm2Kek-" + uuid.uuid4().hex)
        try:
            with self.assertRaises(Exception):
                self.engine.sign_wrapped(
                    other.kek_name, self.sender_wrapped, b"x",
                    role="sender", profile=self.profile,
                )
        finally:
            self.store.destroy(other)


if __name__ == "__main__":
    unittest.main()
