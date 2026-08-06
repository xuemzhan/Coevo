# `protocol/` — Task Package Protocol (US-5, `.agent`)

## Scope

The `.agent` wire format: 36-byte Fixed Header + canonical Envelope, SM2 key
transport, SM4-GCM authenticated payload, SM3/SM2 signatures, replay/duplicate
detection, and a 7-step atomic import. Implements
`docs/protocol/agent-package-protocol.md` strictly.

## Boundaries

- **In scope**: fixed header, envelope, key-transport block, AEAD payload,
  signatures, processed-package registry, replay detection, atomic import.
- **Out of scope**: approved-crypto-product integration (reserved, unapproved
  algorithms are explicitly rejected), workspace initialization (`workspace/`).

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `agent_package.py` | `EnvelopeHeader`, `FixedHeader`, `parse_package_header()` | Byte-exact header/envelope codec; canonical JSON; length agreement; unknown flags/trailing data rejected |
| `agent_payload.py` | `PayloadBlock` | SM4-GCM payload layer (nonce/ciphertext/tag validation) |
| `sm2_keywrap.py` | `encode_key_transport_bytes()` | SM2 session-key transport block |
| `sm2_sign.py` | `compute_sm3_digest()`, sign/verify | SM2 signing + SM3 digest layer |
| `sm2_extension.py` | — | Placeholder for future approved algorithms (fail-closed) |
| `package_builder.py` | `build_encrypted_package/open_encrypted_package` | End-to-end build/parse (sign-blocked until approved product, read-back checks, handle-certificate binding) |
| `replay_detector.py` | `check_replay()`, `check_reference_target()` | Duplicate/replay/revocation/invalid-reference detection (protocol §17) |
| `import_transaction.py` | `AtomicImporter`, `ImportTransaction` | 7-step atomic import state machine (rollback, no half state) |
| `import_service.py` | `PackageImportService.import_package()` | Import facade: replay gate + fixed-header consistency + explicit revision requirement |
| `processed_package_store.py` | `ProcessedPackageStore` | In-memory processed-package registry (package_id/digest dedupe + indexes) |
| `package_store_db.py` | SQLite registry | Persistent processed packages: hash chain, row-level validation, unique constraints |

## Entry points and data flow

```
Build: state/manifest → build_unsigned_package → SM2 wrap + SM4-GCM → sender signature
  → Fixed/Envelope header → .agent file
Import: quarantine → parse_package_header → recipient/version/replay checks
  → decrypt/verify → file checks → PackageImportService (7-step tx) → workspace init
```

## Security invariants

- Canonical JSON (duplicate keys, non-canonical whitespace, BOM rejected);
  fixed-header lengths must agree with the actual blocks;
- Replay/duplicate/revoked/invalid-reference detection is fail-closed; the same
  package is never applied twice;
- **Sequence numbers must be strictly increasing** within a
  (sender, recipient, project) scope (protocol §13); an equal sequence with
  different content is a reordering/replay anomaly and is rejected;
- Atomic import rolls back on failure; abnormal packages stay quarantined;
- Unapproved algorithms are explicitly rejected; private keys/passwords never
  enter the protocol layer (controlled handles only).

## Testing

- `tests/integration/package_header_test.py` (56), `package_header_extended_test.py`,
  `test_agent_package_aead.py` (payload/key-transport/signature/replay),
  `test_agent_package_atomic_import.py`, `test_package_store_persistence.py`;
- `tests/unit/test_protocol_sign_blocked.py`; e2e in `test_demo_runner.py` /
  `test_return_chain.py`.

## Dependencies and consumers

- **Upstream**: `crypto` (operations), `identity` (certificates/handles),
  `docs/protocol/agent-package-protocol.md`;
- **Downstream**: `workspace`, `merge`, `report`, `orchestrator`, `cockpit`.

## Errors and performance

- Error codes follow protocol §22 (`AGT-PKG-*`, `AGT-ID-*`, `AGT-CRY-*`,
  `AGT-RPL-*`, `AGT-FILE-*`, `AGT-IMP-*`, `AGT-POL-*`, `AGT-TIME-*`);
- Bounded parsing (64 KiB envelope, 1 TiB payload hard cap); `payload_length`
  is the full cipher block size and is normalized by the builders and enforced
  by both parse surfaces (2026-08-07 OPTIMIZE-5); replay checks are a linear
  scan of the scope registry; atomic-import state transitions are O(1).
