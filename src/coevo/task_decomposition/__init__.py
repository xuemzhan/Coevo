"""US-2 task decomposition (US-2-AC-1).

Scope (AC closed loop in this slice)
------------------------------------
* ``models.py`` — frozen dataclasses for ProjectBaseline, WorkPackage,
  Task, Milestone, Deliverable, DependencyEdge, plus strict monotonic
  version + ISO-8601 UTC 'Z' invariants (mirrors US-1 dataclass style).
* ``dependency_graph.py`` — deterministic DAG builder that consumes a
  US-1 :class:`StageGraph` and produces a cycle-checked dependency
  graph with a stable topological ordering. Cycle detection is
  fail-closed (raises :class:`TaskDecompositionError`).
* ``baseline.py`` — :class:`ProjectBaseline` factory that binds a
  process-flow snapshot (unit_id + version) to a decomposition
  proposal (tasks + dependencies + milestones). Strict monotonic
  version enforcement; baseline IDs are immutable.
* ``service.py`` — :class:`TaskDecompositionService` facade that
  pulls a :class:`FlowUnderstanding` from US-1 and emits a draft
  :class:`ProjectBaseline` without ever calling a model.

AC test matrix (each TestCase class locks one AC):
  AC-1  ``test_input_*`` — name / objective / window / units parsed.
  AC-5  ``test_dependency_*`` — cycle fail-closed + topo order.
  AC-7  ``test_baseline_*`` — strict monotonic version + ISO-8601 UTC.

What this is NOT
----------------
* No LLM call. ``service.decompose_from_flow`` is a deterministic
  state machine; the production 任务分解 agent is a future slice.
* No I/O. Inputs and outputs are Python objects only.
* No re-derivation of stage mappings — we consume the StageGraph that
  US-1-AC-2 already produced.
"""
from .models import (
    DependencyEdge,
    Deliverable,
    Milestone,
    ProjectBaseline,
    Task,
    TaskDecompositionError,
    TaskDecompositionValidationError,
    WorkPackage,
)
from .dependency_graph import (
    DependencyGraph,
    cycle_in_components,
    topological_order,
)
from .baseline import (
    BaselineInput,
    build_baseline,
    confirm_baseline,
)
from .service import TaskDecompositionService
from .editing import (
    add_task,
    remove_task,
    reorder_tasks,
    update_task,
)

__all__ = [
    "BaselineInput",
    "DependencyEdge",
    "DependencyGraph",
    "Deliverable",
    "Milestone",
    "ProjectBaseline",
    "Task",
    "TaskDecompositionError",
    "TaskDecompositionService",
    "TaskDecompositionValidationError",
    "WorkPackage",
    "add_task",
    "build_baseline",
    "confirm_baseline",
    "cycle_in_components",
    "remove_task",
    "reorder_tasks",
    "topological_order",
    "update_task",
]
