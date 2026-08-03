"""HANDLE-1: CNG-protected, key-handle-backed GmSSL provider.

This provider satisfies the ``APPROVED_PRODUCT`` policy surface
(``key_handle_backed=True``, explicit ``ProviderScope.APPROVED_PRODUCT``)
while delegating the underlying SM3 / SM4-GCM / public-key SM2
operations to the locked open-source GmSSL 3.2.0 engine
(:class:`GmsslPrototypeProvider`).

Protected-handle boundary (see ``cng_handle.py``):

* the SM2 private-key material is wrapped at rest under a non-exportable
  CNG RSA KEK and only ciphertext + metadata are stored;
* ``sign`` / ``open`` require unwrapping that private key **inside the
  controlled crypto helper** (wrapped blob + KEK name consumed by the
  helper, raw bytes never cross to Python). That helper action is
  HANDLE-2; until it is wired these operations fail closed with a
  precise error instead of silently using the unprotected prototype
  profile path.
* ``sm3`` (hash), ``seal`` (recipient public key + SM4-GCM) and
  ``verify`` (public certificate) are functional today because they do
  not need the protected private key.
"""
from __future__ import annotations

from typing import Any, Final

from .cng_handle import CngKekError, CngKekStore, CngProtectedKeyHandle
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
    ) -> None:
        for method in ("sm3", "seal", "verify"):
            if not callable(getattr(engine, method, None)):
                raise CngKekError(f"engine must implement {method}()")
        if not isinstance(kek_store, CngKekStore):
            raise CngKekError("kek_store must be CngKekStore")
        if not isinstance(handle, CngProtectedKeyHandle):
            raise CngKekError("handle must be CngProtectedKeyHandle")
        self._engine = engine
        self._kek_store = kek_store
        self._handle = handle

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
        raise CngKekError(
            "HANDLE-2: CNG-protected SM2 signing requires the crypto-helper "
            "unwrap action (wrapped SM2 blob + KEK name consumed inside the "
            "helper); refusing to fall back to the unprotected prototype path"
        )

    def open(self, handle: Any, sealed: Any, *, associated_data: bytes) -> bytes:
        raise CngKekError(
            "HANDLE-2: CNG-protected SM2 unwrap/open requires the crypto-helper "
            "unwrap action; refusing to fall back to the unprotected prototype path"
        )


__all__ = ["GmsslProtectedProvider"]
