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
  (``basis`` / ``recommendation``) per project policy."""

from __future__ import annotations

import datetime as dt
import enum
from dataclasses import dataclass
from typing import Iterable
from src.coevo.risk import Risk, RiskKind, RiskReport, RiskValidationError, SourceKind

from .models import (COORDINATION_RECOMMENDED_KINDS, EscalationLevel, EscalationSuggestion, MEETING_DOMAIN, MEETING_SCHEMA, MeetingAgendaItem, MeetingConclusionKind, MeetingConclusionProjection, MeetingProposal, REMINDER_WINDOW_SEC, ReminderKind, ReminderSuggestion, SUPERVISABLE_RISK_KINDS, SUPERVISION_DOMAIN, SUPERVISION_SCHEMA, SupervisionError, SupervisionItem, SupervisionOutcome, SupervisionValidationError, _non_empty, _parse_utc)

from .service import (SupervisionCoordinator, _agenda_title_for, _closing_condition_for, _conclusions_for, _escalation_level_for, _escalation_reason_for, _meeting_proposal_for, _reminder_for, _supervision_item_id)

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
    "REMINDER_WINDOW_SEC",
    "ReminderKind",
    "ReminderSuggestion",
    "SUPERVISABLE_RISK_KINDS",
    "SUPERVISION_DOMAIN",
    "SUPERVISION_SCHEMA",
    "SupervisionCoordinator",
    "SupervisionError",
    "SupervisionItem",
    "SupervisionOutcome",
    "SupervisionValidationError",
]
