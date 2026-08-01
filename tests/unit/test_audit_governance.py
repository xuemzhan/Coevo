"""Tests for US-15-AC-1 security audit governance facade.

Covers AC-1, AC-5, AC-6 (the ACs that this slice actually implements;
AC-2/AC-3/AC-4/AC-7/AC-8 are covered by prior slices US-5/6/0/10 and
are out of scope here). Pure-function tests, no IO.
"""
from __future__ import annotations

import dataclasses
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.audit_governance import (
    AuditEvent,
    AuditEventResult,
    AuditEventSource,
    AuditEventValidationError,
    AuditExportFormat,
    AuditExportPayload,
    AuditGovernanceError,
    AuditQuery,
    AuditQueryResult,
    AuditQueryValidationError,
    InterceptionDecision,
    InterceptionReason,
    SecurityAuditFacade,
)

NOW = "2026-08-22T00:00:00Z"
NOW2 = "2026-08-22T00:05:00Z"
NOW3 = "2026-08-22T00:10:00Z"

GOOD_DIGEST = "a" * 64


def _ev(
    *,
    ts: str = NOW,
    actor: str = "u.alice",
    source: AuditEventSource = AuditEventSource.IMPORT,
    action: str = "import",
    project_id: str = "PRJ001",
    task_id: str = "t.1",
    result: AuditEventResult = AuditEventResult.OK,
    tool: str = "PackageImportService",
    fingerprint: str = "",
    record_hash: str = "",
) -> AuditEvent:
    return AuditEvent(
        ts=ts,
        actor=actor,
        source=source,
        action=action,
        project_id=project_id,
        task_id=task_id,
        result=result,
        tool=tool,
        fingerprint=fingerprint,
        record_hash=record_hash,
    )


def _record(**overrides) -> dict:
    base = {
        "ts": NOW,
        "actor": "u.alice",
        "result": "ok",
        "action": "import",
        "project_id": "PRJ001",
        "task_id": "t.1",
        "tool": "PackageImportService",
    }
    base.update(overrides)
    return base


class AuditEventTests(unittest.TestCase):
    """AC-5: AuditEvent enforces ts/actor/action/result fields."""

    def test_audit_event_from_valid_record_succeeds(self):
        ev = AuditEvent.from_audit_record(_record(), source=AuditEventSource.IMPORT)
        self.assertEqual(NOW, ev.ts)
        self.assertEqual("u.alice", ev.actor)
        self.assertEqual("import", ev.action)
        self.assertEqual(AuditEventResult.OK, ev.result)

    def test_audit_event_from_missing_field_is_rejected(self):
        for missing in ("ts", "actor", "action", "result"):
            r = _record()
            del r[missing]
            with self.assertRaises(AuditEventValidationError):
                AuditEvent.from_audit_record(r, source=AuditEventSource.IMPORT)

    def test_audit_event_from_bad_timestamp_is_rejected(self):
        with self.assertRaises(AuditEventValidationError):
            AuditEvent.from_audit_record(
                _record(ts="2026/08/22 00:00:00"),
                source=AuditEventSource.IMPORT,
            )

    def test_audit_event_from_unknown_result_is_rejected(self):
        with self.assertRaises(AuditEventValidationError):
            AuditEvent.from_audit_record(
                _record(result="maybe"), source=AuditEventSource.IMPORT
            )

    def test_audit_event_ignores_unknown_keys(self):
        ev = AuditEvent.from_audit_record(
            _record(some_extra="ignored"),
            source=AuditEventSource.MERGE,
        )
        # unknown keys are silently dropped -- the projection is forward-compatible
        self.assertEqual(AuditEventSource.MERGE, ev.source)

    def test_audit_event_direct_construction_rejects_non_iso_ts(self):
        with self.assertRaises(AuditEventValidationError):
            AuditEvent(
                ts="not-iso",
                actor="u.alice",
                source=AuditEventSource.IMPORT,
                action="import",
                project_id="PRJ001",
                task_id="t.1",
                result=AuditEventResult.OK,
                tool="x",
            )


