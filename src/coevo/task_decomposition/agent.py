"""US-2-AC-3: model-assisted task-decomposition suggestion agent.

The agent consumes a US-1 :class:`FlowUnderstanding` plus project
input and asks a :class:`ModelProvider` (DeepSeek by configuration,
replaceable per mandatory constraint 9.2) for *candidate* task
additions and dependency-edge suggestions.

Boundaries (fail-closed by construction)
----------------------------------------
* Output is a :class:`ModelTaskSuggestion` -- a **draft**. It is
  never written to a confirmed baseline: :meth:`apply` produces a
  ``version + 1`` draft through the editing layer with
  ``Override`` records marked ``model.suggestion:`` and the human
  confirmation flow (``confirm_baseline``) stays mandatory.
* Offline mode: when the provider is unavailable (no key / no
  egress approval / offline), :meth:`suggest` returns ``None`` and
  callers keep the deterministic decomposition -- quality gates
  never call a network.
* Strict schema + bounds: malformed / oversized / unknown-package /
  unknown-task output raises :class:`ModelValidationError` and is
  never partially applied.
"""
from __future__ import annotations

import json
import re
import dataclasses
from dataclasses import dataclass
from typing import Any, Mapping

from src.coevo.model import (
    ModelConfig,
    ModelProvider,
    ModelUnavailableError,
    ModelValidationError,
    PromptRegistry,
    parse_json_object,
)
from src.coevo.task_flow import FlowUnderstanding

from .baseline import BaselineInput
from .editing import _rebuild
from .models import (
    Deliverable,
    Override,
    ProjectBaseline,
    Task,
    TaskDecompositionValidationError,
    WorkPackage,
)


_SAFE_ID = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.\-]{0,63}$")
_ISO_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
_MAX_SUGGESTED_TASKS = 8
_MAX_SUGGESTED_EDGES = 16
_MAX_STRING_BYTES = 512
_MAX_ACCEPTANCE_ITEMS = 8
_MAX_PROMPT_BYTES = 16 * 1024
_MAX_RESPONSE_BYTES = 64 * 1024


@dataclass(frozen=True)
class SuggestionEdge:
    predecessor_task_id: str
    successor_task_id: str


@dataclass(frozen=True)
class SuggestionTask:
    work_package_id: str
    task_id: str
    title: str
    responsible_role: str
    plan_start: str
    plan_end: str
    deliverable_title: str
    acceptance_criteria: tuple[str, ...]


@dataclass(frozen=True)
class ModelTaskSuggestion:
    tasks: tuple[SuggestionTask, ...]
    candidate_edges: tuple[SuggestionEdge, ...]


