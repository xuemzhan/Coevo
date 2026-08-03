"""supervision.models - US-12 supervision/meeting domain models, enums, errors and shared validators."""

from __future__ import annotations

import datetime as dt
import enum
from dataclasses import dataclass
from typing import Final
from src.coevo.risk import RiskKind

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

class ReminderKind(enum.Enum):
    """AC-3 reminder/urge granularity for the responsible subject."""
    NONE = "none"
    REMIND = "remind"
    URGE = "urge"

REMINDER_WINDOW_SEC: Final[int] = 86_400  # 24h before due_at

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
class ReminderSuggestion:
    """AC-3: a reminder/urge suggestion bound to one supervision item.

    ``REMIND`` fires when ``due_at`` is inside :data:`REMINDER_WINDOW_SEC`;
    ``URGE`` fires once ``due_at`` has passed. The suggestion is advisory
    only -- the responsible subject decides whether to act.
    """
    item_id: str
    kind: ReminderKind
    reason: str
    suggested_at: str

    def __post_init__(self) -> None:
        _non_empty(self.item_id, field="item_id")
        if not isinstance(self.kind, ReminderKind):
            raise SupervisionValidationError("kind must be ReminderKind")
        _non_empty(self.reason, field="reason")
        _parse_utc(self.suggested_at, field="suggested_at")

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "kind": self.kind.value,
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
    reminders: tuple[ReminderSuggestion, ...] = ()

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
        if not isinstance(self.reminders, tuple):
            raise SupervisionValidationError(
                "reminders must be a tuple of ReminderSuggestion"
            )
        if any(not isinstance(r, ReminderSuggestion) for r in self.reminders):
            raise SupervisionValidationError(
                "reminders must be exact ReminderSuggestion"
            )
        reminder_item_ids = tuple(r.item_id for r in self.reminders)
        if len(set(reminder_item_ids)) != len(reminder_item_ids):
            raise SupervisionValidationError("reminder item_id must be unique")
        if reminder_item_ids != tuple(sorted(reminder_item_ids)):
            raise SupervisionValidationError(
                "reminders must use stable item_id order"
            )
        if set(reminder_item_ids) - set(item_ids):
            raise SupervisionValidationError(
                "reminders reference unknown supervision items"
            )
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
            "reminder_count": len(self.reminders),
            "meeting_proposal": (
                self.meeting_proposal.to_dict() if self.meeting_proposal is not None else None
            ),
            "conclusion_count": len(self.conclusions),
            "created_at": self.created_at,
            "requires_owner_confirmation": True,
            "formally_released": False,
        }

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
