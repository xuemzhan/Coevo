# Approved Crypto Product / Key-Handle Onboarding Path

> Status: approved procedure (2026-08-02, business-owner approved the
> whole process). This document defines how an **approved production
> cryptographic product** and a **protected private-key handle** are
> onboarded into Coevo without runtime downloads, silent fallback, or
> raw key exposure.

## 1. Boundary

The locked open-source GmSSL 3.2.0 engine
(`coevo.crypto.GmsslPrototypeProvider`, Apache-2.0) is the project's
**functional crypto engine** since 2026-08-03 (business-owner approval
to use an open-source third-party library): real SM2 sign/verify, SM2
key transport, SM4-GCM authenticated encryption, and SM3 digests
(default digest paths use the pure-Python `coevo.crypto.sm3`
implementation, cross-checked against GmSSL). It is NOT a nationally
certified module and still uses test PKI + DPAPI key files, so it does
not satisfy the protected-key-handle requirement below. The formal
path below remains the long-term target for certified products and
protected handles.

## 2. Required artifacts for approval

Before a product can be approved, the business owner or vendor must
supply, offline:

1. Product name, exact version, vendor and provenance statement.
2. The offline binary/source archive with a published SHA-256 and size
   (the artifact must be placed into the local offline approval area;
   Coevo never downloads at runtime).
3. License text and permission to integrate, plus any support/security
   update commitments.
4. Capability evidence: SM2 sign/verify, SM2 key encapsulation, SM3
   digest, SM4-GCM authenticated encryption (official test vectors).
5. Key-handle mechanism: SKF / PKCS#11 / vendor OpenSSL provider /
   validated hardware module with non-exportable private keys.
6. Identity material: CA-issued sender and recipient SM2 certificate
   chains and revocation data (or a documented test-CA plan for the
   pilot).

## 3. Offline import procedure

1. Verify the archive hash, size, and provenance against the vendor
   publication (recorded in `docs/dependencies/evidence/`).
2. Unpack into the locked toolchain area (`.tools/<vendor>/<version>/`).
3. Add a `tools.<id>` entry to `docs/dependencies/toolchain-lock.json`
   with exact path, size, SHA-256, and Authenticode/vendor signature
   status. No un-locked binary may be loaded.
4. Register the provider binary/module path in the same lock; the
   Python launcher must verify the lock before any invocation.
5. Record the import and approval in `loop/DECISIONS.md` and the
   traceability matrix.

## 4. Provider contract

The approved product must implement the structural contract
`coevo.crypto.CryptoProvider` with `scope = ProviderScope.APPROVED_PRODUCT`:

* `sm3(data: bytes) -> bytes` -- SM3 digest.
* `sign(handle, data) -> bytes` / `verify(handle, data, signature) -> bool`
  -- SM2-SM3 signature over the canonical manifest bytes.
* `seal(handle, plaintext, *, associated_data, nonce) -> sealed` /
  `open(handle, sealed, *, associated_data) -> bytes` -- SM2 key wrap +
  SM4-GCM authenticated encryption of the inner payload, bound to the
  canonical envelope bytes as associated data.

Handles are non-secret identity references (profile/role/certificate
id). Private-key bytes, passwords, and unwrapped session keys never
enter Python objects, logs, argv, or model context.

Consumers (unchanged): `protocol.build_encrypted_package`,
`protocol.open_encrypted_package`, `protocol.sign_manifest`,
`protocol.verify_signature`, and
`orchestrator._real_chain.resume_real_chain` (explicit injection).
Policy enforcement uses `crypto.validate_provider_scope` with the
`APPROVED_PRODUCT` allow-list at the caller boundary.

## 5. Protected private-key handle requirements

* Keys MUST be non-exportable and held by CNG / Smart Card / SKF /
  PKCS#11 / HSM; the existing `coevo.identity.private_keys`
  `PrivateKeyStore` / `PrivateKeyService` seam is the integration
  point for handles.
* No PEM/PKCS#8 private-key file may be committed, logged, or
  referenced by the Python runtime.
* Signature/seal operations occur inside the trusted module or a
  controlled one-shot helper; only cryptographic results return to
  Python.

## 6. Acceptance gates

Onboarding is complete only when ALL hold:

1. `make quality` exit 0 with the product's integration tests (the
   prototype and product may run side by side under distinct scopes).
2. Independent security review: Critical/High/Medium = 0.
3. Protocol review passes for the `.agent` wire surface (no layout
   change is expected; cipher-suite metadata must be updated if a new
   suite is introduced).
4. Audit chain fully sealed and verification recorded in
   `loop/VERIFICATION.md`.
5. Traceability matrix has a `done` row binding the product, the
   contract, and the integration tests.
6. `loop/DECISIONS.md` records the approval, scope, and any
   exceptions.

## 7. Next step when a product arrives

The same loop discipline applies: DISCOVER (verify artifacts) ->
PLAN -> IMPLEMENT (adapter implementing `CryptoProvider` with
`APPROVED_PRODUCT` scope + key-handle integration) -> VERIFY ->
REVIEW (security + protocol) -> RECORD -> DECIDE. No runtime
downloads and no silent fallback to the prototype are permitted.

## 8. Status on protected key handle (2026-08-03, HANDLE-1 / HANDLE-2)

The protected-key-handle path is partially implemented:

* **Done (HANDLE-1)**: `coevo.crypto.CngKekStore` creates / opens /
  destroys a **non-exportable CNG RSA-2048 KEK** (ExportPolicy=None) via
  the controlled `scripts/cng-kek.ps1`; SM2 private-key material is
  wrapped at rest under that KEK (RSA-OAEP-SHA256) and only ciphertext +
  metadata are persisted in `CngWrappedKeyRegistry` (append-only SHA-256
  hash chain, tamper-rejecting open, revoke/destroy lifecycle).
  `GmsslProtectedProvider` (`key_handle_backed=True`, scope
  `APPROVED_PRODUCT`) satisfies the policy surface; `sm3` / `seal` /
  `verify` (public-key side) are functional today.
* **Remaining (HANDLE-2)**: a crypto-helper action that consumes the
  wrapped SM2 blob + KEK name **inside the helper**, unwraps with the
  CNG handle, and performs SM2 sign / open without ever returning the
  key to Python. Until wired, `sign` / `open` fail closed on
  `GmsslProtectedProvider`.
* **External**: a nationally certified SM2/SM3/SM4 module (SKF /
  PKCS#11 / validated hardware) still requires vendor procurement; the
  adapter contract in §4 and acceptance gates in §6 apply unchanged.
