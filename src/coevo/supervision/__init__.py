"""US-12 监督/会议协调 service facade (9 AC).

Scope
-----
Consumes the US-11 ``RiskReport`` and emits:

* :class:`SupervisionItem`        (AC-1, AC-2: 风险转督办项 + 责任主体 / 完成时间 / 关闭条件)
* :class:`EscalationSuggestion`   (AC-4: 逾期/未关闭分级升级)
* :class:`MeetingProposal`        (AC-5/6/7: 会议建议 + 议题/背景/待决)
* :class:`MeetingConclusion`      (AC-8: 会议结论 -> 任务 / 风险处置 / 督办项 投影)

This slice is the PURE half:

* No IO, no LLM, no scheduler.
* The "meeting" output is a *proposal only* -- no actual invitation,
  no calendar, no model output. The coordinating agent consumes the
  proposal and decides whether to convene.
* All dataclasses are frozen + exact-type + ISO-8601 UTC `Z` time strings.
* ``to_audit_record`` excludes sensitive business phrasing
  (``basis`` / ``recommendation``) per project policy.
"""
from __future__ import annotations

import datetime as dt
import enum
from dataclasses import dataclass
from typing import Iterable

from src.coevo.risk import (
    Risk,
    RiskKind,
    RiskReport,
    RiskValidationError,
    SourceKind,
)


SUPERVISION_DOMAIN = "coevo.supervision"
SUPERVISION_SCHEMA = "1.0"
MEETING_DOMAIN = "coevo.meeting.coordination"
MEETING_SCHEMA = "1.0"

SUPERVISABLE_RISK_KINDS = frozenset({
    RiskKind.DEADLINE_OVERRUN,
    RiskKind.PREDECESSOR_UNFINISHED,
    RiskKind.LONG_SILENCE,
    RiskKind.INSUFFICIENT_EVIDENCE,
    RiskKind.SEVERE_COORDINATION_NEEDED,
    RiskKind.AT_RISK_BLOOM,
    RiskKind.BLOCKED_BLOOM,
})

COORDINATION_RECOMMENDED_KINDS = frozenset({
    RiskKind.SEVERE_COORDINATION_NEEDED,
    RiskKind.BLOCKED_BLOOM,
    RiskKind.DEADLINE_OVERRUN,
})


class SupervisionError(Exception):
    """Base class for fail-closed US-12 errors."""


class SupervisionValidationError(SupervisionError):
    """The risk report or the project context is inconsistent."""


class EscalationLevel(enum.Enum):
    """AC-4 graded escalation; higher levels imply owner-level action."""
    NONE = "none"
    WATCH = "watch"
    ESCALATE_TO_OWNER = "escalate_to_owner"
    EMERGENCY = "emergency"


class MeetingConclusionKind(enum.Enum):
    """AC-8 conclusion projection: where the meeting outcome lands."""
    NEW_TASK = "new_task"
    RISK_DISPOSITION = "risk_disposition"
    NEW_SUPERVISION_ITEM = "new_supervision_item"


