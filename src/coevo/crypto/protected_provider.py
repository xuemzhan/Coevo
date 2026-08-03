"""HANDLE-1/2: CNG-protected, key-handle-backed GmSSL provider.

This provider satisfies the ``APPROVED_PRODUCT`` policy surface
(``key_handle_backed=True``, explicit ``ProviderScope.APPROVED_PRODUCT``)
while delegating the underlying SM3 / SM4-GCM / public-key SM2
operations to the locked open-source GmSSL 3.2.0 engine
(:class:`GmsslPrototypeProvider`).

Protected-handle boundary (see ``cng_handle.py``):

* the SM2 key's PKCS#8 password is wrapped at rest under a
  non-exportable CNG RSA KEK; the key itself stays encrypted under
  that password in the profile, and only the wrapped password blob +
  metadata are stored;
* ``sign`` / ``open`` unwrap that password **inside the controlled
  crypto helper** (actions 6/7: wrapped password blob + KEK name
  consumed by the helper; the helper decrypts the PKCS#8 key, signs /
  opens, and zeroizes the password and key in memory). Raw key bytes
  never cross to Python.
* ``sm3`` (hash), ``seal`` (recipient public key + SM4-GCM) and
  ``verify`` (public certificate) are functional today because they do
  not need the protected private key.
"""
from __future__ import annotations

from typing import Any, Final

from .cng_handle import CngKekError, CngKekReference, CngKekStore, CngProtectedKeyHandle
from .contract import ProviderScope


class GmsslProtectedProvider:
    """Key-handle-backed provider over the locked GmSSL 3.2.0 engine."""

    name: Final[str] = "gmssl-3.2.0-cng-protected"
    scope: Final[ProviderScope] = ProviderScope.APPROVED_PRODUCT
    key_handle_backed: Final[bool] = True

    def __init__(
        self,
        engine: Any,
        kek_store: CngKekStore,
        handle: CngProtectedKeyHandle,
        wrapped: bytes,
        kek_ref: CngKekReference,
        profile: str,
        role: str,
    ) -> None:
        for method in ("sm3", "seal", "verify"):
            if not callable(getattr(engine, method, None)):
                raise CngKekError(f"engine must implement {method}()")
        if not isinstance(kek_store, CngKekStore):
            raise CngKekError("kek_store must be CngKekStore")
        if not isinstance(handle, CngProtectedKeyHandle):
            raise CngKekError("handle must be CngProtectedKeyHandle")
        if not isinstance(wrapped, bytes) or not wrapped:
            raise CngKekError("wrapped must be non-empty bytes")
        if not isinstance(kek_ref, CngKekReference):
            raise CngKekError("kek_ref must be CngKekReference")
        if not isinstance(profile, str) or not profile:
            raise CngKekError("profile must be a non-empty string")
        if role not in {"sender", "recipient"}:
            raise CngKekError("role must be sender or recipient")
        self._engine = engine
        self._kek_store = kek_store
        self._handle = handle
        self._wrapped = wrapped
        self._kek_ref = kek_ref
        self._profile = profile
        self._role = role

    @property
    def handle(self) -> CngProtectedKeyHandle:
        return self._handle

    def sm3(self, data: bytes) -> bytes:
        return self._engine.sm3(data)

    def seal(
        self,
        handle: Any,
        plaintext: bytes,
        *,
        associated_data: bytes,
        nonce: bytes | None = None,
    ) -> Any:
        # Recipient public-key operation only: functional without the
        # protected private key.
        return self._engine.seal(
            handle, plaintext, associated_data=associated_data, nonce=nonce
        )

    def verify(self, handle: Any, data: bytes, signature: bytes) -> bool:
        # Public-certificate operation: functional without the private key.
        return self._engine.verify(handle, data, signature)

    def sign(self, handle: Any, data: bytes) -> bytes:
        return self._engine.sign_wrapped(
            self._kek_ref.kek_name,
            self._wrapped,
            data,
            role=self._role,
            profile=self._profile,
        )

    def open(self, handle: Any, sealed: Any, *, associated_data: bytes) -> bytes:
        return self._engine.open_wrapped(
            self._kek_ref.kek_name,
            self._wrapped,
            sealed,
            role=self._role,
            profile=self._profile,
            associated_data=associated_data,
        )


__all__ = ["GmsslProtectedProvider"]
