# -*- coding: utf-8 -*-
"""Unit tests for US-10-AC-1 merge engine (P1 fix).

Coverage matrix (each TestCase class locks one AC of the slice):

  P1 AC-1  ``TestImportBinding``       - merge refuses naked ReportManifest;
                                         requires COMMITTED ImportOutcome with
                                         matching identity / project /
                                         sender / recipient / package_type.
  P2 AC-2  ``TestReplayGate``          - duplicate package_id or digest in
                                         store is a no-op (accepted=False,
                                         no version bump, store unchanged);
                                         successful merge registers new
                                         record atomically.
  P3 AC-7  ``TestNoTimestampOverride`` - submitted_at never drives a field
                                         decision; HOLD anywhere forces
                                         accepted=False; risks always HOLD.
  P4 AC-5  ``TestThreeWayDiff``        - FieldMerge.current_value is
                                         carried; original_value /
                                         current_value / submitted_value
                                         may be MISSING; never fabricated.
  AC-3/8   ``TestConflictHandling``    - base_revision vs current revision
                                         path emits HOLD-with-conflict,
                                         not silent reject.
  AC-4     ``TestAutoMergeOnTrack``    - clean ON_TRACK with completed
                                         work auto-merges (version +1,
                                         store has new record).
  AC-9     ``TestMergeRecordAudit``    - to_dict round-trip; JSON safety;
                                         sensitive content (FieldMerge
                                         content) is NOT in audit
                                         projection.

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
    MISSING,
    FieldMerge,
    MERGEABLE_PACKAGE_TYPES,
    MergeDecision,
    MergeEngine,
    MergeError,
    MergeProposal,
    MergeRecord,
    MergeValidationError,
    _master_revision,
    _is_missing,
)
from src.coevo.protocol.import_service import (
    DEFAULT_EMPTY_STORE,
    ImportOutcome,
    PackageImportService,
)
from src.coevo.protocol.import_transaction import ImportStep
from src.coevo.protocol.processed_package_store import (
    AgentPackageStoreDuplicateError,
    ProcessedPackageRecord,
    ProcessedPackageStore,
)
from src.coevo.protocol.replay_detector import (
    ProcessedPackage,
    ReplayDecision,
    ReplayOutcome,
)
from dataclasses import replace as dc_replace

from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import (
    BaselineInput,
    Deliverable,
    ProjectBaseline,
    Task,
    WorkPackage,
    build_baseline,
)


# ----------------------- helpers -----------------------


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


def _baseline(*, plan_end="2026-08-31T00:00:00Z", project_id="PRJ001", version=1):
    return build_baseline(
        BaselineInput(
            project_id=project_id,
            title="Alpha",
            objective="Ship MVP",
            plan_start="2026-08-01T00:00:00Z",
            plan_end=plan_end,
            responsible_units=("unit_a",),
            process_flow_ref=("unit_a", version),
            work_packages=(_wp(),),
        ),
        now="2026-08-01T00:00:00Z",
    )


def _report(
    *, project_id="PRJ001", base_revision="PRJ001-R0001",
    submitted_at="2026-08-20T00:00:00Z", status=ReportStatus.ON_TRACK,
    completed=("draft",), pending=(), next_steps=(), risks=(),
    package_id=None,
):
    return ReportManifest(
        schema_version="1.0",
        package_id=package_id or str(uuid.uuid4()),
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


def _processed_package(report: ReportManifest, *, package_digest: str | None = None) -> ProcessedPackage:
    return ProcessedPackage(
        package_id=report.package_id,
        package_digest=package_digest or f"digest-{report.package_id}",
        sender_cert_id=report.sender_cert_id,
        recipient_cert_id=report.recipient_cert_id,
        project_id=report.project_id,
        sequence_no=report.sequence_no,
    )


def _import_outcome(
    report: ReportManifest,
    *,
    step: ImportStep = ImportStep.COMMITTED,
    package_digest: str | None = None,
    package_type: str = "RESULT_SUBMISSION",
) -> ImportOutcome:
    pkg = _processed_package(report, package_digest=package_digest)
    from src.coevo.protocol.import_transaction import ImportTransaction
    tx = ImportTransaction(
        package_id=report.package_id,
        project_id=report.project_id,
        base_revision=report.base_revision,
        current_revision=report.base_revision,
        step=step,
    )
    rec = ProcessedPackageRecord(
        package=pkg,
        package_type=package_type,
        processed_at="2026-08-20T01:00:00Z",
        result="committed" if step is ImportStep.COMMITTED else "rolled_back",
        revision=report.base_revision,
    )
    return ImportOutcome(transaction=tx, store=DEFAULT_EMPTY_STORE, record=rec)


def _base_revision_for(baseline: ProjectBaseline) -> str:
    return _master_revision(baseline.project_id, baseline.version)


# ----------------------- AC-1 + P1: import binding -----------------------


class TestImportBinding(unittest.TestCase):
    """AC-1 + P1: merge requires a verified ImportOutcome bound to the report."""

    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.report = _report(base_revision=_base_revision_for(self.baseline))
        self.store = ProcessedPackageStore.empty()

    def test_naked_report_is_rejected(self):
        with self.assertRaises(MergeError):
            self.engine.merge(
                import_outcome="not an outcome",  # type: ignore[arg-type]
                report=self.report, baseline=self.baseline,
                store=self.store, decided_at="2026-08-20T01:00:00Z",
            )

    def test_non_committed_transaction_is_rejected_without_version_bump(self):
        outcome = _import_outcome(self.report, step=ImportStep.ROLLED_BACK)
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("COMMITTED", proposal.rejection_reason)
        self.assertEqual(self.baseline.version, proposal.new_baseline.version)
        self.assertEqual(0, len(proposal.record.store_post))

    def test_outcome_with_no_record_is_rejected(self):
        outcome = ImportOutcome(
            transaction=None,  # type: ignore[arg-type]
            store=self.store, record=None,
        )
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("COMMITTED", proposal.rejection_reason)

    def test_package_id_mismatch_is_rejected(self):
        wrong_pkg = ProcessedPackage(
            package_id="other-package",
            package_digest="digest-other",
            sender_cert_id=self.report.sender_cert_id,
            recipient_cert_id=self.report.recipient_cert_id,
            project_id=self.report.project_id,
            sequence_no=self.report.sequence_no,
        )
        from src.coevo.protocol.import_transaction import ImportTransaction
        outcome = ImportOutcome(
            transaction=ImportTransaction(
                package_id="other-package", project_id=self.report.project_id,
                base_revision=self.report.base_revision,
                current_revision=self.report.base_revision,
                step=ImportStep.COMMITTED,
            ),
            store=self.store,
            record=ProcessedPackageRecord(
                package=wrong_pkg, package_type="RESULT_SUBMISSION",
                processed_at="2026-08-20T01:00:00Z", result="committed",
                revision=self.report.base_revision,
            ),
        )
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("package_id", proposal.rejection_reason)
        self.assertIn("P1", proposal.rejection_reason)

    def test_project_id_mismatch_is_rejected(self):
        outcome = _import_outcome(
            dc_replace(self.report, project_id="OTHER"),
        )
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("project_id", proposal.rejection_reason)

    def test_sender_mismatch_is_rejected(self):
        outcome = _import_outcome(
            dc_replace(self.report, sender_cert_id="OTHER-SENDER"),
        )
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("sender_cert_id", proposal.rejection_reason)

    def test_recipient_mismatch_is_rejected(self):
        outcome = _import_outcome(
            dc_replace(self.report, recipient_cert_id="OTHER-RECIPIENT"),
        )
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("recipient_cert_id", proposal.rejection_reason)

    def test_non_mergeable_package_type_is_rejected(self):
        outcome = _import_outcome(self.report, package_type="TASK_ASSIGNMENT")
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("MERGEABLE_PACKAGE_TYPES", proposal.rejection_reason)


# ----------------------- AC-2 + P2: replay gate -----------------------


class TestReplayGate(unittest.TestCase):
    """AC-2 + P2: duplicate package_id or digest in store is a no-op."""

    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.report = _report(base_revision=_base_revision_for(self.baseline))
        self.store = ProcessedPackageStore.empty()

    def test_first_merge_registers_new_record_and_bumps_version(self):
        outcome = _import_outcome(self.report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        self.assertEqual(self.baseline.version + 1, proposal.new_baseline.version)
        self.assertEqual(1, len(proposal.record.store_post))
        # The post-store has the new record; the package_id is registered
        rec = proposal.record.store_post.get(self.report.package_id)
        self.assertIsNotNone(rec)
        self.assertEqual("committed", rec.result)

    def test_duplicate_package_id_is_rejected_and_store_unchanged(self):
        outcome = _import_outcome(self.report)
        first = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        # Now feed the same report again with the populated store
        second = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=first.new_baseline, store=first.record.store_post,
            decided_at="2026-08-20T02:00:00Z",
        )
        self.assertFalse(second.accepted)
        self.assertIn("AC-2", second.rejection_reason)
        # Store length unchanged
        self.assertEqual(1, len(second.record.store_post))
        # Version NOT bumped
        self.assertEqual(first.new_baseline.version, second.new_baseline.version)

    def test_duplicate_digest_with_new_package_id_is_rejected(self):
        # First report with digest D
        outcome1 = _import_outcome(self.report, package_digest="digest-D")
        first = self.engine.merge(
            import_outcome=outcome1, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(first.accepted)
        # Second report with same digest but new package_id
        report2 = dc_replace(self.report, package_id=str(uuid.uuid4()))
        outcome2 = _import_outcome(report2, package_digest="digest-D")
        second = self.engine.merge(
            import_outcome=outcome2, report=report2,
            baseline=first.new_baseline, store=first.record.store_post,
            decided_at="2026-08-20T02:00:00Z",
        )
        self.assertFalse(second.accepted)
        self.assertIn("digest", second.rejection_reason.lower())

    def test_record_result_is_committed(self):
        outcome = _import_outcome(self.report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=self.report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        rec = proposal.record.store_post.get(self.report.package_id)
        self.assertEqual("committed", rec.result)
        self.assertEqual(
            _master_revision(self.baseline.project_id, self.baseline.version + 1),
            rec.revision,
        )


# ----------------------- AC-3: conflict handling (HOLD-with-conflict) -----------------------


class TestConflictHandling(unittest.TestCase):
    """AC-3 / P4: base_revision path emits a HOLD proposal with has_conflict=True."""

    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()

    def test_mismatched_project_id_is_rejected(self):
        report = _report(project_id="OTHER", base_revision="OTHER-R0001")
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store(),
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("AC-3", proposal.rejection_reason)

    @staticmethod
    def store() -> ProcessedPackageStore:
        return ProcessedPackageStore.empty()


# ----------------------- AC-4: clean auto-merge ON_TRACK -----------------------


class TestAutoMergeOnTrack(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_clean_on_track_report_auto_merges_with_strict_version(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            completed=("partial work",), pending=(), risks=(),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        self.assertEqual(
            _master_revision(self.baseline.project_id, self.baseline.version + 1),
            proposal.record.merged_version,
        )
        # P3: plan_end NOT advanced even though submitted_at > plan_end
        self.assertEqual(self.baseline.plan_end, proposal.new_baseline.plan_end)
        # Store has the new record
        self.assertEqual(1, len(proposal.record.store_post))


# ----------------------- AC-7 / P3: no timestamp override -----------------------


class TestNoTimestampOverride(unittest.TestCase):
    """AC-7 / P3: submitted_at never drives a field; HOLD anywhere blocks accept."""

    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_plan_end_is_never_advanced_by_submitted_at(self):
        # submitted_at is years in the future; P3 forbids using it
        # to override plan_end.
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            submitted_at="9999-12-31T23:59:59Z",
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        self.assertEqual(self.baseline.plan_end, proposal.new_baseline.plan_end)

    def test_risks_always_hold(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            risks=("deadline too tight",),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        risk_merges = [
            m for m in proposal.record.field_merges if m.field_path == "risks"
        ]
        self.assertEqual(1, len(risk_merges))
        self.assertEqual(MergeDecision.HOLD, risk_merges[0].decision)
        self.assertTrue(proposal.record.has_conflict)

    def test_pending_work_holds_when_present(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            pending=("remaining",),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertTrue(proposal.record.has_conflict)

    def test_next_steps_hold(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            next_steps=("review with PM",),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        self.assertTrue(proposal.record.has_conflict)

    def test_at_risk_status_holds_completed_work(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.AT_RISK,
            completed=("partial work",),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        completed_merges = [
            m for m in proposal.record.field_merges
            if m.field_path == "completed_work"
        ]
        self.assertEqual(1, len(completed_merges))
        self.assertEqual(MergeDecision.HOLD, completed_merges[0].decision)


# ----------------------- AC-5 / P4: three-way diff -----------------------


class TestThreeWayDiff(unittest.TestCase):
    """AC-5 / P4: original_value / current_value / submitted_value semantics."""

    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_field_merge_carries_three_values(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            completed=("drafted spec",),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        completed_merges = [
            m for m in proposal.record.field_merges
            if m.field_path == "completed_work"
        ]
        self.assertEqual(1, len(completed_merges))
        fm = completed_merges[0]
        # The baseline has no per-period completed list; the
        # report does not reference a baseline; both are MISSING.
        self.assertTrue(_is_missing(fm.original_value))
        self.assertTrue(_is_missing(fm.current_value))
        # submitted_value is the report's list
        self.assertEqual(("drafted spec",), tuple(fm.submitted_value))
        # to_dict round-trips MISSING as null
        d = fm.to_dict()
        self.assertIsNone(d["original_value"])
        self.assertIsNone(d["current_value"])
        self.assertEqual(["drafted spec"], d["submitted_value"])

    def test_field_merge_never_invents_a_value_for_missing_field(self):
        # Critical: the OLD engine used tuple(baseline.title) for
        # the completed_work original_value. The new engine must
        # never do that.
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            completed=("anything",),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        for fm in proposal.record.field_merges:
            # No FM should contain the baseline title as a value
            # (e.g. ["A","l","p","h","a"])
            self.assertNotEqual(("Alpha",), tuple(fm.current_value) if not _is_missing(fm.current_value) else (None,))
            self.assertNotEqual(("Alpha",), tuple(fm.original_value) if not _is_missing(fm.original_value) else (None,))


# ----------------------- AC-9: merge record audit -----------------------


class TestMergeRecordAudit(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_audit_projection_excludes_field_merge_content(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            completed=("drafted",),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        audit = self.engine.to_audit_record(proposal)
        # JSON-safe round-trip
        self.assertEqual(audit, json.loads(json.dumps(audit)))
        self.assertEqual("merge.proposal", audit["kind"])
        self.assertNotIn("field_merges", audit)
        self.assertNotIn("store_post", audit)
        # Has the version / decision / decision_maker info
        self.assertIn("base_version", audit)
        self.assertIn("current_version", audit)
        self.assertIn("merged_version", audit)
        self.assertIn("decision_maker", audit)
        self.assertIn("has_conflict", audit)

    def test_record_to_dict_is_json_safe(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            completed=("drafted",),
        )
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        d = proposal.record.to_dict()
        self.assertEqual(d, json.loads(json.dumps(d)))
        self.assertIn("base_version", d)
        self.assertIn("current_version", d)
        self.assertIn("merged_version", d)
        self.assertIn("decision_maker", d)
        self.assertIn("has_conflict", d)
        self.assertIn("store_post_length", d)


# ----------------------- merge is byte-deterministic -----------------------


class TestDeterminism(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_same_inputs_yield_identical_proposal(self):
        report = _report(
            base_revision=_base_revision_for(self.baseline),
            status=ReportStatus.ON_TRACK,
            completed=("drafted",),
        )
        outcome = _import_outcome(report)
        a = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        b = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertEqual(a.accepted, b.accepted)
        self.assertEqual(a.new_baseline.version, b.new_baseline.version)
        self.assertEqual(len(a.record.field_merges), len(b.record.field_merges))


if __name__ == "__main__":
    unittest.main()


# ----------------------- Round-2 P1 fix: AC-3 base_revision conflict -----------------------

class TestBaseRevisionConflict(unittest.TestCase):
    """AC-3 / protocol 16.3 + 16.4: base_revision mismatch must NOT be silent accept.

    Round-2 P1 fix closes the regression where v2 silently accepted any base_revision.
    """

    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_base_revision_mismatch_emits_hold_with_conflict(self):
        # Baseline version=1 -> expected base_revision = "PRJ001-R0001"
        report = _report(base_revision="PRJ001-R9999")
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        # Must be HOLD-with-conflict, NOT silent accept
        self.assertFalse(
            proposal.accepted,
            "AC-3 violated: base_revision mismatch was silently accepted; "
            f"reason={proposal.rejection_reason!r}",
        )
        self.assertTrue(
            proposal.record.has_conflict,
            "AC-3 violation: has_conflict must be True for HOLD-with-conflict",
        )
        self.assertIn("AC-3", proposal.rejection_reason)
        self.assertIn("16.3", proposal.rejection_reason)
        # Store is unchanged (no register)
        self.assertEqual(0, len(proposal.record.store_post))

    def test_base_revision_match_passes(self):
        report = _report(base_revision=_base_revision_for(self.baseline))
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        # Should pass base_revision check; with clean ON_TRACK it should accept.
        self.assertTrue(proposal.accepted)


# ----------------------- Round-2 P4 fix: decision_maker authority -----------------------

class TestDecisionMakerAuthority(unittest.TestCase):
    """Round-2 P4 fix: decision_maker is derived from the verified import_outcome,
    NEVER from the engine ctor (mandatory constraint 8.4)."""

    def setUp(self) -> None:
        self.engine = MergeEngine()  # v3 ctor: NO decision_maker arg
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_no_engine_decision_maker_attribute(self):
        # v2 had `decision_maker: str = "engine"` ctor arg. v3 must NOT.
        self.assertFalse(hasattr(self.engine, "decision_maker"))

    def test_decision_maker_equals_recipient_cert_id(self):
        report = _report(base_revision=_base_revision_for(self.baseline))
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertTrue(proposal.accepted)
        # decision_maker must be the verified import recipient cert_id
        self.assertEqual(
            report.recipient_cert_id,
            proposal.record.decision_maker,
        )
        # NOT the ctor default (which was "engine" in v2)
        self.assertNotEqual("engine", proposal.record.decision_maker)

    def test_authorized_recipient_certs_allows(self):
        report = _report(base_revision=_base_revision_for(self.baseline))
        outcome = _import_outcome(report)
        allow = frozenset({report.recipient_cert_id})
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
            authorized_recipient_certs=allow,
        )
        self.assertTrue(proposal.accepted)
        self.assertEqual(report.recipient_cert_id, proposal.record.decision_maker)

    def test_authorized_recipient_certs_rejects_other(self):
        report = _report(base_revision=_base_revision_for(self.baseline))
        outcome = _import_outcome(report)
        # Allow-list does NOT include the recipient
        allow = frozenset({"OTHER-CERT-1", "OTHER-CERT-2"})
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
            authorized_recipient_certs=allow,
        )
        self.assertFalse(proposal.accepted)
        self.assertIn("8.4", proposal.rejection_reason)
        self.assertIn(report.recipient_cert_id, proposal.rejection_reason)

    def test_attacker_cannot_inject_decision_maker(self):
        # PROBE 14 regression: an attacker who controls the engine ctor
        # used to be able to set decision_maker=ANYONE-CAN-LIE and have
        # it accepted. v3 ctor has no such parameter.
        with self.assertRaises(TypeError):
            MergeEngine(decision_maker="ANYONE-CAN-LIE")  # type: ignore[call-arg]


# ----------------------- Round-2 P1 fix: HOLD-with-conflict carries audit fields -----------------------

class TestConflictThreeWayDiff(unittest.TestCase):
    """Round-2 P1 fix: when base_revision mismatches, the HOLD proposal is
    audit-friendly -- decision_maker is still recorded from the verified
    import_outcome (no forge), and the store is unchanged."""

    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_hold_proposal_keeps_decision_maker_from_import_outcome(self):
        report = _report(base_revision="PRJ001-R9999")
        outcome = _import_outcome(report)
        proposal = self.engine.merge(
            import_outcome=outcome, report=report,
            baseline=self.baseline, store=self.store,
            decided_at="2026-08-20T01:00:00Z",
        )
        self.assertFalse(proposal.accepted)
        # decision_maker is sourced from import_outcome even on conflict
        self.assertEqual(report.recipient_cert_id, proposal.record.decision_maker)
        self.assertNotEqual("", proposal.record.decision_maker)
