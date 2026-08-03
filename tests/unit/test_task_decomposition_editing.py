"""Unit tests for US-2-AC-2 (AC-6): user task-editing operations."""
from __future__ import annotations

import unittest

from src.coevo.task_decomposition import (
    ProjectBaseline,
    Task,
    TaskDecompositionValidationError,
    add_task,
    remove_task,
    reorder_tasks,
    update_task,
)
from src.coevo.task_decomposition.baseline import build_baseline
from src.coevo.task_decomposition.dependency_graph import build_dependency_graph
from src.coevo.task_decomposition.models import Deliverable
from tests.unit.test_task_decomposition import _baseline_input


NOW = "2026-07-25T10:00:00Z"


def _baseline() -> ProjectBaseline:
    return build_baseline(_baseline_input(), now=NOW)


def _task(task_id: str = "t.new") -> Task:
    return Task(
        task_id=task_id,
        title="New task",
        responsible_role="engineer",
        plan_start="2026-08-06T00:00:00Z",
        plan_end="2026-08-12T00:00:00Z",
        deliverables=(
            Deliverable(
                deliverable_id=f"d.{task_id}",
                title="output",
                kind="document",
                acceptance_criteria=("accepted",),
            ),
        ),
    )


def _task_ids(baseline: ProjectBaseline) -> set[str]:
    return {
        task.task_id
        for wp in baseline.work_packages
        for task in wp.tasks
    }


class AddTaskTests(unittest.TestCase):
    def test_add_task_appends_bumps_version_and_rebuilds_graph(self):
        baseline = _baseline()
        edited = add_task(
            baseline,
            work_package_id="wp.execution",
            task=_task(),
            reason="user added a task",
            now="2026-07-25T11:00:00Z",
        )
        self.assertEqual(baseline.version + 1, edited.version)
        self.assertIn("t.new", _task_ids(edited))
        self.assertEqual(1, len(edited.overrides))
        self.assertEqual("t.new", edited.overrides[0].edited_value)
        # every dependency edge references known tasks
        known = _task_ids(edited)
        for edge in edited.dependencies:
            self.assertIn(edge.predecessor_task_id, known)
            self.assertIn(edge.successor_task_id, known)
        # deterministic topological order includes the new task
        graph = build_dependency_graph(edited.work_packages)
        self.assertIn("t.new", graph.topo_order)

    def test_add_task_rejects_duplicate_and_unknown_package(self):
        baseline = _baseline()
        with self.assertRaises(TaskDecompositionValidationError):
            add_task(
                baseline,
                work_package_id="wp.execution",
                task=_task(task_id="t.exec.1"),
                reason="duplicate",
                now=NOW,
            )
        with self.assertRaises(TaskDecompositionValidationError):
            add_task(
                baseline,
                work_package_id="wp.ghost",
                task=_task(),
                reason="unknown package",
                now=NOW,
            )


class RemoveTaskTests(unittest.TestCase):
    def test_remove_task_removes_and_keeps_graph_consistent(self):
        baseline = _baseline()
        added = add_task(
            baseline,
            work_package_id="wp.execution",
            task=_task(),
            reason="add",
            now="2026-07-25T11:00:00Z",
        )
        edited = remove_task(
            added,
            task_id="t.new",
            reason="user removed the task",
            now="2026-07-25T12:00:00Z",
        )
        self.assertNotIn("t.new", _task_ids(edited))
        self.assertEqual(added.version + 1, edited.version)
        self.assertEqual(2, len(edited.overrides))
        self.assertEqual("t.new", edited.overrides[1].original_value)
        known = _task_ids(edited)
        for edge in edited.dependencies:
            self.assertIn(edge.predecessor_task_id, known)
            self.assertIn(edge.successor_task_id, known)

    def test_remove_task_refuses_to_empty_a_package(self):
        baseline = _baseline()
        with self.assertRaises(TaskDecompositionValidationError):
            remove_task(
                baseline,
                task_id="t.exec.1",
                reason="last task",
                now=NOW,
            )
        with self.assertRaises(TaskDecompositionValidationError):
            remove_task(
                baseline,
                task_id="t.ghost",
                reason="unknown",
                now=NOW,
            )


class UpdateTaskTests(unittest.TestCase):
    def test_update_task_changes_fields_and_records_override(self):
        baseline = _baseline()
        edited = update_task(
            baseline,
            task_id="t.exec.1",
            reason="user corrected the title",
            now="2026-07-25T11:00:00Z",
            title="Develop with tests",
            responsible_role="tech_lead",
        )
        self.assertEqual(baseline.version + 1, edited.version)
        task = edited.work_packages[1].tasks[0]
        self.assertEqual("Develop with tests", task.title)
        self.assertEqual("tech_lead", task.responsible_role)
        self.assertEqual(1, len(edited.overrides))
        self.assertIn("title", edited.overrides[0].original_value)

    def test_update_task_rejects_unknown_and_empty_updates(self):
        baseline = _baseline()
        with self.assertRaises(TaskDecompositionValidationError):
            update_task(
                baseline,
                task_id="t.ghost",
                reason="unknown",
                now=NOW,
                title="x",
            )
        with self.assertRaises(TaskDecompositionValidationError):
            update_task(
                baseline,
                task_id="t.exec.1",
                reason="no fields",
                now=NOW,
            )


class ReorderTasksTests(unittest.TestCase):
    def test_reorder_tasks_permutation_and_override(self):
        baseline = _baseline()
        added = add_task(
            baseline,
            work_package_id="wp.execution",
            task=_task(),
            reason="add",
            now="2026-07-25T11:00:00Z",
        )
        edited = reorder_tasks(
            added,
            work_package_id="wp.execution",
            ordered_task_ids=("t.new", "t.exec.1"),
            reason="user reordered",
            now="2026-07-25T12:00:00Z",
        )
        wp = edited.work_packages[1]
        self.assertEqual(("t.new", "t.exec.1"), tuple(t.task_id for t in wp.tasks))
        self.assertEqual(added.version + 1, edited.version)
        self.assertEqual(
            ["t.exec.1", "t.new"],
            edited.overrides[1].original_value,
        )
        self.assertEqual(
            ["t.new", "t.exec.1"],
            edited.overrides[1].edited_value,
        )

    def test_reorder_tasks_rejects_non_permutation(self):
        baseline = _baseline()
        added = add_task(
            baseline,
            work_package_id="wp.execution",
            task=_task(),
            reason="add",
            now="2026-07-25T11:00:00Z",
        )
        with self.assertRaises(TaskDecompositionValidationError):
            reorder_tasks(
                added,
                work_package_id="wp.execution",
                ordered_task_ids=("t.new",),
                reason="missing one",
                now=NOW,
            )
        with self.assertRaises(TaskDecompositionValidationError):
            reorder_tasks(
                added,
                work_package_id="wp.ghost",
                ordered_task_ids=("t.exec.1", "t.new"),
                reason="unknown package",
                now=NOW,
            )


if __name__ == "__main__":
    unittest.main()