class InterceptionTests(unittest.TestCase):
    """AC-1: five interception reasons, centralized decision."""

    def _eval(self, **overrides) -> InterceptionDecision:
        base = dict(
            package_id="pkg.001",
            envelope_status="ok",
            signature_status="ok",
            expiration_ts="",
            now=NOW,
            replay_status="ok",
            envelope_recipient_cert_id="CERT-X",
            expected_recipient_cert_id="CERT-X",
        )
        base.update(overrides)
        return SecurityAuditFacade.evaluate_interception(**base)

    def test_clean_package_passes(self):
        d = self._eval()
        self.assertFalse(d.intercepted)
        self.assertEqual((), d.reasons)

    def test_corrupted_envelope_intercepts(self):
        d = self._eval(envelope_status="corrupted")
        self.assertTrue(d.intercepted)
        self.assertIn(InterceptionReason.CORRUPTED, d.reasons)
        self.assertIn("envelope corrupted", d.detail)

    def test_tampered_signature_intercepts(self):
        d = self._eval(signature_status="invalid")
        self.assertTrue(d.intercepted)
        self.assertIn(InterceptionReason.TAMPERED, d.reasons)
        self.assertNotIn(InterceptionReason.CORRUPTED, d.reasons)
        self.assertIn("signature invalid", d.detail)

    def test_corrupted_short_circuits_tampered(self):
        # When envelope is fully corrupted, signature verification is not
        # independently meaningful -- only CORRUPTED is reported.
        d = self._eval(envelope_status="corrupted", signature_status="invalid")
        self.assertIn(InterceptionReason.CORRUPTED, d.reasons)
        self.assertNotIn(InterceptionReason.TAMPERED, d.reasons)

    def test_expired_package_intercepts(self):
        d = self._eval(expiration_ts="2026-08-21T00:00:00Z")
        self.assertTrue(d.intercepted)
        self.assertIn(InterceptionReason.EXPIRED, d.reasons)

    def test_not_yet_expired_passes(self):
        d = self._eval(expiration_ts="2026-08-22T23:59:59Z")
        self.assertNotIn(InterceptionReason.EXPIRED, d.reasons)

    def test_duplicate_replay_intercepts(self):
        d = self._eval(replay_status="duplicate")
        self.assertTrue(d.intercepted)
        self.assertIn(InterceptionReason.DUPLICATE, d.reasons)

    def test_recipient_mismatch_intercepts(self):
        d = self._eval(
            envelope_recipient_cert_id="CERT-X",
            expected_recipient_cert_id="CERT-Y",
        )
        self.assertTrue(d.intercepted)
        self.assertIn(InterceptionReason.RECIPIENT_MISMATCH, d.reasons)

    def test_multiple_reasons_are_listed(self):
        d = self._eval(
            signature_status="invalid",
            expiration_ts="2026-08-21T00:00:00Z",
            replay_status="duplicate",
            envelope_recipient_cert_id="CERT-X",
            expected_recipient_cert_id="CERT-Y",
        )
        self.assertTrue(d.intercepted)
        self.assertEqual(
            {
                InterceptionReason.TAMPERED,
                InterceptionReason.EXPIRED,
                InterceptionReason.DUPLICATE,
                InterceptionReason.RECIPIENT_MISMATCH,
            },
            set(d.reasons),
        )
        # detail lists all four
        self.assertIn("signature invalid", d.detail)
        self.assertIn("expired at", d.detail)
        self.assertIn("replay detected", d.detail)
        self.assertIn("recipient mismatch", d.detail)

    def test_interception_input_validation(self):
        for bad in [
            dict(package_id=".."),  # not safe-id
            dict(envelope_status=""),  # empty
            dict(signature_status=None),  # wrong type
            dict(now="2026/08/22 00:00:00"),  # bad format
            dict(expiration_ts="not-iso"),
            dict(envelope_recipient_cert_id=".."),  # not safe-id
            dict(expected_recipient_cert_id=""),
        ]:
            with self.assertRaises(AuditEventValidationError):
                self._eval(**bad)