@dataclass(frozen=True)
class SupervisionItem:
    """AC-1/AC-2: a single supervision item bound to one risk.

    The ``item_id`` format is ``sup.<project_id>.<risk_id>.<index>``
    so the audit log can trace every supervision item back to the
    originating risk.
    """
    item_id: str
    project_id: str
    risk_id: str
    risk_kind: RiskKind
    responsible_subject: str
    due_at: str
    closing_condition: str
    affected_tasks: tuple[str, ...]
    created_at: str

    def __post_init__(self) -> None:
        _non_empty(self.item_id, field="item_id")
        _non_empty(self.project_id, field="project_id")
        _non_empty(self.risk_id, field="risk_id")
        if not isinstance(self.risk_kind, RiskKind):
            raise SupervisionValidationError("risk_kind must be RiskKind")
        _non_empty(self.responsible_subject, field="responsible_subject")
        _parse_utc(self.due_at, field="due_at")
        _non_empty(self.closing_condition, field="closing_condition")
        if not isinstance(self.affected_tasks, tuple) or not self.affected_tasks:
            raise SupervisionValidationError("affected_tasks must be a non-empty tuple")
        for task_id in self.affected_tasks:
            _non_empty(task_id, field="affected_tasks item")
        if len(set(self.affected_tasks)) != len(self.affected_tasks):
            raise SupervisionValidationError("affected_tasks must not contain duplicates")
        # NOTE: we silently sort here; sortedness is a projection
        # property of the audit output, not a precondition on the
        # caller. The earlier check rejects duplicates (the only
        # structural violation we care about).
        object.__setattr__(
            self, "affected_tasks", tuple(sorted(self.affected_tasks)),
        )
        _parse_utc(self.created_at, field="created_at")

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "project_id": self.project_id,
            "risk_id": self.risk_id,
            "risk_kind": self.risk_kind.value,
            "responsible_subject": self.responsible_subject,
            "due_at": self.due_at,
            "closing_condition": self.closing_condition,
            "affected_tasks": list(self.affected_tasks),
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class EscalationSuggestion:
    """AC-4 graded escalation suggestion; owner decides whether to act."""
    item_id: str
    level: EscalationLevel
    reason: str
    suggested_at: str

    def __post_init__(self) -> None:
        _non_empty(self.item_id, field="item_id")
        if not isinstance(self.level, EscalationLevel):
            raise SupervisionValidationError("level must be EscalationLevel")
        _non_empty(self.reason, field="reason")
        _parse_utc(self.suggested_at, field="suggested_at")

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "level": self.level.value,
            "reason": self.reason,
            "suggested_at": self.suggested_at,
        }


@dataclass(frozen=True)
class MeetingAgendaItem:
    """AC-7: one agenda entry with background materials and open questions."""
    agenda_id: str
    title: str
    background: str
    open_questions: tuple[str, ...]

    def __post_init__(self) -> None:
        _non_empty(self.agenda_id, field="agenda_id")
        _non_empty(self.title, field="title")
        _non_empty(self.background, field="background")
        if not isinstance(self.open_questions, tuple) or not self.open_questions:
            raise SupervisionValidationError("open_questions must be a non-empty tuple")
        for question in self.open_questions:
            _non_empty(question, field="open_questions item")
        if len(set(self.open_questions)) != len(self.open_questions):
            raise SupervisionValidationError("open_questions must not contain duplicates")
        if self.open_questions != tuple(sorted(self.open_questions)):
            raise SupervisionValidationError("open_questions must use stable sorted order")

    def to_dict(self) -> dict[str, object]:
        return {
            "agenda_id": self.agenda_id,
            "title": self.title,
            "background": self.background,
            "open_questions": list(self.open_questions),
        }