def _flow_json(understanding: FlowUnderstanding) -> str:
    stages: list[dict[str, object]] = []
    node_count = 0
    for stage_id in understanding.graph.stage_ids_in_order:
        nodes = [
            m
            for m in understanding.mapped.nodes
            if understanding.graph.stage_id_for_node(m.node.node_id) == stage_id
        ]
        entries: list[dict[str, object]] = []
        for m in nodes:
            node_count += 1
            if node_count > 200:
                break
            entries.append(
                {
                    "node_id": m.node.node_id,
                    "title": m.node.title,
                    "responsible_roles": [
                        role.value for role in m.node.responsible_roles
                    ],
                }
            )
        if entries:
            stages.append({"stage": stage_id, "nodes": entries})
    flow = json.dumps(
        {"flow_stages": stages},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    if len(flow.encode("utf-8")) > _MAX_PROMPT_BYTES:
        raise ModelValidationError("prompt exceeds the size limit")
    return flow


def _project_json(project_input: Mapping[str, Any]) -> str:
    payload = {
        "title": project_input.get("title"),
        "objective": project_input.get("objective"),
        "plan_start": project_input.get("plan_start"),
        "plan_end": project_input.get("plan_end"),
        "responsible_units": list(project_input.get("responsible_units", ())),
    }
    project = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if len(project.encode("utf-8")) > _MAX_PROMPT_BYTES:
        raise ModelValidationError("prompt exceeds the size limit")
    return project


class TaskDecompositionAgent:
    """Model-assisted task-decomposition suggestion facade."""

    def suggest(
        self,
        *,
        understanding: FlowUnderstanding,
        project_input: Mapping[str, Any],
        provider: ModelProvider,
        config: ModelConfig,
        prompt_registry: PromptRegistry,
    ) -> ModelTaskSuggestion | None:
        """Ask the provider for candidate tasks/edges; ``None`` when offline."""
        if not isinstance(provider, ModelProvider):
            raise TaskDecompositionValidationError(
                "provider must implement ModelProvider"
            )
        provider_key = (
            f"{provider.name}/{config.model}"
            if getattr(provider, "name", None) == "deepseek"
            else None
        )
        template = prompt_registry.resolve(
            "task_decomposition.suggest",
            provider_key=provider_key,
        )
        user = template.expand(
            values={
                "project": _project_json(project_input),
                "flow": _flow_json(understanding),
            },
            max_bytes=_MAX_PROMPT_BYTES,
        )
        try:
            content = provider.complete(
                system=template.system,
                user=user,
                max_tokens=config.max_tokens,
                timeout_seconds=config.timeout_seconds,
            )
        except ModelUnavailableError:
            return None
        parsed = parse_json_object(content, max_bytes=_MAX_RESPONSE_BYTES)
        return self._validate(parsed, understanding, project_input)

    def apply(
        self,
        *,
        suggestion: ModelTaskSuggestion,
        draft: ProjectBaseline,
        reason: str,
        now: str,
    ) -> ProjectBaseline:
        """Apply suggested task additions to a draft at version+1.

        Candidate dependency edges are surfaced for human review only
        and are NOT applied (explicit edge application is a future
        slice). Every applied task carries an ``Override`` marked
        ``model.suggestion:``; confirmation still happens through
        ``confirm_baseline``.
        """
        if not isinstance(suggestion, ModelTaskSuggestion):
            raise TaskDecompositionValidationError(
                "suggestion must be ModelTaskSuggestion"
            )
        if not isinstance(draft, ProjectBaseline):
            raise TaskDecompositionValidationError(
                "draft must be ProjectBaseline"
            )
        known_packages = {
            wp.work_package_id for wp in draft.work_packages
        }
        existing_ids = {
            task.task_id
            for wp in draft.work_packages
            for task in wp.tasks
        }
        suggested_ids = [task.task_id for task in suggestion.tasks]
        if len(set(suggested_ids)) != len(suggested_ids):
            raise TaskDecompositionValidationError(
                "suggestion contains duplicate task ids"
            )
        if set(suggested_ids) & existing_ids:
            raise TaskDecompositionValidationError(
                "suggestion repeats existing task ids"
            )
        for task in suggestion.tasks:
            if task.work_package_id not in known_packages:
                raise TaskDecompositionValidationError(
                    f"suggestion references unknown work_package "
                    f"{task.work_package_id!r}"
                )
        packages = list(draft.work_packages)
        overrides: list[Override] = []
        for task in suggestion.tasks:
            packages = [
                replace_wp(wp, task)
                if wp.work_package_id == task.work_package_id
                else wp
                for wp in packages
            ]
            overrides.append(
                Override(
                    target_path=f"work_packages[].{task.task_id}",
                    original_value=None,
                    edited_value=task.task_id,
                    reason=f"model.suggestion: {reason}",
                )
            )
        return _rebuild(
            draft,
            tuple(packages),
            tuple(overrides),
            now=now,
        )

    def _validate(
        self,
        parsed: dict[str, object],
        understanding: FlowUnderstanding,
        project_input: Mapping[str, Any],
    ) -> ModelTaskSuggestion:
        raw_tasks = parsed.get("tasks", [])
        raw_edges = parsed.get("candidate_edges", [])
        if not isinstance(raw_tasks, list) or len(raw_tasks) > _MAX_SUGGESTED_TASKS:
            raise ModelValidationError("tasks must be a bounded list")
        if not isinstance(raw_edges, list) or len(raw_edges) > _MAX_SUGGESTED_EDGES:
            raise ModelValidationError(
                "candidate_edges must be a bounded list"
            )
        known_packages = {
            f"wp.{understanding.graph.stage_id_for_node(m.node.node_id)}"
            for m in understanding.mapped.nodes
        }
        tasks: list[SuggestionTask] = []
        for raw in raw_tasks:
            if not isinstance(raw, dict):
                raise ModelValidationError("task entry must be an object")
            try:
                work_package_id = raw["work_package_id"]
                task_id = raw["task_id"]
                title = raw["title"]
                role = raw["responsible_role"]
                plan_start = raw["plan_start"]
                plan_end = raw["plan_end"]
                deliverable_title = raw["deliverable_title"]
                criteria = raw["acceptance_criteria"]
            except KeyError as exc:
                raise ModelValidationError(
                    f"task entry missing field {exc.args[0]!r}"
                ) from exc
            if not _SAFE_ID.fullmatch(work_package_id) or work_package_id not in known_packages:
                raise ModelValidationError(
                    f"unknown or unsafe work_package_id {work_package_id!r}"
                )
            if not _SAFE_ID.fullmatch(task_id):
                raise ModelValidationError(f"unsafe task_id {task_id!r}")
            for value, name in (
                (title, "title"),
                (role, "responsible_role"),
                (deliverable_title, "deliverable_title"),
            ):
                if (
                    not isinstance(value, str)
                    or not value.strip()
                    or len(value.encode("utf-8")) > _MAX_STRING_BYTES
                ):
                    raise ModelValidationError(f"invalid {name}")
            if not _ISO_Z.fullmatch(plan_start) or not _ISO_Z.fullmatch(plan_end):
                raise ModelValidationError("task window must be ISO-8601 Z")
            if plan_end < plan_start:
                raise ModelValidationError("task window is inverted")
            if (
                not isinstance(criteria, list)
                or not criteria
                or len(criteria) > _MAX_ACCEPTANCE_ITEMS
                or any(
                    not isinstance(item, str) or not item.strip()
                    for item in criteria
                )
            ):
                raise ModelValidationError("invalid acceptance_criteria")
            tasks.append(
                SuggestionTask(
                    work_package_id=work_package_id,
                    task_id=task_id,
                    title=title,
                    responsible_role=role,
                    plan_start=plan_start,
                    plan_end=plan_end,
                    deliverable_title=deliverable_title,
                    acceptance_criteria=tuple(criteria),
                )
            )
        known_ids = {
            m.node.node_id for m in understanding.mapped.nodes
        }
        edges: list[SuggestionEdge] = []
        for raw in raw_edges:
            if not isinstance(raw, dict):
                raise ModelValidationError("edge entry must be an object")
            try:
                pred = raw["predecessor_task_id"]
                succ = raw["successor_task_id"]
            except KeyError as exc:
                raise ModelValidationError(
                    f"edge entry missing field {exc.args[0]!r}"
                ) from exc
            if not _SAFE_ID.fullmatch(pred) or not _SAFE_ID.fullmatch(succ):
                raise ModelValidationError("edge ids must be safe-ids")
            if pred == succ:
                raise ModelValidationError("edge cannot be a self-loop")
            suggested = {task.task_id for task in tasks}
            if pred not in known_ids | suggested or succ not in known_ids | suggested:
                raise ModelValidationError(
                    "edge references an unknown task id"
                )
            edges.append(SuggestionEdge(pred, succ))
        # de-duplicate edges deterministically
        edges = list(dict.fromkeys(edges))
        return ModelTaskSuggestion(
            tasks=tuple(tasks),
            candidate_edges=tuple(edges),
        )


def replace_wp(wp: WorkPackage, task: SuggestionTask) -> WorkPackage:
    """Append a suggested task to a work package (helper for ``apply``)."""
    new_task = Task(
        task_id=task.task_id,
        title=task.title,
        responsible_role=task.responsible_role,
        plan_start=task.plan_start,
        plan_end=task.plan_end,
        deliverables=(
            Deliverable(
                deliverable_id=f"d.{task.task_id}",
                title=task.deliverable_title,
                kind="document",
                acceptance_criteria=task.acceptance_criteria,
            ),
        ),
    )
    return dataclasses.replace(wp, tasks=wp.tasks + (new_task,))


__all__ = [
    "ModelTaskSuggestion",
    "SuggestionEdge",
    "SuggestionTask",
    "TaskDecompositionAgent",
]
