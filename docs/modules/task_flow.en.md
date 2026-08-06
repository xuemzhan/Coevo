# `task_flow/` — Process Flow Understanding (US-1)

## Scope

Parses canonical/tabular/tree inputs into a unified flow model, maps nodes to
standard stages, and builds stage graphs and review views; supports audited
Override edits with monotonic versions.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `Traced`, `ProcessFlow`, `Override`, `Stage`, `StandardStage` | Models: value + source path + confidence + SourceKind; monotonic versions |
| `parser.py` | `parse_flow()` | Deterministic three-schema parsing (fail-closed) |
| `mapping.py` | `apply_mapping()`, `DEFAULT_MAPPING_RULES` (27) | Rule-table mapping with O(1) lookup |
| `service.py` | `FlowUnderstandingService.understand/confirm`, `StageGraph`, `ReviewerView` | Parse → map → graph → review view; confirm bumps version via Override |

## Security invariants

- Duplicate IDs, invalid types, confidence out of [0,1], non-UTF-8 all
  fail-closed; output is deterministic (input-order independent);
- Every field carries source_path + confidence + SourceKind; audit projections
  record structural facts only.

## Testing

- `tests/unit/test_task_flow_models.py` (18), `test_task_flow_service.py` (27).
