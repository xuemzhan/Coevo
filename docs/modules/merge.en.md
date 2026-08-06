# `merge/` — State Merge (US-10)

## Scope

Field-level merge decisions, project master-version updates, signed receipts
and a sealed receipt store, using the verified import and an authoritative
signature as the trust boundary. Timestamp-only overrides are forbidden.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `FieldMerge`, `MergeDecision`, `MergeProposal`, `MergeRecord`, `MISSING` | Field-merge/proposal/record models + sentinel + errors |
| `engine.py` | `MergeEngine.merge/merge_and_commit` | P1..P4 checks → per-field merge → commit (any HOLD rejects) |
| `receipt.py` | `build_signed_merge_commit_receipt`, `verify_signed_receipt`, `MergeCommitReceiptStore` | Signed receipt + sealed store (full re-verify on access) + frozen baseline snapshot |
| `repository.py` | `MergeReceiptRepository` | SQLite receipt history + freshness anchor + streaming row validation |

## Security invariants

- The decision maker is derived from the verified import recipient and must be
  in the project allow-list (mandatory constraint §8.4); an **empty allow-list
  rejects everything**;
- `base_revision` mismatch → HOLD with a three-way diff, never auto-overwrite;
- Receipt snapshots are frozen; the receipt chain must advance exactly once per
  commit; history is validated row-by-row;
- Audit projections exclude field details (counts/decisions only).

## Errors

- `MergeValidationError` (fixable input), `MergeError` (invariant broken),
  `MergeCommitReceiptError` (receipt build/verify), `MergeReceiptRepositoryError`
  / `AuditAnchorError` (persistence/anchor).

## Testing

- `tests/unit/test_merge_engine.py`, `test_merge_engine_v3.py`,
  `test_merge_commit_receipt.py`;
- `tests/security/test_merge_receipt_repository.py`;
- `tests/integration/test_merge_risk_receipt_chain.py`;
- `tests/e2e/test_return_chain.py`.

## Dependencies and consumers

- **Upstream**: `protocol`, `report`, `task_decomposition`, `identity`;
- **Downstream**: `risk`, `decision_brief`, `knowledge_base`.
