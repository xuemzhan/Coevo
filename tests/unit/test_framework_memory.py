"""US-16-AC-4: framework Memory abstraction tests (AC-4.1..4.5)."""

from __future__ import annotations

import ast
import hashlib
import sys
import unittest
from pathlib import Path

from src.coevo.framework.memory import (
    MEMORY_PROJECTION_KEYS,
    MemoryKind,
    MemoryRecord,
    MemoryValidationError,
    REDACTION_PREFIX,
    record_fingerprint,
    redact_record,
    validate_record,
    write_memory,
)

ROOT = Path(__file__).resolve().parents[2]


def digest(value: str) -> str:
    return REDACTION_PREFIX + hashlib.sha256(value.encode("utf-8")).hexdigest()


class _DigestRedactor:
    def redact(self, value: str) -> str:
        return digest(value)


class _BrokenRedactor:
    def redact(self, value: str) -> str:
        return "not-a-digest"


class _RaisingRedactor:
    def redact(self, value: str) -> str:
        raise RuntimeError("redactor down")


class _RecordingEpisodicStore:
    def __init__(self) -> None:
        self.records: list[MemoryRecord] = []

    def append(self, record: MemoryRecord) -> None:
        self.records.append(record)


class _BoomEpisodicStore:
    def append(self, record: MemoryRecord) -> None:
        raise RuntimeError("store down")


class _Approval:
    def __init__(self, approved: bool = True) -> None:
        self.approved = approved

    def is_approved(self, record: MemoryRecord) -> bool:
        return self.approved


class _BoomApproval(_Approval):
    def is_approved(self, record: MemoryRecord) -> bool:
        raise RuntimeError("approval down")


class _RecordingSemanticStore:
    def __init__(self) -> None:
        self.records: list[MemoryRecord] = []

    def ingest(self, record: MemoryRecord) -> None:
        self.records.append(record)


def make_record(
    *,
    kind: MemoryKind = MemoryKind.EPISODIC,
    fields: tuple[tuple[str, str], ...] = (("status", "done"), ("member_name", "Alice")),
    sensitive: tuple[str, ...] = ("member_name",),
    record_id: str | None = None,
) -> MemoryRecord:
    record = MemoryRecord(
        record_id="0" * 64,
        kind=kind,
        project_id="PRJ001",
        occurred_at="2026-08-08T08:00:00Z",
        fields=fields,
        sensitive_fields=sensitive,
        source_ref="unit.test",
    )
    if record_id is None:
        record = MemoryRecord(
            record_id=record_fingerprint(record),
            kind=record.kind,
            project_id=record.project_id,
            occurred_at=record.occurred_at,
            fields=record.fields,
            sensitive_fields=record.sensitive_fields,
            source_ref=record.source_ref,
        )
    else:
        record = MemoryRecord(
            record_id=record_id,
            kind=record.kind,
            project_id=record.project_id,
            occurred_at=record.occurred_at,
            fields=record.fields,
            sensitive_fields=record.sensitive_fields,
            source_ref=record.source_ref,
        )
    return record


