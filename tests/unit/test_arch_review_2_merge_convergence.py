"""ARCH-REVIEW-2: offline merge convergence property tests.

Contract (docs/architecture/merge-convergence.md):

* P1 deterministic replay -- the same ordered input sequence yields a
  byte-identical final baseline and the same accept/hold sequence;
* P2 idempotent duplicates -- re-merging an already registered package is
  a no-op (accepted=False, no version bump, store unchanged);
* P3 all-or-nothing -- any HOLD field forces accepted=False and the new
  baseline equals the input baseline (no partial versions);
* P4 stale-baseline serialization -- a report whose base_revision does not
  equal the current master never silently merges (HOLD-with-conflict);
* P5 version monotonicity -- every accepted merge bumps the version by
  exactly +1;
* P6 convergence -- replaying the same accepted sequence converges (P1);
  conflicts converge through human review + resubmission on the new master.

The engine is stdlib-only, so "property" testing uses fixed-seed pseudo
random sequences (deterministic across runs and platforms).
"""

from __future__ import annotations

import random
import unittest

from src.coevo.merge import (
    MergeEngine,
    _master_revision,
    canonical_baseline_digest,
)
from src.coevo.protocol.import_service import ImportOutcome
from src.coevo.protocol.import_transaction import ImportStep, ImportTransaction
from src.coevo.protocol.processed_package_store import (
    ProcessedPackageRecord,
    ProcessedPackageStore,
)
from src.coevo.protocol.replay_detector import ProcessedPackage
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import (
    BaselineInput,
    Deliverable,
    ProjectBaseline,
    Task,
    WorkPackage,
    build_baseline,
)

DECIDED_AT = "2026-08-20T01:00:00Z"


def _wp() -> WorkPackage:
    return WorkPackage(
        work_package_id="wp.intake",
        standard_stage="intake",
        title="Intake",
        tasks=(
            Task(
                task_id="t.1",
                title="Receive",
                responsible_role="pm",
                plan_start="2026-08-01T00:00:00Z",
                plan_end="2026-08-05T00:00:00Z",
                deliverables=(
                    Deliverable("d.1", "Doc", "document", ("ok",)),
                ),
            ),
        ),
    )


def _baseline() -> ProjectBaseline:
    return build_baseline(
        BaselineInput(
            project_id="PRJ001",
            title="Alpha",
            objective="Ship MVP",
            plan_start="2026-08-01T00:00:00Z",
            plan_end="2026-08-31T00:00:00Z",
            responsible_units=("unit_a",),
            process_flow_ref=("unit_a", 1),
            work_packages=(_wp(),),
        ),
        now="2026-08-01T00:00:00Z",
    )


def _report(
    *,
    base_revision: str,
    package_id: str,
    completed: tuple[str, ...] = ("draft",),
    risks: tuple[str, ...] = (),
) -> ReportManifest:
    return ReportManifest(
        schema_version="1.0",
        package_id=package_id,
        package_type="RESULT_SUBMISSION",
        project_id="PRJ001",
        task_id="TASK-001",
        base_revision=base_revision,
        sequence_no=1,
        submitted_at="2026-08-20T00:00:00Z",
        sender_user_id="USR021",
        sender_client_id="CLI021",
        sender_organization_id="ORG002",
        sender_cert_id="CERT-RECIPIENT-021",
        recipient_user_id="USR001",
        recipient_client_id="CLI001",
        recipient_organization_id="ORG001",
        recipient_cert_id="CERT-SENDER-001",
        status=ReportStatus.ON_TRACK,
        progress_summary="50% complete",
        completed_work=completed,
        pending_work=(),
        next_steps=(),
        risks=risks,
        artifacts=(),
    )


def _import_outcome(report: ReportManifest) -> ImportOutcome:
    pkg = ProcessedPackage(
        package_id=report.package_id,
        package_digest=f"digest-{report.package_id}",
        sender_cert_id=report.sender_cert_id,
        recipient_cert_id=report.recipient_cert_id,
        project_id=report.project_id,
        sequence_no=report.sequence_no,
    )
    tx = ImportTransaction(
        package_id=report.package_id,
        project_id=report.project_id,
        base_revision=report.base_revision,
        current_revision=report.base_revision,
        step=ImportStep.COMMITTED,
    )
    rec = ProcessedPackageRecord(
        package=pkg,
        package_type="RESULT_SUBMISSION",
        processed_at="2026-08-20T01:00:00Z",
        result="committed",
        revision=report.base_revision,
    )
    return ImportOutcome(transaction=tx, store=ProcessedPackageStore.empty(), record=rec)


def _apply(engine: MergeEngine, baseline, store, report):
    proposal = engine.merge(
        import_outcome=_import_outcome(report),
        report=report,
        baseline=baseline,
        store=store,
        decided_at=DECIDED_AT,
    )
    return proposal