@dataclass(frozen=True)
class MeetingProposal:
    """AC-5/AC-6/AC-7: a meeting *proposal* (never an actual meeting).

    ``proposed_for_recipient_cert_id`` is the verified project owner
    cert id from US-10/US-11; the proposal is *addressed* to that
    recipient and the recipient confirms before any meeting is
    convened. ``formally_released=False`` is enforced.
    """
    proposal_id: str
    project_id: str
    proposed_for_recipient_cert_id: str
    agenda: tuple[MeetingAgendaItem, ...]
    created_at: str
    risk_ids: tuple[str, ...]
    coordination_meeting_recommended: bool
    requires_owner_confirmation: bool = True
    formally_released: bool = False

    def __post_init__(self) -> None:
        _non_empty(self.proposal_id, field="proposal_id")
        _non_empty(self.project_id, field="project_id")
        _non_empty(self.proposed_for_recipient_cert_id, field="proposed_for_recipient_cert_id")
        if not isinstance(self.agenda, tuple) or not self.agenda:
            raise SupervisionValidationError("agenda must be a non-empty tuple of MeetingAgendaItem")
        if any(not isinstance(item, MeetingAgendaItem) for item in self.agenda):
            raise SupervisionValidationError("agenda items must be exact MeetingAgendaItem")
        agenda_ids = tuple(item.agenda_id for item in self.agenda)
        if len(set(agenda_ids)) != len(agenda_ids):
            raise SupervisionValidationError("agenda_id must be unique")
        if agenda_ids != tuple(sorted(agenda_ids)):
            raise SupervisionValidationError("agenda must use stable agenda_id order")
        _parse_utc(self.created_at, field="created_at")
        if not isinstance(self.risk_ids, tuple) or not self.risk_ids:
            raise SupervisionValidationError("risk_ids must be a non-empty tuple")
        for risk_id in self.risk_ids:
            _non_empty(risk_id, field="risk_ids item")
        if self.risk_ids != tuple(sorted(set(self.risk_ids))):
            raise SupervisionValidationError("risk_ids must be unique and sorted")
        if not isinstance(self.coordination_meeting_recommended, bool):
            raise SupervisionValidationError("coordination_meeting_recommended must be bool")
        if self.requires_owner_confirmation is not True:
            raise SupervisionValidationError("meeting proposal must require owner confirmation")
        if self.formally_released is not False:
            raise SupervisionValidationError("meeting proposal cannot be formally released")

    def to_dict(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "project_id": self.project_id,
            "proposed_for_recipient_cert_id": self.proposed_for_recipient_cert_id,
            "agenda": [item.to_dict() for item in self.agenda],
            "created_at": self.created_at,
            "risk_ids": list(self.risk_ids),
            "coordination_meeting_recommended": self.coordination_meeting_recommended,
            "requires_owner_confirmation": True,
            "formally_released": False,
        }


@dataclass(frozen=True)
class MeetingConclusionProjection:
    """AC-8: meeting conclusion projected to one of three downstream kinds."""
    kind: MeetingConclusionKind
    subject_ref: str
    note: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, MeetingConclusionKind):
            raise SupervisionValidationError("kind must be MeetingConclusionKind")
        _non_empty(self.subject_ref, field="subject_ref")
        _non_empty(self.note, field="note")

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "subject_ref": self.subject_ref,
            "note": self.note,
        }


@dataclass(frozen=True)
class SupervisionOutcome:
    """AC-9 full audit projection; one immutable record per coordination cycle."""
    project_id: str
    items: tuple[SupervisionItem, ...]
    escalations: tuple[EscalationSuggestion, ...]
    meeting_proposal: MeetingProposal | None
    conclusions: tuple[MeetingConclusionProjection, ...]
    created_at: str
    requires_owner_confirmation: bool = True
    formally_released: bool = False

    def __post_init__(self) -> None:
        _non_empty(self.project_id, field="project_id")
        if not isinstance(self.items, tuple):
            raise SupervisionValidationError("items must be a tuple of SupervisionItem")
        if any(not isinstance(item, SupervisionItem) for item in self.items):
            raise SupervisionValidationError("items must be exact SupervisionItem")
        item_ids = tuple(item.item_id for item in self.items)
        if len(set(item_ids)) != len(item_ids):
            raise SupervisionValidationError("item_id must be unique")
        if item_ids != tuple(sorted(item_ids)):
            raise SupervisionValidationError("items must use stable item_id order")
        if not isinstance(self.escalations, tuple):
            raise SupervisionValidationError("escalations must be a tuple of EscalationSuggestion")
        if any(not isinstance(e, EscalationSuggestion) for e in self.escalations):
            raise SupervisionValidationError("escalations must be exact EscalationSuggestion")
        esc_item_ids = tuple(e.item_id for e in self.escalations)
        if esc_item_ids != tuple(sorted(esc_item_ids)):
            raise SupervisionValidationError("escalations must use stable item_id order")
        if set(esc_item_ids) - set(item_ids):
            raise SupervisionValidationError("escalations reference unknown supervision items")
        if self.meeting_proposal is not None and not isinstance(
            self.meeting_proposal, MeetingProposal,
        ):
            raise SupervisionValidationError("meeting_proposal must be exact MeetingProposal")
        if not isinstance(self.conclusions, tuple):
            raise SupervisionValidationError("conclusions must be a tuple of MeetingConclusionProjection")
        if any(not isinstance(c, MeetingConclusionProjection) for c in self.conclusions):
            raise SupervisionValidationError("conclusions must be exact MeetingConclusionProjection")
        if self.conclusions:
            if any(c.kind is MeetingConclusionKind.NEW_SUPERVISION_ITEM for c in self.conclusions):
                raise SupervisionValidationError(
                    "conclusions cannot synthesise new supervision items; "
                    "supervision items are only synthesised from risks"
                )
        _parse_utc(self.created_at, field="created_at")
        if self.requires_owner_confirmation is not True:
            raise SupervisionValidationError("supervision outcome must require owner confirmation")
        if self.formally_released is not False:
            raise SupervisionValidationError("supervision outcome cannot be formally released")

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "supervision.outcome",
            "schema_version": "1.0",
            "project_id": self.project_id,
            "item_count": len(self.items),
            "escalation_count": len(self.escalations),
            "meeting_proposal": (
                self.meeting_proposal.to_dict() if self.meeting_proposal is not None else None
            ),
            "conclusion_count": len(self.conclusions),
            "created_at": self.created_at,
            "requires_owner_confirmation": True,
            "formally_released": False,
        }


