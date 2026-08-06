# `risk/` — Risk Early Warning (US-11)

## Scope

Deterministic risk analysis over the latest authoritative merge receipt:
delay, missing predecessors, long silence, insufficient evidence, contagion and
coordination recommendations.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `Risk`, `RiskReport`, `RiskKind`, `SourceKind` | Models + validation (four closed risk kinds) |
| `analyzer.py` | `RiskAnalyzer`, `analyze_after_merge()`, `merge_and_analyze()` | Post-merge analysis: latest-receipt validation → rules → contagion → suggestions + audit projection |

## Security invariants

- Only the latest verified receipt is used (stale state rejected); the receipt
  chain must be version-continuous;
- Risk reports default to `requires_owner_confirmation=True`,
  `formally_released=False`; owner confirmation required before formal release.

## Testing

- `tests/unit/test_risk_analyzer.py`; `tests/integration/test_merge_risk_receipt_chain.py`;
  `tests/security/test_merge_receipt_repository.py`.
