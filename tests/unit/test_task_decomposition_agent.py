"""Unit tests for US-2-AC-3 model-assisted decomposition suggestion agent."""
from __future__ import annotations

import json
import unittest

from src.coevo.model import (
    ModelUnavailableError,
    ModelValidationError,
)
from src.coevo.task_decomposition import (
    ModelTaskSuggestion,
    ProjectBaseline,
    SuggestionEdge,
    SuggestionTask,
    TaskDecompositionAgent,
    TaskDecompositionValidationError,
    build_baseline,
)
from tests.unit.test_task_decomposition import _baseline_input, _understanding


class FakeProvider:
    def __init__(self, content: str | None = None, error=None):
        self._content = content
        self._error = error

    def complete(self, *, system, user, max_tokens, timeout_seconds):
        if self._error is not None:
            raise self._error
        return self._content


def _valid_suggestion_json() -> str:
    return json.dumps(
        {
            "tasks": [
                {
                    "work_package_id": "wp.execution",
                    "task_id": "t.llm.1",
                    "title": "Model-suggested subtask",
                    "responsible_role": "engineer",
                    "plan_start": "2026-08-08T00:00:00Z",
                    "plan_end": "2026-08-15T00:00:00Z",
                    "deliverable_title": "Subtask output",
                    "acceptance_criteria": ["accepted", "reviewed"],
                }
            ],
            "candidate_edges": [
                {
                    "predecessor_task_id": "n1",
                    "successor_task_id": "t.llm.1",
                }
            ],
        },
        separators=(",", ":"),
    )


def _project_input() -> dict[str, object]:
    return {
        "project_id": "proj.alpha",
        "title": "Alpha project",
        "objective": "Ship MVP",
        "plan_start": "2026-08-01T00:00:00Z",
        "plan_end": "2026-08-31T00:00:00Z",
        "responsible_units": ("unit_a", "unit_b"),
    }


class SuggestTests(unittest.TestCase):
    def test_suggest_parses_valid_suggestion(self):
        understanding = _understanding()
        suggestion = TaskDecompositionAgent().suggest(
            understanding=understanding,
            project_input=_project_input(),
            provider=FakeProvider(content=_valid_suggestion_json()),
        )
        self.assertIsNotNone(suggestion)
        assert suggestion is not None
        self.assertEqual(1, len(suggestion.tasks))
        self.assertEqual("t.llm.1", suggestion.tasks[0].task_id)
        self.assertEqual("wp.execution", suggestion.tasks[0].work_package_id)
        self.assertEqual(
            SuggestionEdge("n1", "t.llm.1"),
            suggestion.candidate_edges[0],
        )

    def test_suggest_returns_none_when_provider_unavailable(self):
        suggestion = TaskDecompositionAgent().suggest(
            understanding=_understanding(),
            project_input=_project_input(),
            provider=FakeProvider(error=ModelUnavailableError("offline")),
        )
        self.assertIsNone(suggestion)

    def test_suggest_rejects_malformed_and_oversized_output(self):
        agent = TaskDecompositionAgent()
        with self.assertRaises(ModelValidationError):
            agent.suggest(
                understanding=_understanding(),
                project_input=_project_input(),
                provider=FakeProvider(content="not json"),
            )
        with self.assertRaises(ModelValidationError):
            agent.suggest(
                understanding=_understanding(),
                project_input=_project_input(),
                provider=FakeProvider(content='{"tasks": ' + "[" * 1000 + "]}"),
            )

    def test_suggest_rejects_unknown_package_and_unknown_edge(self):
        agent = TaskDecompositionAgent()
        bad_package = json.dumps(
            {
                "tasks": [
                    {
                        "work_package_id": "wp.ghost",
                        "task_id": "t.llm.1",
                        "title": "x",
                        "responsible_role": "r",
                        "plan_start": "2026-08-08T00:00:00Z",
                        "plan_end": "2026-08-15T00:00:00Z",
                        "deliverable_title": "d",
                        "acceptance_criteria": ["ok"],
                    }
                ],
                "candidate_edges": [],
            }
        )
        with self.assertRaises(ModelValidationError):
            agent.suggest(
                understanding=_understanding(),
                project_input=_project_input(),
                provider=FakeProvider(content=bad_package),
            )
        bad_edge = json.dumps(
            {
                "tasks": [],
                "candidate_edges": [
                    {
                        "predecessor_task_id": "t.ghost.9",
                        "successor_task_id": "t.ghost.8",
                    }
                ],
            }
        )
        with self.assertRaises(ModelValidationError):
            agent.suggest(
                understanding=_understanding(),
                project_input=_project_input(),
                provider=FakeProvider(content=bad_edge),
            )


