"""supervision.service - SupervisionCoordinator facade and its private helpers."""

from __future__ import annotations

import datetime as dt
from src.coevo.risk import Risk, RiskKind, RiskReport

from .models import COORDINATION_RECOMMENDED_KINDS, EscalationLevel, EscalationSuggestion, MeetingAgendaItem, MeetingConclusionKind, MeetingConclusionProjection, MeetingProposal, REMINDER_WINDOW_SEC, ReminderKind, ReminderSuggestion, SUPERVISABLE_RISK_KINDS, SupervisionError, SupervisionItem, SupervisionOutcome, SupervisionValidationError, _parse_utc

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
        reminders: list[ReminderSuggestion] = []
        for item in items:
            reminder = _reminder_for(item, reference_time, now)
            if reminder is not None:
                reminders.append(reminder)
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
            reminders=tuple(reminders),
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
            "reminder_kinds": sorted({r.kind.value for r in outcome.reminders}),
            "meeting_proposal_id": (
                outcome.meeting_proposal.proposal_id
                if outcome.meeting_proposal is not None else None
            ),
            "conclusion_kinds": sorted({c.kind.value for c in outcome.conclusions}),
            "created_at": outcome.created_at,
            "requires_owner_confirmation": True,
            "formally_released": False,
        }

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

def _reminder_for(
    item: SupervisionItem,
    reference_time: dt.datetime,
    now: str,
) -> ReminderSuggestion | None:
    """AC-3: emit a REMIND/URGE suggestion for one supervision item.

    ``URGE`` fires once ``due_at`` has passed; ``REMIND`` fires when
    ``due_at`` is inside :data:`REMINDER_WINDOW_SEC`. Items whose due
    date is further out produce no reminder (``None``).
    """
    due = _parse_utc(item.due_at, field="due_at")
    delta = (due - reference_time).total_seconds()
    if delta < 0:
        return ReminderSuggestion(
            item_id=item.item_id,
            kind=ReminderKind.URGE,
            reason=(
                f"due_at {item.due_at} overdue for {item.risk_kind.value} "
                f"(US-12 AC-3 urge); affected tasks={list(item.affected_tasks)}"
            ),
            suggested_at=now,
        )
    if delta <= REMINDER_WINDOW_SEC:
        return ReminderSuggestion(
            item_id=item.item_id,
            kind=ReminderKind.REMIND,
            reason=(
                f"due_at {item.due_at} within {REMINDER_WINDOW_SEC // 3600}h "
                f"for {item.risk_kind.value} (US-12 AC-3 remind); "
                f"affected tasks={list(item.affected_tasks)}"
            ),
            suggested_at=now,
        )
    return None

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
