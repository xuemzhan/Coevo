# `orchestrator/` — Orchestration Hub (US-4)

## Scope

Fixed-chain orchestration: agent registration/status, event dispatch,
human-confirmation gates, and the real-chain SQLite idempotent store with audit
recovery. MVP ships two fixed chains (dispatch, return).

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `AgentSpec/Registry`, `AgentCapability` (11 closed), `OrchestrationStep`, `FailurePolicy`, `MVP_FIXED_CHAIN` | Models + validation |
| `service.py` | `Orchestrator.dispatch_event/confirm_human` | Facade: event dispatch + confirmation + failure policy |
| `real_chain_store.py` | `RealChainStore` | SQLite idempotent store + hash-chained audit + anchor recovery |
| `_real_chain.py` | `dispatch_real_chain/confirm_real_chain/resume_real_chain` | Real facade chain: first 3 steps atomic, stop at human confirm, step 5 builds encrypted package + read-back check |

## Security invariants

- Every step persists atomically with audit; recovery requires anchor
  validation first;
- Human confirmation is mandatory; the confirmation digest binds the stored
  event digest (skipping confirmation cannot produce a package);
- Failure policy is deterministic (RETRY bounded, otherwise escalate to human);
  model output never writes formal state directly.

## Errors

- `OrchestratorValidationError` (fixable), `OrchestratorConflictError`
  (idempotency conflict), `RealChainStoreRecoveryRequired` (must `recover()`).

## Testing

- `tests/unit/test_orchestrator.py`, `test_real_chain_store.py`;
  `tests/integration/test_orchestrator_real_facade_chain.py`;
  `tests/e2e/test_demo_runner.py`.
