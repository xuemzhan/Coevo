"""MATURITY-O-08: model-inferred risk suggestion agent tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.model import (  # noqa: E402
    ConfirmedStateChange,
    ModelConfig,
    ModelUnavailableError,
    ModelValidationError,
    PromptRegistry,
    load_prompt_registry,
)
from src.coevo.risk import (  # noqa: E402
    Risk,
    RiskKind,
    RiskReport,
    RiskSuggestion,
    RiskSuggestionAgent,
    RiskValidationError,
    SourceKind,
)


def _risk(
    *,
    risk_id: str = "risk.1",
    kind: RiskKind = RiskKind.LONG_SILENCE,
    due: str = "2026-08-20T00:00:00Z",
) -> Risk:
    return Risk(
        risk_id=risk_id,
        kind=kind,
        source=SourceKind.FACTUAL,
        basis="basis text",
        affected_tasks=("TASK-001",),
        recommendation="recommend",
        suggested_deadline=due,
        severity=3,
        rationale="rationale",
    )


def _report(*, risks: tuple[Risk, ...] = ()) -> RiskReport:
    return RiskReport(
        merge_reporter_package_id="pkg.retchain",
        project_id="PRJ001",
        analysed_at="2026-08-15T00:00:00Z",
        risks=risks,
        coordination_meeting_recommended=False,
    )


def _config() -> ModelConfig:
    return ModelConfig(
        provider="offline",
        prompts_file=ROOT / "config" / "model-prompts.json",
        model=None,
        max_tokens=2000,
        timeout_seconds=30.0,
    )


def _prompts() -> PromptRegistry:
    return load_prompt_registry(ROOT / "config" / "model-prompts.json")


def _valid_suggestion_json() -> str:
    return json.dumps(
        {
            "inferred_risks": [
                {
                    "risk_id": "risk.inf.1",
                    "kind": "long_silence",
                    "affected_tasks": ["TASK-001", "TASK-002"],
                    "basis": "no progress report in window",
                    "recommendation": "reach out to owner",
                    "suggested_deadline": "2026-08-20T00:00:00Z",
                    "severity": 3,
                    "rationale": "model-inferred",
                }
            ]
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


class _FakeProvider:
    name = "fake"

    def __init__(self, content: str | None = None, error: Exception | None = None) -> None:
        self.content = content
        self.error = error

    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int,
        timeout_seconds: float,
    ) -> str:
        if self.error is not None:
            raise self.error
        assert self.content is not None
        return self.content


class RiskSuggestionModelTests(unittest.TestCase):
    def test_suggestion_validates_shape_and_defaults(self) -> None:
        suggestion = RiskSuggestion(
            risk_id="risk.inf.1",
            kind=RiskKind.LONG_SILENCE,
            affected_tasks=("TASK-001", "TASK-002"),
            basis="basis",
            recommendation="recommend",
            suggested_deadline="2026-08-20T00:00:00Z",
            severity=3,
            rationale="rationale",
        )
        self.assertIs(SourceKind.INFERRED, suggestion.source)
        self.assertTrue(suggestion.requires_confirmation)
        self.assertFalse(suggestion.formally_released)
        risk = suggestion.to_risk()
        self.assertEqual("risk.inf.1", risk.risk_id)
        self.assertIs(SourceKind.INFERRED, risk.source)

    def test_suggestion_rejects_bypass_flags_and_bad_fields(self) -> None:
        base = dict(
            risk_id="risk.inf.1",
            kind=RiskKind.LONG_SILENCE,
            affected_tasks=("TASK-001",),
            basis="basis",
            recommendation="recommend",
            suggested_deadline="2026-08-20T00:00:00Z",
            severity=3,
            rationale="rationale",
        )
        for mutation in (
            {"risk_id": "risk/inf/1"},
            {"kind": "long_silence"},
            {"source": SourceKind.FACTUAL},
            {"affected_tasks": ()},
            {"affected_tasks": ("TASK-002", "TASK-001")},
            {"suggested_deadline": "2026-08-20T00:00:00+00:00"},
            {"severity": 6},
            {"requires_confirmation": False},
            {"formally_released": True},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaises(RiskValidationError):
                    RiskSuggestion(**{**base, **mutation})


class RiskSuggestionAgentTests(unittest.TestCase):
    def test_offline_provider_returns_no_suggestions(self) -> None:
        agent = RiskSuggestionAgent()
        suggestions = agent.suggest(
            risk_report=_report(),
            project_id="PRJ001",
            provider=_FakeProvider(error=ModelUnavailableError("offline")),
            config=_config(),
            prompt_registry=_prompts(),
            now="2026-08-15T00:00:00Z",
        )
        self.assertEqual((), suggestions)

    def test_valid_suggestion_is_parsed_and_audited(self) -> None:
        agent = RiskSuggestionAgent()
        suggestions = agent.suggest(
            risk_report=_report(),
            project_id="PRJ001",
            provider=_FakeProvider(content=_valid_suggestion_json()),
            config=_config(),
            prompt_registry=_prompts(),
            now="2026-08-15T00:00:00Z",
        )
        self.assertEqual(1, len(suggestions))
        suggestion = suggestions[0]
        self.assertEqual("risk.inf.1", suggestion.risk_id)
        self.assertIs(RiskKind.LONG_SILENCE, suggestion.kind)
        audit = RiskSuggestionAgent.to_audit_record(suggestion)
        self.assertEqual("risk.suggestion", audit["kind"])
        joined = repr(audit).lower()
        for forbidden in ("basis", "recommendation", "rationale"):
            self.assertNotIn(forbidden, joined, f"audit leaked {forbidden!r}")

    def test_unknown_kind_is_rejected(self) -> None:
        payload = _valid_suggestion_json().replace("long_silence", "alien_risk")
        with self.assertRaises(ModelValidationError):
            RiskSuggestionAgent().suggest(
                risk_report=_report(),
                project_id="PRJ001",
                provider=_FakeProvider(content=payload),
                config=_config(),
                prompt_registry=_prompts(),
                now="2026-08-15T00:00:00Z",
            )

    def test_duplicate_risk_ids_are_rejected(self) -> None:
        payload = json.dumps(
            {
                "inferred_risks": [
                    {
                        "risk_id": "risk.inf.1",
                        "kind": "long_silence",
                        "affected_tasks": ["TASK-001"],
                        "basis": "b",
                        "recommendation": "r",
                        "suggested_deadline": "2026-08-20T00:00:00Z",
                        "severity": 3,
                        "rationale": "x",
                    },
                    {
                        "risk_id": "risk.inf.1",
                        "kind": "deadline_overrun",
                        "affected_tasks": ["TASK-002"],
                        "basis": "b",
                        "recommendation": "r",
                        "suggested_deadline": "2026-08-21T00:00:00Z",
                        "severity": 4,
                        "rationale": "x",
                    },
                ]
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        with self.assertRaises(ModelValidationError):
            RiskSuggestionAgent().suggest(
                risk_report=_report(),
                project_id="PRJ001",
                provider=_FakeProvider(content=payload),
                config=_config(),
                prompt_registry=_prompts(),
                now="2026-08-15T00:00:00Z",
            )


class RiskSuggestionApplyTests(unittest.TestCase):
    def _suggestions(self) -> tuple[RiskSuggestion, ...]:
        return (
            RiskSuggestion(
                risk_id="risk.inf.1",
                kind=RiskKind.LONG_SILENCE,
                affected_tasks=("TASK-001",),
                basis="basis",
                recommendation="recommend",
                suggested_deadline="2026-08-20T00:00:00Z",
                severity=3,
                rationale="rationale",
            ),
        )

    def _change(self, risk_ids: list[str]) -> ConfirmedStateChange:
        return ConfirmedStateChange(
            confirmed_by="u.pm",
            confirmed_at="2026-08-16T00:00:00Z",
            source_draft_id="draft.risk.inf",
            changes={"confirmed_risk_ids": risk_ids},
        )

    def test_apply_requires_confirmed_state_change(self) -> None:
        with self.assertRaises(ModelValidationError):
            RiskSuggestionAgent().apply(
                report=_report(),
                suggestions=self._suggestions(),
                change={"confirmed_risk_ids": ["risk.inf.1"]},  # type: ignore[arg-type]
            )

    def test_apply_appends_confirmed_suggestions_sorted(self) -> None:
        report = _report(risks=(_risk(risk_id="risk.2"),))
        updated = RiskSuggestionAgent().apply(
            report=report,
            suggestions=self._suggestions(),
            change=self._change(["risk.inf.1"]),
        )
        self.assertEqual(
            ("risk.2", "risk.inf.1"),
            tuple(risk.risk_id for risk in updated.risks),
        )
        inferred = updated.risks[1]
        self.assertIs(SourceKind.INFERRED, inferred.source)
        self.assertFalse(updated.formally_released)
        self.assertTrue(updated.requires_owner_confirmation)

    def test_apply_rejects_unknown_duplicate_or_existing_ids(self) -> None:
        agent = RiskSuggestionAgent()
        with self.assertRaises(ModelValidationError):
            agent.apply(
                report=_report(),
                suggestions=self._suggestions(),
                change=self._change(["risk.ghost"]),
            )
        with self.assertRaises(ModelValidationError):
            agent.apply(
                report=_report(),
                suggestions=self._suggestions(),
                change=self._change(["risk.inf.1", "risk.inf.1"]),
            )
        with self.assertRaises(ModelValidationError):
            agent.apply(
                report=_report(risks=(_risk(risk_id="risk.inf.1"),)),
                suggestions=self._suggestions(),
                change=self._change(["risk.inf.1"]),
            )

    def test_apply_rejects_deadline_before_analysed_at(self) -> None:
        suggestion = RiskSuggestion(
            risk_id="risk.inf.early",
            kind=RiskKind.LONG_SILENCE,
            affected_tasks=("TASK-001",),
            basis="basis",
            recommendation="recommend",
            suggested_deadline="2026-08-10T00:00:00Z",
            severity=3,
            rationale="rationale",
        )
        with self.assertRaises(ModelValidationError):
            RiskSuggestionAgent().apply(
                report=_report(),
                suggestions=(suggestion,),
                change=self._change(["risk.inf.early"]),
            )


if __name__ == "__main__":
    unittest.main()
