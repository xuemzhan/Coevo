"""Tests for US-14-AC-1 knowledge base service facade.

Covers AC-1..AC-7 (7 acceptance criteria) plus quality / regression tests.
Pure-function tests, no IO.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.knowledge_base import (
    ClassificationDenied,
    KnowledgeBaseError,
    KnowledgeBaseFacade,
    KnowledgeBaseValidationError,
    KnowledgeBundle,
    KnowledgeClassification,
    KnowledgeEntry,
    KnowledgeSourceKind,
    ReusableTemplate,
    ReusableTemplateKind,
    RetrospectiveDraft,
    ReviewConflictError,
    ReviewDecision,
    ReviewDecisionKind,
)


NOW = "2026-08-22T00:00:00Z"
NOW2 = "2026-08-22T01:00:00Z"


def _baseline() -> dict:
    return {
        "title": "PRJ001 baseline",
        "summary": "initial baseline summary",
        "stages": ["plan", "execute", "review"],
        "work_packages": ["wp.1", "wp.2"],
    }


def _aggregate(**overrides) -> KnowledgeBundle:
    args = dict(
        project_id="PRJ001",
        baseline=_baseline(),
        merge_records=({"id": "mr.1", "title": "merge wp.1", "summary": "merged"},),
        risk_reports=({"id": "r.1", "kind": "DEADLINE_OVERRUN", "recommendation": "add buffer"},),
        meeting_conclusions=({"id": "mc.1", "title": "align on X"},),
        decision_briefs=(),
        progress_captures=(),
        model_summaries=({"id": "ms.1", "title": "LLM summary"},),
        now=NOW,
    )
    args.update(overrides)
    return KnowledgeBaseFacade.aggregate(**args)


# ---------------------------------------------------------------------------
# AC-5 / AC-7 closed-set + model_summary guard
# ---------------------------------------------------------------------------


class ClosedSetTests(unittest.TestCase):
    def test_knowledge_classification_closed_set(self):
        names = {c.name for c in KnowledgeClassification}
        for required in ("PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"):
            self.assertIn(required, names)

    def test_knowledge_source_kind_includes_model_summary(self):
        # AC-7: model summaries are a tracked source kind.
        names = {k.name for k in KnowledgeSourceKind}
        self.assertIn("MODEL_SUMMARY", names)
        # MODEL_SUMMARY is the only kind with default requires_owner_approval=True.
        ms = KnowledgeSourceKind.MODEL_SUMMARY
        self.assertEqual(ms.value, "model_summary")


class AggregateTests(unittest.TestCase):
    """AC-1 aggregation."""

    def test_aggregate_with_baseline_only(self):
        b = KnowledgeBaseFacade.aggregate(
            project_id="PRJ001", baseline=_baseline(), now=NOW
        )
        self.assertEqual(1, len(b.entries))
        self.assertEqual(KnowledgeSourceKind.PROJECT_BASELINE, b.entries[0].kind)
        self.assertFalse(b.entries[0].requires_owner_approval)

    def test_aggregate_with_all_provided_kinds(self):
        # _aggregate() provides baseline + merge + risk + conclusion +
        # model_summary (5 sources). DECISION_BRIEF + PROGRESS_CAPTURE
        # are tested separately as zero-arg paths.
        b = _aggregate()
        kinds = {e.kind for e in b.entries}
        self.assertEqual(5, len(b.entries))
        for expected in (
            KnowledgeSourceKind.PROJECT_BASELINE,
            KnowledgeSourceKind.MERGE_RECORD,
            KnowledgeSourceKind.RISK_REPORT,
            KnowledgeSourceKind.MEETING_CONCLUSION,
            KnowledgeSourceKind.MODEL_SUMMARY,
        ):
            self.assertIn(expected, kinds)

    def test_aggregate_with_decision_briefs_and_progress(self):
        b = _aggregate(
            decision_briefs=({"id": "db.1", "title": "decision"},),
            progress_captures=({"id": "pc.1", "title": "progress"},),
        )
        kinds = {e.kind for e in b.entries}
        self.assertIn(KnowledgeSourceKind.DECISION_BRIEF, kinds)
        self.assertIn(KnowledgeSourceKind.PROGRESS_CAPTURE, kinds)
        self.assertEqual(7, len(b.entries))

    def test_aggregate_marks_model_summary_requires_owner_approval(self):
        b = _aggregate()
        ms_entries = [e for e in b.entries if e.kind == KnowledgeSourceKind.MODEL_SUMMARY]
        self.assertEqual(1, len(ms_entries))
        self.assertTrue(ms_entries[0].requires_owner_approval)

    def test_aggregate_other_kinds_default_to_no_owner_approval(self):
        b = _aggregate()
        for e in b.entries:
            if e.kind != KnowledgeSourceKind.MODEL_SUMMARY:
                self.assertFalse(
                    e.requires_owner_approval,
                    f"{e.kind.value} should default to no owner approval",
                )


class RetrospectiveTests(unittest.TestCase):
    """AC-2 retrospective draft."""

    def test_aggregate_generates_retrospective_draft_with_five_sections(self):
        b = _aggregate()
        self.assertEqual(5, len(b.retrospective.body_sections))
        # Five canonical section names in headers.
        joined = "\n".join(b.retrospective.body_sections)
        for label in ("总体进展", "重要变化", "高风险", "待决策", "最佳实践"):
            self.assertIn(label, joined)

    def test_retrospective_requires_user_review_forced_true(self):
        b = _aggregate()
        self.assertTrue(b.retrospective.requires_user_review)

    def test_construct_retrospective_with_requires_user_review_false_rejected(self):
        with self.assertRaises(KnowledgeBaseValidationError):
            RetrospectiveDraft(
                draft_id="rd.1",
                project_id="PRJ001",
                title="x",
                body_sections=("a", "b", "c", "d", "e"),
                sources=("s.1",),
                generated_at=NOW,
                requires_user_review=False,
            )


class TemplateTests(unittest.TestCase):
    """AC-3 reusable template extraction."""

    def test_aggregate_extracts_process_template_from_baseline(self):
        b = _aggregate()
        process = [t for t in b.reusable_templates if t.kind == ReusableTemplateKind.PROCESS_TEMPLATE]
        self.assertEqual(1, len(process))
        self.assertIn("stages", process[0].body)

    def test_aggregate_extracts_risk_rule_from_risk_reports(self):
        b = _aggregate()
        risk_rules = [t for t in b.reusable_templates if t.kind == ReusableTemplateKind.RISK_RULE]
        self.assertEqual(1, len(risk_rules))
        self.assertEqual("DEADLINE_OVERRUN", risk_rules[0].body["risk_kind"])
        self.assertEqual("add buffer", risk_rules[0].body["rule"])


# ---------------------------------------------------------------------------
# AC-6 review + AC-7 formally_committed
# ---------------------------------------------------------------------------


class ReviewTests(unittest.TestCase):
    def _decisions(self, b: KnowledgeBundle) -> tuple[ReviewDecision, ...]:
        return tuple(
            ReviewDecision(
                decision_id=f"d.{i}",
                entry_id=e.entry_id,
                decision=ReviewDecisionKind.APPROVE,
                decided_by="u.alice",
                reason="ok",
                decided_at=NOW2,
            )
            for i, e in enumerate(b.entries)
            if e.requires_owner_approval
        )

    def test_review_approve_moves_entry_to_accepted(self):
        b = _aggregate()
        ms_id = next(e.entry_id for e in b.entries if e.kind == KnowledgeSourceKind.MODEL_SUMMARY)
        d = ReviewDecision(
            decision_id="d.1",
            entry_id=ms_id,
            decision=ReviewDecisionKind.APPROVE,
            decided_by="u.alice",
            reason="ok",
            decided_at=NOW2,
        )
        b2 = KnowledgeBaseFacade.review(b, decisions=(d,), now=NOW2)
        self.assertIn(ms_id, b2.accepted_entries)
        self.assertNotIn(ms_id, b2.rejected_entries)

    def test_review_reject_moves_entry_to_rejected(self):
        b = _aggregate()
        ms_id = next(e.entry_id for e in b.entries if e.kind == KnowledgeSourceKind.MODEL_SUMMARY)
        d = ReviewDecision(
            decision_id="d.1",
            entry_id=ms_id,
            decision=ReviewDecisionKind.REJECT,
            decided_by="u.alice",
            reason="too speculative",
            decided_at=NOW2,
        )
        b2 = KnowledgeBaseFacade.review(b, decisions=(d,), now=NOW2)
        self.assertIn(ms_id, b2.rejected_entries)

    def test_review_formally_committed_requires_all_model_summaries_decided(self):
        # With only the model_summary decided, formally_committed=True.
        b = _aggregate()
        d = self._decisions(b)[0]
        b2 = KnowledgeBaseFacade.review(b, decisions=(d,), now=NOW2)
        self.assertTrue(b2.formally_committed)
        self.assertEqual(NOW2, b2.committed_at)

    def test_review_no_decisions_stays_uncommitted(self):
        b = _aggregate()
        b2 = KnowledgeBaseFacade.review(b, decisions=(), now=NOW2)
        self.assertFalse(b2.formally_committed)
        self.assertEqual("", b2.committed_at)

    def test_review_rejects_duplicate_decision_for_same_entry(self):
        b = _aggregate()
        ms_id = next(e.entry_id for e in b.entries if e.kind == KnowledgeSourceKind.MODEL_SUMMARY)
        d1 = ReviewDecision(decision_id="d.1", entry_id=ms_id, decision=ReviewDecisionKind.APPROVE, decided_by="u.alice", reason="x", decided_at=NOW2)
        d2 = ReviewDecision(decision_id="d.2", entry_id=ms_id, decision=ReviewDecisionKind.REJECT, decided_by="u.alice", reason="y", decided_at=NOW2)
        with self.assertRaises(KnowledgeBaseValidationError):
            KnowledgeBaseFacade.review(b, decisions=(d1, d2), now=NOW2)

    def test_review_rejects_already_committed_bundle(self):
        b = _aggregate()
        ms_id = next(e.entry_id for e in b.entries if e.kind == KnowledgeSourceKind.MODEL_SUMMARY)
        d = ReviewDecision(decision_id="d.1", entry_id=ms_id, decision=ReviewDecisionKind.APPROVE, decided_by="u.alice", reason="x", decided_at=NOW2)
        b2 = KnowledgeBaseFacade.review(b, decisions=(d,), now=NOW2)
        with self.assertRaises(ReviewConflictError):
            KnowledgeBaseFacade.review(b2, decisions=(d,), now=NOW2)


# ---------------------------------------------------------------------------
# AC-5 classification check
# ---------------------------------------------------------------------------


class ClassificationTests(unittest.TestCase):
    def test_check_classification_accepts_sufficient_clearance(self):
        b = _aggregate()
        # Default bundle_classification is INTERNAL (all defaults).
        self.assertEqual(KnowledgeClassification.INTERNAL, b.bundle_classification)
        b2 = KnowledgeBaseFacade.check_classification(
            b,
            actor_clearances=frozenset({KnowledgeClassification.INTERNAL, KnowledgeClassification.CONFIDENTIAL}),
            now=NOW2,
        )
        self.assertIs(b2, b)

    def test_check_classification_denies_insufficient_clearance(self):
        b = _aggregate(baseline={**_baseline(), "classification": "restricted"})
        self.assertEqual(KnowledgeClassification.RESTRICTED, b.bundle_classification)
        with self.assertRaises(ClassificationDenied):
            KnowledgeBaseFacade.check_classification(
                b,
                actor_clearances=frozenset({KnowledgeClassification.PUBLIC}),
                now=NOW2,
            )

    def test_bundle_classification_is_max_across_mixed_entries(self):
        # OPTIMIZE-13: AC-5 takes the max classification over ALL entries;
        # an INTERNAL baseline plus a RESTRICTED brief must yield RESTRICTED.
        b = _aggregate(
            baseline=_baseline(),
            decision_briefs=(
                {"id": "db.1", "title": "brief", "classification": "restricted"},
            ),
        )
        self.assertEqual(KnowledgeClassification.RESTRICTED, b.bundle_classification)


# ---------------------------------------------------------------------------
# AC-7 fail-closed at construction
# ---------------------------------------------------------------------------


class ConstructBundleTests(unittest.TestCase):
    def test_construct_bundle_with_formally_committed_true_without_approval_rejected(self):
        # AC-7: formally_committed=True requires committed_at + committed_by.
        b = _aggregate()
        with self.assertRaises(KnowledgeBaseValidationError):
            KnowledgeBundle(
                bundle_id=b.bundle_id,
                project_id=b.project_id,
                entries=b.entries,
                retrospective=b.retrospective,
                reusable_templates=b.reusable_templates,
                accepted_entries=b.accepted_entries,
                rejected_entries=b.rejected_entries,
                bundle_classification=b.bundle_classification,
                requires_user_confirmation=True,
                formally_committed=True,
                committed_at="",
                committed_by="",
                created_at=NOW,
            )

    def test_construct_bundle_requires_user_confirmation_false_rejected(self):
        b = _aggregate()
        with self.assertRaises(KnowledgeBaseValidationError):
            KnowledgeBundle(
                bundle_id=b.bundle_id,
                project_id=b.project_id,
                entries=b.entries,
                retrospective=b.retrospective,
                reusable_templates=b.reusable_templates,
                accepted_entries=b.accepted_entries,
                rejected_entries=b.rejected_entries,
                bundle_classification=b.bundle_classification,
                requires_user_confirmation=False,
                formally_committed=False,
                committed_at="",
                committed_by="",
                created_at=NOW,
            )


class AuditProjectionTests(unittest.TestCase):
    def test_to_audit_record_excludes_sensitive_bodies(self):
        b = _aggregate()
        record = KnowledgeBaseFacade.to_audit_record(b)
        # Round-trip JSON-safe.
        self.assertEqual(record, json.loads(json.dumps(record)))
        serialized = json.dumps(record)
        # Body strings MUST NOT appear; only their SHA-256 hashes.
        self.assertNotIn("initial baseline summary", serialized)
        self.assertNotIn("merged", serialized)
        self.assertNotIn("总体进展", serialized)
        # 16-char hash present per entry.
        for entry in record["entries"]:
            self.assertEqual(16, len(entry["title_hash"]))
            self.assertEqual(16, len(entry["body_hash"]))
        # Metadata fields.
        self.assertEqual("coevo.knowledge_base", record["domain"])
        self.assertEqual("1.0", record["schema_version"])


class PureFunctionTests(unittest.TestCase):
    def test_pure_function_determinism(self):
        a = _aggregate()
        b = _aggregate()
        self.assertEqual(a.bundle_id, b.bundle_id)
        self.assertEqual(a.entries, b.entries)
        self.assertEqual(a.retrospective, b.retrospective)
        self.assertEqual(a.reusable_templates, b.reusable_templates)


if __name__ == "__main__":
    unittest.main()
