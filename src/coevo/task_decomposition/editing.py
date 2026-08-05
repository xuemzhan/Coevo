"""US-2-AC-2 (AC-6): user task-editing operations over a baseline.

Every operation is a pure function over a :class:`ProjectBaseline`
and returns a *new* baseline at ``version + 1`` carrying an
:class:`Override` audit record. The rebuilt structure is re-validated
through :func:`build_baseline` (task-ID uniqueness, ISO-8601 UTC
windows, closed deliverable kinds, dependency cycle fail-closed,
deterministic milestones), so a single edited baseline cannot drift
into an invalid state.

Operations
----------
* :func:`add_task`       -- append a task to a work package.
* :func:`remove_task`    -- remove a task (refuses to empty a package).
* :func:`update_task`    -- modify title / role / window / deliverables.
* :func:`reorder_tasks`  -- reorder tasks inside a package (permutation).

Non-goals
---------
* No I/O, no UI, no LLM -- this is the deterministic edit surface.
* No cross-package task moves in this slice.
"""
from __future__ import annotations

import dataclasses
from dataclasses import replace
from typing import Iterable

from .baseline import BaselineInput, build_baseline
from .models import (
    Deliverable,
    Override,
    ProjectBaseline,
    Task,
    TaskDecompositionValidationError,
    WorkPackage,
)


def _freeze_override_value(value: object) -> object:
    """Flatten tuple fields for an Override record; other values pass through."""
    return dataclasses.asdict(value) if isinstance(value, tuple) else value


def _package_index(baseline: ProjectBaseline, work_package_id: str) -> int:
    for index, wp in enumerate(baseline.work_packages):
        if wp.work_package_id == work_package_id:
            return index
    raise TaskDecompositionValidationError(
        f"work_package {work_package_id!r} is not in the baseline"
    )


def _task_location(baseline: ProjectBaseline, task_id: str) -> tuple[int, int]:
    for wp_index, wp in enumerate(baseline.work_packages):
        for task_index, task in enumerate(wp.tasks):
            if task.task_id == task_id:
                return wp_index, task_index
    raise TaskDecompositionValidationError(
        f"task {task_id!r} is not in the baseline"
    )


def _rebuild(
    baseline: ProjectBaseline,
    work_packages: tuple[WorkPackage, ...],
    overrides: tuple[Override, ...],
    *,
    now: str,
) -> ProjectBaseline:
    """Re-validate and rebuild a baseline at version+1 with overrides."""
    if not overrides:
        raise TaskDecompositionValidationError(
            "rebuild requires at least one override"
        )
    draft = build_baseline(
        BaselineInput(
            project_id=baseline.project_id,
            title=baseline.title,
            objective=baseline.objective,
            plan_start=baseline.plan_start,
            plan_end=baseline.plan_end,
            responsible_units=baseline.responsible_units,
            process_flow_ref=baseline.process_flow_ref,
            work_packages=work_packages,
        ),
        now=now,
    )
    return replace(
        draft,
        version=baseline.version + 1,
        created_at=now,
        overrides=baseline.overrides + overrides,
    )


def add_task(
    baseline: ProjectBaseline,
    *,
    work_package_id: str,
    task: Task,
    reason: str,
    now: str,
) -> ProjectBaseline:
    """Append ``task`` to a work package and return baseline version+1."""
    if not isinstance(baseline, ProjectBaseline):
        raise TaskDecompositionValidationError(
            "baseline must be ProjectBaseline"
        )
    if not isinstance(task, Task):
        raise TaskDecompositionValidationError("task must be Task")
    existing = {
        t.task_id
        for wp in baseline.work_packages
        for t in wp.tasks
    }
    if task.task_id in existing:
        raise TaskDecompositionValidationError(
            f"task_id {task.task_id!r} already exists in the baseline"
        )
    wp_index = _package_index(baseline, work_package_id)
    packages = list(baseline.work_packages)
    wp = packages[wp_index]
    packages[wp_index] = replace(wp, tasks=wp.tasks + (task,))
    return _rebuild(
        baseline,
        tuple(packages),
        (Override(
            target_path=f"work_packages[{wp_index}].tasks",
            original_value=None,
            edited_value=task.task_id,
            reason=reason,
        ),),
        now=now,
    )


