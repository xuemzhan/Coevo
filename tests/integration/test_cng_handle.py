"""HANDLE-1: real CNG non-exportable KEK integration tests."""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
import uuid
from pathlib import Path

from src.coevo.crypto import CngKekStore, CngKekUnavailableError, CngWrappedKeyRegistry


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


if __name__ == "__main__":
    unittest.main()
