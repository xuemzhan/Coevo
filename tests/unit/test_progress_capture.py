"""Tests for US-8-AC-1 progress capture service facade.

Covers AC-1..AC-8 (8 acceptance criteria) plus quality/regression tests.
Pure-function tests, no IO.
"""
from __future__ import annotations

import dataclasses
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.progress_capture import (
    DOMAIN,
    FORBIDDEN_KIND_TOKENS,
    SCHEMA_VERSION,
    EvidenceInput,
    EvidenceKind,
    EvidenceRef,
    ItemOverride,
    ProgressCapture,
    ProgressCaptureConflictError,
    ProgressCaptureError,
    ProgressCaptureService,
    ProgressCaptureValidationError,
    ProgressDraft,
    ProgressItem,
    ProgressItemKind,
    ProgressItemStatus,
)
from src.coevo.workspace.models import WorkspaceEntry


NOW = "2026-08-22T00:00:00Z"
NOW2 = "2026-08-22T00:05:00Z"
NOW3 = "2026-08-22T00:10:00Z"

GOOD_DIGEST = "a" * 64


def _ws() -> WorkspaceEntry:
    return WorkspaceEntry(
        project_id="PRJ001",
        role_id="a.pm",
        package_id="pkg.1",
        revision="r1",
    )


def _ev_ref(path: str = "docs/draft.md", role: str = "document") -> EvidenceRef:
    return EvidenceRef(
        path=path,
        role=role,
        media_type="text/markdown",
        digest_hex=GOOD_DIGEST,
        size_bytes=128,
    )


def _ev_input(
    *,
    task_id: str = "t.1",
    kind: EvidenceKind = EvidenceKind.DOCUMENT_CONTENT,
    source_ref: str = "docs/draft.md",
    text: str = "completed draft",
    confidence: float = 0.8,
    refs: tuple[EvidenceRef, ...] = (_ev_ref(),),
) -> EvidenceInput:
    return EvidenceInput(
        task_id=task_id,
        kind=kind,
        source_ref=source_ref,
        text=text,
        confidence=confidence,
        evidence_refs=refs,
    )


class ProgressCaptureModelTests(unittest.TestCase):
    def test_schema_version_constant_is_one_dot_zero(self):
        self.assertEqual("1.0", SCHEMA_VERSION)
        self.assertEqual("coevo.progress_capture", DOMAIN)

    def test_evidence_kind_has_no_file_mtime_member(self):
        # AC-7 fail-closed: the closed set must not include any mtime-based kind.
        names = {k.name for k in EvidenceKind}
        values = {k.value for k in EvidenceKind}
        for forbidden in ("FILE_MTIME_ONLY", "FileMtimeOnly", "file_mtime_only", "MTIME"):
            self.assertNotIn(forbidden, names)
            self.assertNotIn(forbidden, values)
        # Also assert the public string-token allow-list is enforced.
        self.assertIn("file_mtime_only", FORBIDDEN_KIND_TOKENS)


