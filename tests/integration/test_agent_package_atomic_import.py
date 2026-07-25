"""Integration tests for US-5-AC-3 atomic-import + persistence layer.

Coverage matrix (each TestCase class locks one § layer):

  § 15  ``TestImportTransaction``      - 7-step state machine + rollback.
  § 17  ``TestProcessedPackageStore`` - in-memory registry + scope / digest queries.
  § 15+§ 17 ``TestPackageImportService`` - end-to-end facade.

All operations are PURE (no IO, no DB). The facade enforces
replay acceptance, base_revision match (协议 § 16), and atomic
register into the processed-package store.
"""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.protocol import (
    AgentPackageImportConflictError,
    AgentPackageImportError,
    AgentPackageImportReplayError,
    AgentPackageImportValidationError,
    AgentPackageStoreDuplicateError,
    AgentPackageStoreError,
    AtomicImporter,
    DEFAULT_EMPTY_STORE,
    ImportOutcome,
    ImportStep,
    ImportTransaction,
    PackageImportService,
    ProcessedPackage,
    ProcessedPackageRecord,
    ProcessedPackageStore,
    ReplayDecision,
    ReplayOutcome,
    build_envelope_template,
    build_key_transport_block,
    build_unsigned_package,
    assemble_payload_block,
    check_replay,
)


def _build_package(
    *,
    sender: str = "CERT-SENDER",
    recipient: str = "CERT-RECIPIENT",
    project: str = "PRJ001",
    sequence_no: int = 1,
):
    import base64
    nonce_b64 = base64.b64encode(b"\x00" * 12).decode("ascii")
    env = build_envelope_template(
        sender_cert_id=sender,
        recipient_cert_id=recipient,
        project_id=project,
        package_type="TASK_ASSIGNMENT",
        sequence_no=sequence_no,
        payload_length=16,
        nonce_b64=nonce_b64,
    )
    return build_unsigned_package(
        envelope=env,
        key_block=build_key_transport_block(recipient_cert_id=recipient),
        payload_block=assemble_payload_block(b"\x42" * 16),
    )


def _record_for(pkg, *, processed_at="2026-07-25T12:00:00Z", revision="PRJ001-R0001"):
    return ProcessedPackageRecord(
        package=ProcessedPackage(
            package_id=pkg.envelope.package_id,
            package_digest=f"{pkg.envelope.package_id}|{pkg.envelope.sequence_no}|{pkg.expected_total_length()}",
            sender_cert_id=pkg.envelope.sender_cert_id,
            recipient_cert_id=pkg.envelope.recipient_cert_id,
            project_id=pkg.envelope.project_id,
            sequence_no=pkg.envelope.sequence_no,
        ),
        package_type=pkg.envelope.package_type,
        processed_at=processed_at,
        result="committed",
        revision=revision,
    )


# ----------------------- § 15 ImportTransaction -----------------------


