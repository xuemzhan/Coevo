"""Offline identity registry for US-0-AC-1 + private-key interface for US-0-AC-2."""

from .models import Actor, RegistrationResult
from .private_keys import (
    PrivateKeyError,
    PrivateKeyHandleError,
    PrivateKeyHandleUnavailableError,
    PrivateKeyReference,
    PrivateKeyRevokedError,
    PrivateKeyService,
    PrivateKeyStore,
    PrivateKeyUsageError,
    PrivateKeyValidationError,
    WindowsPrivateKeyStore,
    format_handle,
    validate_handle_payload,
)
from .repository import ConflictError, IdentityRepository
from .service import IdentityService, UnauthorizedError
from .validation import SensitiveInputError, ValidationError

__all__ = [
    "Actor",
    "ConflictError",
    "IdentityRepository",
    "IdentityService",
    "PrivateKeyError",
    "PrivateKeyHandleError",
    "PrivateKeyHandleUnavailableError",
    "PrivateKeyReference",
    "PrivateKeyRevokedError",
    "PrivateKeyService",
    "PrivateKeyStore",
    "PrivateKeyUsageError",
    "PrivateKeyValidationError",
    "RegistrationResult",
    "SensitiveInputError",
    "UnauthorizedError",
    "ValidationError",
    "WindowsPrivateKeyStore",
    "format_handle",
    "validate_handle_payload",
]