class SupervisionCoordinator:
    """Pure facade; consumes one verified RiskReport per cycle."""

    def __init__(
        self,
        *,
        responsible_subject_resolver=None,
    ) -> None:
        # Default resolver: project_id == responsible_subject
        # (the real resolver is out-of-scope and remains an owner-side
        # call; here we just provide a deterministic placeholder so
        # the facade is testable in isolation).
        self._resolver = responsible_subject_resolver or (lambda project_id: project_id)

    def coordinate(
        self,
        *,
        risk_report: RiskReport,
        project_recipient_cert_id: str,
        now: str,
    ) -> SupervisionOutcome:
        if not isinstance(risk_report, RiskReport):
            raise SupervisionValidationError("risk_report must be RiskReport")
        if not isinstance(project_recipient_cert_id, str) or not project_recipient_cert_id:
            raise SupervisionValidationError("project_recipient_cert_id must be a non-empty string")
        _parse_utc(now, field="now")
        try:
            reference_time = _parse_utc(now, field="now")
        except SupervisionValidationError:
            raise
        # Reject any risk that fails our kind-allow-list (defense in depth:
        # US-11's RiskKind enum is closed so this is a no-op today, but
        # a future additive enum value would be rejected here).
        unknown_kinds = sorted(
            {risk.kind.value for risk in risk_report.risks}
            - {kind.value for kind in SUPERVISABLE_RISK_KINDS}
        )
        if unknown_kinds:
            raise SupervisionValidationError(
                f"risk_report contains non-supervisable kinds: {unknown_kinds}"
            )
        responsible_subject = self._resolver(risk_report.project_id)
        items: list[SupervisionItem] = []
        for index, risk in enumerate(
            sorted(risk_report.risks, key=lambda r: r.risk_id),
        ):
            items.append(SupervisionItem(
                item_id=_supervision_item_id(
                    risk_report.project_id, risk.risk_id, index,
                ),
                project_id=risk_report.project_id,
                risk_id=risk.risk_id,
                risk_kind=risk.kind,
                responsible_subject=responsible_subject,
                due_at=risk.suggested_deadline,
                closing_condition=_closing_condition_for(risk),
                affected_tasks=risk.affected_tasks,
                created_at=now,
            ))
        escalations: list[EscalationSuggestion] = []
        for item in items:
            level = _escalation_level_for(item, reference_time)
            if level is EscalationLevel.NONE:
                continue
            escalations.append(EscalationSuggestion(
                item_id=item.item_id,
                level=level,
                reason=_escalation_reason_for(item, level),
                suggested_at=now,
            ))
        meeting = _meeting_proposal_for(
            risk_report=risk_report,
            project_recipient_cert_id=project_recipient_cert_id,
            now=now,
        )
        conclusions = _conclusions_for(
            risk_report=risk_report,
            meeting=meeting,
        )
        return SupervisionOutcome(
            project_id=risk_report.project_id,
            items=tuple(items),
            escalations=tuple(escalations),
            meeting_proposal=meeting,
            conclusions=tuple(conclusions),
            created_at=now,
        )

    def to_audit_record(self, outcome: SupervisionOutcome) -> dict[str, object]:
        if not isinstance(outcome, SupervisionOutcome):
            raise SupervisionError("outcome must be SupervisionOutcome")
        return {
            "kind": "supervision.coordination",
            "schema_version": "1.0",
            "project_id": outcome.project_id,
            "item_ids": [item.item_id for item in outcome.items],
            "risk_ids": sorted({item.risk_id for item in outcome.items}),
            "escalation_levels": sorted({e.level.value for e in outcome.escalations}),
            "meeting_proposal_id": (
                outcome.meeting_proposal.proposal_id
                if outcome.meeting_proposal is not None else None
            ),
            "conclusion_kinds": sorted({c.kind.value for c in outcome.conclusions}),
            "created_at": outcome.created_at,
            "requires_owner_confirmation": True,
            "formally_released": False,
        }


