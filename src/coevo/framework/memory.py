"""US-16-AC-4: framework Memory abstraction (CTAF §6.2 / M3).

Unifies episodic and semantic memory writes behind one pure, fail-closed
model:

* ``MemoryRecord`` is a frozen, hashable record (EPISODIC / SEMANTIC);
* every episodic write must produce an audit projection (AC-4.2);
* semantic writes require an approval check that maps to the existing
  ``knowledge_base.ReviewDecisionKind.APPROVE`` semantics (AC-4.3);
* **L12**: sensitive fields are redacted by an injected :class:`Redactor`
  into a non-recoverable ``REDACTED:<sha256>`` digest before the record
  reaches any store — plaintext never crosses the write boundary (AC-4.4).

All persistence, approval and redaction IO is injected; injected exceptions
are treated as rejections.  L15: standard library only.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from src.coevo.framework.validation import is_iso_utc_z

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")

REDACTION_PREFIX = "REDACTED:"
MEMORY_PROJECTION_KEYS = frozenset(
    {
        "accepted",
        "record_id",
        "kind",
        "occurred_at",
        "failure_reason",
    }
)


class MemoryValidationError(Exception):
    """Raised when a memory record violates the framework invariants."""


class MemoryKind(Enum):
    """CTAF §6.2 memory categories."""

    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"


@dataclass(frozen=True)
class MemoryRecord:
    """A canonical, hashable memory record."""

    record_id: str
    kind: MemoryKind
    project_id: str
    occurred_at: str
    fields: tuple[tuple[str, str], ...]
    sensitive_fields: tuple[str, ...]
    source_ref: str = ""


@runtime_checkable
class Redactor(Protocol):
    """Converts plaintext into a non-recoverable digest (L12)."""

    def redact(self, value: str) -> str: ...


@runtime_checkable
class EpisodicMemoryStore(Protocol):
    """Episodic persistence (production adapter: ``progress_capture/``)."""

    def append(self, record: MemoryRecord) -> None: ...


@runtime_checkable
class SemanticApprovalChecker(Protocol):
    """Semantic approval gate (maps to ``ReviewDecisionKind.APPROVE``)."""

    def is_approved(self, record: MemoryRecord) -> bool: ...


@runtime_checkable
class SemanticMemoryStore(Protocol):
    """Semantic persistence (production adapter: ``knowledge_base/``)."""

    def ingest(self, record: MemoryRecord) -> None: ...


@dataclass(frozen=True)
class MemoryWriteResult:
    accepted: bool
    record_id: str
    kind: MemoryKind
    occurred_at: str
    failure_reason: str | None

    def to_audit_record(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "record_id": self.record_id,
            "kind": self.kind.value
            if isinstance(self.kind, MemoryKind)
            else str(self.kind),
            "occurred_at": self.occurred_at,
            "failure_reason": self.failure_reason,
        }


def canonical_record_bytes(record: MemoryRecord) -> bytes:
    """Canonical JSON excluding the self-referential ``record_id``."""

    payload = {
        "kind": record.kind.value,
        "project_id": record.project_id,
        "occurred_at": record.occurred_at,
        "fields": list(record.fields),
        "sensitive_fields": list(record.sensitive_fields),
        "source_ref": record.source_ref,
    }
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def record_fingerprint(record: MemoryRecord) -> str:
    return hashlib.sha256(canonical_record_bytes(record)).hexdigest()


def _is_redaction_digest(value: str) -> bool:
    return value.startswith(REDACTION_PREFIX) and bool(_HEX64.match(value[len(REDACTION_PREFIX) :]))


def validate_record(record: MemoryRecord) -> None:
    """Structural validation (pure, fail-closed)."""

    if not isinstance(record, MemoryRecord):
        raise MemoryValidationError("record must be a MemoryRecord instance")
    if not isinstance(record.kind, MemoryKind):
        raise MemoryValidationError("kind must be a MemoryKind member")
    if not _HEX64.match(record.record_id):
        raise MemoryValidationError("record_id must be a 64-hex fingerprint")
    if record.record_id != record_fingerprint(record):
        raise MemoryValidationError("record_id does not match the record fingerprint")
    if not _SAFE_ID.match(record.project_id):
        raise MemoryValidationError("project_id must be a safe-id")
    if not is_iso_utc_z(record.occurred_at):
        raise MemoryValidationError(
            "occurred_at must be ISO-8601 UTC with trailing Z (L7)"
        )
    if not isinstance(record.fields, tuple) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in record.fields
    ):
        raise MemoryValidationError("fields must be a tuple of (str, str) pairs")
    if not isinstance(record.sensitive_fields, tuple) or not all(
        isinstance(item, str) for item in record.sensitive_fields
    ):
        raise MemoryValidationError("sensitive_fields must be a tuple of strings")
    if not isinstance(record.source_ref, str):
        raise MemoryValidationError("source_ref must be a string")


def redact_record(record: MemoryRecord, redactor: Redactor) -> MemoryRecord:
    """Return a copy whose sensitive fields are redaction digests (L12)."""

    sensitive = set(record.sensitive_fields)
    unknown_redactions = [
        key
        for key, value in record.fields
        if _is_redaction_digest(value) and key not in sensitive
    ]
    if unknown_redactions:
        raise MemoryValidationError(
            "redacted value present for a non-sensitive field: "
            + ", ".join(unknown_redactions)
        )
    new_fields: list[tuple[str, str]] = []
    for key, value in record.fields:
        if key in sensitive and not _is_redaction_digest(value):
            try:
                value = redactor.redact(value)
            except Exception as exc:  # noqa: BLE001 - injected redactor fails closed
                raise MemoryValidationError(
                    f"redaction failed for field {key!r}: {type(exc).__name__}"
                ) from exc
            if not _is_redaction_digest(value):
                raise MemoryValidationError(
                    f"redactor produced a non-digest value for field {key!r}"
                )
        new_fields.append((key, value))
    redacted = MemoryRecord(
        record_id="0" * 64,
        kind=record.kind,
        project_id=record.project_id,
        occurred_at=record.occurred_at,
        fields=tuple(new_fields),
        sensitive_fields=record.sensitive_fields,
        source_ref=record.source_ref,
    )
    return MemoryRecord(
        record_id=record_fingerprint(redacted),
        kind=redacted.kind,
        project_id=redacted.project_id,
        occurred_at=redacted.occurred_at,
        fields=redacted.fields,
        sensitive_fields=redacted.sensitive_fields,
        source_ref=redacted.source_ref,
    )


def write_memory(
    record: MemoryRecord,
    *,
    redactor: Redactor,
    episodic_store: EpisodicMemoryStore | None = None,
    semantic_store: SemanticMemoryStore | None = None,
    approval_checker: SemanticApprovalChecker | None = None,
) -> MemoryWriteResult:
    """Validate, redact, approve (semantic) and persist (fail-closed)."""

    def reject(reason: str) -> MemoryWriteResult:
        return MemoryWriteResult(
            accepted=False,
            record_id=record.record_id if isinstance(record, MemoryRecord) else "",
            kind=record.kind if isinstance(record, MemoryRecord) else MemoryKind.EPISODIC,
            occurred_at=record.occurred_at if isinstance(record, MemoryRecord) else "",
            failure_reason=reason,
        )

    try:
        validate_record(record)
        redacted = redact_record(record, redactor)
        if record.kind is MemoryKind.EPISODIC:
            if episodic_store is None:
                return reject("episodic write requires an episodic store")
            episodic_store.append(redacted)
        elif record.kind is MemoryKind.SEMANTIC:
            if semantic_store is None or approval_checker is None:
                return reject("semantic write requires a semantic store and approval checker")
            try:
                approved = approval_checker.is_approved(record)
            except Exception as exc:  # noqa: BLE001 - injected checker fails closed
                return reject(f"semantic approval check failed: {type(exc).__name__}")
            if not approved:
                return reject("semantic write rejected: not approved (ReviewDecisionKind.APPROVE)")
            semantic_store.ingest(redacted)
        else:
            return reject(f"unsupported memory kind: {record.kind!r}")
    except MemoryValidationError as exc:
        return reject(str(exc))
    except Exception as exc:  # noqa: BLE001 - injected stores fail closed
        return reject(f"memory write failed: {type(exc).__name__}")
    return MemoryWriteResult(
        accepted=True,
        record_id=redacted.record_id,
        kind=redacted.kind,
        occurred_at=redacted.occurred_at,
        failure_reason=None,
    )
