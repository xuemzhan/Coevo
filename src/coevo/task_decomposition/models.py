"""US-2 task decomposition domain model (US-2-AC-1).

Design notes
------------
* Every domain class is a frozen dataclass so a confirmed
  :class:`ProjectBaseline` is immutable once stored; later edits go
  through the override layer or produce a new baseline with a higher
  monotonic ``version``.
* Versions are integers, never timestamps (AGENTS.md §3 第 2 条).
* Dependency edges are explicit integer pairs ``(predecessor, successor)``
  so the DAG can be reconstructed deterministically without scanning
  task text.
* Cycle detection lives in :mod:`.dependency_graph` and runs at
  baseline-confirm time (fail-closed).
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field, replace


class TaskDecompositionError(Exception):
    """Base class for all US-2 errors. Fail-closed by default."""


class TaskDecompositionValidationError(TaskDecompositionError):
    """Raised when an input cannot be reconciled into a baseline.

    Distinct from :class:`TaskDecompositionError` so callers can branch
    on "validation failed (user-fixable)" vs "structural invariant
    violated (engineering bug)".
    """


@dataclass(frozen=True)
class Deliverable:
    """A single concrete deliverable attached to a task.

    ``deliverable_id`` is a stable identifier (e.g. ``"d.req_doc"``);
    ``kind`` is a closed enum so downstream audit code can reason
    about it without parsing free-form text.
    """

    deliverable_id: str
    title: str
    kind: str  # closed set enforced at parse-time in baseline.py
    acceptance_criteria: tuple[str, ...]


@dataclass(frozen=True)
class Task:
    """A single task within a work package.

    ``plan_start`` / ``plan_end`` are ISO-8601 UTC strings with the
    'Z' suffix; informational only (AGENTS.md §3 第 2 条 forbids
    using timestamps as version surrogates).
    """

    task_id: str
    title: str
    responsible_role: str
    plan_start: str
    plan_end: str
    deliverables: tuple[Deliverable, ...]


@dataclass(frozen=True)
class WorkPackage:
    """A grouped collection of tasks within a single standard stage.

    ``standard_stage`` references the US-1 :class:`StandardStage`
    enum value as a plain string so US-2 stays decoupled from US-1's
    enum identity (US-1 may grow the enum in future slices).
    """

    work_package_id: str
    standard_stage: str
    title: str
    tasks: tuple[Task, ...]


@dataclass(frozen=True)
class Milestone:
    """A delivery checkpoint attached to a baseline.

    Milestones are derived from work packages by the baseline
    factory; they are not user-edited in this AC.
    """

    milestone_id: str
    title: str
    target_date: str  # ISO-8601 UTC 'Z'
    work_package_id: str


@dataclass(frozen=True)
class DependencyEdge:
    """A directed dependency edge between two tasks.

    Edges are stored as ordered ``(predecessor_task_id, successor_task_id)``
    pairs so the DAG can be reconstructed deterministically. The graph
    builder verifies the pair is well-formed and that the task IDs
    resolve to known tasks at baseline-confirm time.
    """

    predecessor_task_id: str
    successor_task_id: str
    kind: str  # "fs" (finish-to-start) — single closed value at this AC

    def __post_init__(self) -> None:
        if self.kind != "fs":
            raise TaskDecompositionError(
                f"unsupported dependency kind {self.kind!r}; only 'fs' is supported"
            )
        if self.predecessor_task_id == self.successor_task_id:
            raise TaskDecompositionError(
                f"self-loop on task {self.predecessor_task_id!r} is forbidden"
            )


@dataclass(frozen=True)
class ProjectBaseline:
    """AC-7: a confirmed, versioned project baseline.

    ``project_id`` is the project name (matches US-2 user input); the
    pair ``(project_id, version)`` is unique. ``process_flow_ref``
    pins the baseline to the exact :class:`ProcessFlow` snapshot it
    was derived from (US-1 unit_id + version). This makes rollbacks
    deterministic and prevents accidental baseline↔flow drift.
    """

    project_id: str
    version: int
    created_at: str  # ISO-8601 UTC with 'Z' suffix (informational only)
    title: str
    process_flow_ref: tuple[str, int]  # (unit_id, process_flow_version)
    objective: str
    plan_start: str
    plan_end: str
    responsible_units: tuple[str, ...]
    work_packages: tuple[WorkPackage, ...]
    dependencies: tuple[DependencyEdge, ...]
    milestones: tuple[Milestone, ...]
    overrides: tuple["Override", ...] = field(default_factory=tuple)

    def with_overrides(
        self,
        overrides: tuple["Override", ...],
        new_created_at: str,
    ) -> "ProjectBaseline":
        """Return a new :class:`ProjectBaseline` at version+1 with overrides.

        Mirrors US-1's :meth:`ProcessFlow.with_overrides` so callers
        that already understand the override contract continue to work.
        """
        if not overrides:
            raise TaskDecompositionError("with_overrides requires non-empty overrides")
        if not new_created_at:
            raise TaskDecompositionError("new_created_at must be non-empty")
        return replace(
            self,
            version=self.version + 1,
            created_at=new_created_at,
            overrides=overrides,
        )


@dataclass(frozen=True)
class Override:
    """A reviewer edit applied to a baseline."""

    target_path: str
    original_value: object
    edited_value: object
    reason: str
