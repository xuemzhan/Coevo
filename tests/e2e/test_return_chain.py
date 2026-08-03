"""E2E proof of the fixed RETURN chain (GOAL.md mvp-complete condition 3).

Drives the second fixed orchestration chain end-to-end with a REAL
encrypted ``.agent`` package (GmSSL prototype provider):

    成果包导入 → 版本差异审核(merge + signed receipt) → 项目主版本更新
    → 风险预警 → 决策简报生成 → 知识沉淀入库

Every hop uses the production facades; the only in-memory stand-ins are
the merge receipt repository and risk/brief repositories (mirroring the
integration tests). The package itself is genuinely encrypted with
SM2/SM4, decrypted, signature-verified and re-parsed on the owner side.
"""
from __future__ import annotations

import base64
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.app import DEMO_PROFILE, ensure_demo_profile  # noqa: E402
from src.coevo.crypto import GmsslPrototypeProvider  # noqa: E402
from src.coevo.decision_brief import (  # noqa: E402
    ApprovedTemplateRegistry,
    BriefType,
    DecisionBriefRepository,
    DecisionBriefService,
    RiskConfirmationRepository,
)
from src.coevo.knowledge_base import (  # noqa: E402
    KnowledgeBaseFacade,
    KnowledgeStore,
)
from src.coevo.merge import MergeEngine  # noqa: E402
from src.coevo.protocol import (  # noqa: E402
    PackageImportService,
    ReplayDecision,
    ReplayOutcome,
    build_encrypted_package,
    build_envelope_template,
    check_replay,
    open_encrypted_package,
    parse_package_bytes,
)
from src.coevo.protocol.import_transaction import ImportStep  # noqa: E402
from src.coevo.protocol.processed_package_store import (  # noqa: E402
    ProcessedPackageStore,
)
from src.coevo.protocol.replay_detector import ProcessedPackage  # noqa: E402
from src.coevo.protocol.sm2_sign import compute_sm3_digest  # noqa: E402
from src.coevo.report import ReportManifest, ReportStatus  # noqa: E402
from src.coevo.risk import merge_and_analyze  # noqa: E402
from tests.unit.test_merge_commit_receipt import (  # noqa: E402
    baseline,
    new_repository,
    signing_authority,
)


NOW = "2026-08-03T00:00:00Z"
DECIDED_AT = "2026-08-03T01:00:00Z"
CONFIRMED_AT = "2026-08-03T02:00:00Z"
GENERATED_AT = "2026-08-03T03:00:00Z"
ANALYSED_AT = "2026-08-03T01:30:00Z"
TEMPLATE = "templates/decision-brief.docx"
SENDER = "CERT-SENDER"
RECIPIENT = "CERT-OWNER"


