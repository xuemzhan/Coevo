# `talent/` — Team Formation (US-3)

## Scope

Redacted talent pool, deterministic recommendations and SQLite persistence:
raw PII never enters models; scoring is reproducible; staffing is confirmed by
the project owner.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `Talent`, `TalentPool`, `RedactedIdentity`, `AvailabilityWindow`, `LoadAlert` | Models (minimal field contract) |
| `redaction.py` | `redact_identity()`, `stable_pool_code()` | Irreversible PII redaction (stable pool code + SHA-256 identity hash) |
| `recommender.py` | `recommend()`, `score_candidate()` | Deterministic scoring (pre-warmed sets, O(R·N)) |
| `service.py` | `TalentRecommenderService` | Facade: requirements → recommendations + reasons + alerts |
| `store.py` | `TalentStore` | SQLite persistence: hash chain, row validation, metadata cache |

## Security invariants

- Raw PII never enters models/logs; redacted identity = code + bounded hint +
  hash;
- Load alerts (AT_CAPACITY/OVER_CAPACITY) and window conflicts
  (WINDOW_CONFLICT) are detected; personnel changes are audited.

## Testing

- `tests/unit/test_talent_recommender.py` (32), `test_talent_store.py`;
  `tests/integration/test_talent_store_persistence.py`.