class QueryTests(unittest.TestCase):
    """AC-6: query_events with multi-field filters + pagination."""

    def setUp(self):
        self.events = (
            _ev(record_hash="h1", actor="u.alice", action="import", source=AuditEventSource.IMPORT),
            _ev(record_hash="h2", actor="u.bob", action="merge", source=AuditEventSource.MERGE, project_id="PRJ002"),
            _ev(record_hash="h3", actor="u.alice", action="approve", source=AuditEventSource.APPROVAL),
            _ev(record_hash="h4", actor="u.alice", action="import", source=AuditEventSource.IMPORT, result=AuditEventResult.FAILED),
            _ev(record_hash="h5", actor="u.alice", action="schedule", source=AuditEventSource.SCHEDULE),
        )

    def test_query_filters_by_actor(self):
        q = AuditQuery(actor="u.alice")
        result = SecurityAuditFacade.query_events(self.events, q)
        self.assertEqual(4, len(result.events))
        self.assertTrue(all(e.actor == "u.alice" for e in result.events))

    def test_query_filters_by_project_id(self):
        q = AuditQuery(project_id="PRJ002")
        result = SecurityAuditFacade.query_events(self.events, q)
        self.assertEqual(1, len(result.events))
        self.assertEqual("h2", result.events[0].record_hash)

    def test_query_filters_by_result(self):
        q = AuditQuery(result=AuditEventResult.FAILED)
        result = SecurityAuditFacade.query_events(self.events, q)
        self.assertEqual(1, len(result.events))
        self.assertEqual("h4", result.events[0].record_hash)

    def test_query_filters_by_source(self):
        q = AuditQuery(source=AuditEventSource.IMPORT)
        result = SecurityAuditFacade.query_events(self.events, q)
        self.assertEqual(2, len(result.events))

    def test_query_combines_filters(self):
        q = AuditQuery(actor="u.alice", source=AuditEventSource.IMPORT, result=AuditEventResult.FAILED)
        result = SecurityAuditFacade.query_events(self.events, q)
        self.assertEqual(1, len(result.events))
        self.assertEqual("h4", result.events[0].record_hash)

    def test_query_limit_and_cursor_paginate(self):
        q1 = AuditQuery(actor="u.alice", limit=2)
        r1 = SecurityAuditFacade.query_events(self.events, q1)
        self.assertEqual(2, len(r1.events))
        self.assertEqual("h1", r1.events[0].record_hash)
        self.assertEqual("h3", r1.events[1].record_hash)
        self.assertEqual("h3", r1.cursor_next)
        # Next page starts AFTER cursor.
        q2 = AuditQuery(actor="u.alice", limit=2, cursor=r1.cursor_next)
        r2 = SecurityAuditFacade.query_events(self.events, q2)
        self.assertEqual(2, len(r2.events))
        self.assertEqual("h4", r2.events[0].record_hash)
        self.assertEqual("h5", r2.events[1].record_hash)
        # Last page: cursor_next is empty (fewer than limit).
        q3 = AuditQuery(actor="u.alice", limit=10, cursor=r2.cursor_next)
        r3 = SecurityAuditFacade.query_events(self.events, q3)
        self.assertEqual(0, len(r3.events))
        self.assertEqual("", r3.cursor_next)

    def test_query_limit_hard_cap_rejected(self):
        with self.assertRaises(AuditQueryValidationError):
            AuditQuery(limit=10_001)
        with self.assertRaises(AuditQueryValidationError):
            AuditQuery(limit=0)
        with self.assertRaises(AuditQueryValidationError):
            AuditQuery(limit=-5)

    def test_query_ts_range_validated(self):
        with self.assertRaises(AuditQueryValidationError):
            AuditQuery(ts_from="not-iso")
        with self.assertRaises(AuditQueryValidationError):
            AuditQuery(ts_from=NOW2, ts_to=NOW)


