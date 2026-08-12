"""US-11-AC-4 + MATURITY-O-08: model-inferred risk suggestion agent.

The deterministic :class:`RiskAnalyzer` covers factual/rule risks; this
optional agent asks a :class:`ModelProvider` for **additional** inferred
risks (``SourceKind.INFERRED``). Product positioning follows T-01 option B:
the model is an optional aid, the default stays offline.

Boundaries (fail-closed by construction)
----------------------------------------
* Output is a :class:`RiskSuggestion` -- a **draft**. It is never written
  into a confirmed report directly: :meth:`RiskSuggestionAgent.apply`
  requires a :class:`~src.coevo.model.ConfirmedStateChange` (human
  authorisation) and only then returns a new candidate
  :class:`RiskReport` with the confirmed suggestions appended as
  ``SourceKind.INFERRED`` risks. The report itself still requires owner
  confirmation before formal release (US-11 AC-8).
* Offline mode: when the provider is unavailable (no key / no egress
  approval / offline), :meth:`suggest` returns ``()`` and callers keep the
  deterministic analysis -- quality gates never call a network.
* Strict schema + bounds: malformed / oversized / unknown-kind /
  duplicate / out-of-window output raises :class:`ModelValidationError`
  and is never partially applied.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from src.coevo.model import (
    ConfirmedStateChange,
    ModelConfig,
    ModelProvider,
    ModelUnavailableError,
    ModelValidationError,
    PromptRegistry,
    ensure_confirmed_state_change,
    parse_json_object,
)
from src.coevo.timefmt import is_iso_utc_z

from .models import Risk, RiskKind, RiskReport, RiskValidationError, SourceKind


_SAFE_ID = re.compile(r"^[a-zA-Z0-9_.\-]{1,128}$")
_MAX_SUGGESTIONS = 5
_MAX_STRING_BYTES = 1024
_MAX_AFFECTED_TASKS = 16
_MAX_PROMPT_BYTES = 16 * 1024
_MAX_RESPONSE_BYTES = 64 * 1024
_KIND_VALUES = frozenset(kind.value for kind in RiskKind)


@dataclass(frozen=True)
class RiskSuggestion:
    """A model-inferred risk candidate that must be human-confirmed."""

    risk_id: str
    kind: RiskKind
    affected_tasks: tuple[str, ...]
    basis: str
    recommendation: str
    suggested_deadline: str
    severity: int
    rationale: str
    source: SourceKind = SourceKind.INFERRED
    requires_confirmation: bool = True
    formally_released: bool = False

    def __post_init__(self) -> None:
        if not _SAFE_ID.fullmatch(self.risk_id):
            raise RiskValidationError(
                f"risk_id must be a safe id; got {self.risk_id!r}"
            )
        if not isinstance(self.kind, RiskKind):
            raise RiskValidationError("kind must be RiskKind")
        if self.source is not SourceKind.INFERRED:
            raise RiskValidationError(
                "risk suggestions must carry SourceKind.INFERRED"
            )
        if (
            not isinstance(self.affected_tasks, tuple)
            or not self.affected_tasks
            or len(self.affected_tasks) > _MAX_AFFECTED_TASKS
        ):
            raise RiskValidationError(
                "affected_tasks must be a non-empty bounded tuple"
            )
        for task_id in self.affected_tasks:
            if not _SAFE_ID.fullmatch(task_id):
                raise RiskValidationError(
                    f"affected_tasks item must be a safe id; got {task_id!r}"
                )
        if len(set(self.affected_tasks)) != len(self.affected_tasks):
            raise RiskValidationError("affected_tasks must not contain duplicates")
        if self.affected_tasks != tuple(sorted(self.affected_tasks)):
            raise RiskValidationError("affected_tasks must use stable sorted order")
        for name in ("basis", "recommendation", "rationale"):
            value = getattr(self, name)
            if (
                not isinstance(value, str)
                or not value.strip()
                or len(value.encode("utf-8")) > _MAX_STRING_BYTES
            ):
                raise RiskValidationError(f"{name} must be a bounded non-empty string")
        if not is_iso_utc_z(self.suggested_deadline):
            raise RiskValidationError(
                f"suggested_deadline must be ISO-8601 UTC 'Z'; got {self.suggested_deadline!r}"
            )
        if (
            isinstance(self.severity, bool)
            or not isinstance(self.severity, int)
            or not 1 <= self.severity <= 5
        ):
            raise RiskValidationError("severity must be an integer in [1, 5]")
        if self.requires_confirmation is not True:
            raise RiskValidationError(
                "risk suggestions must require owner confirmation"
            )
        if self.formally_released is not False:
            raise RiskValidationError(
                "risk suggestions cannot be formally released"
            )

    def to_risk(self) -> Risk:
        """Convert the confirmed suggestion into a risk-report candidate."""

        return Risk(
            risk_id=self.risk_id,
            kind=self.kind,
            source=self.source,
            basis=self.basis,
            affected_tasks=self.affected_tasks,
            recommendation=self.recommendation,
            suggested_deadline=self.suggested_deadline,
            severity=self.severity,
            rationale=self.rationale,
        )


def _project_summary(project_id: str, now: str) -> str:
    return json.dumps(
        {"project_id": project_id, "analysed_at": now},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _risk_report_summary(report: RiskReport) -> str:
    payload = {
        "merge_reporter_package_id": report.merge_reporter_package_id,
        "project_id": report.project_id,
        "analysed_at": report.analysed_at,
        "existing_risks": [
            {
                "risk_id": risk.risk_id,
                "kind": risk.kind.value,
                "severity": risk.severity,
                "suggested_deadline": risk.suggested_deadline,
                "affected_tasks": list(risk.affected_tasks),
            }
            for risk in report.risks
        ],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _parse_suggestion(raw: object) -> RiskSuggestion:
    if not isinstance(raw, dict):
        raise ModelValidationError("risk suggestion entry must be an object")
    try:
        risk_id = raw["risk_id"]
        kind_value = raw["kind"]
        affected = raw["affected_tasks"]
        basis = raw["basis"]
        recommendation = raw["recommendation"]
        suggested_deadline = raw["suggested_deadline"]
        severity = raw["severity"]
        rationale = raw["rationale"]
    except KeyError as exc:
        raise ModelValidationError(
            f"risk suggestion missing field {exc.args[0]!r}"
        ) from exc
    if not isinstance(kind_value, str) or kind_value not in _KIND_VALUES:
        raise ModelValidationError(f"unknown risk kind {kind_value!r}")
    if (
        not isinstance(affected, list)
        or not affected
        or len(affected) > _MAX_AFFECTED_TASKS
    ):
        raise ModelValidationError("affected_tasks must be a bounded list")
    if any(not isinstance(item, str) for item in affected):
        raise ModelValidationError("affected_tasks items must be strings")
    return RiskSuggestion(
        risk_id=risk_id,
        kind=RiskKind(kind_value),
        affected_tasks=tuple(sorted(set(affected))),
        basis=basis,
        recommendation=recommendation,
        suggested_deadline=suggested_deadline,
        severity=severity,
        rationale=rationale,
    )


class RiskSuggestionAgent:
    """Model-assisted inferred-risk suggestion facade (optional aid)."""

    def suggest(
        self,
        *,
        risk_report: RiskReport,
        project_id: str,
        provider: ModelProvider,
        config: ModelConfig,
        prompt_registry: PromptRegistry,
        now: str,
    ) -> tuple[RiskSuggestion, ...]:
        """Ask the provider for candidate inferred risks; ``()`` when offline."""

        if not isinstance(risk_report, RiskReport):
            raise RiskValidationError("risk_report must be RiskReport")
        if not isinstance(project_id, str) or not _SAFE_ID.fullmatch(project_id):
            raise RiskValidationError("project_id must be a safe id")
        if not isinstance(provider, ModelProvider):
            raise RiskValidationError("provider must implement ModelProvider")
        provider_key = (
            f"{provider.name}/{config.model}"
            if getattr(provider, "name", None) == "deepseek"
            else None
        )
        template = prompt_registry.resolve(
            "risk.suggest",
            provider_key=provider_key,
        )
        user = template.expand(
            values={
                "project": _project_summary(project_id, now),
                "flow": _risk_report_summary(risk_report),
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
            return ()
        parsed = parse_json_object(content, max_bytes=_MAX_RESPONSE_BYTES)
        return self._validate(parsed)

    def _validate(self, parsed: dict[str, object]) -> tuple[RiskSuggestion, ...]:
        raw = parsed.get("inferred_risks", [])
        if not isinstance(raw, list) or not raw or len(raw) > _MAX_SUGGESTIONS:
            raise ModelValidationError(
                "inferred_risks must be a bounded non-empty list"
            )
        suggestions = tuple(_parse_suggestion(item) for item in raw)
        ids = [suggestion.risk_id for suggestion in suggestions]
        if len(set(ids)) != len(ids):
            raise ModelValidationError("inferred_risks contain duplicate risk ids")
        return suggestions

    def apply(
        self,
        *,
        report: RiskReport,
        suggestions: tuple[RiskSuggestion, ...],
        change: ConfirmedStateChange,
    ) -> RiskReport:
        """Return a new candidate report including the confirmed suggestions.

        Fail-closed: only a :class:`ConfirmedStateChange` may pass; unknown /
        duplicate / out-of-window suggestion ids are rejected and no partial
        report is produced. The returned report still requires owner
        confirmation (US-11 AC-8).
        """

        if not isinstance(report, RiskReport):
            raise RiskValidationError("report must be RiskReport")
        if not isinstance(suggestions, tuple) or not all(
            isinstance(item, RiskSuggestion) for item in suggestions
        ):
            raise RiskValidationError("suggestions must be a tuple of RiskSuggestion")
        confirmed = ensure_confirmed_state_change(change)
        changes = confirmed.changes
        raw_ids = changes.get("confirmed_risk_ids")
        if not isinstance(raw_ids, list) or not raw_ids:
            raise ModelValidationError(
                "confirmed_risk_ids must be a non-empty list"
            )
        ids = [str(item) for item in raw_ids]
        if len(set(ids)) != len(ids):
            raise ModelValidationError("confirmed_risk_ids contain duplicates")
        by_id = {suggestion.risk_id: suggestion for suggestion in suggestions}
        unknown = [risk_id for risk_id in ids if risk_id not in by_id]
        if unknown:
            raise ModelValidationError(
                f"confirmed suggestions reference unknown ids: {unknown}"
            )
        existing_ids = {risk.risk_id for risk in report.risks}
        if set(ids) & existing_ids:
            raise ModelValidationError(
                "confirmed suggestions repeat existing risk ids"
            )
        analysed = report.analysed_at
        for risk_id in ids:
            deadline = by_id[risk_id].suggested_deadline
            if deadline < analysed:
                raise ModelValidationError(
                    f"suggested_deadline {deadline} precedes analysed_at {analysed}"
                )
        new_risks = tuple(
            sorted(
                report.risks + tuple(by_id[risk_id].to_risk() for risk_id in ids),
                key=lambda risk: risk.risk_id,
            )
        )
        return RiskReport(
            merge_reporter_package_id=report.merge_reporter_package_id,
            project_id=report.project_id,
            analysed_at=report.analysed_at,
            risks=new_risks,
            coordination_meeting_recommended=report.coordination_meeting_recommended,
            requires_owner_confirmation=report.requires_owner_confirmation,
            formally_released=report.formally_released,
        )

    @staticmethod
    def to_audit_record(suggestion: RiskSuggestion) -> dict[str, object]:
        """Project a suggestion to audit without sensitive business phrasing."""

        if not isinstance(suggestion, RiskSuggestion):
            raise RiskValidationError("suggestion must be a RiskSuggestion")
        return {
            "kind": "risk.suggestion",
            "schema_version": "1.0",
            "risk_id": suggestion.risk_id,
            "risk_kind": suggestion.kind.value,
            "source": suggestion.source.value,
            "severity": suggestion.severity,
            "suggested_deadline": suggestion.suggested_deadline,
            "affected_task_count": len(suggestion.affected_tasks),
            "requires_confirmation": True,
            "formally_released": False,
        }


__all__ = ["RiskSuggestion", "RiskSuggestionAgent"]
