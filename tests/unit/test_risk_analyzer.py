"""Unit tests for receipt-authoritative US-11 risk analysis."""
from __future__ import annotations

import dataclasses
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.merge import MergeEngine
from src.coevo.protocol.processed_package_store import ProcessedPackageStore
from src.coevo.report import ReportStatus
from src.coevo.risk import (
    Risk,
    RiskAnalyzer,
    RiskKind,
    RiskReport,
    RiskValidationError,
    SourceKind,
    analyze_after_merge,
    merge_and_analyze,
)
from tests.unit.test_merge_commit_receipt import (
    baseline,
    committed,
    imported,
    new_repository,
    report,
    repository_for,
    signing_authority,
)


class RiskAnalysisTests(unittest.TestCase):
    def test_authoritative_store_is_required_and_caller_baseline_is_not_accepted(self):
        outcome = committed()
        receipt = outcome.receipt
        assert receipt is not None
        with self.assertRaises(RiskValidationError):
            analyze_after_merge(
                receipt_id=receipt.receipt_id,
                receipt_repository=object(),
                now="2026-08-21T00:00:00Z",
            )
        with self.assertRaises(TypeError):
            analyze_after_merge(
                receipt_id=receipt.receipt_id,
                receipt_repository=repository_for(outcome),
                baseline=dataclasses.replace(
                    outcome.proposal.new_baseline, title="tampered",
                ),
                now="2026-08-21T00:00:00Z",
            )

    def test_real_completed_status_is_authoritative_completion(self):
        outcome = committed()
        receipt = outcome.receipt
        assert receipt is not None
        risk_report = analyze_after_merge(
            receipt_id=receipt.receipt_id,
            receipt_repository=repository_for(outcome),
            now="2026-08-21T00:00:00Z",
        )
        dependency = next(
            risk for risk in risk_report.risks
            if risk.kind is RiskKind.PREDECESSOR_UNFINISHED
        )
        self.assertEqual(("TASK-003",), dependency.affected_tasks)
        self.assertIn("TASK-002", dependency.basis)
        self.assertNotIn("TASK-001", dependency.basis)

    def test_project_receipt_history_aggregates_completed_tasks(self):
        first = committed()
        second_report = report(
            task_id="TASK-002", status=ReportStatus.COMPLETED,
            version=2, sequence_no=2,
        )
        second = committed(
            current_baseline=first.proposal.new_baseline,
            manifest=second_report,
            store=first.proposal.record.store_post,
            receipt_repository=repository_for(first),
        )
        second_receipt = second.receipt
        assert second_receipt is not None
        result = analyze_after_merge(
            receipt_id=second_receipt.receipt_id,
            receipt_repository=repository_for(second),
            now="2026-08-21T00:00:00Z",
        )
        self.assertNotIn(
            RiskKind.PREDECESSOR_UNFINISHED,
            {risk.kind for risk in result.risks},
        )

    def test_free_text_completed_work_never_marks_task_complete(self):
        first = committed()
        free_text_report = report(
            task_id="TASK-002", status=ReportStatus.ON_TRACK,
            version=2, sequence_no=2,
            completed_work=("TASK-002", "completed=true"),
        )
        second = committed(
            current_baseline=first.proposal.new_baseline,
            manifest=free_text_report,
            store=first.proposal.record.store_post,
            receipt_repository=repository_for(first),
        )
        second_receipt = second.receipt
        assert second_receipt is not None
        self.assertIsNone(second_receipt.completed_task_id)
        result = analyze_after_merge(
            receipt_id=second_receipt.receipt_id,
            receipt_repository=repository_for(second),
            now="2026-08-21T00:00:00Z",
        )
        dependency = next(
            risk for risk in result.risks
            if risk.kind is RiskKind.PREDECESSOR_UNFINISHED
        )
        self.assertIn("TASK-002", dependency.basis)

    def test_merge_and_analyze_runs_real_chain_and_failure_has_no_risk(self):
        manifest = report()
        success_repository = new_repository()
        success = merge_and_analyze(
            engine=MergeEngine(
                receipt_repository=success_repository,
                receipt_authority=success_repository._authority,
            ), import_outcome=imported(manifest),
            report=manifest, baseline=baseline(),
            store=ProcessedPackageStore.empty(),
            receipt_repository=success_repository,
            decided_at="2026-08-20T00:00:00Z",
            now="2026-08-21T00:00:00Z",
        )
        self.assertTrue(success.commit.proposal.accepted)
        self.assertIsNotNone(success.commit.receipt)
        self.assertIsNotNone(success.risk_report)

        held_report = report(status=ReportStatus.AT_RISK)
        failure_repository = new_repository()
        failure = merge_and_analyze(
            engine=MergeEngine(
                receipt_repository=failure_repository,
                receipt_authority=failure_repository._authority,
            ), import_outcome=imported(held_report),
            report=held_report, baseline=baseline(),
            store=ProcessedPackageStore.empty(),
            receipt_repository=failure_repository,
            decided_at="2026-08-20T00:00:00Z",
            now="2026-08-21T00:00:00Z",
        )
        self.assertFalse(failure.commit.proposal.accepted)
        self.assertIsNone(failure.commit.receipt)
        self.assertIsNone(failure.risk_report)

    def test_time_boundaries_and_deadline_risk(self):
        outcome = committed()
        receipt = outcome.receipt
        assert receipt is not None
        with self.assertRaises(RiskValidationError):
            analyze_after_merge(
                receipt_id=receipt.receipt_id,
                receipt_repository=repository_for(outcome),
                now="2026-08-19T23:59:59Z",
            )
        result = analyze_after_merge(
            receipt_id=receipt.receipt_id,
            receipt_repository=repository_for(outcome),
            now="2026-09-03T00:00:00Z",
        )
        kinds = {risk.kind for risk in result.risks}
        self.assertIn(RiskKind.LONG_SILENCE, kinds)
        self.assertIn(RiskKind.DEADLINE_OVERRUN, kinds)

    def test_replay_is_deterministic_and_audit_excludes_sensitive_content(self):
        outcome = committed()
        receipt = outcome.receipt
        assert receipt is not None
        kwargs = {
            "receipt_id": receipt.receipt_id,
            "receipt_repository": repository_for(outcome),
            "now": "2026-09-03T00:00:00Z",
        }
        first = RiskAnalyzer().analyze_after_merge(**kwargs)
        second = RiskAnalyzer().analyze_after_merge(**kwargs)
        self.assertEqual(first, second)
        audit = RiskAnalyzer().to_audit_record(first)
        encoded = json.dumps(audit, sort_keys=True)
        for forbidden in ("basis", "recommendation", "rationale", "affected_tasks"):
            self.assertNotIn(forbidden, encoded)

    def test_models_reject_bool_severity_duplicate_ids_and_release_bypass(self):
        valid = Risk(
            "risk.1", RiskKind.LONG_SILENCE, SourceKind.FACTUAL, "basis",
            ("TASK-001",), "act", "2026-08-22T00:00:00Z", 3, "why",
        )
        with self.assertRaises(ValueError):
            dataclasses.replace(valid, severity=True)
        with self.assertRaises(ValueError):
            RiskReport(
                "pkg-1", "PRJ001", "2026-08-21T00:00:00Z",
                (valid, valid), False,
            )
        with self.assertRaises(ValueError):
            RiskReport(
                "pkg-1", "PRJ001", "2026-08-21T00:00:00Z",
                (valid,), False, requires_owner_confirmation=False,
            )
        with self.assertRaises(ValueError):
            RiskReport(
                "pkg-1", "PRJ001", "2026-08-21T00:00:00Z",
                (valid,), False, formally_released=True,
            )


if __name__ == "__main__":
    unittest.main()
