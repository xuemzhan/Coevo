"""MATURITY-O-06: supervision/meeting cockpit wiring tests.

Covers the ``SupervisionSummary`` snapshot model, the
``SupervisionSummary.from_outcome`` projection and the new
``SUPERVISION_VIEW`` cockpit route (view-only; confirmation stays on the
pending-action handler).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.cockpit import (  # noqa: E402
    CockpitFacade,
    CockpitRequest,
    CockpitResponseStatus,
    CockpitRoute,
    CockpitServerState,
    CockpitValidationError,
    SupervisionSummary,
    WorkspaceView,
)
from src.coevo.risk import Risk, RiskKind, RiskReport, SourceKind  # noqa: E402
from src.coevo.supervision import (  # noqa: E402
    EscalationLevel,
    ReminderKind,
    SupervisionCoordinator,
)


def _risk(
    *,
    risk_id: str = "risk.1",
    kind: RiskKind = RiskKind.SEVERE_COORDINATION_NEEDED,
    tasks: tuple[str, ...] = ("TASK-001",),
    due: str = "2026-08-20T00:00:00Z",
    severity: int = 5,
) -> Risk:
    return Risk(
        risk_id=risk_id,
        kind=kind,
        source=SourceKind.FACTUAL,
        basis="basis text",
        affected_tasks=tasks,
        recommendation="recommend",
        suggested_deadline=due,
        severity=severity,
        rationale="rationale",
    )


def _report(*, coordination: bool = True) -> RiskReport:
    return RiskReport(
        merge_reporter_package_id="pkg.retchain",
        project_id="PRJ001",
        analysed_at="2026-08-19T00:00:00Z",
        risks=(_risk(),),
        coordination_meeting_recommended=coordination,
    )


def _workspace() -> WorkspaceView:
    return WorkspaceView(
        project_id="PRJ001",
        display_name="Project One",
        roles=("a.pm",),
        task_count=1,
        milestone_count=0,
        artifact_count=0,
    )


class SupervisionSummaryModelTests(unittest.TestCase):
    def test_valid_summary_round_trips(self) -> None:
        summary = SupervisionSummary(
            project_id="PRJ001",
            item_id="sup.PRJ001.risk.1.00",
            risk_id="risk.1",
            risk_kind="severe_coordination_needed",
            responsible_subject="PRJ001",
            due_at="2026-08-20T00:00:00Z",
            escalation_level=EscalationLevel.EMERGENCY.value,
            reminder_kind=ReminderKind.URGE.value,
            meeting_proposal_id="meeting.PRJ001.pkg.retchain",
            requires_confirmation=True,
        )
        self.assertEqual("PRJ001", summary.project_id)
        self.assertEqual(
            EscalationLevel.EMERGENCY.value, summary.escalation_level
        )

    def test_rejects_bad_ids_times_and_closed_set_values(self) -> None:
        base = dict(
            project_id="PRJ001",
            item_id="sup.PRJ001.risk.1.00",
            risk_id="risk.1",
            risk_kind="severe_coordination_needed",
            responsible_subject="PRJ001",
            due_at="2026-08-20T00:00:00Z",
        )
        for mutation in (
            {"project_id": "PRJ/001"},
            {"item_id": "../sup"},
            {"due_at": "2026-08-20T00:00:00+00:00"},
            {"escalation_level": "urgent"},
            {"reminder_kind": "ping"},
            {"meeting_proposal_id": "meeting/PRJ001/x"},
            {"requires_confirmation": False},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaises(CockpitValidationError):
                    SupervisionSummary(**{**base, **mutation})

    def test_accepts_empty_optional_state(self) -> None:
        summary = SupervisionSummary(
            project_id="PRJ001",
            item_id="sup.PRJ001.risk.1.00",
            risk_id="risk.1",
            risk_kind="long_silence",
            responsible_subject="PRJ001",
            due_at="2026-08-22T00:00:00Z",
        )
        self.assertEqual("", summary.escalation_level)
        self.assertEqual("", summary.reminder_kind)
        self.assertEqual("", summary.meeting_proposal_id)


class SupervisionSummaryProjectionTests(unittest.TestCase):
    def test_from_outcome_projects_items_without_sensitive_text(self) -> None:
        outcome = SupervisionCoordinator().coordinate(
            risk_report=_report(),
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        summaries = SupervisionSummary.from_outcome(outcome)
        self.assertEqual(1, len(summaries))
        summary = summaries[0]
        self.assertEqual("sup.PRJ001.risk.1.00", summary.item_id)
        self.assertEqual(EscalationLevel.EMERGENCY.value, summary.escalation_level)
        self.assertEqual(ReminderKind.URGE.value, summary.reminder_kind)
        self.assertTrue(summary.meeting_proposal_id)
        joined = repr(summary).lower()
        for forbidden in ("basis", "recommendation", "rationale", "closing_condition"):
            self.assertNotIn(forbidden, joined, f"summary leaked {forbidden!r}")

    def test_from_outcome_rejects_non_outcome(self) -> None:
        with self.assertRaises(CockpitValidationError):
            SupervisionSummary.from_outcome(_report())


class SupervisionViewRouteTests(unittest.TestCase):
    def _state(self, summaries=()) -> CockpitServerState:
        return CockpitFacade.start_server(
            workspace_views=(_workspace(),),
            role_views=(),
            supervision_views=summaries,
            now="2026-08-21T00:00:00Z",
        )

    def test_supervision_view_returns_items_for_project(self) -> None:
        outcome = SupervisionCoordinator().coordinate(
            risk_report=_report(),
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        state = self._state(SupervisionSummary.from_outcome(outcome))
        response = CockpitFacade.dispatch(
            CockpitRequest(
                route=CockpitRoute.SUPERVISION_VIEW,
                project_id="PRJ001",
                role_id="",
                task_id="",
                artifact_path="",
                ts="2026-08-21T00:00:00Z",
            ),
            server_state=state,
            now="2026-08-21T00:00:00Z",
        )
        self.assertEqual(CockpitResponseStatus.OK, response.status)
        self.assertEqual(1, response.payload["count"])
        self.assertEqual(
            "sup.PRJ001.risk.1.00",
            response.payload["items"][0]["item_id"],
        )
        joined = repr(response.payload).lower()
        for forbidden in ("basis", "recommendation", "rationale", "closing_condition"):
            self.assertNotIn(forbidden, joined, f"payload leaked {forbidden!r}")

    def test_supervision_view_requires_project_id(self) -> None:
        response = CockpitFacade.dispatch(
            CockpitRequest(
                route=CockpitRoute.SUPERVISION_VIEW,
                project_id="",
                role_id="",
                task_id="",
                artifact_path="",
                ts="2026-08-21T00:00:00Z",
            ),
            server_state=self._state(),
            now="2026-08-21T00:00:00Z",
        )
        self.assertEqual(CockpitResponseStatus.BAD_REQUEST, response.status)

    def test_supervision_view_unknown_project_is_not_found(self) -> None:
        response = CockpitFacade.dispatch(
            CockpitRequest(
                route=CockpitRoute.SUPERVISION_VIEW,
                project_id="PRJ999",
                role_id="",
                task_id="",
                artifact_path="",
                ts="2026-08-21T00:00:00Z",
            ),
            server_state=self._state(),
            now="2026-08-21T00:00:00Z",
        )
        self.assertEqual(CockpitResponseStatus.NOT_FOUND, response.status)

    def test_audit_record_excludes_sensitive_text(self) -> None:
        outcome = SupervisionCoordinator().coordinate(
            risk_report=_report(),
            project_recipient_cert_id="CERT-OWNER",
            now="2026-08-21T00:00:00Z",
        )
        state = self._state(SupervisionSummary.from_outcome(outcome))
        request = CockpitRequest(
            route=CockpitRoute.SUPERVISION_VIEW,
            project_id="PRJ001",
            role_id="",
            task_id="",
            artifact_path="",
            ts="2026-08-21T00:00:00Z",
        )
        response = CockpitFacade.dispatch(
            request, server_state=state, now="2026-08-21T00:00:00Z"
        )
        record = CockpitFacade.to_audit_record(request, response)
        self.assertEqual("supervision_view", record["route"])
        joined = repr(record).lower()
        for forbidden in ("basis", "recommendation", "rationale", "closing_condition"):
            self.assertNotIn(forbidden, joined, f"audit leaked {forbidden!r}")


if __name__ == "__main__":
    unittest.main()
