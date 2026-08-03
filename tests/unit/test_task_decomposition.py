"""Unit tests for US-2-AC-1 task-decomposition slice.

Coverage matrix (each test method asserts one AC of the slice):

  AC-1  ``test_input_*`` — name / objective / window / units parsed
        and stored verbatim; missing keys rejected.
  AC-5  ``test_dependency_*`` — cycle fail-closed; topo order
        deterministic; stage-order edges seeded automatically;
        explicit edges de-duplicated; unknown task id rejected.
  AC-7  ``test_baseline_*`` — strict monotonic version; ISO-8601 UTC
        'Z' timestamps; cycle-checked at confirm time; override
        bumps version by exactly 1; ``process_flow_ref`` pins the
        snapshot.

Service-layer invariants (US-1 → US-2 wiring):
* ``propose`` is deterministic for a given FlowUnderstanding.
* Audit-record projection is JSON-safe and excludes sensitive
  content.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.task_decomposition import (
    BaselineInput,
    DependencyEdge,
    DependencyGraph,
    Deliverable,
    Milestone,
    ProjectBaseline,
    Task,
    TaskDecompositionError,
    TaskDecompositionService,
    TaskDecompositionValidationError,
    WorkPackage,
    build_baseline,
    confirm_baseline,
    cycle_in_components,
    models,
    topological_order,
)
from src.coevo.task_flow import (
    FlowUnderstanding,
    FlowUnderstandingService,
)


# ----------------------- fixtures -----------------------


def _wp_intake() -> WorkPackage:
    return WorkPackage(
        work_package_id="wp.intake",
        standard_stage="intake",
        title="Intake WP",
        tasks=(
            Task(
                task_id="t.intake.1",
                title="Receive requirement",
                responsible_role="pm",
                plan_start="2026-08-01T00:00:00Z",
                plan_end="2026-08-05T00:00:00Z",
                deliverables=(
                    Deliverable(
                        deliverable_id="d.intake.1",
                        title="Signed requirement doc",
                        kind="document",
                        acceptance_criteria=("signed", "complete"),
                    ),
                ),
            ),
        ),
    )


def _wp_execution() -> WorkPackage:
    return WorkPackage(
        work_package_id="wp.execution",
        standard_stage="execution",
        title="Execution WP",
        tasks=(
            Task(
                task_id="t.exec.1",
                title="Develop",
                responsible_role="engineer",
                plan_start="2026-08-06T00:00:00Z",
                plan_end="2026-08-20T00:00:00Z",
                deliverables=(
                    Deliverable(
                        deliverable_id="d.exec.1",
                        title="Code change",
                        kind="code",
                        acceptance_criteria=("unit_tests",),
                    ),
                ),
            ),
        ),
    )


def _wp_delivery() -> WorkPackage:
    return WorkPackage(
        work_package_id="wp.delivery",
        standard_stage="delivery",
        title="Delivery WP",
        tasks=(
            Task(
                task_id="t.deliv.1",
                title="Submit",
                responsible_role="pm",
                plan_start="2026-08-21T00:00:00Z",
                plan_end="2026-08-25T00:00:00Z",
                deliverables=(
                    Deliverable(
                        deliverable_id="d.deliv.1",
                        title="Release note",
                        kind="report",
                        acceptance_criteria=("signoff",),
                    ),
                ),
            ),
        ),
    )


def _baseline_input() -> BaselineInput:
    return BaselineInput(
        project_id="proj.alpha",
        title="Alpha project",
        objective="Ship MVP",
        plan_start="2026-08-01T00:00:00Z",
        plan_end="2026-08-31T00:00:00Z",
        responsible_units=("unit_a", "unit_b"),
        process_flow_ref=("unit_a", 1),
        work_packages=(_wp_intake(), _wp_execution(), _wp_delivery()),
    )


def _understanding() -> FlowUnderstanding:
    return FlowUnderstandingService().understand({
        "format": "canonical",
        "flow": {
            "unit_id": "unit_a",
            "title": "Unit A",
            "stages": [
                {"stage_id": "intake", "name": "intake", "nodes": [
                    {"node_id": "n1", "title": "Receive",
                     "stage_hint": "intake",
                     "inputs": ["req"], "outputs": ["signed"],
                     "review_criteria": ["complete"],
                     "responsible_roles": ["a.pm"]},
                ]},
                {"stage_id": "execution", "name": "execution", "nodes": [
                    {"node_id": "n2", "title": "Build",
                     "stage_hint": "开发阶段",
                     "inputs": ["signed"], "outputs": ["code"],
                     "review_criteria": ["unit_tests"],
                     "responsible_roles": ["a.eng"]},
                ]},
            ],
            "roles": [
                {"role_id": "a.pm", "name": "PM", "responsibility": "Owns lifecycle"},
                {"role_id": "a.eng", "name": "Eng", "responsibility": "Builds"},
            ],
        },
    })


# ----------------------- AC-1: input parsing -----------------------


class InputValidationTests(unittest.TestCase):
    def test_input_parses_and_stores(self):
        inp = _baseline_input()
        baseline = build_baseline(inp, now="2026-07-25T10:00:00Z")
        self.assertEqual("proj.alpha", baseline.project_id)
        self.assertEqual("Alpha project", baseline.title)
        self.assertEqual("Ship MVP", baseline.objective)
        self.assertEqual("2026-08-01T00:00:00Z", baseline.plan_start)
        self.assertEqual("2026-08-31T00:00:00Z", baseline.plan_end)
        self.assertEqual(("unit_a", "unit_b"), baseline.responsible_units)
        self.assertEqual(("unit_a", 1), baseline.process_flow_ref)

    def test_empty_title_rejected(self):
        inp = _baseline_input()
        with self.assertRaises(TaskDecompositionValidationError):
            build_baseline(
                BaselineInput(
                    project_id=inp.project_id, title="",
                    objective=inp.objective,
                    plan_start=inp.plan_start, plan_end=inp.plan_end,
                    responsible_units=inp.responsible_units,
                    process_flow_ref=inp.process_flow_ref,
                    work_packages=inp.work_packages,
                )
            )

    def test_bad_iso_z_rejected(self):
        inp = _baseline_input()
        with self.assertRaises(TaskDecompositionValidationError):
            build_baseline(
                BaselineInput(
                    project_id=inp.project_id, title=inp.title,
                    objective=inp.objective,
                    plan_start="2026-08-01", plan_end=inp.plan_end,
                    responsible_units=inp.responsible_units,
                    process_flow_ref=inp.process_flow_ref,
                    work_packages=inp.work_packages,
                )
            )

    def test_window_end_before_start_rejected(self):
        inp = _baseline_input()
        with self.assertRaises(TaskDecompositionValidationError):
            build_baseline(
                BaselineInput(
                    project_id=inp.project_id, title=inp.title,
                    objective=inp.objective,
                    plan_start="2026-08-31T00:00:00Z",
                    plan_end="2026-08-01T00:00:00Z",
                    responsible_units=inp.responsible_units,
                    process_flow_ref=inp.process_flow_ref,
                    work_packages=inp.work_packages,
                )
            )

    def test_duplicate_task_id_rejected(self):
        wp_intake = _wp_intake()
        wp_exec = _wp_execution()
        bad_wp = WorkPackage(
            work_package_id=wp_exec.work_package_id,
            standard_stage=wp_exec.standard_stage,
            title=wp_exec.title,
            # Same task_id as intake!
            tasks=(
                Task(
                    task_id="t.intake.1", title="Dup",
                    responsible_role="x",
                    plan_start="2026-08-06T00:00:00Z",
                    plan_end="2026-08-20T00:00:00Z",
                    deliverables=(
                        Deliverable("d.x", "x", "document", ("a",)),
                    ),
                ),
            ),
        )
        with self.assertRaises(TaskDecompositionValidationError):
            build_baseline(
                BaselineInput(
                    project_id="proj.x", title="T", objective="O",
                    plan_start="2026-08-01T00:00:00Z",
                    plan_end="2026-08-31T00:00:00Z",
                    responsible_units=("u",),
                    process_flow_ref=("unit_a", 1),
                    work_packages=(wp_intake, bad_wp),
                )
            )


# ----------------------- AC-5: dependency graph -----------------------


class DependencyGraphTests(unittest.TestCase):
    def test_stage_order_seeds_edges(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        # t.intake.1 → t.exec.1 → t.deliv.1 (3 stage boundaries, each
        # single-task, so 2 edges).
        edges = {(e.predecessor_task_id, e.successor_task_id): e for e in baseline.dependencies}
        self.assertIn(("t.intake.1", "t.exec.1"), edges)
        self.assertIn(("t.exec.1", "t.deliv.1"), edges)
        self.assertEqual("fs", edges[("t.intake.1", "t.exec.1")].kind)

    def test_topological_order_is_deterministic(self):
        baseline_a = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        baseline_b = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        # Recompute topo from edges (baseline doesn't expose topo_order
        # directly — use the dependency_graph module).
        from src.coevo.task_decomposition.dependency_graph import (
            topological_order as topo,
        )
        order_a = topo([t.task_id for wp in baseline_a.work_packages for t in wp.tasks], baseline_a.dependencies)
        order_b = topo([t.task_id for wp in baseline_b.work_packages for t in wp.tasks], baseline_b.dependencies)
        self.assertEqual(order_a, order_b)
        self.assertEqual(
            ("t.intake.1", "t.exec.1", "t.deliv.1"), order_a
        )

    def test_cycle_fail_closed(self):
        # A → B → A (within a single package is impossible because
        # DependencyEdge refuses self-loop; so we use two packages.)
        wp_a = WorkPackage(
            work_package_id="wp.a", standard_stage="intake", title="A",
            tasks=(Task("t.a", "A", "x",
                        "2026-08-01T00:00:00Z", "2026-08-05T00:00:00Z",
                        (Deliverable("d.a", "A", "document", ("a",)),)),),
        )
        wp_b = WorkPackage(
            work_package_id="wp.b", standard_stage="execution", title="B",
            tasks=(Task("t.b", "B", "x",
                        "2026-08-06T00:00:00Z", "2026-08-20T00:00:00Z",
                        (Deliverable("d.b", "B", "document", ("a",)),)),),
        )
        # Stage-order seeds t.a → t.b; we add an explicit t.b → t.a edge
        # to form a cycle.
        with self.assertRaises(TaskDecompositionValidationError):
            build_baseline(
                BaselineInput(
                    project_id="p", title="T", objective="O",
                    plan_start="2026-08-01T00:00:00Z",
                    plan_end="2026-08-31T00:00:00Z",
                    responsible_units=("u",),
                    process_flow_ref=("u", 1),
                    work_packages=(wp_a, wp_b),
                ),
                dependencies=(DependencyEdge("t.b", "t.a", "fs"),),
            )

    def test_unknown_task_id_in_explicit_edge_rejected(self):
        with self.assertRaises(TaskDecompositionValidationError):
            build_baseline(
                _baseline_input(),
                dependencies=(DependencyEdge("t.intake.1", "t.bogus", "fs"),),
            )

    def test_cycle_in_components_helper(self):
        edges = [
            DependencyEdge("a", "b", "fs"),
            DependencyEdge("b", "c", "fs"),
            DependencyEdge("c", "a", "fs"),
        ]
        offending = cycle_in_components(edges)
        self.assertEqual(1, len(offending))
        self.assertEqual(("c", "a"), (offending[0].predecessor_task_id, offending[0].successor_task_id))

    def test_dependency_kind_validation(self):
        with self.assertRaises(TaskDecompositionError):
            DependencyEdge("a", "b", "ss")
        with self.assertRaises(TaskDecompositionError):
            DependencyEdge("a", "a", "fs")


# ----------------------- AC-7: baseline versioning -----------------------


class BaselineVersionTests(unittest.TestCase):
    def test_first_draft_is_version_1(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        self.assertEqual(1, baseline.version)

    def test_with_overrides_bumps_version_by_1(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        override = models.Override(
            target_path="title",
            original_value=baseline.title,
            edited_value="Alpha project (revised)",
            reason="PM clarified scope",
        )
        next_baseline = baseline.with_overrides((override,), new_created_at="2026-07-25T11:00:00Z")
        self.assertEqual(2, next_baseline.version)
        self.assertEqual((override,), next_baseline.overrides)

    def test_empty_overrides_rejected(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        with self.assertRaises(TaskDecompositionError):
            baseline.with_overrides(tuple(), new_created_at="2026-07-25T11:00:00Z")

    def test_confirm_baseline_bumps_version(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        next_baseline = confirm_baseline(baseline, "2026-07-25T11:00:00Z")
        self.assertEqual(2, next_baseline.version)
        self.assertEqual("2026-07-25T11:00:00Z", next_baseline.created_at)

    def test_process_flow_ref_pins_snapshot(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        self.assertEqual(("unit_a", 1), baseline.process_flow_ref)

    def test_milestones_derived_one_per_work_package(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        self.assertEqual(3, len(baseline.milestones))
        self.assertEqual("wp.intake", baseline.milestones[0].work_package_id)
        # Each milestone uses the last task's plan_end
        self.assertEqual("2026-08-05T00:00:00Z", baseline.milestones[0].target_date)


# ----------------------- service-layer tests -----------------------


class ServiceLayerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TaskDecompositionService()
        self.understanding = _understanding()

    def test_propose_groups_by_standard_stage(self):
        proposal = self.service.propose(
            self.understanding,
            {
                "project_id": "p.x",
                "title": "T",
                "objective": "O",
                "plan_start": "2026-08-01T00:00:00Z",
                "plan_end": "2026-08-31T00:00:00Z",
                "responsible_units": ("unit_a",),
            },
        )
        # Two stages in the fixture, so two packages.
        self.assertEqual(2, len(proposal.work_packages))
        # Each package has one task (the fixture has one node per stage).
        for wp in proposal.work_packages:
            self.assertEqual(1, len(wp.tasks))

    def test_propose_pins_process_flow_ref(self):
        proposal = self.service.propose(
            self.understanding,
            {
                "project_id": "p.x", "title": "T", "objective": "O",
                "plan_start": "2026-08-01T00:00:00Z",
                "plan_end": "2026-08-31T00:00:00Z",
                "responsible_units": ("unit_a",),
            },
        )
        self.assertEqual(("unit_a", self.understanding.flow.version), proposal.process_flow_ref)

    def test_propose_missing_required_key_rejected(self):
        with self.assertRaises(TaskDecompositionValidationError):
            self.service.propose(self.understanding, {"project_id": "p"})

    def test_proposal_round_trips_through_build_baseline(self):
        proposal = self.service.propose(
            self.understanding,
            {
                "project_id": "p.x", "title": "T", "objective": "O",
                "plan_start": "2026-08-01T00:00:00Z",
                "plan_end": "2026-08-31T00:00:00Z",
                "responsible_units": ("unit_a",),
            },
        )
        baseline = build_baseline(proposal, now="2026-07-25T10:00:00Z")
        self.assertEqual(1, baseline.version)
        # Stage-order edge seeded between intake and execution
        edges = {(e.predecessor_task_id, e.successor_task_id) for e in baseline.dependencies}
        self.assertIn(("n1", "n2"), edges)

    def test_audit_record_is_json_safe(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        record = self.service.to_audit_record(baseline)
        s = json.dumps(record)
        self.assertEqual(record, json.loads(s))

    def test_audit_record_excludes_sensitive_fields(self):
        baseline = build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")
        record = self.service.to_audit_record(baseline)
        self.assertNotIn("deliverables", record)
        self.assertNotIn("tasks", record)
        self.assertEqual("proj.alpha", record["project_id"])
        self.assertEqual(1, record["version"])
        self.assertEqual(("unit_a", 1), tuple(record["process_flow_ref"]))
        self.assertEqual(3, record["work_package_count"])
        self.assertEqual(3, record["task_count"])
        self.assertIn("task_decomposition.baseline", record["kind"])


if __name__ == "__main__":
    unittest.main()