class ExtractProgressTests(unittest.TestCase):
    def test_extract_progress_recognizes_four_evidence_kinds(self):
        # AC-1
        inputs = (
            _ev_input(kind=EvidenceKind.EXPLICIT_USER_TEXT, source_ref="feedback/1", text="all done"),
            _ev_input(kind=EvidenceKind.DOCUMENT_CONTENT, source_ref="docs/a.md", text="doc updated"),
            _ev_input(kind=EvidenceKind.ARTIFACT_FILE, source_ref="out/x.bin", text="artifact produced", refs=(_ev_ref("out/x.bin", "artifact"),)),
            _ev_input(kind=EvidenceKind.TASK_DEPENDENCY_RESOLVED, source_ref="dep/t.0", text="predecessor finished"),
        )
        cap = ProgressCaptureService.extract_progress(_ws(), inputs, now=NOW)
        self.assertEqual(4, len(cap.progress_items))
        kinds = [item.source_kind for item in cap.progress_items]
        self.assertEqual(
            [
                EvidenceKind.EXPLICIT_USER_TEXT,
                EvidenceKind.DOCUMENT_CONTENT,
                EvidenceKind.ARTIFACT_FILE,
                EvidenceKind.TASK_DEPENDENCY_RESOLVED,
            ],
            kinds,
        )

    def test_extract_progress_categorizes_into_four_kinds(self):
        # AC-2: TASK_DEPENDENCY_RESOLVED -> NEXT_STEP; ARTIFACT_FILE -> COMPLETED;
        # DOCUMENT_CONTENT with blocker cue -> BLOCKER; text "next" -> NEXT_STEP;
        # text "pending" -> PENDING.
        inputs = (
            _ev_input(kind=EvidenceKind.TASK_DEPENDENCY_RESOLVED, source_ref="dep/t.0", text="dep finished"),
            _ev_input(kind=EvidenceKind.ARTIFACT_FILE, source_ref="out/x.bin", text="artifact", refs=(_ev_ref("out/x.bin", "artifact"),)),
            _ev_input(kind=EvidenceKind.DOCUMENT_CONTENT, source_ref="docs/c.md", text="we are blocked on infra"),
            _ev_input(kind=EvidenceKind.EXPLICIT_USER_TEXT, source_ref="fb/2", text="next: polish docs"),
            _ev_input(kind=EvidenceKind.EXPLICIT_USER_TEXT, source_ref="fb/3", text="pending review with eng"),
            _ev_input(kind=EvidenceKind.EXPLICIT_USER_TEXT, source_ref="fb/4", text="all done"),
        )
        cap = ProgressCaptureService.extract_progress(_ws(), inputs, now=NOW)
        actual_kinds = [item.kind for item in cap.progress_items]
        self.assertEqual(
            [
                ProgressItemKind.NEXT_STEP,
                ProgressItemKind.COMPLETED,
                ProgressItemKind.BLOCKER,
                ProgressItemKind.NEXT_STEP,
                ProgressItemKind.PENDING,
                ProgressItemKind.COMPLETED,
            ],
            actual_kinds,
        )

    def test_extract_progress_links_evidence_refs_per_item(self):
        # AC-3
        ref_a = _ev_ref("docs/a.md")
        ref_b = _ev_ref("out/x.bin", "artifact")
        inputs = (
            _ev_input(refs=(ref_a,)),
            _ev_input(kind=EvidenceKind.ARTIFACT_FILE, source_ref="out/x.bin", text="done", refs=(ref_b,)),
        )
        cap = ProgressCaptureService.extract_progress(_ws(), inputs, now=NOW)
        for item in cap.progress_items:
            self.assertGreaterEqual(len(item.evidence_refs), 1)
            for ref in item.evidence_refs:
                self.assertIsInstance(ref, EvidenceRef)
                self.assertEqual(64, len(ref.digest_hex))

    def test_extract_progress_requires_source_kind_and_confidence_in_range(self):
        # AC-4
        # confidence out of range
        with self.assertRaises(ProgressCaptureValidationError):
            _ev_input(confidence=1.5)
        with self.assertRaises(ProgressCaptureValidationError):
            _ev_input(confidence=-0.1)
        # bool is not a number
        with self.assertRaises(ProgressCaptureValidationError):
            _ev_input(confidence=True)  # type: ignore[arg-type]

    def test_extract_progress_rejects_file_mtime_only_evidence(self):
        # AC-7: kind must be in the closed set; a bogus kind value must fail.
        ev = _ev_input()
        # Simulate a caller that bypasses the enum (e.g. a future field).
        with self.assertRaises(ProgressCaptureValidationError):
            EvidenceInput(
                task_id="t.1",
                kind="file_mtime_only",  # type: ignore[arg-type]
                source_ref="docs/x.md",
                text="",
                confidence=0.5,
                evidence_refs=(_ev_ref(),),
            )

    def test_extract_progress_rejects_traversing_evidence_path(self):
        # Traversal check happens at EvidenceRef construction (fail-closed).
        with self.assertRaises(ProgressCaptureValidationError):
            EvidenceRef(
                path="../escape.md",
                role="document",
                media_type="text/markdown",
                digest_hex=GOOD_DIGEST,
                size_bytes=1,
            )
        with self.assertRaises(ProgressCaptureValidationError):
            EvidenceRef(
                path="/abs/escape.md",
                role="document",
                media_type="text/markdown",
                digest_hex=GOOD_DIGEST,
                size_bytes=1,
            )

    def test_extract_progress_rejects_empty_evidence_refs(self):
        with self.assertRaises(ProgressCaptureValidationError):
            EvidenceInput(
                task_id="t.1",
                kind=EvidenceKind.DOCUMENT_CONTENT,
                source_ref="docs/a.md",
                text="x",
                confidence=0.5,
                evidence_refs=(),
            )

    def test_extract_progress_rejects_non_workspace(self):
        with self.assertRaises(ProgressCaptureValidationError):
            ProgressCaptureService.extract_progress(
                "not-a-workspace",  # type: ignore[arg-type]
                (_ev_input(),),
                now=NOW,
            )

    def test_extract_progress_rejects_non_iso_now(self):
        with self.assertRaises(ProgressCaptureValidationError):
            ProgressCaptureService.extract_progress(_ws(), (_ev_input(),), now="2026/08/22 00:00:00")

    def test_empty_inputs_produces_empty_capture_with_user_confirmation_required(self):
        # AC-1 boundary: empty inputs -> empty capture, still confirmation required.
        cap = ProgressCaptureService.extract_progress(_ws(), (), now=NOW)
        self.assertEqual(0, len(cap.progress_items))
        self.assertTrue(cap.requires_user_confirmation)
        self.assertFalse(cap.formally_accepted)
        self.assertEqual(_ws(), cap.workspace)

    def test_pure_function_determinism_same_input_same_capture_id(self):
        a = ProgressCaptureService.extract_progress(_ws(), (_ev_input(),), now=NOW)
        b = ProgressCaptureService.extract_progress(_ws(), (_ev_input(),), now=NOW)
        self.assertEqual(a.capture_id, b.capture_id)
        self.assertEqual(a, b)