def remove_task(
    baseline: ProjectBaseline,
    *,
    task_id: str,
    reason: str,
    now: str,
) -> ProjectBaseline:
    """Remove ``task_id`` (refuses to empty a work package)."""
    wp_index, task_index = _task_location(baseline, task_id)
    packages = list(baseline.work_packages)
    wp = packages[wp_index]
    if len(wp.tasks) == 1:
        raise TaskDecompositionValidationError(
            "cannot remove the last task of a work package"
        )
    removed = wp.tasks[task_index]
    packages[wp_index] = replace(
        wp, tasks=wp.tasks[:task_index] + wp.tasks[task_index + 1 :]
    )
    return _rebuild(
        baseline,
        tuple(packages),
        (Override(
            target_path=f"work_packages[{wp_index}].tasks",
            original_value=removed.task_id,
            edited_value=None,
            reason=reason,
        ),),
        now=now,
    )


def update_task(
    baseline: ProjectBaseline,
    *,
    task_id: str,
    reason: str,
    now: str,
    title: str | None = None,
    responsible_role: str | None = None,
    plan_start: str | None = None,
    plan_end: str | None = None,
    deliverables: tuple[Deliverable, ...] | None = None,
) -> ProjectBaseline:
    """Modify selected fields of a task and return baseline version+1."""
    wp_index, task_index = _task_location(baseline, task_id)
    packages = list(baseline.work_packages)
    wp = packages[wp_index]
    task = wp.tasks[task_index]
    updates: dict[str, object] = {}
    if title is not None:
        updates["title"] = title
    if responsible_role is not None:
        updates["responsible_role"] = responsible_role
    if plan_start is not None:
        updates["plan_start"] = plan_start
    if plan_end is not None:
        updates["plan_end"] = plan_end
    if deliverables is not None:
        updates["deliverables"] = deliverables
    if not updates:
        raise TaskDecompositionValidationError(
            "update_task requires at least one field to change"
        )
    updated = replace(task, **updates)
    packages[wp_index] = replace(
        wp, tasks=wp.tasks[:task_index] + (updated,) + wp.tasks[task_index + 1 :]
    )
    return _rebuild(
        baseline,
        tuple(packages),
        (Override(
            target_path=f"work_packages[{wp_index}].tasks[{task_index}].{task_id}",
            original_value={
                key: _freeze_override_value(getattr(task, key))
                for key in updates
            },
            edited_value={
                key: _freeze_override_value(getattr(updated, key))
                for key in updates
            },
            reason=reason,
        ),),
        now=now,
    )


def reorder_tasks(
    baseline: ProjectBaseline,
    *,
    work_package_id: str,
    ordered_task_ids: Iterable[str],
    reason: str,
    now: str,
) -> ProjectBaseline:
    """Reorder tasks inside a package (must be an exact permutation)."""
    wp_index = _package_index(baseline, work_package_id)
    packages = list(baseline.work_packages)
    wp = packages[wp_index]
    ordered = tuple(ordered_task_ids)
    current_ids = tuple(task.task_id for task in wp.tasks)
    if set(ordered) != set(current_ids) or len(ordered) != len(current_ids):
        raise TaskDecompositionValidationError(
            "ordered_task_ids must be a permutation of the package tasks"
        )
    by_id = {task.task_id: task for task in wp.tasks}
    packages[wp_index] = replace(
        wp, tasks=tuple(by_id[task_id] for task_id in ordered)
    )
    return _rebuild(
        baseline,
        tuple(packages),
        (Override(
            target_path=f"work_packages[{wp_index}].tasks",
            original_value=list(current_ids),
            edited_value=list(ordered),
            reason=reason,
        ),),
        now=now,
    )


__all__ = [
    "add_task",
    "remove_task",
    "reorder_tasks",
    "update_task",
]
