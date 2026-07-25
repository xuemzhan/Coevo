"""US-2 task-decomposition service layer (US-2-AC-1).

Consumes a US-1 :class:`FlowUnderstanding` and produces a draft
:class:`ProjectBaseline` with strict monotonic version, fail-closed
cycle detection, and a deterministic topological task order.

The service does NOT call any model. It derives a default work
package per standard stage (one per unique
:class:`StandardStage` present in the mapped flow), then transcribes
each per-unit node into a default :class:`Task` inside the
corresponding package. Callers may override the proposal before
calling :meth:`build_baseline`.

What this layer adds on top of US-2's data model
------------------------------------------------
* :class:`TaskDecompositionService` — deterministic facade that
  bridges US-1's :class:`FlowUnderstanding` and US-2's
  :class:`BaselineInput`. Exposes one public method:
  :meth:`propose` returns a populated :class:`BaselineInput` that
  the caller passes to :func:`build_baseline`.
* :meth:`to_audit_record` — emits a deterministic JSON-safe dict
  suitable for ``loop/tool-audit.jsonl`` ingestion; same shape
  convention as US-1's
  :meth:`FlowUnderstandingService.to_audit_record`.

Non-goals (out of scope for US-2-AC-1)
--------------------------------------
* No LLM call. The production 任务分解 agent is a separate slice.
* No I/O. The service is a pure function over its inputs.
* No automatic edge proposal. Stage-order edges are seeded
  deterministically (every task in stage i precedes every task in
  stage i+1); explicit LLM-suggested edges are a future slice.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping

from src.coevo.task_flow import (
    FlowUnderstanding,
    StandardStage,
)

from .baseline import BaselineInput
from .models import (
    DependencyEdge,
    Deliverable,
    ProjectBaseline,
    Task,
    TaskDecompositionValidationError,
    WorkPackage,
)


@dataclasses.dataclass(frozen=True)
class TaskDecompositionService:
    """Deterministic facade for the US-2 task-decomposition slice.

    No internal state — every method is a pure function of its
    inputs. Callers may safely construct it once at module import
    time.
    """

    def propose(
        self,
        understanding: FlowUnderstanding,
        project_input: Mapping[str, Any],
    ) -> BaselineInput:
        """Translate a US-1 :class:`FlowUnderstanding` into a draft :class:`BaselineInput`.

        The default proposal groups per-unit nodes by their
        :class:`StandardStage` (one package per stage) and creates
        one task per node inside the corresponding package. The
        proposal is the *starting point* — callers may edit before
        calling :func:`build_baseline`.

        Required ``project_input`` keys: ``project_id``, ``title``,
        ``objective``, ``plan_start``, ``plan_end``,
        ``responsible_units`` (non-empty tuple of strings).
        """
        for key in (
            "project_id", "title", "objective",
            "plan_start", "plan_end", "responsible_units",
        ):
            if key not in project_input:
                raise TaskDecompositionValidationError(
                    f"project_input missing required key {key!r}"
                )

        packages: list[WorkPackage] = []
        # Iterate stages in canonical order; one package per stage
        # that actually has nodes.
        for stage_id in understanding.graph.stage_ids_in_order:
            stage_nodes = [
                m
                for m in understanding.mapped.nodes
                if understanding.graph.stage_id_for_node(m.node.node_id) == stage_id
            ]
            if not stage_nodes:
                continue
            standard_stage = stage_nodes[0].standard_stage
            tasks = tuple(
                Task(
                    task_id=m.node.node_id,
                    title=m.node.title,
                    responsible_role=(
                        m.node.responsible_roles[0].value
                        if m.node.responsible_roles
                        else "unassigned"
                    ),
                    plan_start=project_input["plan_start"],
                    plan_end=project_input["plan_end"],
                    deliverables=(
                        Deliverable(
                            deliverable_id=f"d.{m.node.node_id}",
                            title=f"{m.node.title} output",
                            kind="document",
                            acceptance_criteria=(
                                tuple(t.value for t in m.node.review_criteria)
                                if m.node.review_criteria
                                else ("accepted_by_reviewer",)
                            ),
                        ),
                    ),
                )
                for m in stage_nodes
            )
            packages.append(
                WorkPackage(
                    work_package_id=f"wp.{stage_id}",
                    standard_stage=standard_stage.value,
                    title=f"{standard_stage.value} work package",
                    tasks=tasks,
                )
            )

        return BaselineInput(
            project_id=project_input["project_id"],
            title=project_input["title"],
            objective=project_input["objective"],
            plan_start=project_input["plan_start"],
            plan_end=project_input["plan_end"],
            responsible_units=tuple(project_input["responsible_units"]),
            process_flow_ref=(
                understanding.flow.unit_id,
                understanding.flow.version,
            ),
            work_packages=tuple(packages),
        )

    def to_audit_record(self, baseline: ProjectBaseline) -> dict[str, Any]:
        """Produce a deterministic, JSON-safe audit-record projection.

        Same shape convention as US-1's
        :meth:`FlowUnderstandingService.to_audit_record`. Sensitive
        content (deliverable titles, task descriptions) is *not*
        included — only structural facts.
        """
        return {
            "kind": "task_decomposition.baseline",
            "schema_version": "1.0",
            "project_id": baseline.project_id,
            "version": baseline.version,
            "process_flow_ref": list(baseline.process_flow_ref),
            "work_package_count": len(baseline.work_packages),
            "task_count": sum(len(wp.tasks) for wp in baseline.work_packages),
            "dependency_count": len(baseline.dependencies),
            "milestone_count": len(baseline.milestones),
            "responsible_unit_count": len(baseline.responsible_units),
            "override_count": len(baseline.overrides),
        }