class ProgressCaptureGateTests(unittest.TestCase):
    """AC-6: requires_user_confirmation is forced; formally_accepted only via accept()."""

    def setUp(self):
        self.cap = ProgressCaptureService.extract_progress(
            _ws(), (_ev_input(),), now=NOW
        )

    def test_default_capture_requires_user_confirmation(self):
        self.assertTrue(self.cap.requires_user_confirmation)
        self.assertFalse(self.cap.formally_accepted)

    def test_constructing_with_confirmation_false_is_rejected(self):
        with self.assertRaises(ProgressCaptureValidationError):
            dataclasses.replace(self.cap, requires_user_confirmation=False)

    def test_constructing_with_accepted_without_metadata_is_rejected(self):
        with self.assertRaises(ProgressCaptureValidationError):
            dataclasses.replace(self.cap, formally_accepted=True)

    def test_accept_sets_formally_accepted_and_recorded(self):
        acc = ProgressCaptureService.accept(
            self.cap, accepted_by="u.alice", now=NOW2
        )
        self.assertTrue(acc.formally_accepted)
        self.assertEqual(NOW2, acc.accepted_at)
        self.assertEqual("u.alice", acc.accepted_by)
        # Per-item status becomes ACCEPTED for PROPOSED items.
        for item in acc.progress_items:
            self.assertEqual(ProgressItemStatus.ACCEPTED, item.status)

    def test_accept_again_is_conflict(self):
        acc = ProgressCaptureService.accept(self.cap, accepted_by="u.alice", now=NOW2)
        with self.assertRaises(ProgressCaptureConflictError):
            ProgressCaptureService.accept(acc, accepted_by="u.alice", now=NOW3)

    def test_revise_on_formally_accepted_is_conflict(self):
        # AC-6: an accepted capture is final; further edits require a new
        # capture. revise() must refuse, not silently regress acceptance.
        acc = ProgressCaptureService.accept(self.cap, accepted_by="u.alice", now=NOW2)
        target = acc.progress_items[0].item_id
        with self.assertRaises(ProgressCaptureConflictError):
            ProgressCaptureService.revise(
                acc, target, new_text="updated", reason="x", now=NOW3,
            )

    def test_revise_appends_override_chain(self):
        # Multiple revises on the same item chain overrides without losing them.
        target = self.cap.progress_items[0].item_id
        r1 = ProgressCaptureService.revise(self.cap, target, new_text="v2", reason="r1", now=NOW2)
        r2 = ProgressCaptureService.revise(r1, target, new_kind=ProgressItemKind.PENDING, reason="r2", now=NOW3)
        item = next(i for i in r2.progress_items if i.item_id == target)
        self.assertEqual(2, len(item.overrides))
        self.assertEqual("v2", item.text)
        self.assertEqual(ProgressItemKind.PENDING, item.kind)
        self.assertEqual(ProgressItemStatus.REVISED, item.status)