# ----------------------- helpers -----------------------


def _closing_condition_for(risk: Risk) -> str:
    if risk.kind is RiskKind.DEADLINE_OVERRUN:
        return "renegotiated plan_end accepted by project owner (US-12 AC-1)"
    if risk.kind is RiskKind.PREDECESSOR_UNFINISHED:
        return "predecessor task closed with accepted completion marker (US-12 AC-1)"
    if risk.kind is RiskKind.LONG_SILENCE:
        return "next progress report accepted after follower outreach (US-12 AC-1)"
    if risk.kind is RiskKind.INSUFFICIENT_EVIDENCE:
        return "evidence shortfall satisfied by accepted deliverable (US-12 AC-1)"
    if risk.kind is RiskKind.SEVERE_COORDINATION_NEEDED:
        return "coordination meeting closed and outcome recorded (US-12 AC-1)"
    if risk.kind is RiskKind.AT_RISK_BLOOM:
        return "dependent tasks checkpoint accepted by project owner (US-12 AC-1)"
    if risk.kind is RiskKind.BLOCKED_BLOOM:
        return "blocker removed or accepted unblock plan (US-12 AC-1)"
    raise SupervisionValidationError(f"unknown risk kind: {risk.kind!r}")


def _escalation_level_for(
    item: SupervisionItem, reference_time: dt.datetime,
) -> EscalationLevel:
    due = _parse_utc(item.due_at, field="due_at")
    delta = (reference_time - due).total_seconds()
    if item.risk_kind in (
        RiskKind.SEVERE_COORDINATION_NEEDED, RiskKind.BLOCKED_BLOOM,
    ):
        if delta >= 0:
            return EscalationLevel.EMERGENCY
        return EscalationLevel.ESCALATE_TO_OWNER
    if item.risk_kind is RiskKind.DEADLINE_OVERRUN:
        if delta >= 0:
            return EscalationLevel.ESCALATE_TO_OWNER
        return EscalationLevel.WATCH
    if delta >= 0:
        return EscalationLevel.WATCH
    return EscalationLevel.NONE


def _escalation_reason_for(
    item: SupervisionItem, level: EscalationLevel,
) -> str:
    if level is EscalationLevel.EMERGENCY:
        return (
            f"now >= due_at for {item.risk_kind.value} (US-12 AC-4 emergency); "
            f"affected tasks={list(item.affected_tasks)}"
        )
    if level is EscalationLevel.ESCALATE_TO_OWNER:
        return (
            f"now >= due_at for {item.risk_kind.value} (US-12 AC-4 owner escalation); "
            f"affected tasks={list(item.affected_tasks)}"
        )
    if level is EscalationLevel.WATCH:
        return (
            f"approaching due_at for {item.risk_kind.value} (US-12 AC-4 watch); "
            f"affected tasks={list(item.affected_tasks)}"
        )
    return "no escalation needed"


