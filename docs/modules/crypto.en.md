# `crypto/` — National-Crypto Engine Adapters (SM2/SM3/SM4)

## Scope

Provider contract and scope governance, protected key-handle paths, the locked
GmSSL 3.2.0 prototype plus a pure-Python SM3. Formal deployments must replace
the prototype with an approved product (see
`docs/dependencies/approved-crypto-provider-path.md`).

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `contract.py` | `ProviderScope`, `CryptoProvider`, `ProviderRegistry` | Provider contract + scope governance (unknown scope fail-closed) |
| `gmssl_provider.py` | `GmsslPrototypeProvider` (seal/open/sign/verify/sign_wrapped) | Locked one-shot GmSSL 3.2.0 helper client; bounded retry on launch, never on crypto errors |
| `protected_provider.py` | `GmsslProtectedProvider` | CNG-handle-backed provider (HANDLE-1/2) |
| `cng_handle.py` | `CngProtectedKeyHandle`, `CngKekStore` | CNG-protected SM2 key handle: KEK wrapping, register/revoke/destroy |
| `key_handle.py` | `ProtectedKeyHandle`, `KeyHandleBacked` | Protected key-handle abstraction |
| `sm3.py` | `sm3_digest()`, `sm3_hexdigest()` | Pure-Python SM3 (GB/T 32905-2016) |

## Security invariants

- **Private-key bytes, passwords, and unwrapped session keys never enter the
  Python process**; only crypto results flow back;
- Helper launcher is hash-locked via `toolchain-lock.json`; tampering is
  rejected; session keys/nonces come from a cryptographic RNG;
- `GCP-E-*` diagnostics are authoritative and never retried; launch-level
  failures retry a bounded number of times.

## Errors

- `GmsslPrototypeError` (`AGT-CRY-001`) for helper/frame/crypto failures;
  `CngKekHelperError` for CNG KEK helper lock/timeout/return-code failures.

## Testing

- `tests/unit/test_crypto_contract.py`, `test_crypto_provider_registry.py`,
  `test_crypto_sm3.py`, `test_gmssl_provider_retry.py`;
- `tests/integration/test_gmssl_prototype_provider.py`, `test_crypto_sm3.py`,
  `test_cng_handle.py`, `test_sm2_test_pki_generation.py`.

## Dependencies and consumers

- **Upstream**: `docs/dependencies/toolchain-lock.json`, PowerShell;
- **Downstream**: `identity/private_keys`, `protocol/`, `app/pipeline`.