class ApplyTests(unittest.TestCase):
    def _draft(self) -> ProjectBaseline:
        return build_baseline(_baseline_input(), now="2026-07-25T10:00:00Z")

    def test_apply_adds_tasks_with_model_override_and_no_edge_application(self):
        draft = self._draft()
        suggestion = ModelTaskSuggestion(
            tasks=(
                SuggestionTask(
                    work_package_id="wp.execution",
                    task_id="t.llm.1",
                    title="Model-suggested subtask",
                    responsible_role="engineer",
                    plan_start="2026-08-08T00:00:00Z",
                    plan_end="2026-08-15T00:00:00Z",
                    deliverable_title="Subtask output",
                    acceptance_criteria=("accepted",),
                ),
            ),
            candidate_edges=(SuggestionEdge("t.intake.1", "t.llm.1"),),
        )
        edited = TaskDecompositionAgent().apply(
            suggestion=suggestion,
            draft=draft,
            reason="LLM-assisted decomposition",
            now="2026-07-25T11:00:00Z",
        )
        self.assertEqual(draft.version + 1, edited.version)
        wp = edited.work_packages[1]
        self.assertIn("t.llm.1", tuple(t.task_id for t in wp.tasks))
        self.assertTrue(edited.overrides[-1].reason.startswith("model.suggestion:"))
        # candidate edges are suggestions only -- the rebuilt graph must equal
        # the deterministic stage-order seeds (no explicit edge was added)
        from src.coevo.task_decomposition.dependency_graph import (
            build_dependency_graph,
        )

        self.assertEqual(
            build_dependency_graph(edited.work_packages).edges,
            edited.dependencies,
        )

    def test_apply_rejects_duplicate_and_unknown_package(self):
        draft = self._draft()
        agent = TaskDecompositionAgent()
        duplicate = ModelTaskSuggestion(
            tasks=(
                SuggestionTask(
                    work_package_id="wp.execution",
                    task_id="t.exec.1",
                    title="x",
                    responsible_role="r",
                    plan_start="2026-08-08T00:00:00Z",
                    plan_end="2026-08-15T00:00:00Z",
                    deliverable_title="d",
                    acceptance_criteria=("ok",),
                ),
            ),
            candidate_edges=(),
        )
        with self.assertRaises(TaskDecompositionValidationError):
            agent.apply(
                suggestion=duplicate,
                draft=draft,
                reason="dup",
                now="2026-07-25T11:00:00Z",
            )
        unknown = ModelTaskSuggestion(
            tasks=(
                SuggestionTask(
                    work_package_id="wp.ghost",
                    task_id="t.llm.1",
                    title="x",
                    responsible_role="r",
                    plan_start="2026-08-08T00:00:00Z",
                    plan_end="2026-08-15T00:00:00Z",
                    deliverable_title="d",
                    acceptance_criteria=("ok",),
                ),
            ),
            candidate_edges=(),
        )
        with self.assertRaises(TaskDecompositionValidationError):
            agent.apply(
                suggestion=unknown,
                draft=draft,
                reason="unknown package",
                now="2026-07-25T11:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
