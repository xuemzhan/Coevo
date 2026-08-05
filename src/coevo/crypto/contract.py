"""Cryptographic provider contract and scope governance.

Scope governance
----------------
Coevo distinguishes two provider scopes:

* ``MVP_PROTOTYPE`` -- the locked GmSSL 3.2.0 prototype
  (:class:`coevo.crypto.GmsslPrototypeProvider`). It is approved for
  the project's *functional* path since 2026-08-03 (business-owner
  approval to use the open-source GmSSL 3.2.0 engine, Apache-2.0):
  real SM2 signing/verification, SM2 key transport, SM3 digests and
  SM4-GCM via a one-shot controlled helper. It still uses test PKI
  and DPAPI-encrypted key files, and is NOT a nationally certified
  module.
* ``APPROVED_PRODUCT`` -- a formally approved cryptographic product
  (SKF / PKCS#11 / vendor OpenSSL provider / validated hardware
  module) that was imported offline, hash-locked in
  ``docs/dependencies/toolchain-lock.json``, security-reviewed and
  protocol-reviewed. The approved path additionally requires a
  protected private-key handle (non-exportable CNG / Smart Card /
  HSM); raw key bytes never enter the repository, logs, or model
  context.

The ``MVP_PROTOTYPE`` scope satisfies functional correctness but not
the protected-key-handle requirement; ``require_approved`` continues
to reject it wherever a protected key handle is mandatory (see
``docs/dependencies/approved-crypto-provider-path.md``).

The orchestration layer receives providers by explicit injection only
(see ``coevo.orchestrator._real_chain.resume_real_chain``); a provider
must declare a scope so policy can reject prototype providers wherever
an approved product is required.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 密码提供者契约与作用域治理：ProviderScope/declared_scope 强制，
# ProviderRegistry 只放行已批准作用域。
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


class ProviderRegistry:
    """Named, scope-aware provider registry with fail-closed resolution."""

    def __init__(self) -> None:
        self._providers: dict[str, Any] = {}

    def register(self, name: str, provider: Any) -> None:
        if not isinstance(name, str) or not name:
            raise TypeError("provider name must be a non-empty string")
        if name in self._providers:
            raise ValueError(f"provider {name!r} is already registered")
        if not isinstance(provider, CryptoProvider):
            raise TypeError("provider must satisfy the CryptoProvider contract")
        declared_scope(provider)
        self._providers[name] = provider

    def resolve(self, name: str) -> Any:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(f"no crypto provider named {name!r}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def require_approved(self, name: str) -> Any:
        """Resolve and enforce the approved-product + key-handle policy."""
        provider = self.resolve(name)
        validate_provider_scope(provider, (ProviderScope.APPROVED_PRODUCT,))
        if getattr(provider, "key_handle_backed", False) is not True:
            raise ValueError(
                "approved-product providers must be backed by a protected "
                "non-exportable key handle"
            )
        return provider
