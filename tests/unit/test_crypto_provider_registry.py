"""Unit tests for the approved-provider registry and key-handle policy."""
from __future__ import annotations

import unittest

from src.coevo.crypto import (
    CryptoProvider,
    GmsslPrototypeProvider,
    ProviderRegistry,
    ProviderScope,
    ProtectedKeyHandle,
    require_key_handle_backed,
)


class FakeApprovedKeyHandleBackedProvider:
    name = "approved-vendor"
    scope = ProviderScope.APPROVED_PRODUCT
    key_handle_backed = True

    def sm3(self, data: bytes) -> bytes:
        return b"\x00" * 32

    def sign(self, handle, data: bytes) -> bytes:
        return b"sig"

    def verify(self, handle, data: bytes, signature: bytes) -> bool:
        return True

    def seal(self, handle, plaintext: bytes, *, associated_data: bytes, nonce=None):
        return ("wrapped", nonce, plaintext, b"tag")

    def open(self, handle, sealed, *, associated_data: bytes) -> bytes:
        return sealed[2]


class FakeApprovedWithoutKeyHandle:
    name = "approved-nohandle"
    scope = ProviderScope.APPROVED_PRODUCT
    key_handle_backed = False

    def sm3(self, data: bytes) -> bytes:
        return b"\x00" * 32

    def sign(self, handle, data: bytes) -> bytes:
        return b"sig"

    def verify(self, handle, data: bytes, signature: bytes) -> bool:
        return True

    def seal(self, handle, plaintext: bytes, *, associated_data: bytes, nonce=None):
        return ("wrapped", nonce, plaintext, b"tag")

    def open(self, handle, sealed, *, associated_data: bytes) -> bytes:
        return sealed[2]


def _uninitialized_prototype() -> GmsslPrototypeProvider:
    return GmsslPrototypeProvider.__new__(GmsslPrototypeProvider)


class ProviderRegistryTests(unittest.TestCase):
    def test_register_and_resolve(self):
        registry = ProviderRegistry()
        approved = FakeApprovedKeyHandleBackedProvider()
        registry.register("approved-vendor", approved)
        self.assertEqual(("approved-vendor",), registry.names())
        self.assertIs(approved, registry.resolve("approved-vendor"))

    def test_duplicate_and_invalid_registration_are_rejected(self):
        registry = ProviderRegistry()
        registry.register("approved-vendor", FakeApprovedKeyHandleBackedProvider())
        with self.assertRaises(ValueError):
            registry.register("approved-vendor", FakeApprovedKeyHandleBackedProvider())
        with self.assertRaises(TypeError):
            registry.register("junk", object())

    def test_resolve_missing_raises(self):
        with self.assertRaises(KeyError):
            ProviderRegistry().resolve("missing")

    def test_require_approved_rejects_prototype(self):
        registry = ProviderRegistry()
        registry.register("gmssl", _uninitialized_prototype())
        with self.assertRaises(ValueError):
            registry.require_approved("gmssl")

    def test_require_approved_rejects_without_key_handle(self):
        registry = ProviderRegistry()
        registry.register("approved-nohandle", FakeApprovedWithoutKeyHandle())
        with self.assertRaises(ValueError):
            registry.require_approved("approved-nohandle")

    def test_require_approved_accepts_key_handle_backed_provider(self):
        registry = ProviderRegistry()
        approved = FakeApprovedKeyHandleBackedProvider()
        registry.register("approved-vendor", approved)
        self.assertIs(approved, registry.require_approved("approved-vendor"))


class KeyHandlePolicyTests(unittest.TestCase):
    def test_prototype_is_not_key_handle_backed(self):
        prototype = _uninitialized_prototype()
        self.assertFalse(prototype.key_handle_backed)
        with self.assertRaises(ValueError):
            require_key_handle_backed(prototype)

    def test_approved_provider_declares_key_handle_backing(self):
        self.assertTrue(require_key_handle_backed(FakeApprovedKeyHandleBackedProvider()))

    def test_protected_key_handle_protocol(self):
        class Handle:
            handle_id = "h.1"
            certificate_id = "CERT-SENDER"
            algorithm_oid = "1.2.156.10197.1.301"

        self.assertIsInstance(Handle(), ProtectedKeyHandle)


if __name__ == "__main__":
    unittest.main()
