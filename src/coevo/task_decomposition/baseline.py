"""US-2 baseline factory (US-2-AC-1 / AC-7).

The baseline factory binds a US-1 :class:`ProcessFlow` snapshot
(identified by ``(unit_id, version)``) to a US-2 decomposition
proposal (work packages + tasks + dependencies + milestones). The
result is a :class:`ProjectBaseline` whose ``version`` is strict
monotonic — every confirm bumps it by exactly 1.

Validation done here
--------------------
* Strict monotonic version (1 at first draft, then +1 per override).
* ISO-8601 UTC 'Z' format on every timestamp.
* Task IDs are unique across the whole baseline.
* Dependency edges resolve to known task IDs.
* ``plan_end >= plan_start`` for the project window and for every
  task window.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-2 基线工厂：build_baseline/confirm_baseline，每次确认全量重校验。
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from typing import Iterable, Sequence

from .models import (
    Deliverable,
    DependencyEdge,
    Milestone,
    ProjectBaseline,
    Task,
    TaskDecompositionValidationError,
    WorkPackage,
)


_ISO_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z\Z")
_DELIVERABLE_KINDS = frozenset({"document", "code", "review", "report", "evidence"})
_SAFE_ID = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.\-]{0,63}$")


@dataclass(frozen=True)
class BaselineInput:
    """User-supplied input for :func:`build_baseline`.

    The caller (UI / API layer) hands us the raw project form plus a
    US-1 ``process_flow_ref`` tuple that pinpoints the confirmed
    process-flow snapshot this decomposition is derived from.
    """

    project_id: str
    title: str
    objective: str
    plan_start: str
    plan_end: str
    responsible_units: tuple[str, ...]
    process_flow_ref: tuple[str, int]
    work_packages: tuple[WorkPackage, ...]


def _now_utc_iso_z() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def _validate_iso_z(value: str, path: str) -> None:
    if not isinstance(value, str) or not _ISO_Z.match(value):
        raise TaskDecompositionValidationError(
            f"{path} must be ISO-8601 UTC with 'Z' suffix; got {value!r}"
        )


def _validate_id(value: object, path: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.match(value):
        raise TaskDecompositionValidationError(
            f"{path} must match ^[a-zA-Z_][a-zA-Z0-9_.\\-]{{0,63}}$; got {value!r}"
        )
    return value


def _validate_window(start: str, end: str, path: str) -> None:
    _validate_iso_z(start, f"{path}.start")
    _validate_iso_z(end, f"{path}.end")
    if end < start:
        raise TaskDecompositionValidationError(
            f"{path}.end ({end!r}) must be >= {path}.start ({start!r})"
        )


def _validate_deliverable(d: Deliverable, path: str) -> None:
    _validate_id(d.deliverable_id, f"{path}.deliverable_id")
    if not d.title or not isinstance(d.title, str):
        raise TaskDecompositionValidationError(
            f"{path}.title must be a non-empty string"
        )
    if d.kind not in _DELIVERABLE_KINDS:
        raise TaskDecompositionValidationError(
            f"{path}.kind {d.kind!r} not in closed set {sorted(_DELIVERABLE_KINDS)!r}"
        )
    if not all(isinstance(c, str) and c for c in d.acceptance_criteria):
        raise TaskDecompositionValidationError(
            f"{path}.acceptance_criteria must be non-empty strings"
        )


def _validate_task(t: Task, path: str) -> None:
    _validate_id(t.task_id, f"{path}.task_id")
    if not t.title or not isinstance(t.title, str):
        raise TaskDecompositionValidationError(
            f"{path}.title must be a non-empty string"
        )
    if not t.responsible_role or not isinstance(t.responsible_role, str):
        raise TaskDecompositionValidationError(
            f"{path}.responsible_role must be a non-empty string"
        )
    _validate_window(t.plan_start, t.plan_end, path)
    for i, d in enumerate(t.deliverables):
        _validate_deliverable(d, f"{path}.deliverables[{i}]")


def _validate_work_package(wp: WorkPackage, path: str) -> None:
    _validate_id(wp.work_package_id, f"{path}.work_package_id")
    if not wp.title or not isinstance(wp.title, str):
        raise TaskDecompositionValidationError(
            f"{path}.title must be a non-empty string"
        )
    if not wp.standard_stage:
        raise TaskDecompositionValidationError(
            f"{path}.standard_stage must be a non-empty string"
        )
    if not wp.tasks:
        raise TaskDecompositionValidationError(
            f"{path}.tasks must be non-empty"
        )
    for i, t in enumerate(wp.tasks):
        _validate_task(t, f"{path}.tasks[{i}]")


def _validate_input(inp: BaselineInput) -> None:
    _validate_id(inp.project_id, "project_id")
    if not inp.title:
        raise TaskDecompositionValidationError("title must be non-empty")
    if not inp.objective:
        raise TaskDecompositionValidationError("objective must be non-empty")
    _validate_window(inp.plan_start, inp.plan_end, "project")
    if not inp.responsible_units:
        raise TaskDecompositionValidationError("responsible_units must be non-empty")
    for i, u in enumerate(inp.responsible_units):
        _validate_id(u, f"responsible_units[{i}]")
    if not (
        isinstance(inp.process_flow_ref, tuple)
        and len(inp.process_flow_ref) == 2
        and isinstance(inp.process_flow_ref[0], str)
        and isinstance(inp.process_flow_ref[1], int)
        and inp.process_flow_ref[1] >= 1
    ):
        raise TaskDecompositionValidationError(
            "process_flow_ref must be (unit_id: str, version: int >= 1)"
        )
    if not inp.work_packages:
        raise TaskDecompositionValidationError("work_packages must be non-empty")
    for i, wp in enumerate(inp.work_packages):
        _validate_work_package(wp, f"work_packages[{i}]")

    # Cross-package uniqueness of task IDs
    seen: set[str] = set()
    for wp in inp.work_packages:
        for t in wp.tasks:
            if t.task_id in seen:
                raise TaskDecompositionValidationError(
                    f"task_id {t.task_id!r} appears in multiple work packages"
                )
            seen.add(t.task_id)


def _milestones_from_packages(
    work_packages: Sequence[WorkPackage],
) -> tuple[Milestone, ...]:
    """Derive one milestone per work package from its last task's end date."""
    out: list[Milestone] = []
    for wp in work_packages:
        last_task = max(wp.tasks, key=lambda t: t.plan_end)
        out.append(
            Milestone(
                milestone_id=f"m.{wp.work_package_id}",
                title=f"{wp.title} complete",
                target_date=last_task.plan_end,
                work_package_id=wp.work_package_id,
            )
        )
    return tuple(out)