class TestImportTransaction(unittest.TestCase):
    def test_begin_returns_quarantine_received(self):
        importer = AtomicImporter()
        tx = importer.begin(package_id="p.1", project_id="PRJ")
        self.assertEqual(ImportStep.QUARANTINE_RECEIVED, tx.step)
        self.assertEqual(tuple(), tx.completed_steps)

    def test_advance_strict_monotonic(self):
        importer = AtomicImporter()
        tx = importer.begin(package_id="p.1", project_id="PRJ")
        tx = importer.advance(tx, to_step=ImportStep.DECRYPT_AND_INSPECT)
        tx = importer.advance(tx, to_step=ImportStep.PREPARE_WORKSPACE)
        self.assertEqual((ImportStep.QUARANTINE_RECEIVED, ImportStep.DECRYPT_AND_INSPECT), tx.completed_steps)
        self.assertEqual(ImportStep.PREPARE_WORKSPACE, tx.step)

    def test_advance_backwards_rejected(self):
        importer = AtomicImporter()
        tx = importer.begin(package_id="p.1", project_id="PRJ")
        tx = importer.advance(tx, to_step=ImportStep.DECRYPT_AND_INSPECT)
        with self.assertRaises(AgentPackageImportError):
            importer.advance(tx, to_step=ImportStep.QUARANTINE_RECEIVED)

    def test_full_7_step_path(self):
        importer = AtomicImporter()
        tx = importer.begin(package_id="p.1", project_id="PRJ")
        for step in (
            ImportStep.DECRYPT_AND_INSPECT,
            ImportStep.PREPARE_WORKSPACE,
            ImportStep.WRITE_FILES,
            ImportStep.PREPARE_DATABASE,
            ImportStep.COMMIT,
            ImportStep.PROMOTE,
            ImportStep.CLEANUP,
            ImportStep.COMMITTED,
        ):
            tx = importer.advance(tx, to_step=step)
        self.assertEqual(ImportStep.COMMITTED, tx.step)
        self.assertEqual(8, len(tx.completed_steps))

    def test_fail_marks_rolled_back(self):
        importer = AtomicImporter()
        tx = importer.begin(package_id="p.1", project_id="PRJ")
        tx = importer.advance(tx, to_step=ImportStep.WRITE_FILES)
        failed = importer.fail(tx, reason="disk full")
        self.assertEqual(ImportStep.ROLLED_BACK, failed.step)
        self.assertEqual("disk full", failed.failure_reason)
        # completed_steps holds every step the transaction has *finished*;
        # after advance(to=WRITE_FILES) the most-recently-finished step is
        # PREPARE_WORKSPACE (the step immediately before WRITE_FILES), so
        # the recorded history is (QUARANTINE_RECEIVED, DECRYPT_AND_INSPECT,
        # PREPARE_WORKSPACE). fail() does NOT append further.
        # After advance(QUARANTINE_RECEIVED -> DECRYPT_AND_INSPECT ->
        # PREPARE_WORKSPACE -> WRITE_FILES), the most-recently-finished
        # step is PREPARE_WORKSPACE. fail() records the rollback but
        # does NOT append further steps.
        self.assertEqual(
            (
                ImportStep.QUARANTINE_RECEIVED,
                ImportStep.DECRYPT_AND_INSPECT,
                ImportStep.PREPARE_WORKSPACE,
            ),
            failed.completed_steps,
        )
        # And the current step is WRITE_FILES (the step that was in
        # flight when the rollback fired).
        self.assertEqual(ImportStep.WRITE_FILES, tx.step)
        # fail() promotes to ROLLED_BACK.
        self.assertEqual(ImportStep.ROLLED_BACK, failed.step)

    def test_fail_empty_reason_rejected(self):
        importer = AtomicImporter()
        tx = importer.begin(package_id="p.1", project_id="PRJ")
        with self.assertRaises(AgentPackageImportError):
            importer.fail(tx, reason="")

    def test_check_replay_accepts_only_accept(self):
        importer = AtomicImporter()
        tx = importer.begin(package_id="p.1", project_id="PRJ")
        importer.check_replay(
            tx,
            replay_decision=ReplayDecision(ReplayOutcome.ACCEPT, None, "ok"),
        )
        for outcome in (
            ReplayOutcome.DUPLICATE_PACKAGE_ID,
            ReplayOutcome.REPLAY_SEQUENCE,
            ReplayOutcome.REVOKED_PACKAGE,
        ):
            with self.assertRaises(AgentPackageImportReplayError):
                importer.check_replay(
                    tx,
                    replay_decision=ReplayDecision(outcome, 1, "rejected"),
                )

    def test_check_base_revision_match(self):
        importer = AtomicImporter()
        tx = importer.begin(
            package_id="p.1", project_id="PRJ",
            base_revision="PRJ-R0001", current_revision="PRJ-R0001",
        )
        importer.check_base_revision(tx)  # no error

    def test_check_base_revision_mismatch_rejected(self):
        importer = AtomicImporter()
        tx = importer.begin(
            package_id="p.1", project_id="PRJ",
            base_revision="PRJ-R0001", current_revision="PRJ-R0002",
        )
        with self.assertRaises(AgentPackageImportConflictError):
            importer.check_base_revision(tx)

    def test_check_base_revision_first_import(self):
        importer = AtomicImporter()
        tx = importer.begin(
            package_id="p.1", project_id="PRJ",
            base_revision=None, current_revision=None,
        )
        importer.check_base_revision(tx)  # no error

    def test_audit_record_is_json_safe(self):
        import json
        importer = AtomicImporter()
        tx = importer.begin(package_id="p.1", project_id="PRJ")
        record = importer.to_audit_record(tx)
        s = json.dumps(record)
        self.assertEqual(record, json.loads(s))


# ----------------------- § 17 ProcessedPackageStore -----------------------


