"""Explicitly injected cryptographic providers for Coevo."""

from .contract import (
    CryptoProvider,
    ProviderScope,
    ProviderRegistry,
    crypto_mode,
    declared_scope,
    require_production_crypto,
    validate_provider_scope,
)
from .cng_handle import (
    CngKekError,
    CngKekReference,
    CngKekStore,
    CngKekUnavailableError,
    CngKekValidationError,
    CngProtectedKeyHandle,
    CngWrappedKeyRegistry,
    KEK_NAME_RE,
    KEK_PREFIX,
    SM2_KEY_ALGORITHM_OID,
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
from .sm3 import (
    sm3_digest,
    sm3_hexdigest,
)
from .protected_provider import GmsslProtectedProvider

__all__ = [
    "CryptoProvider",
    "CngKekError",
    "CngKekReference",
    "CngKekStore",
    "CngKekUnavailableError",
    "CngKekValidationError",
    "CngProtectedKeyHandle",
    "CngWrappedKeyRegistry",
    "GmsslProtectedProvider",
    "KEK_NAME_RE",
    "KEK_PREFIX",
    "GmsslPrototypeError",
    "GmsslPrototypeHandle",
    "GmsslPrototypeProvider",
    "KeyHandleBacked",
    "ProtectedKeyHandle",
    "ProviderScope",
    "ProviderRegistry",
    "SealedPayload",
    "crypto_mode",
    "SM2_KEY_ALGORITHM_OID",
    "declared_scope",
    "require_production_crypto",
    "require_key_handle_backed",
    "sm3_digest",
    "sm3_hexdigest",
    "validate_provider_scope",
]
