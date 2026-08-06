# `audit_governance/` — Security Audit (US-15)

## Scope

Unified audit-event model, interception decisions, query/export, and a durable
JSONL + SHA-256 hash-chained audit stream. This is the "full traceability" and
"tamper-detectable audit" layer.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `AuditEvent`, `InterceptionReason`, `AuditQuery`, `AuditExportPayload` | Event model, five-class interception reasons, query/export payloads and validation |
| `facade.py` | `SecurityAuditFacade.evaluate_interception/query_events/export_events` | Central interception decision, paged query (hard cap), stable-digest export |
| `stream.py` | `AuditStreamHub`, `AuditSubscription` | In-memory publish/subscribe + history replay (fail-isolated delivery) |
| `stream_store.py` | `AuditStreamStore` | JSONL + hash-chain persistence, append-exclusive, incremental size accounting |

## Security invariants

- Core `AuditEvent` fields are mandatory (ts/actor/source/action/result);
  sensitive text is stored as hashes/counts only;
- Hash chain `prev_hash → record_hash`; tampering breaks the chain;
- Interception reasons: CORRUPTED, TAMPERED, EXPIRED, DUPLICATE,
  RECIPIENT_MISMATCH — positional precedence, CORRUPTED short-circuits TAMPERED,
  other reasons are independent and all listed;
- Export digests are content-stable.

## Errors

- `AuditEventValidationError` / `AuditQueryValidationError`,
  `AuditGovernanceError`, `AuditStreamStoreError`; chain breaks and size
  overruns fail closed.

## Testing

- `tests/unit/test_audit_governance.py` (event/interception/query/export/
  projection), `test_audit_stream.py`, `test_audit_stream_store.py`;
- `tests/integration/test_audit_stream.py`; `tests/security/test_audit_log.py`,
  `test_audit_seal.py`.

## Dependencies and consumers

- **Upstream**: every domain module's `to_audit_record` projection;
- **Downstream**: cockpit audit queries, `examples/service-api` audit services.