def _write_docx(path: Path) -> None:
    """Write a minimal, non-macro DOCX template (same shape as unit tests)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>',
        )


def _report_manifest(package_id: str) -> ReportManifest:
    return ReportManifest(
        schema_version="1.0",
        package_id=package_id,
        package_type="RESULT_SUBMISSION",
        project_id="PRJ001",
        task_id="TASK-001",
        base_revision="PRJ001-R0001",
        sequence_no=1,
        submitted_at="2026-08-03T00:00:00Z",
        sender_user_id="USR021",
        sender_client_id="CLI021",
        sender_organization_id="ORG002",
        sender_cert_id=SENDER,
        recipient_user_id="USR001",
        recipient_client_id="CLI001",
        recipient_organization_id="ORG001",
        recipient_cert_id=RECIPIENT,
        status=ReportStatus.COMPLETED,
        progress_summary="TASK-001 completed with evidence",
        completed_work=("delivered evidence",),
        pending_work=(),
        next_steps=(),
        risks=(),
        artifacts=(),
    )


class ReturnChainE2ETest(unittest.TestCase):
    def test_real_encrypted_report_drives_merge_risk_brief_knowledge(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            ensure_demo_profile()
            provider = GmsslPrototypeProvider(ROOT)
            sender = provider.sender_handle(DEMO_PROFILE, SENDER)
            recipient = provider.recipient_handle(DEMO_PROFILE, RECIPIENT)

            # ---- member side: build a REAL encrypted RESULT_SUBMISSION ----
            envelope = build_envelope_template(
                sender_cert_id=SENDER,
                recipient_cert_id=RECIPIENT,
                project_id="PRJ001",
                package_type="RESULT_SUBMISSION",
                sequence_no=1,
                payload_length=0,
                created_at=NOW,
                expires_at="2027-08-03T00:00:00Z",
            )
            manifest = _report_manifest(envelope.package_id)
            package = build_encrypted_package(
                envelope=envelope,
                manifest={
                    "schema_version": "1.0",
                    "package_id": manifest.package_id,
                    "package_type": manifest.package_type,
                    "project_id": manifest.project_id,
                    "task_id": manifest.task_id,
                    "base_revision": manifest.base_revision,
                    "sequence_no": manifest.sequence_no,
                    "status": manifest.status.value,
                    "sender_cert_id": SENDER,
                    "recipient_cert_id": RECIPIENT,
                },
                content=b"report payload with evidence digest",
                provider=provider,
                sender_handle=sender,
                recipient_handle=recipient,
                signed_at=NOW,
            )
            wire = package.to_bytes()

            # ---- owner side: parse + decrypt + verify (real crypto) ----
            parsed = parse_package_bytes(wire)
            opened = open_encrypted_package(
                parsed,
                provider=provider,
                recipient_handle=recipient,
                sender_handle=sender,
            )
            self.assertEqual("TASK-001", opened.manifest["task_id"])
            self.assertTrue(opened.signature.signature)

            # ---- replay gate + atomic import (COMMITTED) ----
            digest = compute_sm3_digest(wire)
            replay = check_replay(
                candidate=ProcessedPackage(
                    package_id=manifest.package_id,
                    package_digest=digest,
                    sender_cert_id=SENDER,
                    recipient_cert_id=RECIPIENT,
                    project_id="PRJ001",
                    sequence_no=1,
                ),
                registry=(),
            )
            self.assertIs(ReplayOutcome.ACCEPT, replay.outcome)
            imported = PackageImportService().import_package(
                package=package,
                replay_decision=ReplayDecision(
                    ReplayOutcome.ACCEPT, None, "new report package"
                ),
                store=ProcessedPackageStore.empty(),
                base_revision="PRJ001-R0001",
                current_revision="PRJ001-R0001",
                processed_at=NOW,
            )
            self.assertEqual(ImportStep.COMMITTED, imported.transaction.step)
            self.assertIsNotNone(imported.record)

            # ---- version diff review + merge + signed receipt ----
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
                decided_at=DECIDED_AT,
                now=ANALYSED_AT,
            )
            self.assertTrue(outcome.commit.proposal.accepted)
            self.assertIsNotNone(outcome.commit.receipt)
            self.assertIsNotNone(outcome.risk_report)
            receipt = outcome.commit.receipt
            assert receipt is not None
            self.assertEqual(
                "PRJ001-R0002",
                outcome.commit.proposal.record.merged_version,
            )

            # ---- owner confirms the risk -> decision brief ----
            risk_report = outcome.risk_report
            assert risk_report is not None
            _write_docx(run_dir / TEMPLATE)
            templates = ApprovedTemplateRegistry(run_dir)
            approval = templates.approve(
                approval_id="approval.template.retchain",
                template_ref=TEMPLATE,
            )
            risks = RiskConfirmationRepository(signing_authority())
            confirmation = risks.confirm(
                receipt_id=receipt.receipt_id,
                receipt_repository=repository,
                risk_report=risk_report,
                confirmed_at=CONFIRMED_AT,
                confirmed_by=RECIPIENT,
                event_id="risk.confirm.retchain",
            )
            briefs = DecisionBriefRepository()
            brief = DecisionBriefService().generate(
                receipt_id=receipt.receipt_id,
                receipt_repository=repository,
                risk_confirmation_id=confirmation.confirmation_id,
                risk_repository=risks,
                brief_repository=briefs,
                brief_type=BriefType.STAGE,
                template_ref=TEMPLATE,
                template_approval_id=approval.approval_id,
                template_registry=templates,
                generated_at=GENERATED_AT,
                actor_id=RECIPIENT,
                event_id="brief.generate.retchain",
            )
            self.assertEqual("PRJ001", brief.project_id)

            # ---- knowledge aggregation + persistent store ----
            bundle = KnowledgeBaseFacade.aggregate(
                project_id="PRJ001",
                baseline={
                    "title": baseline().title,
                    "summary": "return-chain baseline",
                    "stages": ["execution"],
                    "work_packages": ["WP-001"],
                },
                merge_records=(outcome.commit.proposal.record.to_dict(),),
                risk_reports=(risk_report.to_dict(),),
                decision_briefs=(
                    {
                        "id": brief.brief_id,
                        "title": "stage decision brief",
                        "summary": "generated from owner-confirmed risk state",
                    },
                ),
                progress_captures=(),
                model_summaries=(),
                now=GENERATED_AT,
            )
            store = KnowledgeStore.create(run_dir / "knowledge.db")
            try:
                store.save(bundle, now=GENERATED_AT)
                self.assertTrue(store.verify_audit_chain())
            finally:
                store.close()
            reopened = KnowledgeStore.open(run_dir / "knowledge.db")
            try:
                self.assertEqual(
                    bundle.bundle_id,
                    reopened.load(bundle.bundle_id).bundle_id,
                )
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