class ReviseRejectTests(unittest.TestCase):
    """AC-5: revise and reject return new captures with overrides recorded."""

    def setUp(self):
        self.cap = ProgressCaptureService.extract_progress(
            _ws(),
            (
                _ev_input(text="original draft", task_id="t.1"),
                _ev_input(text="second item", task_id="t.2", source_ref="docs/b.md"),
            ),
            now=NOW,
        )

    def test_revise_replaces_text_and_records_overrides(self):
        target = self.cap.progress_items[0].item_id
        revised = ProgressCaptureService.revise(
            self.cap,
            target,
            new_text="updated text",
            reason="wording fix",
            now=NOW2,
        )
        self.assertNotEqual(revised, self.cap)
        new_item = next(i for i in revised.progress_items if i.item_id == target)
        self.assertEqual("updated text", new_item.text)
        self.assertEqual(ProgressItemStatus.REVISED, new_item.status)
        self.assertEqual(1, len(new_item.overrides))
        self.assertEqual("text", new_item.overrides[0].target_path)
        self.assertEqual("original draft", new_item.overrides[0].original_value)
        self.assertEqual("updated text", new_item.overrides[0].edited_value)
        self.assertEqual("wording fix", new_item.overrides[0].reason)

    def test_revise_requires_at_least_one_field(self):
        target = self.cap.progress_items[0].item_id
        with self.assertRaises(ProgressCaptureValidationError):
            ProgressCaptureService.revise(
                self.cap, target, reason="noop", now=NOW2
            )

    def test_revise_unknown_item_is_rejected(self):
        with self.assertRaises(ProgressCaptureValidationError):
            ProgressCaptureService.revise(
                self.cap, "pc.NOPE", new_text="x", reason="x", now=NOW2
            )

    def test_reject_marks_status_and_removes_from_report_draft(self):
        target = self.cap.progress_items[1].item_id
        rejected = ProgressCaptureService.reject(
            self.cap, target, reason="not relevant", now=NOW2
        )
        new_item = next(i for i in rejected.progress_items if i.item_id == target)
        self.assertEqual(ProgressItemStatus.REJECTED, new_item.status)
        self.assertEqual(1, len(new_item.overrides))
        self.assertEqual("status", new_item.overrides[0].target_path)
        # Acceptance is still required for to_report_draft; build it now.
        acc = ProgressCaptureService.accept(rejected, accepted_by="u.alice", now=NOW3)
        draft = ProgressCaptureService.to_report_draft(acc)
        self.assertNotIn(target, draft.source_progress_ids)
        self.assertNotIn(target, draft.completed_work)
        self.assertNotIn(target, draft.pending_work)

    def test_reject_twice_is_conflict(self):
        target = self.cap.progress_items[0].item_id
        rejected = ProgressCaptureService.reject(self.cap, target, reason="x", now=NOW2)
        with self.assertRaises(ProgressCaptureConflictError):
            ProgressCaptureService.reject(rejected, target, reason="x", now=NOW3)

    def test_revise_rejected_is_conflict(self):
        target = self.cap.progress_items[0].item_id
        rejected = ProgressCaptureService.reject(self.cap, target, reason="x", now=NOW2)
        with self.assertRaises(ProgressCaptureConflictError):
            ProgressCaptureService.revise(rejected, target, new_text="x", reason="x", now=NOW3)


class ReportDraftTests(unittest.TestCase):
    """AC-8: to_report_draft only after accept; bucketing is by ProgressItemKind."""

    def setUp(self):
        self.cap = ProgressCaptureService.extract_progress(
            _ws(),
            (
                _ev_input(text="done", task_id="t.1"),
                _ev_input(text="still in progress", task_id="t.1", source_ref="docs/b.md"),
                _ev_input(text="next: deploy", task_id="t.1", source_ref="fb/3"),
                _ev_input(text="blocked on infra", task_id="t.1", source_ref="docs/c.md"),
            ),
            now=NOW,
        )

    def test_to_report_draft_requires_formally_accepted(self):
        with self.assertRaises(ProgressCaptureConflictError):
            ProgressCaptureService.to_report_draft(self.cap)

    def test_to_report_draft_buckets_items_by_kind(self):
        acc = ProgressCaptureService.accept(self.cap, accepted_by="u.alice", now=NOW2)
        draft = ProgressCaptureService.to_report_draft(acc)
        self.assertIsInstance(draft, ProgressDraft)
        self.assertEqual(1, len(draft.completed_work))
        self.assertEqual(1, len(draft.pending_work))
        self.assertEqual(1, len(draft.next_steps))
        self.assertEqual(1, len(draft.blockers))
        # Every segment entry must reference an actual item_id.
        all_segment_ids = (
            draft.completed_work
            + draft.pending_work
            + draft.next_steps
            + draft.blockers
        )
        self.assertEqual(4, len(all_segment_ids))
        self.assertEqual(set(draft.source_progress_ids), set(all_segment_ids))


class AuditProjectionTests(unittest.TestCase):
    """Mirrors US-11/12/13: exclude sensitive text and override reasons."""

    def test_to_audit_record_excludes_sensitive_text(self):
        cap = ProgressCaptureService.extract_progress(
            _ws(),
            (_ev_input(text="secret project description"),),
            now=NOW,
        )
        acc = ProgressCaptureService.accept(cap, accepted_by="u.alice", now=NOW2)
        record = ProgressCaptureService.to_audit_record(acc)
        # Round-trip JSON safety.
        self.assertEqual(record, json.loads(json.dumps(record)))
        # Sensitive substrings must not appear anywhere in the audit record.
        serialized = json.dumps(record)
        self.assertNotIn("secret project description", serialized)
        # Counts are present.
        self.assertEqual(1, record["item_count"])
        item_summary = record["items"][0]
        self.assertNotIn("text", item_summary)
        self.assertNotIn("confidence", item_summary)
        self.assertIn("override_count", item_summary)
        # Metadata fields.
        self.assertEqual(SCHEMA_VERSION, record["schema_version"])
        self.assertEqual(DOMAIN, record["domain"])
        self.assertEqual("u.alice", record["accepted_by"])


if __name__ == "__main__":
    unittest.main()