class ExportTests(unittest.TestCase):
    """AC-6: export_events with content-stable digest."""

    def setUp(self):
        self.events = (
            _ev(record_hash="h1", actor="u.alice"),
            _ev(record_hash="h2", actor="u.bob", project_id="PRJ002"),
        )

    def test_export_jsonl_round_trip(self):
        payload = SecurityAuditFacade.export_events(
            self.events, fmt=AuditExportFormat.JSONL, now=NOW3
        )
        self.assertIsInstance(payload, AuditExportPayload)
        self.assertEqual(AuditExportFormat.JSONL, payload.format)
        self.assertEqual(2, payload.event_count)
        # Body: 2 lines + trailing newline.
        lines = payload.content.decode("utf-8").splitlines()
        self.assertEqual(2, len(lines))
        # Each line parses back to a row dict with the same shape.
        for line, event in zip(lines, self.events):
            row = json.loads(line)
            self.assertEqual(event.actor, row["actor"])
            self.assertEqual(event.ts, row["ts"])

    def test_export_json_array_round_trip(self):
        payload = SecurityAuditFacade.export_events(
            self.events, fmt=AuditExportFormat.JSON, now=NOW3
        )
        rows = json.loads(payload.content.decode("utf-8"))
        self.assertIsInstance(rows, list)
        self.assertEqual(2, len(rows))

    def test_export_digest_is_content_stable(self):
        a = SecurityAuditFacade.export_events(self.events, fmt=AuditExportFormat.JSONL, now=NOW3)
        b = SecurityAuditFacade.export_events(self.events, fmt=AuditExportFormat.JSONL, now=NOW3)
        self.assertEqual(a.digest_hex, b.digest_hex)
        self.assertEqual(a.content, b.content)
        # Different inputs produce different digests.
        c = SecurityAuditFacade.export_events(
            self.events + (_ev(record_hash="h3"),),
            fmt=AuditExportFormat.JSONL,
            now=NOW3,
        )
        self.assertNotEqual(a.digest_hex, c.digest_hex)

    def test_export_validates_inputs(self):
        with self.assertRaises(AuditEventValidationError):
            SecurityAuditFacade.export_events(self.events, fmt="csv", now=NOW3)  # type: ignore[arg-type]
        with self.assertRaises(AuditEventValidationError):
            SecurityAuditFacade.export_events(self.events, now="not-iso")


class AuditProjectionTests(unittest.TestCase):
    """to_audit_record on InterceptionDecision mirrors US-11/12/13/8."""

    def test_to_audit_record_excludes_sensitive_detail(self):
        d = SecurityAuditFacade.evaluate_interception(
            package_id="pkg.001",
            envelope_status="ok",
            signature_status="invalid",
            expiration_ts="",
            now=NOW,
            replay_status="ok",
            envelope_recipient_cert_id="CERT-X",
            expected_recipient_cert_id="CERT-X",
        )
        record = SecurityAuditFacade.to_audit_record(d)
        self.assertEqual(record, json.loads(json.dumps(record)))
        # detail text MUST NOT appear in the audit row; only detail_hash.
        serialized = json.dumps(record)
        self.assertNotIn("signature invalid", serialized)
        # reasons are kept as enum values; intercepted flag kept.
        self.assertTrue(record["intercepted"])
        self.assertEqual(["tampered"], record["reasons"])
        # metadata fields.
        self.assertEqual("pkg.001", record["package_id"])
        self.assertEqual(NOW, record["decided_at"])
        # 64-char lowercase hex for detail_hash.
        self.assertEqual(64, len(record["detail_hash"]))


if __name__ == "__main__":
    unittest.main()
