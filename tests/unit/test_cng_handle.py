"""HANDLE-1: pure logic for the CNG-protected key handle layer."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.coevo.crypto import (
    CngKekReference,
    CngKekStore,
    CngKekValidationError,
    CngProtectedKeyHandle,
    CngWrappedKeyRegistry,
    GmsslProtectedProvider,
    ProviderRegistry,
    ProviderScope,
    require_key_handle_backed,
)


def _kek_ref(name: str = "CoevoSm2Kek-" + "a" * 32) -> CngKekReference:
    return CngKekReference(
        kek_name=name,
        public_sha256="b" * 64,
        created_at="2026-08-03T00:00:00Z",
    )


class KekReferenceTests(unittest.TestCase):
    def test_valid_reference(self):
        ref = _kek_ref()
        self.assertEqual("CoevoSm2Kek-" + "a" * 32, ref.kek_name)

    def test_rejects_bad_name(self):
        for bad in ("CoevoSm2Kek-" + "g" * 32, "other", "", "CoevoSm2Kek-" + "A" * 32):
            with self.assertRaises(CngKekValidationError):
                _kek_ref(bad)

    def test_rejects_bad_digest_and_time(self):
        with self.assertRaises(CngKekValidationError):
            CngKekReference("CoevoSm2Kek-" + "a" * 32, "xyz", "2026-08-03T00:00:00Z")
        with self.assertRaises(CngKekValidationError):
            CngKekReference(
                "CoevoSm2Kek-" + "a" * 32, "b" * 64, "2026-08-03 00:00:00"
            )


class ProtectedHandleTests(unittest.TestCase):
    def test_handle_fields(self):
        handle = CngProtectedKeyHandle("h.1", "CERT-SENDER")
        self.assertEqual("1.2.156.10197.1.301", handle.algorithm_oid)

    def test_rejects_missing_fields(self):
        with self.assertRaises(CngKekValidationError):
            CngProtectedKeyHandle("", "CERT")
        with self.assertRaises(CngKekValidationError):
            CngProtectedKeyHandle("h.1", "")


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "wrapped-keys.json"

    def test_create_refuses_existing_and_open_refuses_missing(self):
        CngWrappedKeyRegistry.create(self.path)
        with self.assertRaises(CngKekValidationError):
            CngWrappedKeyRegistry.create(self.path)
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(CngKekValidationError):
                CngWrappedKeyRegistry.open(Path(other) / "missing.json")

    def test_register_revoke_destroy_snapshot(self):
        registry = CngWrappedKeyRegistry.create(self.path)
        entry_hash = registry.register(
            handle_id="h.1",
            kek_name="CoevoSm2Kek-" + "a" * 32,
            wrapped_sha256="c" * 64,
            role="sender",
            certificate_id="CERT-SENDER",
        )
        self.assertEqual(64, len(entry_hash))
        self.assertEqual(1, len(registry.snapshot()))
        registry.revoke("h.1", reason="compromise")
        self.assertEqual(0, len(registry.snapshot()))
        registry.register(
            handle_id="h.2",
            kek_name="CoevoSm2Kek-" + "b" * 32,
            wrapped_sha256="d" * 64,
            role="recipient",
            certificate_id="CERT-RECIPIENT",
        )
        registry.destroy("h.2", reason="retired")
        self.assertEqual(0, len(registry.snapshot()))

    def test_tamper_is_rejected_on_open(self):
        registry = CngWrappedKeyRegistry.create(self.path)
        registry.register(
            handle_id="h.1",
            kek_name="CoevoSm2Kek-" + "a" * 32,
            wrapped_sha256="c" * 64,
            role="sender",
            certificate_id="CERT-SENDER",
        )
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data["entries"][0]["wrapped_sha256"] = "e" * 64
        self.path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(CngKekValidationError):
            CngWrappedKeyRegistry.open(self.path)

    def test_reopen_preserves_snapshot(self):
        CngWrappedKeyRegistry.create(self.path).register(
            handle_id="h.1",
            kek_name="CoevoSm2Kek-" + "a" * 32,
            wrapped_sha256="c" * 64,
            role="sender",
            certificate_id="CERT-SENDER",
        )
        reopened = CngWrappedKeyRegistry.open(self.path)
        self.assertEqual(1, len(reopened.snapshot()))


class _FakeEngine:
    def sm3(self, data: bytes) -> bytes:
        return b"sm3:" + data

    def seal(self, handle, plaintext, *, associated_data, nonce=None):
        return ("sealed", plaintext, associated_data, nonce)

    def verify(self, handle, data, signature) -> bool:
        return data == signature

    def sign_wrapped(self, kek_name, wrapped, data, *, role, profile) -> bytes:
        return b"sig:" + data

    def open_wrapped(self, kek_name, wrapped, sealed, *, role, profile, associated_data) -> bytes:
        return b"open:" + sealed[0]


class ProtectedProviderTests(unittest.TestCase):
    def _provider(self):
        store = CngKekStore.__new__(CngKekStore)  # helper not needed for these tests
        handle = CngProtectedKeyHandle("h.1", "CERT-SENDER")
        kek_ref = CngKekReference(
            "CoevoSm2Kek-" + "a" * 32, "b" * 64, "2026-08-03T00:00:00Z"
        )
        return GmsslProtectedProvider(
            _FakeEngine(), store, handle, b"wrapped", kek_ref, "crypto-test", "sender"
        )

    def test_policy_surface(self):
        provider = self._provider()
        self.assertTrue(require_key_handle_backed(provider))
        self.assertEqual(ProviderScope.APPROVED_PRODUCT, provider.scope)
        registry = ProviderRegistry()
        registry.register("protected", provider)
        self.assertIs(provider, registry.require_approved("protected"))

    def test_public_side_ops_delegate(self):
        provider = self._provider()
        self.assertEqual(b"sm3:abc", provider.sm3(b"abc"))
        self.assertEqual(
            ("sealed", b"x", b"aad", None),
            provider.seal(None, b"x", associated_data=b"aad"),
        )
        self.assertTrue(provider.verify(None, b"d", b"d"))

    def test_private_side_ops_delegate_to_helper(self):
        provider = self._provider()
        self.assertEqual(b"sig:data", provider.sign(None, b"data"))
        self.assertEqual(b"open:plain", provider.open(None, (b"plain",), associated_data=b"aad"))

    def test_requires_real_kek_store_and_handle(self):
        with self.assertRaises(Exception):
            GmsslProtectedProvider(_FakeEngine(), object(), None)

    def test_requires_wrapped_key_kek_ref_and_profile(self):
        store = CngKekStore.__new__(CngKekStore)
        handle = CngProtectedKeyHandle("h.1", "CERT-SENDER")
        kek_ref = CngKekReference(
            "CoevoSm2Kek-" + "a" * 32, "b" * 64, "2026-08-03T00:00:00Z"
        )
        with self.assertRaises(Exception):
            GmsslProtectedProvider(_FakeEngine(), store, handle, b"", kek_ref, "p", "sender")
        with self.assertRaises(Exception):
            GmsslProtectedProvider(_FakeEngine(), store, handle, b"w", object(), "p", "sender")
        with self.assertRaises(Exception):
            GmsslProtectedProvider(_FakeEngine(), store, handle, b"w", kek_ref, "", "sender")
        with self.assertRaises(Exception):
            GmsslProtectedProvider(_FakeEngine(), store, handle, b"w", kek_ref, "p", "admin")


if __name__ == "__main__":
    unittest.main()
