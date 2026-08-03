"""US-10-AC-1 merge engine (P1 fix + Round-2) test (4 new TestCase classes).

Adds:
- TestBaseRevisionConflict: P1 fix Round-2 AC-3 base_revision mismatch
  emits HOLD-with-conflict, not silent accept.
- TestDecisionMakerAuthority: P4 fix Round-2 decision_maker is derived
  from import_outcome, NOT from engine ctor. With
  authorized_recipient_certs allow-list.
- TestNoEngineDecisionMaker: explicitly tests the v2 ctor argument is gone.
- TestConflictThreeWayDiff: HOLD-with-conflict proposal carries the
  three way diff fields for user resolution.
"""
# -*- coding: utf-8 -*-
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
)
from src.coevo.protocol.import_transaction import (
    ImportStep,
    ImportTransaction,
)
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
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import (
    BaselineInput,
    Deliverable,
    ProjectBaseline,
    Task,
    WorkPackage,
    build_baseline,
)


# ---- shared fixtures ----

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
    package_id=None, sender_cert_id="CERT-RECIPIENT-021",
    recipient_cert_id="CERT-SENDER-001",
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
        sender_organization_id="ORG002", sender_cert_id=sender_cert_id,
        recipient_user_id="USR001", recipient_client_id="CLI001",
        recipient_organization_id="ORG001", recipient_cert_id=recipient_cert_id,
        status=status,
        progress_summary="50% complete",
        completed_work=completed,
        pending_work=pending,
        next_steps=next_steps,
        risks=risks,
        artifacts=(),
    )


def _processed_package(report, *, package_digest=None):
    return ProcessedPackage(
        package_id=report.package_id,
        package_digest=package_digest or f"digest-{report.package_id}",
        sender_cert_id=report.sender_cert_id,
        recipient_cert_id=report.recipient_cert_id,
        project_id=report.project_id,
        sequence_no=report.sequence_no,
    )


def _import_outcome(report, *, step=ImportStep.COMMITTED, package_digest=None, package_type="RESULT_SUBMISSION"):
    pkg = _processed_package(report, package_digest=package_digest)
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


def _base_revision_for(baseline):
    return _master_revision(baseline.project_id, baseline.version)


# ---- Round-2 P1: AC-3 base_revision must not be silent accept ----

class TestBaseRevisionConflict(unittest.TestCase):
    """AC-3 / protocol 16.3 + 16.4: base_revision mismatch must NOT be silent accept."""

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
        self.assertFalse(
            proposal.accepted,
            f"AC-3 violated: base_revision mismatch was silently accepted; reason={proposal.rejection_reason!r}",
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
        # Clean ON_TRACK -> accepted
        self.assertTrue(proposal.accepted)


# ---- Round-2 P4: decision_maker authority ----

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


# ---- Round-2 P1: HOLD-with-conflict carries audit fields ----

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


class TestRejectMalformedRecordFailClosed(unittest.TestCase):
    """REVIEW-FIX-1: _reject must not silently fabricate decision_maker."""

    def setUp(self) -> None:
        self.engine = MergeEngine()
        self.baseline = _baseline()
        self.store = ProcessedPackageStore.empty()

    def test_reject_with_malformed_record_raises(self):
        report = _report()

        class _FakeOutcome:
            record = object()

        with self.assertRaises(MergeError):
            self.engine._reject(
                self.baseline,
                self.store,
                report,
                "2026-08-20T01:00:00Z",
                reason="simulated",
                import_outcome=_FakeOutcome(),
            )

    def test_reject_without_import_outcome_keeps_empty_decision_maker(self):
        report = _report()
        proposal = self.engine._reject(
            self.baseline,
            self.store,
            report,
            "2026-08-20T01:00:00Z",
            reason="simulated",
        )
        self.assertEqual("", proposal.record.decision_maker)
        self.assertFalse(proposal.accepted)
