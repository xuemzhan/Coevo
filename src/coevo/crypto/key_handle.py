"""Protected key-handle contract for the approved-product path.

An approved production provider must be backed by a protected,
non-exportable key handle (CNG / Smart Card / SKF / PKCS#11 / HSM).
This module documents that requirement as a structural contract and a
policy flag so the application layer can reject any provider that
cannot prove key-handle backing (``key_handle_backed=True``).

The GmSSL 3.2.0 MVP prototype (``key_handle_backed=False``) therefore
cannot satisfy ``ProviderRegistry.require_approved`` -- exactly the
separation the business owner approved.

HANDLE-1 (2026-08-03) adds the first key-handle-backed provider:
``coevo.crypto.GmsslProtectedProvider`` (``key_handle_backed=True``,
scope ``APPROVED_PRODUCT``) whose SM2 private-key material is wrapped at
rest under a non-exportable CNG RSA KEK (``coevo.crypto.CngKekStore`` /
``coevo.crypto.CngWrappedKeyRegistry``). Unwrapping for SM2 sign/open
happens inside the controlled crypto helper (HANDLE-2); until that
helper action is wired, those operations fail closed with a precise
error rather than falling back to the unprotected prototype path.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtectedKeyHandle(Protocol):
    """A non-secret reference to a non-exportable private key.

    Implementations must never expose raw private-key bytes, passwords,
    or unwrapped session keys to Python.
    """

    handle_id: str
    certificate_id: str
    algorithm_oid: str


@runtime_checkable
class KeyHandleBacked(Protocol):
    """Marker every approved provider must declare."""

    key_handle_backed: bool


def require_key_handle_backed(provider: Any) -> bool:
    """Fail closed unless the provider explicitly declares handle backing."""
    if getattr(provider, "key_handle_backed", False) is not True:
        raise ValueError("provider must declare key_handle_backed=True")
    return True