class MemoryTests(unittest.TestCase):
    def test_record_fingerprint_hashability(self) -> None:
        """AC-4.1: record_id is a canonical fingerprint."""

        record = make_record()
        self.assertEqual(record.record_id, record_fingerprint(record))
        validate_record(record)
        with self.assertRaises(MemoryValidationError):
            validate_record(make_record(record_id="a" * 64))

    def test_kind_and_safe_id_validation(self) -> None:
        bad_kind = MemoryRecord(
            record_id="0" * 64,
            kind="EPISODIC",  # type: ignore[arg-type]
            project_id="PRJ001",
            occurred_at="2026-08-08T08:00:00Z",
            fields=(),
            sensitive_fields=(),
        )
        with self.assertRaises(MemoryValidationError):
            validate_record(bad_kind)
        bad_project = MemoryRecord(
            record_id=record_fingerprint(
                MemoryRecord(
                    record_id="0" * 64,
                    kind=MemoryKind.EPISODIC,
                    project_id="../escape",
                    occurred_at="2026-08-08T08:00:00Z",
                    fields=(),
                    sensitive_fields=(),
                )
            ),
            kind=MemoryKind.EPISODIC,
            project_id="../escape",
            occurred_at="2026-08-08T08:00:00Z",
            fields=(),
            sensitive_fields=(),
        )
        with self.assertRaises(MemoryValidationError):
            validate_record(bad_project)

    def test_episodic_write_audit_and_store(self) -> None:
        """AC-4.2: audit projection is mandatory; injected store is used."""

        store = _RecordingEpisodicStore()
        result = write_memory(
            make_record(),
            redactor=_DigestRedactor(),
            episodic_store=store,
        )
        self.assertTrue(result.accepted, result.failure_reason)
        self.assertEqual(len(store.records), 1)
        persisted = store.records[0]
        # L12: plaintext never reaches the store.
        persisted_fields = dict(persisted.fields)
        self.assertEqual(persisted_fields["member_name"], digest("Alice"))
        record = result.to_audit_record()
        self.assertEqual(set(record), set(MEMORY_PROJECTION_KEYS))
        self.assertTrue(record["accepted"])

    def test_episodic_store_exception_fails_closed(self) -> None:
        result = write_memory(
            make_record(),
            redactor=_DigestRedactor(),
            episodic_store=_BoomEpisodicStore(),
        )
        self.assertFalse(result.accepted)
        self.assertIn("memory write failed", result.failure_reason or "")

    def test_semantic_requires_approval(self) -> None:
        """AC-4.3: semantic write requires approval (ReviewDecisionKind.APPROVE)."""

        store = _RecordingSemanticStore()
        denied = write_memory(
            make_record(kind=MemoryKind.SEMANTIC),
            redactor=_DigestRedactor(),
            semantic_store=store,
            approval_checker=_Approval(False),
        )
        self.assertFalse(denied.accepted)
        self.assertIn("not approved", denied.failure_reason or "")
        self.assertEqual(store.records, [])

        store = _RecordingSemanticStore()
        ok = write_memory(
            make_record(kind=MemoryKind.SEMANTIC),
            redactor=_DigestRedactor(),
            semantic_store=store,
            approval_checker=_Approval(True),
        )
        self.assertTrue(ok.accepted, ok.failure_reason)
        self.assertEqual(len(store.records), 1)

    def test_semantic_missing_store_or_checker_rejected(self) -> None:
        result = write_memory(
            make_record(kind=MemoryKind.SEMANTIC),
            redactor=_DigestRedactor(),
            semantic_store=_RecordingSemanticStore(),
        )
        self.assertFalse(result.accepted)
        result = write_memory(
            make_record(kind=MemoryKind.SEMANTIC),
            redactor=_DigestRedactor(),
            approval_checker=_Approval(True),
        )
        self.assertFalse(result.accepted)

    def test_semantic_approval_exception_fails_closed(self) -> None:
        result = write_memory(
            make_record(kind=MemoryKind.SEMANTIC),
            redactor=_DigestRedactor(),
            semantic_store=_RecordingSemanticStore(),
            approval_checker=_BoomApproval(),
        )
        self.assertFalse(result.accepted)
        self.assertIn("approval check failed", result.failure_reason or "")

    def test_l12_redaction_produces_digest_only(self) -> None:
        """AC-4.4 (L12): sensitive fields are non-recoverable digests."""

        redacted = redact_record(make_record(), _DigestRedactor())
        fields = dict(redacted.fields)
        self.assertTrue(fields["member_name"].startswith(REDACTION_PREFIX))
        self.assertNotIn("Alice", str(redacted.fields))

    def test_l12_redactor_exception_fails_closed(self) -> None:
        result = write_memory(
            make_record(),
            redactor=_RaisingRedactor(),
            episodic_store=_RecordingEpisodicStore(),
        )
        self.assertFalse(result.accepted)
        self.assertIn("redaction failed", result.failure_reason or "")

    def test_l12_redactor_non_digest_rejected(self) -> None:
        result = write_memory(
            make_record(),
            redactor=_BrokenRedactor(),
            episodic_store=_RecordingEpisodicStore(),
        )
        self.assertFalse(result.accepted)
        self.assertIn("non-digest", result.failure_reason or "")

    def test_redaction_on_non_sensitive_field_rejected(self) -> None:
        record = make_record(
            fields=(("status", digest("done")),),
            sensitive=(),
        )
        with self.assertRaises(MemoryValidationError):
            redact_record(record, _DigestRedactor())

    def test_already_redacted_value_kept(self) -> None:
        record = make_record(fields=(("member_name", digest("Alice")),))
        redacted = redact_record(record, _DigestRedactor())
        self.assertEqual(dict(redacted.fields)["member_name"], digest("Alice"))

    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "memory.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        allowed = set(sys.stdlib_module_names) | {"src"}
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] not in allowed:
                        bad.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    continue
                if node.module and node.module.split(".")[0] not in allowed:
                    bad.append(node.module)
        self.assertEqual([], bad, "third-party imports found in memory.py")


if __name__ == "__main__":
    unittest.main()