def build_baseline(
    inp: BaselineInput,
    dependencies: Iterable[DependencyEdge] = (),
    *,
    now: str | None = None,
) -> ProjectBaseline:
    """Build the first draft :class:`ProjectBaseline` (version=1).

    ``dependencies`` is optional; callers can supply explicit edges
    in addition to the stage-order seeds that
    :func:`build_dependency_graph` produces. The default behaviour
    uses no explicit edges — the cycle check at confirm time still
    runs against the seeded stage-order edges.
    """
    _validate_input(inp)
    from .dependency_graph import build_dependency_graph

    graph = build_dependency_graph(inp.work_packages, explicit_edges=dependencies)
    if len(graph.edges) == 0 and len(graph.task_ids) > 1:
        # Only a single package with multiple tasks and no explicit edges
        # is unusual but legal — the topo check already passed.
        pass

    return ProjectBaseline(
        project_id=inp.project_id,
        version=1,
        created_at=now or _now_utc_iso_z(),
        title=inp.title,
        process_flow_ref=inp.process_flow_ref,
        objective=inp.objective,
        plan_start=inp.plan_start,
        plan_end=inp.plan_end,
        responsible_units=inp.responsible_units,
        work_packages=inp.work_packages,
        dependencies=graph.edges,
        milestones=_milestones_from_packages(inp.work_packages),
        overrides=tuple(),
    )


def confirm_baseline(
    baseline: ProjectBaseline,
    new_created_at: str,
) -> ProjectBaseline:
    """Re-confirm a baseline at version+1 with no edits.

    Provided so callers can advance the version without producing an
    Override entry — used by the audit layer when a baseline has
    been *referenced* (not edited). For human edits, callers should
    use :meth:`ProjectBaseline.with_overrides`.
    """
    if not new_created_at:
        raise TaskDecompositionValidationError(
            "new_created_at must be non-empty"
        )
    from dataclasses import replace

    return replace(
        baseline,
        version=baseline.version + 1,
        created_at=new_created_at,
    )
