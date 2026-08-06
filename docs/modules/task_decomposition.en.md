# `task_decomposition/` — Task Decomposition (US-2)

## Scope

Baseline factory, dependency graph, audited task editing and a model-assisted
suggestion agent (drafts only): turns flow models into executable, trackable,
verifiable baselines.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `Task`, `WorkPackage`, `Milestone`, `DependencyEdge`, `ProjectBaseline` | Models (frozen, monotonic versions; self-loops forbidden) |
| `baseline.py` | `build_baseline()`, `confirm_baseline()` | Build v1 / confirm (+1, full re-validation) |
| `dependency_graph.py` | `DependencyGraph`, `cycle_in_components()`, `topological_order()` | Adjacency index, heap topological sort O((V+E) log V), explicit-stack cycle detection |
| `editing.py` | `add/remove/update/reorder_tasks` | Edit + Override audit (re-validated via build_baseline) |
| `service.py` | `TaskDecompositionService.propose()` | Facade: group by standard stage |
| `agent.py` | `TaskDecompositionAgent.suggest()` | Model-assisted suggestions (drafts only) |

## Security invariants

- Task IDs globally unique; dependencies acyclic (self-loop and cycles
  fail-closed); versions strictly monotonic;
- Suggestions require human confirmation before writing formal state.

## Testing

- `tests/unit/test_task_decomposition.py` (23), `test_task_decomposition_agent.py`,
  `test_task_decomposition_editing.py`.