def _meeting_proposal_for(
    *,
    risk_report: RiskReport,
    project_recipient_cert_id: str,
    now: str,
) -> MeetingProposal | None:
    if not risk_report.coordination_meeting_recommended:
        return None
    agenda: list[MeetingAgendaItem] = []
    risk_ids: list[str] = []
    # Build one agenda entry per COORDINATION_RECOMMENDED_KINDS risk
    # (sorted by risk_id for stable order).
    relevant = sorted(
        (risk for risk in risk_report.risks
         if risk.kind in COORDINATION_RECOMMENDED_KINDS),
        key=lambda risk: risk.risk_id,
    )
    for index, risk in enumerate(relevant):
        risk_ids.append(risk.risk_id)
        agenda.append(MeetingAgendaItem(
            agenda_id=f"agenda.{risk_report.project_id}.{index:02d}",
            title=_agenda_title_for(risk),
            background=(
                f"risk_kind={risk.kind.value} affects "
                f"{list(risk.affected_tasks)} (US-12 AC-7 background)"
            ),
            open_questions=tuple(sorted({
                f"is the suggested deadline {risk.suggested_deadline} acceptable?",
                f"who owns the {risk.kind.value} remediation?",
            })),
        ))
    if not agenda:
        return None
    return MeetingProposal(
        proposal_id=f"meeting.{risk_report.project_id}.{risk_report.merge_reporter_package_id}",
        project_id=risk_report.project_id,
        proposed_for_recipient_cert_id=project_recipient_cert_id,
        agenda=tuple(agenda),
        created_at=now,
        risk_ids=tuple(sorted(set(risk_ids))),
        coordination_meeting_recommended=True,
    )


def _agenda_title_for(risk: Risk) -> str:
    return f"address {risk.kind.value} for {','.join(risk.affected_tasks)} (US-12 AC-7)"


def _conclusions_for(
    *,
    risk_report: RiskReport,
    meeting: MeetingProposal | None,
) -> tuple[MeetingConclusionProjection, ...]:
    conclusions: list[MeetingConclusionProjection] = []
    if meeting is None:
        return tuple(conclusions)
    # AC-8: meeting outcome projects to risk_disposition per agenda
    # and to new_task for the highest-severity open question.
    for agenda in meeting.agenda:
        conclusions.append(MeetingConclusionProjection(
            kind=MeetingConclusionKind.RISK_DISPOSITION,
            subject_ref=agenda.agenda_id,
            note=f"meeting outcome must record a risk disposition for {agenda.agenda_id}",
        ))
    if any(r.severity >= 4 for r in risk_report.risks):
        conclusions.append(MeetingConclusionProjection(
            kind=MeetingConclusionKind.NEW_TASK,
            subject_ref=f"new_task.{risk_report.project_id}",
            note="highest-severity risk requires a new remediation task (US-12 AC-8)",
        ))
    # Stable order: kind then subject_ref
    conclusions.sort(key=lambda c: (c.kind.value, c.subject_ref))
    return tuple(conclusions)


def _supervision_item_id(project_id: str, risk_id: str, index: int) -> str:
    return f"sup.{project_id}.{risk_id}.{index:02d}"


def _non_empty(value: object, *, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SupervisionValidationError(f"{field} must be a non-empty string")


def _parse_utc(value: object, *, field: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise SupervisionValidationError(
            f"{field} must be an ISO-8601 UTC string ending in Z"
        )
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise SupervisionValidationError(
            f"{field} must be a valid ISO-8601 UTC string"
        ) from exc
    if parsed.utcoffset() != dt.timedelta(0):
        raise SupervisionValidationError(f"{field} must use UTC")
    return parsed


__all__ = [
    "COORDINATION_RECOMMENDED_KINDS",
    "EscalationLevel",
    "EscalationSuggestion",
    "MEETING_DOMAIN",
    "MEETING_SCHEMA",
    "MeetingAgendaItem",
    "MeetingConclusionKind",
    "MeetingConclusionProjection",
    "MeetingProposal",
    "SUPERVISABLE_RISK_KINDS",
    "SUPERVISION_DOMAIN",
    "SUPERVISION_SCHEMA",
    "SupervisionCoordinator",
    "SupervisionError",
    "SupervisionItem",
    "SupervisionOutcome",
    "SupervisionValidationError",
]