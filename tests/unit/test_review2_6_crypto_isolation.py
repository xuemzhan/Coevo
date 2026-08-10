"""REVIEW2-6: crypto prototype/production isolation guard tests.

Contract (docs/architecture/crypto-mode-isolation.md):

* ``crypto_mode(provider)`` reports ``prototype`` | ``production`` and
  fails closed on undeclared/unknown scope;
* ``require_production_crypto`` refuses prototype providers and
  non-key-handle-backed providers at startup (fail-closed);
* ``ProviderRegistry.require_approved`` refuses prototype providers;
* the real GmSSL prototype provider always declares ``mvp-prototype``
  and can never satisfy the production guard.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.crypto import (
    ProviderRegistry,
    ProviderScope,
    crypto_mode,
    require_production_crypto,
)
from src.coevo.crypto.contract import declared_scope
from src.coevo.crypto.gmssl_provider import GmsslPrototypeProvider

ROOT = Path(__file__).resolve().parents[2]


class _Stub:
    name = "stub"

    def __init__(self, scope: ProviderScope, key_handle_backed: bool) -> None:
        self.scope = scope
        self.key_handle_backed = key_handle_backed

    def sm3(self, data: bytes) -> bytes:
        return b""

    def sign(self, handle: object, data: bytes) -> bytes:
        return b""

    def verify(self, handle: object, data: bytes, signature: bytes) -> bool:
        return False

    def seal(
        self,
        handle: object,
        plaintext: bytes,
        *,
        associated_data: bytes,
        nonce: bytes | None = None,
    ) -> object:
        return object()

    def open(
        self, handle: object, sealed: object, *, associated_data: bytes
    ) -> bytes:
        return b""


class CryptoIsolationTests(unittest.TestCase):
    def test_crypto_mode_reports_prototype(self) -> None:
        self.assertEqual(
            crypto_mode(_Stub(ProviderScope.MVP_PROTOTYPE, False)),
            "prototype",
        )

    def test_crypto_mode_reports_production(self) -> None:
        self.assertEqual(
            crypto_mode(_Stub(ProviderScope.APPROVED_PRODUCT, True)),
            "production",
        )

    def test_crypto_mode_undeclared_fails_closed(self) -> None:
        with self.assertRaises(TypeError):
            crypto_mode(object())

    def test_require_production_refuses_prototype_at_startup(self) -> None:
        with self.assertRaises(ValueError):
            require_production_crypto(
                _Stub(ProviderScope.MVP_PROTOTYPE, False)
            )

    def test_require_production_accepts_approved_key_handle_backed(self) -> None:
        provider = _Stub(ProviderScope.APPROVED_PRODUCT, True)
        self.assertIs(require_production_crypto(provider), provider)

    def test_require_production_refuses_approved_without_key_handle(self) -> None:
        with self.assertRaises(ValueError):
            require_production_crypto(
                _Stub(ProviderScope.APPROVED_PRODUCT, False)
            )

    def test_registry_require_approved_refuses_prototype(self) -> None:
        registry = ProviderRegistry()
        registry.register(
            "proto", _Stub(ProviderScope.MVP_PROTOTYPE, False)
        )
        with self.assertRaises(ValueError):
            registry.require_approved("proto")

    def test_real_prototype_provider_declares_prototype_mode(self) -> None:
        provider = GmsslPrototypeProvider(ROOT)
        self.assertEqual(
            declared_scope(provider), ProviderScope.MVP_PROTOTYPE
        )
        self.assertEqual(crypto_mode(provider), "prototype")
        with self.assertRaises(ValueError):
            require_production_crypto(provider)

    def test_doc_exists(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "crypto-mode-isolation.md"
        ).read_text(encoding="utf-8")
        self.assertIn("prototype", text)
        self.assertIn("production", text)
        self.assertIn("require_production_crypto", text)


if __name__ == "__main__":
    unittest.main()
