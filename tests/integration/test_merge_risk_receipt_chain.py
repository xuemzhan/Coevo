"""Integration proof for verified import → merge → receipt → risk."""
from __future__ import annotations

import sys
import unittest
import base64
import dataclasses
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.merge import MergeEngine
from src.coevo.merge.repository import (
    MergeReceiptRepository, MergeReceiptRepositoryRecoveryRequired,
)
from src.coevo.protocol.processed_package_store import ProcessedPackageStore
from src.coevo.protocol import (
    PackageImportService,
    ReplayDecision,
    ReplayOutcome,
    assemble_payload_block,
    build_envelope_template,
    build_key_transport_block,
    build_unsigned_package,
)
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.risk import RiskAnalyzer, analyze_after_merge, merge_and_analyze
from src.coevo.task_decomposition.models import Override
from tests.unit.test_merge_commit_receipt import (
    baseline, commit_override_receipt, committed, new_repository, repository_for,
)


class MergeRiskReceiptChainTests(unittest.TestCase):
    def test_verified_objects_drive_complete_automatic_chain(self):
        envelope = build_envelope_template(
            sender_cert_id="CERT-SENDER", recipient_cert_id="CERT-OWNER",
            project_id="PRJ001", package_type="RESULT_SUBMISSION",
            sequence_no=1, payload_length=16,
            nonce_b64=base64.b64encode(b"\x00" * 12).decode("ascii"),
        )
        package = build_unsigned_package(
            envelope=envelope,
            key_block=build_key_transport_block(
                recipient_cert_id="CERT-OWNER",
            ),
            payload_block=assemble_payload_block(b"\x42" * 16),
        )
        imported = PackageImportService().import_package(
            package=package,
            replay_decision=ReplayDecision(
                ReplayOutcome.ACCEPT, None, "new package",
            ),
            store=ProcessedPackageStore.empty(),
            base_revision="PRJ001-R0001",
            current_revision="PRJ001-R0001",
            processed_at="2026-08-19T01:00:00Z",
        )
        manifest = ReportManifest(
            schema_version="1.0", package_id=envelope.package_id,
            package_type="RESULT_SUBMISSION", project_id="PRJ001",
            task_id="TASK-001", base_revision="PRJ001-R0001",
            sequence_no=1, submitted_at="2026-08-19T00:00:00Z",
            sender_user_id="USR021", sender_client_id="CLI021",
            sender_organization_id="ORG002",
            sender_cert_id="CERT-SENDER",
            recipient_user_id="USR001", recipient_client_id="CLI001",
            recipient_organization_id="ORG001",
            recipient_cert_id="CERT-OWNER",
            status=ReportStatus.COMPLETED, progress_summary="complete",
            completed_work=("evidence",), pending_work=(), next_steps=(),
            risks=(), artifacts=(),
        )
        repository = new_repository()
        outcome = merge_and_analyze(
            engine=MergeEngine(
                receipt_repository=repository,
                receipt_authority=repository._authority,
            ),
            import_outcome=imported,
            report=manifest,
            baseline=baseline(),
            store=ProcessedPackageStore.empty(),
            receipt_repository=repository,
            decided_at="2026-08-20T00:00:00Z",
            now="2026-08-21T00:00:00Z",
        )
        receipt = outcome.commit.receipt
        self.assertTrue(outcome.commit.proposal.accepted)
        self.assertIsNotNone(receipt)
        assert receipt is not None
        self.assertEqual(
            receipt,
            outcome.commit.receipt_store.get(receipt.receipt_id),
        )
        self.assertIsNotNone(outcome.risk_report)
        assert outcome.risk_report is not None
        self.assertEqual(receipt.package_id, outcome.risk_report.merge_reporter_package_id)

    def test_promote_failure_propagates_recovery_required_without_risk(self):
        repository = new_repository()
        original_promote = repository.anchor.promote
        repository.anchor.promote = lambda: (_ for _ in ()).throw(
            RuntimeError("injected promote failure")
        )

        class CountingAnalyzer(RiskAnalyzer):
            calls = 0

            def analyze_after_merge(self, **kwargs):
                type(self).calls += 1
                return super().analyze_after_merge(**kwargs)

        manifest = ReportManifest(
            schema_version="1.0", package_id="pkg-recovery",
            package_type="RESULT_SUBMISSION", project_id="PRJ001",
            task_id="TASK-001", base_revision="PRJ001-R0001",
            sequence_no=1, submitted_at="2026-08-19T00:00:00Z",
            sender_user_id="USR021", sender_client_id="CLI021",
            sender_organization_id="ORG002", sender_cert_id="CERT-SENDER",
            recipient_user_id="USR001", recipient_client_id="CLI001",
            recipient_organization_id="ORG001", recipient_cert_id="CERT-OWNER",
            status=ReportStatus.COMPLETED, progress_summary="complete",
            completed_work=("evidence",), pending_work=(), next_steps=(),
            risks=(), artifacts=(),
        )
        from tests.unit.test_merge_commit_receipt import imported
        try:
            with self.assertRaises(MergeReceiptRepositoryRecoveryRequired):
                merge_and_analyze(
                    engine=MergeEngine(
                        receipt_repository=repository,
                        receipt_authority=repository._authority,
                    ),
                    import_outcome=imported(manifest), report=manifest,
                    baseline=baseline(), store=ProcessedPackageStore.empty(),
                    receipt_repository=repository,
                    decided_at="2026-08-20T00:00:00Z",
                    now="2026-08-21T00:00:00Z",
                    analyzer=CountingAnalyzer(),
                )
            self.assertEqual(0, CountingAnalyzer.calls)
        finally:
            repository.anchor.promote = original_promote

    def test_override_survives_close_open_verification_and_drives_risk(self):
        source = dataclasses.replace(
            baseline(), version=2, created_at="2026-08-20T00:00:00Z",
            overrides=(
                Override(
                    target_path="title", original_value=None,
                    edited_value={
                        "label": "Approved Alpha",
                        "flags": [True, 7, {"order": ["first", "second"]}],
                    },
                    reason="owner approved",
                ),
                Override(
                    target_path="objective",
                    original_value=["Ship MVP", {"approved": False}],
                    edited_value="Ship trusted MVP",
                    reason="scope clarified",
                ),
            ),
        )
        repository, receipt = commit_override_receipt(source)
        database = repository.database
        authority = repository._authority
        signer = repository.anchor.signer
        freshness = repository.anchor.freshness
        repository.close()
        reopened = MergeReceiptRepository.open(
            database, authority, signer, freshness,
        )
        try:
            verified = reopened.get_verified(
                receipt.receipt_id,
                trusted_time=dt.datetime(2026, 8, 21, tzinfo=dt.UTC),
            )
            self.assertEqual(source.overrides, verified.snapshot.baseline.overrides)
            self.assertEqual(
                ["first", "second"],
                verified.snapshot.baseline.overrides[0]
                .edited_value["flags"][2]["order"],
            )
            self.assertEqual(receipt.payload, verified.payload)
            self.assertEqual(receipt.snapshot.payload, verified.snapshot.payload)
            risk = analyze_after_merge(
                receipt_id=receipt.receipt_id,
                receipt_repository=reopened,
                now="2026-08-21T00:00:00Z",
            )
            self.assertEqual(receipt.project_id, risk.project_id)
        finally:
            reopened.close()


if __name__ == "__main__":
    unittest.main()
