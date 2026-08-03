"""Unit tests for US-12 supervision + meeting coordination service facade."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.coevo.risk import Risk, RiskKind, RiskReport, SourceKind
from src.coevo.supervision import (
    COORDINATION_RECOMMENDED_KINDS,
    EscalationLevel,
    EscalationSuggestion,
    MEETING_DOMAIN,
    MEETING_SCHEMA,
    MeetingAgendaItem,
    MeetingConclusionKind,
    MeetingConclusionProjection,
    MeetingProposal,
    ReminderKind,
    ReminderSuggestion,
    SUPERVISABLE_RISK_KINDS,
    SUPERVISION_DOMAIN,
    SUPERVISION_SCHEMA,
    SupervisionCoordinator,
    SupervisionError,
    SupervisionItem,
    SupervisionOutcome,
    SupervisionValidationError,
)


def _risk(
    *,
    risk_id: str = "risk.1",
    kind: RiskKind = RiskKind.LONG_SILENCE,
    tasks: tuple[str, ...] = ("TASK-001",),
    due: str = "2026-08-22T00:00:00Z",
    severity: int = 3,
) -> Risk:
    return Risk(
        risk_id=risk_id, kind=kind, source=SourceKind.FACTUAL,
        basis="basis text", affected_tasks=tasks,
        recommendation="recommend", suggested_deadline=due,
        severity=severity, rationale="rationale",
    )


def _report(
    *,
    risks: tuple[Risk, ...] = (_risk(),),
    project_id: str = "PRJ001",
    package_id: str = "pkg-1",
    coordination: bool = False,
) -> RiskReport:
    return RiskReport(
        merge_reporter_package_id=package_id,
        project_id=project_id,
        analysed_at="2026-08-15T00:00:00Z",
        risks=risks,
        coordination_meeting_recommended=coordination,
    )


class SupervisionModelTests(unittest.TestCase):
    def test_supervision_item_validates_field_shape_and_sorted_tasks(self):
        item = SupervisionItem(
            item_id="sup.PRJ001.risk.1.00",
            project_id="PRJ001", risk_id="risk.1",
            risk_kind=RiskKind.LONG_SILENCE,
            responsible_subject="PRJ001",
            due_at="2026-08-22T00:00:00Z",
            closing_condition="closure",
            affected_tasks=("TASK-001", "TASK-002"),
            created_at="2026-08-21T00:00:00Z",
        )
        self.assertEqual(("TASK-001", "TASK-002"), item.affected_tasks)
        for bad_factory in (
            lambda: SupervisionItem(
                item_id="", project_id="PRJ001", risk_id="risk.1",
                risk_kind=RiskKind.LONG_SILENCE, responsible_subject="x",
                due_at="2026-08-22T00:00:00Z", closing_condition="c",
                affected_tasks=("TASK-001",), created_at="2026-08-21T00:00:00Z",
            ),
            lambda: SupervisionItem(
                item_id="sup.PRJ001.risk.1.00", project_id="PRJ001",
                risk_id="risk.1", risk_kind="LONG_SILENCE",
                responsible_subject="x", due_at="2026-08-22T00:00:00Z",
                closing_condition="c", affected_tasks=("TASK-001",),
                created_at="2026-08-21T00:00:00Z",
            ),
            lambda: SupervisionItem(
                item_id="sup.PRJ001.risk.1.00", project_id="PRJ001",
                risk_id="risk.1", risk_kind=RiskKind.LONG_SILENCE,
                responsible_subject="x", due_at="2026-08-22T00:00:00+00:00",
                closing_condition="c", affected_tasks=("TASK-001",),
                created_at="2026-08-21T00:00:00Z",
            ),
            lambda: SupervisionItem(
                item_id="sup.PRJ001.risk.1.00", project_id="PRJ001",
                risk_id="risk.1", risk_kind=RiskKind.LONG_SILENCE,
                responsible_subject="x", due_at="2026-08-22T00:00:00Z",
                closing_condition="c", affected_tasks=("TASK-001", "TASK-001"),
                created_at="2026-08-21T00:00:00Z",
            ),
        ):
            with self.subTest(bad_factory=bad_factory):
                with self.assertRaises(SupervisionValidationError):
                    bad_factory()  # __post_init__ runs on construct

    def test_meeting_proposal_rejects_subclass_and_bypass_flags(self):
        proposal = MeetingProposal(
            proposal_id="meeting.PRJ001.pkg-1",
            project_id="PRJ001",
            proposed_for_recipient_cert_id="CERT-OWNER",
            agenda=(MeetingAgendaItem(
                agenda_id="agenda.PRJ001.00",
                title="t", background="b",
                open_questions=("q1", "q2"),
            ),),
            created_at="2026-08-21T00:00:00Z",
            risk_ids=("risk.1",),
            coordination_meeting_recommended=True,
        )
        self.assertTrue(proposal.requires_owner_confirmation)
        self.assertFalse(proposal.formally_released)
        with self.assertRaises(SupervisionValidationError):
            MeetingProposal(
                proposal_id="meeting.PRJ001.pkg-1", project_id="PRJ001",
                proposed_for_recipient_cert_id="CERT-OWNER",
                agenda=(MeetingAgendaItem(
                    agenda_id="agenda.PRJ001.00", title="t",
                    background="b", open_questions=("q1",),
                ),),
                created_at="2026-08-21T00:00:00Z", risk_ids=("risk.1",),
                coordination_meeting_recommended=True,
                requires_owner_confirmation=False,
            )
        with self.assertRaises(SupervisionValidationError):
            MeetingProposal(
                proposal_id="meeting.PRJ001.pkg-1", project_id="PRJ001",
                proposed_for_recipient_cert_id="CERT-OWNER",
                agenda=(MeetingAgendaItem(
                    agenda_id="agenda.PRJ001.00", title="t",
                    background="b", open_questions=("q1",),
                ),),
                created_at="2026-08-21T00:00:00Z", risk_ids=("risk.1",),
                coordination_meeting_recommended=True,
                formally_released=True,
            )

    def test_outcome_rejects_unknown_escalation_and_new_supervision_synthesis(self):
        with self.assertRaises(SupervisionValidationError):
            SupervisionOutcome(
                project_id="PRJ001", items=(), escalations=(
                    EscalationSuggestion(
                        item_id="ghost", level=EscalationLevel.WATCH,
                        reason="r", suggested_at="2026-08-21T00:00:00Z",
                    ),
                ),
                meeting_proposal=None, conclusions=(),
                created_at="2026-08-21T00:00:00Z",
            )
        with self.assertRaises(SupervisionValidationError):
            SupervisionOutcome(
                project_id="PRJ001", items=(), escalations=(),
                meeting_proposal=None,
                conclusions=(MeetingConclusionProjection(
                    kind=MeetingConclusionKind.NEW_SUPERVISION_ITEM,
                    subject_ref="x", note="n",
                ),),
                created_at="2026-08-21T00:00:00Z",
            )

    def test_reminder_suggestion_validates_shape(self):
        suggestion = ReminderSuggestion(
            item_id="sup.PRJ001.risk.1.00",
            kind=ReminderKind.REMIND,
            reason="due soon",
            suggested_at="2026-08-21T00:00:00Z",
        )
        self.assertEqual("remind", suggestion.kind.value)
        self.assertEqual(
            {
                "item_id": "sup.PRJ001.risk.1.00",
                "kind": "remind",
                "reason": "due soon",
                "suggested_at": "2026-08-21T00:00:00Z",
            },
            suggestion.to_dict(),
        )
        for bad_factory in (
            lambda: ReminderSuggestion(
                item_id="", kind=ReminderKind.REMIND, reason="r",
                suggested_at="2026-08-21T00:00:00Z",
            ),
            lambda: ReminderSuggestion(
                item_id="sup.PRJ001.risk.1.00", kind="remind", reason="r",
                suggested_at="2026-08-21T00:00:00Z",
            ),
            lambda: ReminderSuggestion(
                item_id="sup.PRJ001.risk.1.00", kind=ReminderKind.URGE,
                reason="", suggested_at="2026-08-21T00:00:00Z",
            ),
            lambda: ReminderSuggestion(
                item_id="sup.PRJ001.risk.1.00", kind=ReminderKind.URGE,
                reason="r", suggested_at="2026-08-21T00:00:00+00:00",
            ),
        ):
            with self.subTest(bad_factory=bad_factory):
                with self.assertRaises(SupervisionValidationError):
                    bad_factory()

    def test_outcome_rejects_unknown_or_duplicate_reminders(self):
        item = SupervisionItem(
            item_id="sup.PRJ001.risk.1.00", project_id="PRJ001",
            risk_id="risk.1", risk_kind=RiskKind.LONG_SILENCE,
            responsible_subject="x", due_at="2026-08-22T00:00:00Z",
            closing_condition="c", affected_tasks=("TASK-001",),
            created_at="2026-08-21T00:00:00Z",
        )
        reminder = ReminderSuggestion(
            item_id=item.item_id, kind=ReminderKind.REMIND,
            reason="r", suggested_at="2026-08-21T00:00:00Z",
        )
        ok = SupervisionOutcome(
            project_id="PRJ001", items=(item,), escalations=(),
            meeting_proposal=None, conclusions=(),
            created_at="2026-08-21T00:00:00Z",
            reminders=(reminder,),
        )
        self.assertEqual(1, ok.to_dict()["reminder_count"])
        with self.assertRaises(SupervisionValidationError):
            SupervisionOutcome(
                project_id="PRJ001", items=(item,), escalations=(),
                meeting_proposal=None, conclusions=(),
                created_at="2026-08-21T00:00:00Z",
                reminders=(ReminderSuggestion(
                    item_id="ghost", kind=ReminderKind.URGE, reason="r",
                    suggested_at="2026-08-21T00:00:00Z",
                ),),
            )
        with self.assertRaises(SupervisionValidationError):
            SupervisionOutcome(
                project_id="PRJ001", items=(item,), escalations=(),
                meeting_proposal=None, conclusions=(),
                created_at="2026-08-21T00:00:00Z",
                reminders=(reminder, reminder),
            )


class SupervisionCoordinatorTests(unittest.TestCase):
    def test_constructs_one_supervision_item_per_risk_with_stable_id(self):
        risks = (
            _risk(risk_id="risk.a", kind=RiskKind.LONG_SILENCE, tasks=("TASK-001",)),
            _risk(risk_id="risk.b", kind=RiskKind.LONG_SILENCE, tasks=("TASK-002",)),
        )
        report = _report(risks=risks)
        outcome = SupervisionCoordinator().coordinate(
            risk_report=report,
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        self.assertEqual(2, len(outcome.items))
        ids = tuple(item.item_id for item in outcome.items)
        self.assertEqual(tuple(sorted(ids)), ids)
        self.assertEqual(("sup.PRJ001.risk.a.00", "sup.PRJ001.risk.b.01"), ids)

    def test_escalation_levels_cover_overdue_emergency_watch_and_none(self):
        risks = (
            _risk(risk_id="risk.coord_overdue",
                  kind=RiskKind.SEVERE_COORDINATION_NEEDED,
                  due="2026-08-20T00:00:00Z", severity=5),
            _risk(risk_id="risk.deadline_overdue",
                  kind=RiskKind.DEADLINE_OVERRUN, due="2026-08-19T00:00:00Z",
                  severity=4),
            _risk(risk_id="risk.deadline_watch",
                  kind=RiskKind.DEADLINE_OVERRUN, due="2026-08-22T00:00:00Z",
                  severity=4),
            _risk(risk_id="risk.future", kind=RiskKind.LONG_SILENCE,
                  due="2026-08-25T00:00:00Z"),
            _risk(risk_id="risk.od", kind=RiskKind.LONG_SILENCE,
                  due="2026-08-20T00:00:00Z"),
        )
        report = _report(risks=risks)
        outcome = SupervisionCoordinator().coordinate(
            risk_report=report,
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        by_id = {e.item_id: e.level for e in outcome.escalations}
        self.assertEqual(EscalationLevel.EMERGENCY,
                         by_id["sup.PRJ001.risk.coord_overdue.00"])
        self.assertEqual(EscalationLevel.ESCALATE_TO_OWNER,
                         by_id["sup.PRJ001.risk.deadline_overdue.01"])
        self.assertEqual(EscalationLevel.WATCH,
                         by_id["sup.PRJ001.risk.deadline_watch.02"])
        self.assertNotIn("sup.PRJ001.risk.future.03", by_id)
        self.assertEqual(EscalationLevel.WATCH,
                         by_id["sup.PRJ001.risk.od.04"])

    def test_meeting_proposal_emitted_only_when_coordination_recommended(self):
        report_no = _report(coordination=False)
        outcome_no = SupervisionCoordinator().coordinate(
            risk_report=report_no,
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        self.assertIsNone(outcome_no.meeting_proposal)
        self.assertEqual((), outcome_no.conclusions)

        report_yes = _report(
            coordination=True,
            risks=(
                _risk(risk_id="risk.1", kind=RiskKind.BLOCKED_BLOOM, severity=5),
                _risk(risk_id="risk.2", kind=RiskKind.LONG_SILENCE),
            ),
        )
        outcome_yes = SupervisionCoordinator().coordinate(
            risk_report=report_yes,
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        meeting = outcome_yes.meeting_proposal
        self.assertIsNotNone(meeting)
        assert meeting is not None
        self.assertEqual("CERT-OWNER", meeting.proposed_for_recipient_cert_id)
        self.assertEqual(("risk.1",), meeting.risk_ids)
        self.assertEqual(1, len(meeting.agenda))
        agenda = meeting.agenda[0]
        self.assertEqual("agenda.PRJ001.00", agenda.agenda_id)
        self.assertEqual(MEETING_DOMAIN, MEETING_DOMAIN)
        kinds = tuple(c.kind for c in outcome_yes.conclusions)
        self.assertIn(MeetingConclusionKind.RISK_DISPOSITION, kinds)
        self.assertIn(MeetingConclusionKind.NEW_TASK, kinds)

    def test_coordinator_validates_inputs(self):
        with self.assertRaises(SupervisionValidationError):
            SupervisionCoordinator().coordinate(
                risk_report=None,  # type: ignore[arg-type]
                project_recipient_cert_id="CERT-OWNER",
                now="2026-08-21T00:00:00Z",
            )
        with self.assertRaises(SupervisionValidationError):
            SupervisionCoordinator().coordinate(
                risk_report=_report(),
                project_recipient_cert_id="",
                now="2026-08-21T00:00:00Z",
            )
        with self.assertRaises(SupervisionValidationError):
            SupervisionCoordinator().coordinate(
                risk_report=_report(),
                project_recipient_cert_id="CERT-OWNER",
                now="2026-08-21 00:00:00",
            )

    def test_audit_record_excludes_sensitive_business_phrasing(self):
        outcome = SupervisionCoordinator().coordinate(
            risk_report=_report(
                risks=(_risk(risk_id="risk.1", kind=RiskKind.LONG_SILENCE),),
                coordination=True,
            ),
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        record = SupervisionCoordinator().to_audit_record(outcome)
        self.assertEqual("supervision.coordination", record["kind"])
        self.assertEqual(SUPERVISION_SCHEMA, record["schema_version"])
        self.assertEqual("PRJ001", record["project_id"])
        # sensitive phrasing must not appear
        joined = repr(record).lower()
        for forbidden in ("basis", "recommendation", "rationale", "closing_condition"):
            self.assertNotIn(forbidden, joined,
                             f"audit_record leaked {forbidden!r}")
        self.assertTrue(record["requires_owner_confirmation"])
        self.assertFalse(record["formally_released"])

    def test_to_audit_record_rejects_non_outcome(self):
        with self.assertRaises(SupervisionError):
            SupervisionCoordinator().to_audit_record(_report())

    def test_reminders_cover_remind_urge_and_none(self):
        risks = (
            _risk(risk_id="risk.far", kind=RiskKind.LONG_SILENCE,
                  due="2026-08-30T00:00:00Z"),
            _risk(risk_id="risk.overdue", kind=RiskKind.LONG_SILENCE,
                  due="2026-08-20T00:00:00Z"),
            _risk(risk_id="risk.soon", kind=RiskKind.LONG_SILENCE,
                  due="2026-08-21T12:00:00Z"),
        )
        report = _report(risks=risks)
        outcome = SupervisionCoordinator().coordinate(
            risk_report=report,
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        by_id = {r.item_id: r.kind for r in outcome.reminders}
        self.assertEqual(
            ReminderKind.URGE, by_id["sup.PRJ001.risk.overdue.01"]
        )
        self.assertEqual(
            ReminderKind.REMIND, by_id["sup.PRJ001.risk.soon.02"]
        )
        self.assertNotIn("sup.PRJ001.risk.far.00", by_id)
        self.assertEqual(2, len(outcome.reminders))

    def test_audit_record_includes_reminder_kinds(self):
        outcome = SupervisionCoordinator().coordinate(
            risk_report=_report(
                risks=(
                    _risk(risk_id="risk.overdue", kind=RiskKind.LONG_SILENCE,
                          due="2026-08-20T00:00:00Z"),
                    _risk(risk_id="risk.soon", kind=RiskKind.LONG_SILENCE,
                          due="2026-08-21T12:00:00Z"),
                ),
            ),
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        record = SupervisionCoordinator().to_audit_record(outcome)
        self.assertEqual(["remind", "urge"], record["reminder_kinds"])


class SupervisionDomainConstantsTests(unittest.TestCase):
    def test_supervisable_and_coordination_kinds_match_risk_enum(self):
        for kind in RiskKind:
            self.assertIn(kind, SUPERVISABLE_RISK_KINDS)
        self.assertTrue(COORDINATION_RECOMMENDED_KINDS.issubset(SUPERVISABLE_RISK_KINDS))
        self.assertEqual("coevo.supervision", SUPERVISION_DOMAIN)
        self.assertEqual("1.0", SUPERVISION_SCHEMA)
        self.assertEqual("coevo.meeting.coordination", MEETING_DOMAIN)
        self.assertEqual("1.0", MEETING_SCHEMA)


if __name__ == "__main__":
    unittest.main()