class TestProcessedPackageStore(unittest.TestCase):
    def test_empty_store(self):
        store = ProcessedPackageStore.empty()
        self.assertEqual(0, len(store))
        self.assertIsNone(store.get("missing"))
        self.assertIsNone(store.by_digest("missing"))

    def test_register_then_get(self):
        pkg = _build_package()
        store = ProcessedPackageStore.empty()
        store = store.register(_record_for(pkg))
        self.assertEqual(1, len(store))
        rec = store.get(pkg.envelope.package_id)
        self.assertEqual(pkg.envelope.package_id, rec.package.package_id)

    def test_register_rejects_duplicate_package_id(self):
        pkg = _build_package()
        store = ProcessedPackageStore.empty().register(_record_for(pkg))
        with self.assertRaises(AgentPackageStoreDuplicateError):
            store.register(_record_for(pkg))

    def test_register_rejects_duplicate_digest(self):
        # Two records whose package_digest matches must be rejected
        # even when package_id differs. The store uses the package_id
        # registered above; the second record keeps a different id
        # but the same digest string.
        pkg1 = _build_package()
        store = ProcessedPackageStore.empty()
        store = store.register(_record_for(pkg1))
        # Synthesise a second record whose package_digest equals pkg1's.
        duplicate_record = ProcessedPackageRecord(
            package=ProcessedPackage(
                package_id="00000000-0000-0000-0000-000000000999",
                package_digest=f"{pkg1.envelope.package_id}|{pkg1.envelope.sequence_no}|{pkg1.expected_total_length()}",
                sender_cert_id=pkg1.envelope.sender_cert_id,
                recipient_cert_id=pkg1.envelope.recipient_cert_id,
                project_id=pkg1.envelope.project_id,
                sequence_no=pkg1.envelope.sequence_no + 1,
            ),
            package_type=pkg1.envelope.package_type,
            processed_at="2026-07-25T12:00:01Z",
            result="committed",
            revision="PRJ001-R0001",
        )
        with self.assertRaises(AgentPackageStoreDuplicateError):
            store.register(duplicate_record)

    def test_by_scope_sorted_by_sequence(self):
        pkg_a = _build_package(sequence_no=3)
        pkg_b = _build_package(sequence_no=1)
        pkg_c = _build_package(sequence_no=2)
        store = ProcessedPackageStore.empty()
        store = store.register(_record_for(pkg_b))
        store = store.register(_record_for(pkg_c))
        store = store.register(_record_for(pkg_a))
        recs = store.by_scope(
            sender_cert_id="CERT-SENDER",
            recipient_cert_id="CERT-RECIPIENT",
            project_id="PRJ001",
        )
        self.assertEqual([1, 2, 3], [r.package.sequence_no for r in recs])

    def test_revision_for_returns_highest_revision(self):
        pkg1 = _build_package()
        pkg2 = _build_package()
        store = ProcessedPackageStore.empty().register(_record_for(pkg1, revision="PRJ-R0001"))
        store = store.register(_record_for(pkg2, revision="PRJ-R0002"))
        self.assertEqual("PRJ-R0002", store.revision_for("PRJ001"))
        self.assertIsNone(store.revision_for("UNRELATED"))


# ----------------------- § 15 + § 17 PackageImportService -----------------------


