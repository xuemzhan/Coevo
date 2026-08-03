"""Unit tests for the crypto provider contract and scope governance."""
from __future__ import annotations

import unittest

from src.coevo.crypto import (
    CryptoProvider,
    GmsslPrototypeProvider,
    ProviderScope,
    declared_scope,
    validate_provider_scope,
)


def _uninitialized_prototype() -> GmsslPrototypeProvider:
    # Avoid touching the controlled launcher; class-level attrs are
    # sufficient for the structural contract checks.
    return GmsslPrototypeProvider.__new__(GmsslPrototypeProvider)


class FakeApprovedProvider:
    name = "approved-vendor-provider"
    scope = ProviderScope.APPROVED_PRODUCT

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


class CryptoContractTests(unittest.TestCase):
    def test_prototype_declares_mvp_prototype_scope(self):
        provider = _uninitialized_prototype()
        self.assertIs(provider.scope, ProviderScope.MVP_PROTOTYPE)
        self.assertIs(declared_scope(provider), ProviderScope.MVP_PROTOTYPE)

    def test_prototype_satisfies_provider_protocol(self):
        self.assertIsInstance(_uninitialized_prototype(), CryptoProvider)
        self.assertIsInstance(FakeApprovedProvider(), CryptoProvider)

    def test_approved_only_policy_rejects_prototype(self):
        with self.assertRaises(ValueError):
            validate_provider_scope(
                _uninitialized_prototype(),
                (ProviderScope.APPROVED_PRODUCT,),
            )
        self.assertIs(
            validate_provider_scope(
                _uninitialized_prototype(),
                (ProviderScope.MVP_PROTOTYPE, ProviderScope.APPROVED_PRODUCT),
            ),
            ProviderScope.MVP_PROTOTYPE,
        )

    def test_approved_provider_passes_approved_only_policy(self):
        self.assertIs(
            validate_provider_scope(
                FakeApprovedProvider(),
                (ProviderScope.APPROVED_PRODUCT,),
            ),
            ProviderScope.APPROVED_PRODUCT,
        )

    def test_undeclared_scope_fails_closed(self):
        class Undeclared:
            name = "anonymous"

            def sm3(self, data: bytes) -> bytes:
                return b"\x00" * 32

            def sign(self, handle, data: bytes) -> bytes:
                return b"sig"

            def verify(self, handle, data: bytes, signature: bytes) -> bool:
                return True

            def seal(self, handle, plaintext: bytes, *, associated_data: bytes, nonce=None):
                return (nonce, plaintext, b"tag")

            def open(self, handle, sealed, *, associated_data: bytes) -> bytes:
                return sealed[1]

        with self.assertRaises(TypeError):
            validate_provider_scope(Undeclared(), (ProviderScope.APPROVED_PRODUCT,))

    def test_invalid_allowed_argument_is_rejected(self):
        with self.assertRaises(TypeError):
            validate_provider_scope(FakeApprovedProvider(), ())  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            validate_provider_scope(FakeApprovedProvider(), "approved-product")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
