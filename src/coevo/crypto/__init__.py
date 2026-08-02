"""Explicitly injected cryptographic providers for Coevo."""

from .contract import (
    CryptoProvider,
    ProviderScope,
    ProviderRegistry,
    declared_scope,
    validate_provider_scope,
)
from .key_handle import (
    KeyHandleBacked,
    ProtectedKeyHandle,
    require_key_handle_backed,
)
from .gmssl_provider import (
    GmsslPrototypeError,
    GmsslPrototypeHandle,
    GmsslPrototypeProvider,
    SealedPayload,
)

__all__ = [
    "CryptoProvider",
    "GmsslPrototypeError",
    "GmsslPrototypeHandle",
    "GmsslPrototypeProvider",
    "KeyHandleBacked",
    "ProtectedKeyHandle",
    "ProviderScope",
    "ProviderRegistry",
    "SealedPayload",
    "declared_scope",
    "require_key_handle_backed",
    "validate_provider_scope",
]
