"""Cryptographic provider contract and scope governance.

Scope governance
----------------
Coevo distinguishes two provider scopes:

* ``MVP_PROTOTYPE`` -- the locked GmSSL 3.2.0 prototype
  (:class:`coevo.crypto.GmsslPrototypeProvider`). It is approved for
  MVP demonstration only: test PKI, DPAPI-encrypted key files, and a
  one-shot controlled helper. It MUST NOT be presented as production
  cryptography.
* ``APPROVED_PRODUCT`` -- a formally approved cryptographic product
  (SKF / PKCS#11 / vendor OpenSSL provider / validated hardware
  module) that was imported offline, hash-locked in
  ``docs/dependencies/toolchain-lock.json``, security-reviewed and
  protocol-reviewed. The approved path additionally requires a
  protected private-key handle (non-exportable CNG / Smart Card /
  HSM); raw key bytes never enter the repository, logs, or model
  context.

The orchestration layer receives providers by explicit injection only
(see ``coevo.orchestrator._real_chain.resume_real_chain``); a provider
must declare a scope so policy can reject prototype providers wherever
an approved product is required.
"""
from __future__ import annotations

import enum
from typing import Any, Protocol, runtime_checkable


class ProviderScope(enum.Enum):
    """The approval scope of a crypto provider."""

    MVP_PROTOTYPE = "mvp-prototype"
    APPROVED_PRODUCT = "approved-product"


@runtime_checkable
class CryptoProvider(Protocol):
    """Structural contract every Coevo crypto provider must satisfy.

    Handles are non-secret identity references (profile / role /
    certificate_id); private-key bytes and passwords never enter
    Python objects, logs, or model context. ``seal`` returns an
    opaque sealed payload (wrapped key + nonce + ciphertext + tag);
    ``open`` reverses it with the same associated data.
    """

    name: str
    scope: ProviderScope

    def sm3(self, data: bytes) -> bytes: ...

    def sign(self, handle: Any, data: bytes) -> bytes: ...

    def verify(self, handle: Any, data: bytes, signature: bytes) -> bool: ...

    def seal(
        self,
        handle: Any,
        plaintext: bytes,
        *,
        associated_data: bytes,
        nonce: bytes | None = None,
    ) -> Any: ...

    def open(self, handle: Any, sealed: Any, *, associated_data: bytes) -> bytes: ...


def declared_scope(provider: Any) -> ProviderScope:
    """Return the provider scope, failing closed when undeclared."""
    scope = getattr(provider, "scope", None)
    if not isinstance(scope, ProviderScope):
        raise TypeError("provider must declare a ProviderScope")
    return scope


def validate_provider_scope(
    provider: Any,
    allowed: tuple[ProviderScope, ...],
) -> ProviderScope:
    """Fail closed unless the provider declares one of the allowed scopes."""
    if (
        not isinstance(allowed, tuple)
        or not allowed
        or not all(isinstance(scope, ProviderScope) for scope in allowed)
    ):
        raise TypeError("allowed must be a non-empty tuple of ProviderScope")
    scope = declared_scope(provider)
    if scope not in allowed:
        raise ValueError(
            f"provider scope {scope.value!r} is not allowed; "
            f"allowed={[item.value for item in allowed]}"
        )
    return scope
