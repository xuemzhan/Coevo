# `identity/` — Identity and Trust (US-0)

## Scope

Offline identity and trust: user/client/org/certificate/role registration,
controlled X.509 inspection, private-key handle interface (bytes never enter
Python), SQLite persistence and signed audit anchors with freshness
monotonicity.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `Actor`, `UserIdentity`, `ClientIdentity`, `TrustedCertificate`, `ProjectRoleBinding` | Immutable identity/certificate models (unique certificate fingerprint) |
| `validation.py` | `validate_bundle()`, `reject_sensitive_input()` | Pre-store validation: sensitive-key rejection, closed role set, certificate usability |
| `certificates.py` | `inspect_certificate()` | X.509 via controlled PowerShell helper (input/output DER digest must match) |
| `private_keys.py` | `PrivateKeyReference`, `PrivateKeyService` | Handle interface: metadata only; validity/revocation/destroy policy + hash-chained audit |
| `repository.py` | `IdentityRepository` | SQLite: atomic five-table registration, unique-certificate constraint, audit anchor |
| `service.py` | `IdentityService.register_identity_bundle()` | Authorize → validate → register → audit; `request_id` idempotent |
| `audit_anchor.py` | `SignedAuditAnchor` | Signed audit head + per-generation non-exportable freshness (anti-rollback/anti-tamper) |

## Security invariants

- Private-key bytes/passwords never enter Python; handle payloads reject
  sensitive fields heuristically;
- Certificate fingerprint conflicts roll back and record `conflict`; repeated
  `request_id` is idempotent;
- Audit anchor signature chain + freshness monotonic checks fail closed.

## Errors

- `ValidationError`/`SensitiveInputError`, `PrivateKeyValidationError`/
  `PrivateKeyHandleError`/`PrivateKeyRevokedError`/`PrivateKeyUsageError`,
  `ConflictError` (fingerprint conflict), `UnauthorizedError`,
  `AuditAnchorError`.

## Testing

- Unit: `test_identity_validation.py`, `test_private_key_handles_bindings.py`;
- Integration: `identity_store_test.py`, `private_key_windows_store_test.py`;
- Security: `test_identity_store_security.py`, `test_identity_freshness_security.py`,
  `test_identity_retirement_security.py`, `test_private_key_storage.py`;
- E2E: `test_identity_dev_environment.py`.

## Dependencies and consumers

- **Upstream**: `crypto/cng_handle`, `scripts/inspect_certificate.ps1`,
  `scripts/store_private_key.ps1`;
- **Downstream**: `protocol/`, `merge/`, `decision_brief/`.