def _random_sequence(seed: int, steps: int, stale_rate: float = 0.3):
    """Generate (base_version, completed) intents; current-base first."""
    rng = random.Random(seed)
    pool = [f"w{i}" for i in range(24)]
    current = 1
    reports: list[tuple[int, tuple[str, ...]]] = []
    for _ in range(steps):
        if rng.random() > stale_rate and current > 1:
            base = rng.randint(1, current - 1)
        else:
            base = current
        completed = tuple(rng.sample(pool, rng.randint(1, 3)))
        reports.append((base, completed))
        if base == current:
            current += 1
    return reports


class MergeConvergencePropertyTests(unittest.TestCase):
    """P1-P5 invariants over fixed-seed pseudo random merge sequences."""

    def _run(self, reports):
        engine = MergeEngine()
        baseline = _baseline()
        store = ProcessedPackageStore.empty()
        outcomes = []
        for index, (base_version, completed) in enumerate(reports):
            report = _report(
                base_revision=_master_revision("PRJ001", base_version),
                package_id=f"pkg-{index}",
                completed=completed,
            )
            proposal = _apply(engine, baseline, store, report)
            outcomes.append(proposal)
            baseline = proposal.new_baseline
            store = proposal.record.store_post
        return baseline, outcomes

    def test_replay_same_sequence_is_deterministic(self) -> None:
        reports = _random_sequence(seed=7, steps=10)
        baseline_a, outcomes_a = self._run(reports)
        baseline_b, outcomes_b = self._run(reports)
        self.assertEqual(
            canonical_baseline_digest(baseline_a),
            canonical_baseline_digest(baseline_b),
        )
        self.assertEqual(baseline_a.version, baseline_b.version)
        self.assertEqual(
            [p.accepted for p in outcomes_a],
            [p.accepted for p in outcomes_b],
        )

    def test_duplicate_application_is_idempotent_noop(self) -> None:
        engine = MergeEngine()
        baseline = _baseline()
        store = ProcessedPackageStore.empty()
        report = _report(
            base_revision=_master_revision("PRJ001", baseline.version),
            package_id="pkg-dupe",
            completed=("draft",),
        )
        first = _apply(engine, baseline, store, report)
        self.assertTrue(first.accepted)
        after_first = first.new_baseline
        store_after_first = first.record.store_post
        second = _apply(engine, after_first, store_after_first, report)
        self.assertFalse(second.accepted)
        self.assertIn("duplicate", second.rejection_reason.lower())
        self.assertEqual(second.new_baseline.version, after_first.version)
        self.assertEqual(
            canonical_baseline_digest(second.new_baseline),
            canonical_baseline_digest(after_first),
        )
        self.assertEqual(len(second.record.store_post), len(store_after_first))

    def test_stale_baseline_never_silently_merges(self) -> None:
        engine = MergeEngine()
        baseline = _baseline()  # version 1
        first = _apply(
            engine,
            baseline,
            ProcessedPackageStore.empty(),
            _report(
                base_revision=_master_revision("PRJ001", 1),
                package_id="pkg-current",
                completed=("draft",),
            ),
        )
        self.assertTrue(first.accepted)
        self.assertEqual(first.new_baseline.version, 2)
        stale = _apply(
            engine,
            first.new_baseline,
            first.record.store_post,
            _report(
                base_revision=_master_revision("PRJ001", 1),
                package_id="pkg-stale",
                completed=("review",),
            ),
        )
        self.assertFalse(stale.accepted)
        self.assertTrue(stale.record.has_conflict)
        self.assertEqual(stale.new_baseline.version, 2)
        self.assertEqual(
            canonical_baseline_digest(stale.new_baseline),
            canonical_baseline_digest(first.new_baseline),
        )

    def test_hold_is_all_or_nothing(self) -> None:
        engine = MergeEngine()
        baseline = _baseline()
        before = canonical_baseline_digest(baseline)
        held = _apply(
            engine,
            baseline,
            ProcessedPackageStore.empty(),
            _report(
                base_revision=_master_revision("PRJ001", baseline.version),
                package_id="pkg-risks",
                completed=("draft",),
                risks=("r1",),
            ),
        )
        self.assertFalse(held.accepted)
        self.assertEqual(held.new_baseline.version, baseline.version)
        self.assertEqual(
            canonical_baseline_digest(held.new_baseline),
            before,
        )

    def test_accepted_merge_bumps_version_exactly_one(self) -> None:
        reports = _random_sequence(seed=11, steps=8)
        _, outcomes = self._run(reports)
        version = 1
        for proposal in outcomes:
            if proposal.accepted:
                self.assertEqual(proposal.new_baseline.version, version + 1)
                version += 1
            else:
                self.assertEqual(proposal.new_baseline.version, version)

    def test_random_sequences_preserve_all_invariants(self) -> None:
        for seed in (1, 2, 3, 4, 5):
            reports = _random_sequence(seed=seed, steps=8)
            baseline, outcomes = self._run(reports)
            version = 1
            accepted_count = 0
            for proposal in outcomes:
                if proposal.accepted:
                    accepted_count += 1
                    self.assertEqual(proposal.new_baseline.version, version + 1)
                    version += 1
                else:
                    self.assertEqual(proposal.new_baseline.version, version)
                    self.assertTrue(proposal.record.has_conflict)
            self.assertEqual(baseline.version, 1 + accepted_count)


if __name__ == "__main__":
    unittest.main()
