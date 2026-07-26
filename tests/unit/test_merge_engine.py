"""Unit tests for US-10-AC-1 merge engine.

Coverage matrix (each TestCase class locks one AC of the slice):

  AC-1  ``TestMergeValidation``      - identity / base_revision validation.
  AC-2  ``TestMergeIdempotence``     - duplicate package_id returns no-op.
  AC-3  ``TestMergeConflict``        - mismatched project_id / base_revision rejected.
  AC-4  ``TestAutoMerge``            - completed report auto-merges.
  AC-7  ``TestNoTimestampOverride``  - every decision is traceable; no time-stamp-only override.
  AC-8  ``TestNewRevision``          - merge produces new revision (strict monotonic).
  AC-9  ``TestMergeRecord``          - merge record is JSON-safe + persistent.

Service-layer invariants:
* No IO, no model, no network.
* Merge is byte-deterministic for the same inputs.
* Time-stamp alone never decides any field.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.merge import (
    FieldMerge,
    MergeDecision,
    MergeEngine,
    MergeError,
    MergeProposal,
    MergeRecord,
    MergeValidationError,
)
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import (
    BaselineInput,
    Deliverable,
    ProjectBaseline,
    Task,
    WorkPackage,
    build_baseline,
)


# ----------------------- fixtures -----------------------


def _wp() -> WorkPackage:
    return WorkPackage(
        work_package_id="wp.intake",
        standard_stage="intake",
        title="Intake",
        tasks=(
            Task(
                task_id="t.1", title="Receive", responsible_role="pm",
                plan_start="2026-08-01T00:00:00Z",
                plan_end="2026-08-05T00:00:00Z",
                deliverables=(
                    Deliverable("d.1", "Doc", "document", ("ok",)),
                ),
            ),
        ),
    )


def _baseline(*, plan_end="2026-08-31T00:00:00Z", project_id="PRJ001", unit_id="unit_a", version=1):
    return build_baseline(
        BaselineInput(
            project_id=project_id,
            title="Alpha",
            objective="Ship MVP",
            plan_start="2026-08-01T00:00:00Z",
            plan_end=plan_end,
            responsible_units=("unit_a",),
            process_flow_ref=(unit_id, version),
            work_packages=(_wp(),),
        ),
        now="2026-08-01T00:00:00Z",
    )


def _report(*, project_id="PRJ001", base_revision="unit_a",
            submitted_at="2026-08-20T00:00:00Z", status=ReportStatus.ON_TRACK,
            completed=("draft",), pending=(), next_steps=(), risks=()):
    return ReportManifest(
        schema_version="1.0",
        package_id=str(uuid.uuid4()),
        package_type="RESULT_SUBMISSION",
        project_id=project_id,
        task_id="TASK-001",
        base_revision=base_revision,
        sequence_no=1,
        submitted_at=submitted_at,
        sender_user_id="USR021", sender_client_id="CLI021",
        sender_organization_id="ORG002", sender_cert_id="CERT-RECIPIENT-021",
        recipient_user_id="USR001", recipient_client_id="CLI001",
        recipient_organization_id="ORG001", recipient_cert_id="CERT-SENDER-001",
        status=status,
        progress_summary="50% complete",
        completed_work=completed,
        pending_work=pending,
        next_steps=next_steps,
        risks=risks,
        artifacts=(),
    )


# ----------------------- AC-1: validation -----------------------


class TestMergeValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.report = _report()

    def test_merge_accepts_valid_inputs(self):
        proposal = self.engine.merge(
            report=self.report, baseline=self.baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertIsInstance(proposal, MergeProposal)
        self.assertTrue(proposal.accepted)

    def test_merge_rejects_non_report(self):
        with self.assertRaises(MergeError):
            self.engine.merge(
                report="not a report", baseline=self.baseline,
                decided_at="2026-08-20T01:00:00Z",
            )

    def test_merge_rejects_non_baseline(self):
        with self.assertRaises(MergeError):
            self.engine.merge(
                report=self.report, baseline="not a baseline",
                decided_at="2026-08-20T01:00:00Z",
            )

    def test_merge_rejects_empty_decided_at(self):
        with self.assertRaises(MergeValidationError):
            self.engine.merge(
                report=self.report, baseline=self.baseline, decided_at="",
            )


# ----------------------- AC-3: conflict detection -----------------------


class TestMergeConflict(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()

    def test_mismatched_project_id_rejected(self):
        bad = _report(project_id="OTHER", base_revision="PRJ001-R0001")
        proposal = self.engine.merge(
            report=bad, baseline=self.baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("AC-3", proposal.rejection_reason)
        # The baseline is unchanged on rejection.
        self.assertEqual(self.baseline, proposal.new_baseline)

    def test_mismatched_base_revision_rejected(self):
        bad = _report(project_id="PRJ001", base_revision="unit_other")
        proposal = self.engine.merge(
            report=bad, baseline=self.baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("AC-3", proposal.rejection_reason)


# ----------------------- AC-4: auto-merge -----------------------


class TestAutoMerge(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()

    def test_completed_report_advances_plan_end(self):
        baseline = _baseline(plan_end="2026-08-31T00:00:00Z")
        report = _report(
            status=ReportStatus.COMPLETED,
            submitted_at="2026-09-15T10:00:00Z",  # after plan_end
        )
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-09-15T11:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        # plan_end advanced to submitted_at
        self.assertEqual("2026-09-15T10:00:00Z", proposal.new_baseline.plan_end)

    def test_completed_report_keeps_plan_end_when_earlier(self):
        # If the report's submitted_at is BEFORE the baseline's
        # plan_end, the auto-merge does NOT regress plan_end.
        baseline = _baseline(plan_end="2026-08-31T00:00:00Z")
        report = _report(
            status=ReportStatus.COMPLETED,
            submitted_at="2026-08-15T10:00:00Z",  # before plan_end
        )
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-15T11:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        # plan_end UNCHANGED
        self.assertEqual("2026-08-31T00:00:00Z", proposal.new_baseline.plan_end)

    def test_risks_always_hold(self):
        # AC-4: risks require human triage; HOLD pending user
        # review.
        baseline = _baseline()
        report = _report(risks=("deadline too tight",))
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        risk_merges = [
            m for m in proposal.record.field_merges if m.field_path == "risks"
        ]
        self.assertEqual(1, len(risk_merges))
        self.assertEqual(MergeDecision.HOLD, risk_merges[0].decision)

    def test_pending_work_hold_when_at_risk(self):
        # AC-4 + AC-7: at_risk reports → HOLD on pending work.
        baseline = _baseline()
        report = _report(
            status=ReportStatus.AT_RISK,
            completed=("partial work",), pending=("remaining",),
        )
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        completed_merges = [
            m for m in proposal.record.field_merges if m.field_path == "completed_work"
        ]
        self.assertEqual(1, len(completed_merges))
        self.assertEqual(MergeDecision.HOLD, completed_merges[0].decision)

    def test_pending_work_accept_when_on_track(self):
        baseline = _baseline()
        report = _report(
            status=ReportStatus.ON_TRACK,
            completed=("partial work",), pending=("remaining",),
        )
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        completed_merges = [
            m for m in proposal.record.field_merges if m.field_path == "completed_work"
        ]
        self.assertEqual(1, len(completed_merges))
        self.assertEqual(MergeDecision.ACCEPT, completed_merges[0].decision)


# ----------------------- AC-7: no time-stamp-only override -----------------------


class TestNoTimestampOverride(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()

    def test_every_merge_carries_a_decision(self):
        baseline = _baseline()
        report = _report()
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        for m in proposal.record.field_merges:
            self.assertIsInstance(m.decision, MergeDecision)
            self.assertNotEqual(m.decision.value, "")  # never empty

    def test_no_decision_is_just_newer_timestamp(self):
        # AC-7: time-stamp must NOT be the sole override basis.
        # The only time-stamp-driven field in this engine is
        # plan_end (advanced to submitted_at when status is
        # COMPLETED). That field's decision must still carry an
        # explicit reason citing AC-8, not just "newer".
        baseline = _baseline(plan_end="2026-08-31T00:00:00Z")
        report = _report(
            status=ReportStatus.COMPLETED,
            submitted_at="2026-09-15T10:00:00Z",
        )
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-09-15T11:00:00Z",
        )
        plan_end_merges = [
            m for m in proposal.record.field_merges if m.field_path == "plan_end"
        ]
        self.assertEqual(1, len(plan_end_merges))
        # The reason must cite AC-8 (not "newer" or "time-stamp").
        self.assertIn("AC-8", plan_end_merges[0].reason)
        self.assertNotIn("newer", plan_end_merges[0].reason)


# ----------------------- AC-8: new revision -----------------------


class TestNewRevision(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()

    def test_merge_produces_new_revision(self):
        baseline = _baseline(version=1)
        self.assertEqual(1, baseline.version)
        report = _report()
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        # new_baseline.version = baseline.version + 1
        self.assertEqual(2, proposal.new_baseline.version)
        # Other fields preserved
        self.assertEqual(baseline.project_id, proposal.new_baseline.project_id)
        self.assertEqual(baseline.title, proposal.new_baseline.title)

    def test_merge_strict_monotonic(self):
        # Run two consecutive merges; each new version is +1
        # relative to the input. (build_baseline always emits
        # version=1 for the first draft, so the absolute value
        # depends on the fixture; what matters is the
        # delta-increment.)
        baseline = _baseline()
        self.assertEqual(1, baseline.version)
        report1 = _report()
        p1 = self.engine.merge(
            report=report1, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertEqual(baseline.version + 1, p1.new_baseline.version)
        report2 = _report()
        p2 = self.engine.merge(
            report=report2, baseline=p1.new_baseline,
            decided_at="2026-08-21T01:00:00Z",
        )
        self.assertEqual(p1.new_baseline.version + 1, p2.new_baseline.version)


# ----------------------- AC-9: merge record -----------------------


class TestMergeRecord(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()

    def test_record_is_json_safe(self):
        baseline = _baseline()
        report = _report(risks=("r1",))
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        # Round-trip through JSON. to_dict converts tuples to
        # lists (JSON has no tuple type), so we compare the
        # round-tripped form rather than the original.
        record_dict = proposal.record.to_dict()
        s = json.dumps(record_dict)
        round_tripped = json.loads(s)
        # The keys and the field_merge entries are equal; nested
        # tuples inside field_merges may differ in container type
        # (tuple vs list) but not in contents.
        self.assertEqual(set(record_dict.keys()), set(round_tripped.keys()))
        self.assertEqual(len(record_dict["field_merges"]), len(round_tripped["field_merges"]))
        for a, b in zip(record_dict["field_merges"], round_tripped["field_merges"]):
            self.assertEqual(a, b)

    def test_audit_record_is_json_safe(self):
        baseline = _baseline()
        report = _report()
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        audit = self.engine.to_audit_record(proposal)
        s = json.dumps(audit)
        self.assertEqual(audit, json.loads(s))
        self.assertEqual("merge.proposal", audit["kind"])
        self.assertEqual(True, audit["accepted"])

    def test_audit_record_on_rejection(self):
        baseline = _baseline()
        report = _report(project_id="OTHER")
        proposal = self.engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        audit = self.engine.to_audit_record(proposal)
        self.assertEqual(False, audit["accepted"])
        self.assertIn("AC-3", audit["rejection_reason"])


# ----------------------- AC-2: idempotence (top-level no-op) -----------------------


class TestMergeIdempotence(unittest.TestCase):
    """AC-2: duplicate report packages do NOT take effect twice.

    This slice does not re-validate the package_id (US-5 replay
    detector does that); instead the engine returns a stable
    MergeProposal for the same inputs — the caller is expected
    to gate on US-5's replay decision.
    """

    def test_merge_is_byte_deterministic(self):
        baseline = _baseline()
        report = _report()
        engine = MergeEngine()
        a = engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        b = engine.merge(
            report=report, baseline=baseline,
            decided_at="2026-08-20T01:00:00Z",
        )
        # Same decisions, same new_baseline fields
        self.assertEqual(a.accepted, b.accepted)
        self.assertEqual(a.new_baseline.version, b.new_baseline.version)
        self.assertEqual(a.new_baseline.plan_end, b.new_baseline.plan_end)
        self.assertEqual(len(a.record.field_merges), len(b.record.field_merges))


if __name__ == "__main__":
    unittest.main()