class TestPackageImportService(unittest.TestCase):
    def test_full_import_committed(self):
        pkg = _build_package()
        replay = check_replay(candidate=ProcessedPackage(
            package_id=pkg.envelope.package_id,
            package_digest=f"{pkg.envelope.package_id}|{pkg.envelope.sequence_no}|{pkg.expected_total_length()}",
            sender_cert_id=pkg.envelope.sender_cert_id,
            recipient_cert_id=pkg.envelope.recipient_cert_id,
            project_id=pkg.envelope.project_id,
            sequence_no=pkg.envelope.sequence_no,
        ))
        service = PackageImportService()
        outcome = service.import_package(
            package=pkg,
            replay_decision=replay,
            store=DEFAULT_EMPTY_STORE,
            base_revision="PRJ001-R0001",
            current_revision="PRJ001-R0001",
        )
        self.assertEqual(ImportStep.COMMITTED, outcome.transaction.step)
        self.assertEqual(1, len(outcome.store))
        self.assertIsNotNone(outcome.record)
        self.assertEqual(pkg.envelope.package_id, outcome.record.package.package_id)

    def test_replay_rejected_returns_rolled_back(self):
        pkg = _build_package()
        replay = ReplayDecision(ReplayOutcome.REPLAY_SEQUENCE, 5, "earlier")
        service = PackageImportService()
        outcome = service.import_package(
            package=pkg,
            replay_decision=replay,
            store=DEFAULT_EMPTY_STORE,
        )
        self.assertEqual(ImportStep.ROLLED_BACK, outcome.transaction.step)
        self.assertEqual(0, len(outcome.store))
        self.assertIsNone(outcome.record)

    def test_base_revision_mismatch_returns_rolled_back(self):
        pkg = _build_package()
        replay = check_replay(candidate=ProcessedPackage(
            package_id=pkg.envelope.package_id,
            package_digest=f"{pkg.envelope.package_id}|{pkg.envelope.sequence_no}|{pkg.expected_total_length()}",
            sender_cert_id=pkg.envelope.sender_cert_id,
            recipient_cert_id=pkg.envelope.recipient_cert_id,
            project_id=pkg.envelope.project_id,
            sequence_no=pkg.envelope.sequence_no,
        ))
        service = PackageImportService()
        outcome = service.import_package(
            package=pkg,
            replay_decision=replay,
            store=DEFAULT_EMPTY_STORE,
            base_revision="PRJ001-R0001",
            current_revision="PRJ001-R0002",  # mismatch
        )
        self.assertEqual(ImportStep.ROLLED_BACK, outcome.transaction.step)
        self.assertEqual(0, len(outcome.store))

    def test_first_import_no_revision(self):
        pkg = _build_package()
        replay = check_replay(candidate=ProcessedPackage(
            package_id=pkg.envelope.package_id,
            package_digest=f"{pkg.envelope.package_id}|{pkg.envelope.sequence_no}|{pkg.expected_total_length()}",
            sender_cert_id=pkg.envelope.sender_cert_id,
            recipient_cert_id=pkg.envelope.recipient_cert_id,
            project_id=pkg.envelope.project_id,
            sequence_no=pkg.envelope.sequence_no,
        ))
        service = PackageImportService()
        outcome = service.import_package(
            package=pkg,
            replay_decision=replay,
            store=DEFAULT_EMPTY_STORE,
            # no base_revision / current_revision
        )
        self.assertEqual(ImportStep.COMMITTED, outcome.transaction.step)
        self.assertEqual(1, len(outcome.store))

    def test_duplicate_package_id_rolls_back(self):
        pkg = _build_package()
        replay = check_replay(candidate=ProcessedPackage(
            package_id=pkg.envelope.package_id,
            package_digest=f"{pkg.envelope.package_id}|{pkg.envelope.sequence_no}|{pkg.expected_total_length()}",
            sender_cert_id=pkg.envelope.sender_cert_id,
            recipient_cert_id=pkg.envelope.recipient_cert_id,
            project_id=pkg.envelope.project_id,
            sequence_no=pkg.envelope.sequence_no,
        ))
        store = ProcessedPackageStore.empty().register(_record_for(pkg))
        service = PackageImportService()
        outcome = service.import_package(
            package=pkg,
            replay_decision=replay,
            store=store,
        )
        self.assertEqual(ImportStep.ROLLED_BACK, outcome.transaction.step)
        self.assertEqual(1, len(outcome.store))  # unchanged

    def test_import_advances_through_all_steps(self):
        pkg = _build_package()
        replay = check_replay(candidate=ProcessedPackage(
            package_id=pkg.envelope.package_id,
            package_digest=f"{pkg.envelope.package_id}|{pkg.envelope.sequence_no}|{pkg.expected_total_length()}",
            sender_cert_id=pkg.envelope.sender_cert_id,
            recipient_cert_id=pkg.envelope.recipient_cert_id,
            project_id=pkg.envelope.project_id,
            sequence_no=pkg.envelope.sequence_no,
        ))
        service = PackageImportService()
        outcome = service.import_package(
            package=pkg,
            replay_decision=replay,
            store=DEFAULT_EMPTY_STORE,
            base_revision="PRJ001-R0001",
            current_revision="PRJ001-R0001",
        )
        completed = outcome.transaction.completed_steps
        self.assertEqual(
            ImportStep.COMMITTED,
            outcome.transaction.step,
        )
        # 7 mandatory steps before COMMITTED must all be in completed_steps
        for step in (
            ImportStep.QUARANTINE_RECEIVED,
            ImportStep.DECRYPT_AND_INSPECT,
            ImportStep.PREPARE_WORKSPACE,
            ImportStep.WRITE_FILES,
            ImportStep.PREPARE_DATABASE,
            ImportStep.COMMIT,
            ImportStep.PROMOTE,
            ImportStep.CLEANUP,
        ):
            self.assertIn(step, completed)


if __name__ == "__main__":
    unittest.main()