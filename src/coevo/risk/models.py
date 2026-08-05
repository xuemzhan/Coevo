"""risk.models - US-11 risk domain models, enums, errors and shared validation helpers (merged from the former package __init__)."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-11 风险领域模型：风险/报告/来源类型与校验。

from __future__ import annotations

import datetime as dt
import enum
from dataclasses import dataclass
from typing import Iterable
from src.coevo.merge import MergeCommitOutcome

class SourceKind(enum.Enum):
    FACTUAL = "factual"
    RULE = "rule"
    INFERRED = "inferred"

class RiskKind(enum.Enum):
    DEADLINE_OVERRUN = "deadline_overrun"
    PREDECESSOR_UNFINISHED = "predecessor_unfinished"
    LONG_SILENCE = "long_silence"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    SEVERE_COORDINATION_NEEDED = "severe_coordination_needed"
    AT_RISK_BLOOM = "at_risk_bloom"
    BLOCKED_BLOOM = "blocked_bloom"

@dataclass(frozen=True)
class Risk:
    risk_id: str
    kind: RiskKind
    source: SourceKind
    basis: str
    affected_tasks: tuple[str, ...]
    recommendation: str
    suggested_deadline: str
    severity: int
    rationale: str

    def __post_init__(self) -> None:
        _non_empty(self.risk_id, field="risk_id")
        if not isinstance(self.kind, RiskKind):
            raise ValueError("kind must be RiskKind")
        if not isinstance(self.source, SourceKind):
            raise ValueError("source must be SourceKind")
        if isinstance(self.severity, bool) or not isinstance(self.severity, int):
            raise ValueError("severity must be an integer in [1, 5]")
        if not 1 <= self.severity <= 5:
            raise ValueError("severity must be in [1, 5]")
        if not isinstance(self.affected_tasks, tuple) or not self.affected_tasks:
            raise ValueError("affected_tasks must be a non-empty tuple")
        for task_id in self.affected_tasks:
            _non_empty(task_id, field="affected_tasks item")
        if len(set(self.affected_tasks)) != len(self.affected_tasks):
            raise ValueError("affected_tasks must not contain duplicates")
        if self.affected_tasks != tuple(sorted(self.affected_tasks)):
            raise ValueError("affected_tasks must use stable sorted order")
        for name in ("basis", "recommendation", "rationale"):
            _non_empty(getattr(self, name), field=name)
        _parse_utc(self.suggested_deadline, field="suggested_deadline")

    def to_dict(self) -> dict[str, object]:
        """Serialize a risk to a JSON-safe dict."""
        return {
            "risk_id": self.risk_id,
            "kind": self.kind.value,
            "source": self.source.value,
            "basis": self.basis,
            "affected_tasks": list(self.affected_tasks),
            "recommendation": self.recommendation,
            "suggested_deadline": self.suggested_deadline,
            "severity": self.severity,
            "rationale": self.rationale,
        }

@dataclass(frozen=True)
class RiskReport:
    """Candidate-only report; formal publication remains an owner action."""

    merge_reporter_package_id: str
    project_id: str
    analysed_at: str
    risks: tuple[Risk, ...]
    coordination_meeting_recommended: bool
    requires_owner_confirmation: bool = True
    formally_released: bool = False

    def __post_init__(self) -> None:
        _non_empty(self.merge_reporter_package_id, field="merge_reporter_package_id")
        _non_empty(self.project_id, field="project_id")
        analysed_time = _parse_utc(self.analysed_at, field="analysed_at")
        if not isinstance(self.risks, tuple) or any(
            not isinstance(risk, Risk) for risk in self.risks
        ):
            raise ValueError("risks must be a tuple of Risk")
        risk_ids = tuple(risk.risk_id for risk in self.risks)
        if len(set(risk_ids)) != len(risk_ids):
            raise ValueError("risk IDs must be unique")
        if risk_ids != tuple(sorted(risk_ids)):
            raise ValueError("risks must use stable risk-ID order")
        if any(
            _parse_utc(risk.suggested_deadline, field="suggested_deadline")
            < analysed_time
            for risk in self.risks
        ):
            raise ValueError("suggested deadlines must not precede analysed_at")
        if not isinstance(self.coordination_meeting_recommended, bool):
            raise ValueError("coordination_meeting_recommended must be bool")
        if self.requires_owner_confirmation is not True:
            raise ValueError("risk reports must require owner confirmation")
        if self.formally_released is not False:
            raise ValueError("risk analysis cannot formally release risks")

    def to_dict(self) -> dict[str, object]:
        """Serialize a risk report to a JSON-safe dict."""
        return {
            "kind": "risk.report",
            "schema_version": "1.0",
            "merge_reporter_package_id": self.merge_reporter_package_id,
            "project_id": self.project_id,
            "analysed_at": self.analysed_at,
            "risk_count": len(self.risks),
            "risks": [risk.to_dict() for risk in self.risks],
            "coordination_meeting_recommended": self.coordination_meeting_recommended,
            "requires_owner_confirmation": self.requires_owner_confirmation,
            "formally_released": self.formally_released,
        }

class RiskAnalysisError(Exception):
    """Base class for fail-closed US-11 errors."""

class RiskValidationError(RiskAnalysisError):
    """The claimed post-merge facts or analysis inputs are inconsistent."""

@dataclass(frozen=True)
class MergeAndAnalyzeOutcome:
    commit: MergeCommitOutcome
    risk_report: RiskReport | None

    def __post_init__(self) -> None:
        if not isinstance(self.commit, MergeCommitOutcome):
            raise ValueError("commit must be MergeCommitOutcome")
        if self.commit.proposal.accepted != (self.risk_report is not None):
            raise ValueError("risk report must exist exactly for a committed merge")

def _non_empty(value: object, *, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")

def _parse_utc(value: object, *, field: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise RiskValidationError(f"{field} must be an ISO-8601 UTC string ending in Z")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise RiskValidationError(f"{field} must be a valid ISO-8601 UTC string") from exc
    if parsed.utcoffset() != dt.timedelta(0):
        raise RiskValidationError(f"{field} must use UTC")
    return parsed

def _source_kind_counts(risks: Iterable[Risk]) -> dict[str, int]:
    counts = {source.value: 0 for source in SourceKind}
    for risk in risks:
        counts[risk.source.value] += 1
    return counts
