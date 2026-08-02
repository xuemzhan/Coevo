"""US-15 security audit governance facade (8 AC).

Scope
-----
Pure half of US-15: the *governance* layer above the existing audit
infrastructure (US-0 audit_anchor, US-5 atomic import, US-9/10/12/13
to_audit_record).

This module provides:

* :class:`AuditEvent` -- a uniform wrapper around the dict-shaped
  ``to_audit_record`` projection emitted by every business-side
  facade. Forces AC-5 fields (ts / actor / action / result /
  project_id / task_id) and tags the event with a closed
  :class:`AuditEventSource` enum so queries can filter by phase.
* :class:`SecurityAuditFacade` -- three pure-function entry points:
    - :meth:`evaluate_interception` -- centralizes AC-1's five
      interception reasons (CORRUPTED / TAMPERED / EXPIRED / DUPLICATE
      / RECIPIENT_MISMATCH). Returns an :class:`InterceptionDecision`.
    - :meth:`query_events` -- AC-6 query over an in-memory event list.
      Hard cap on limit (DoS guard). Cursor is the last returned
      event's record_hash; ``None`` means "no more pages".
    - :meth:`export_events` -- AC-6 export. Pure function: returns an
      :class:`AuditExportPayload` holding the bytes, content digest,
      event count, and exported_at timestamp. No IO.
* :func:`SecurityAuditFacade.to_audit_record` -- audit projection of an
  :class:`InterceptionDecision`. Mirrors US-11/12/13/8 by EXCLUDING
  free-form ``detail`` text and only keeping reason codes + flags.
  The decision itself becomes a single audit row.

AC mapping
----------
* AC-1 损坏/篡改/过期/重复/接收人不匹配拦截 -- evaluate_interception.
* AC-2 验签失败不初始化工作区或更新状态 -- NOT in this slice; US-5/6
  fail-closed covers AC-2 already.
* AC-3 全过程留痕 -- AuditEvent.from_audit_record normalizes the
  per-facade to_audit_record dicts into one shape; existing US-0/5/9
  /10/12/13 emitters are unchanged.
* AC-4 摘要链防篡改 -- NOT in this slice; US-0 audit_anchor + the
  full signing chain covers AC-4 already.
* AC-5 日志含时间/主体/项目/任务/动作/结果 -- AuditEvent enforces
  the AC-5 schema; missing fields raise.
* AC-6 安全管理员查询和导出 -- query_events + export_events +
  AuditQuery / AuditExportPayload data classes.
* AC-7 异常包不导致崩溃 -- NOT in this slice; US-5/6 fail-closed
  covers AC-7 already.
* AC-8 脚本/可执行/未授权类型不自动运行 -- NOT in this slice;
  protocol-layer ban + AGENTS.md §3 rule 4 covers AC-8 already.

Non-goals
---------
* No IO, no DB, no LLM, no scheduler.
* No mutation of any existing module's ``to_audit_record`` schema.
* No introduction of a new dependency.
"""
from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import re
from typing import Mapping

# safe-id: same alphabet as the rest of the codebase (US-2 / US-5 / US-8).
_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")

# ISO-8601 UTC 'Z' -- strict format used everywhere else (US-8 / US-9 / US-13).
_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")

# Result codes that mirror what audit_log.py's append_record already uses,
# plus the explicit "blocked" code introduced for AC-1 interception.
_AUDIT_RESULT_CODES: frozenset[str] = frozenset({"ok", "rejected", "failed", "blocked"})

# Hard cap on query results to bound CPU + memory on large audit logs.
_QUERY_LIMIT_HARD_CAP: int = 10_000
_QUERY_LIMIT_DEFAULT: int = 100


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class AuditGovernanceError(Exception):
    """Base class for all US-15 errors. Fail-closed by default."""


class AuditEventValidationError(AuditGovernanceError):
    """An AuditEvent input failed validation (user-fixable)."""


class AuditQueryValidationError(AuditGovernanceError):
    """An AuditQuery input or query boundary failed validation."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AuditEventSource(enum.Enum):
    """AC-3/AC-5: closed set of audit event sources.

    Every to_audit_record projection in the codebase is tagged with one
    of these so query_events can filter by phase (import / decrypt /
    verify / merge / schedule / approval / identity / replay /
    exception / state).
    """

    IMPORT = "import"
    DECRYPT = "decrypt"
    VERIFY = "verify"
    MERGE = "merge"
    SCHEDULE = "schedule"
    APPROVAL = "approval"
    IDENTITY = "identity"
    REPLAY = "replay"
    EXCEPTION = "exception"
    STATE = "state"


class AuditEventResult(enum.Enum):
    """AC-5: closed set of result codes."""

    OK = "ok"
    REJECTED = "rejected"
    FAILED = "failed"
    BLOCKED = "blocked"


class InterceptionReason(enum.Enum):
    """AC-1: five closed reasons a package can be intercepted."""

    CORRUPTED = "corrupted"
    TAMPERED = "tampered"
    EXPIRED = "expired"
    DUPLICATE = "duplicate"
    RECIPIENT_MISMATCH = "recipient_mismatch"


class AuditExportFormat(enum.Enum):
    """AC-6: export format choices."""

    JSON = "json"
    JSONL = "jsonl"


# ---------------------------------------------------------------------------
# AuditEvent
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AuditEvent:
    """AC-5: a single uniform audit record.

    Fields are populated from a business-side ``to_audit_record`` dict
    plus an explicit :class:`AuditEventSource` tag. Empty ``project_id``
    / ``task_id`` are allowed (events that don't carry one), but when
    a query filters on those columns, empty values never match a
    non-empty filter.
    """

    ts: str
    actor: str
    source: AuditEventSource
    action: str
    project_id: str
    task_id: str
    result: AuditEventResult
    tool: str
    detail: dict = dataclasses.field(default_factory=dict)
    fingerprint: str = ""
    record_hash: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.ts, str) or not _ISO_UTC_Z.match(self.ts):
            raise AuditEventValidationError(
                f"AuditEvent.ts must be ISO-8601 UTC with 'Z' suffix; got {self.ts!r}"
            )
        if not isinstance(self.actor, str) or not self.actor:
            raise AuditEventValidationError(
                "AuditEvent.actor must be a non-empty string"
            )
        if not isinstance(self.source, AuditEventSource):
            raise AuditEventValidationError(
                f"AuditEvent.source must be AuditEventSource; got {self.source!r}"
            )
        if not isinstance(self.action, str) or not self.action:
            raise AuditEventValidationError(
                "AuditEvent.action must be a non-empty string"
            )
        if not isinstance(self.project_id, str):
            raise AuditEventValidationError(
                "AuditEvent.project_id must be a string (use '' if absent)"
            )
        if not isinstance(self.task_id, str):
            raise AuditEventValidationError(
                "AuditEvent.task_id must be a string (use '' if absent)"
            )
        if not isinstance(self.result, AuditEventResult):
            raise AuditEventValidationError(
                f"AuditEvent.result must be AuditEventResult; got {self.result!r}"
            )
        if not isinstance(self.tool, str):
            raise AuditEventValidationError("AuditEvent.tool must be a string")
        if not isinstance(self.detail, dict):
            raise AuditEventValidationError("AuditEvent.detail must be a dict")
        if not isinstance(self.fingerprint, str):
            raise AuditEventValidationError(
                "AuditEvent.fingerprint must be a string (use '' if absent)"
            )
        if self.fingerprint and not re.fullmatch(r"[0-9a-fA-F]{1,64}", self.fingerprint):
            raise AuditEventValidationError(
                f"AuditEvent.fingerprint must be hex (1..64 chars); got {self.fingerprint!r}"
            )
        if not isinstance(self.record_hash, str):
            raise AuditEventValidationError(
                "AuditEvent.record_hash must be a string (use '' if absent)"
            )

    @staticmethod
    def from_audit_record(
        record: Mapping[str, object],
        *,
        source: AuditEventSource,
    ) -> "AuditEvent":
        """Construct from a business-side to_audit_record dict.

        Required keys: ts, actor, action, result. Optional: project_id,
        task_id, tool, detail, fingerprint. Unknown keys are ignored.

        Fail-closed on missing required keys, bad types, bad ts format,
        unknown result code, or non-hex fingerprint.
        """
        if not isinstance(record, Mapping):
            raise AuditEventValidationError(
                "AuditEvent.from_audit_record requires a mapping"
            )
        if not isinstance(source, AuditEventSource):
            raise AuditEventValidationError(
                f"source must be AuditEventSource; got {source!r}"
            )
        for required in ("ts", "actor", "action", "result"):
            if required not in record:
                raise AuditEventValidationError(
                    f"to_audit_record missing required key {required!r}"
                )
        result_raw = record["result"]
        if not isinstance(result_raw, str) or result_raw not in _AUDIT_RESULT_CODES:
            raise AuditEventValidationError(
                f"result must be one of {sorted(_AUDIT_RESULT_CODES)}; got {result_raw!r}"
            )
        return AuditEvent(
            ts=str(record["ts"]),
            actor=str(record["actor"]),
            source=source,
            action=str(record["action"]),
            project_id=str(record.get("project_id", "")),
            task_id=str(record.get("task_id", "")),
            result=AuditEventResult(result_raw),
            tool=str(record.get("tool", "")),
            detail=dict(record.get("detail", {})) if isinstance(record.get("detail"), Mapping) else {},
            fingerprint=str(record.get("fingerprint", "")),
            record_hash=str(record.get("record_hash", "")),
        )


# ---------------------------------------------------------------------------
# InterceptionDecision
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class InterceptionDecision:
    """AC-1: a single interception decision for a package."""

    package_id: str
    intercepted: bool
    reasons: tuple[InterceptionReason, ...]
    detail: str
    decided_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.package_id, str) or not _SAFE_ID.match(self.package_id):
            raise AuditEventValidationError(
                f"package_id must be safe-id; got {self.package_id!r}"
            )
        if not isinstance(self.intercepted, bool):
            raise AuditEventValidationError(
                f"intercepted must be bool; got {self.intercepted!r}"
            )
        if not isinstance(self.reasons, tuple) or not all(
            isinstance(r, InterceptionReason) for r in self.reasons
        ):
            raise AuditEventValidationError(
                "reasons must be a tuple of InterceptionReason"
            )
        if not isinstance(self.detail, str):
            raise AuditEventValidationError("detail must be a string")
        if not isinstance(self.decided_at, str) or not _ISO_UTC_Z.match(self.decided_at):
            raise AuditEventValidationError(
                f"decided_at must be ISO-8601 UTC 'Z'; got {self.decided_at!r}"
            )
        # consistency: intercepted is True iff reasons is non-empty
        if self.intercepted and not self.reasons:
            raise AuditEventValidationError(
                "intercepted=True requires at least one reason"
            )
        if not self.intercepted and self.reasons:
            raise AuditEventValidationError(
                "intercepted=False requires an empty reasons tuple"
            )


# ---------------------------------------------------------------------------
# AuditQuery / AuditQueryResult
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AuditQuery:
    """AC-6: a query descriptor. All filters are inclusive AND."""

    actor: str = ""
    source: AuditEventSource | None = None
    action: str = ""
    project_id: str = ""
    task_id: str = ""
    result: AuditEventResult | None = None
    ts_from: str = ""
    ts_to: str = ""
    limit: int = _QUERY_LIMIT_DEFAULT
    cursor: str = ""

    def __post_init__(self) -> None:
        if self.actor and not _SAFE_ID.match(self.actor):
            raise AuditQueryValidationError(
                f"actor filter must be safe-id; got {self.actor!r}"
            )
        if self.source is not None and not isinstance(self.source, AuditEventSource):
            raise AuditQueryValidationError(
                f"source must be AuditEventSource; got {self.source!r}"
            )
        if self.action and not isinstance(self.action, str):
            raise AuditQueryValidationError("action filter must be a string")
        if self.project_id and not _SAFE_ID.match(self.project_id):
            raise AuditQueryValidationError(
                f"project_id filter must be safe-id; got {self.project_id!r}"
            )
        if self.task_id and not _SAFE_ID.match(self.task_id):
            raise AuditQueryValidationError(
                f"task_id filter must be safe-id; got {self.task_id!r}"
            )
        if self.result is not None and not isinstance(self.result, AuditEventResult):
            raise AuditQueryValidationError(
                f"result must be AuditEventResult; got {self.result!r}"
            )
        if self.ts_from and not _ISO_UTC_Z.match(self.ts_from):
            raise AuditQueryValidationError(
                f"ts_from must be ISO-8601 UTC 'Z'; got {self.ts_from!r}"
            )
        if self.ts_to and not _ISO_UTC_Z.match(self.ts_to):
            raise AuditQueryValidationError(
                f"ts_to must be ISO-8601 UTC 'Z'; got {self.ts_to!r}"
            )
        if self.ts_from and self.ts_to and self.ts_from > self.ts_to:
            raise AuditQueryValidationError(
                f"ts_from must be <= ts_to; got {self.ts_from!r} > {self.ts_to!r}"
            )
        if not isinstance(self.limit, int) or self.limit <= 0:
            raise AuditQueryValidationError("limit must be a positive integer")
        if self.limit > _QUERY_LIMIT_HARD_CAP:
            raise AuditQueryValidationError(
                f"limit must be <= {_QUERY_LIMIT_HARD_CAP} (DoS guard); got {self.limit}"
            )
        if self.cursor and not _SAFE_ID.match(self.cursor):
            raise AuditQueryValidationError(
                f"cursor must be safe-id; got {self.cursor!r}"
            )


@dataclasses.dataclass(frozen=True)
class AuditQueryResult:
    """AC-6: query result."""

    events: tuple[AuditEvent, ...]
    total_scanned: int
    cursor_next: str

    def __post_init__(self) -> None:
        if not isinstance(self.events, tuple) or not all(
            isinstance(e, AuditEvent) for e in self.events
        ):
            raise AuditEventValidationError(
                "events must be a tuple of AuditEvent"
            )
        if not isinstance(self.total_scanned, int) or self.total_scanned < 0:
            raise AuditEventValidationError("total_scanned must be a non-negative integer")
        if not isinstance(self.cursor_next, str):
            raise AuditEventValidationError("cursor_next must be a string")


# ---------------------------------------------------------------------------
# AuditExportPayload
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AuditExportPayload:
    """AC-6: a self-contained export payload (no IO)."""

    format: AuditExportFormat
    content: bytes
    byte_count: int
    event_count: int
    exported_at: str
    digest_hex: str

    def __post_init__(self) -> None:
        if not isinstance(self.format, AuditExportFormat):
            raise AuditEventValidationError(
                f"format must be AuditExportFormat; got {self.format!r}"
            )
        if not isinstance(self.content, bytes):
            raise AuditEventValidationError("content must be bytes")
        if not isinstance(self.byte_count, int) or self.byte_count < 0:
            raise AuditEventValidationError("byte_count must be a non-negative integer")
        if not isinstance(self.event_count, int) or self.event_count < 0:
            raise AuditEventValidationError("event_count must be a non-negative integer")
        if not isinstance(self.exported_at, str) or not _ISO_UTC_Z.match(self.exported_at):
            raise AuditEventValidationError(
                f"exported_at must be ISO-8601 UTC 'Z'; got {self.exported_at!r}"
            )
        if (
            not isinstance(self.digest_hex, str)
            or len(self.digest_hex) != 64
            or not re.fullmatch(r"[0-9a-f]{64}", self.digest_hex)
        ):
            raise AuditEventValidationError(
                f"digest_hex must be 64-char lowercase hex; got {self.digest_hex!r}"
            )
        # consistency: byte_count == len(content)
        if self.byte_count != len(self.content):
            raise AuditEventValidationError(
                f"byte_count ({self.byte_count}) must equal len(content) ({len(self.content)})"
            )
        # consistency: digest_hex == sha256(content)
        if hashlib.sha256(self.content).hexdigest() != self.digest_hex:
            raise AuditEventValidationError("digest_hex must equal SHA-256(content)")


# ---------------------------------------------------------------------------
# Service facade
# ---------------------------------------------------------------------------


class SecurityAuditFacade:
    """Pure-function facade over the US-15 data model."""

    @staticmethod
    def evaluate_interception(
        *,
        package_id: str,
        envelope_status: str,
        signature_status: str,
        expiration_ts: str,
        now: str,
        replay_status: str,
        envelope_recipient_cert_id: str,
        expected_recipient_cert_id: str,
    ) -> InterceptionDecision:
        """AC-1: centralize the 5 interception reasons into one decision.

        Reason precedence is positional in the output tuple
        (``CORRUPTED``, ``TAMPERED``, ``EXPIRED``, ``DUPLICATE``,
        ``RECIPIENT_MISMATCH``). A clean package yields
        ``intercepted=False`` with an empty reasons tuple.
        """
        if not isinstance(package_id, str) or not _SAFE_ID.match(package_id):
            raise AuditEventValidationError(
                f"package_id must be safe-id; got {package_id!r}"
            )
        for field_name, value in (
            ("envelope_status", envelope_status),
            ("signature_status", signature_status),
            ("replay_status", replay_status),
            ("envelope_recipient_cert_id", envelope_recipient_cert_id),
            ("expected_recipient_cert_id", expected_recipient_cert_id),
        ):
            if not isinstance(value, str) or not value:
                raise AuditEventValidationError(
                    f"{field_name} must be a non-empty string"
                )
        if not _ISO_UTC_Z.match(now):
            raise AuditEventValidationError(
                f"now must be ISO-8601 UTC 'Z'; got {now!r}"
            )
        if expiration_ts and not _ISO_UTC_Z.match(expiration_ts):
            raise AuditEventValidationError(
                f"expiration_ts must be ISO-8601 UTC 'Z' or empty; got {expiration_ts!r}"
            )
        for cert in (envelope_recipient_cert_id, expected_recipient_cert_id):
            if not _SAFE_ID.match(cert):
                raise AuditEventValidationError(
                    f"cert id must be safe-id; got {cert!r}"
                )

        reasons: list[InterceptionReason] = []
        details: list[str] = []

        if envelope_status == "corrupted":
            reasons.append(InterceptionReason.CORRUPTED)
            details.append("envelope corrupted")

        # TAMPERED means signature invalid AND envelope not fully corrupted
        # (a corrupted envelope short-circuits signature verification).
        if envelope_status != "corrupted" and signature_status == "invalid":
            reasons.append(InterceptionReason.TAMPERED)
            details.append("signature invalid")

        if expiration_ts and now > expiration_ts:
            reasons.append(InterceptionReason.EXPIRED)
            details.append(f"expired at {expiration_ts}")

        if replay_status == "duplicate":
            reasons.append(InterceptionReason.DUPLICATE)
            details.append("replay detected")

        if envelope_recipient_cert_id != expected_recipient_cert_id:
            reasons.append(InterceptionReason.RECIPIENT_MISMATCH)
            details.append(
                f"recipient mismatch: envelope={envelope_recipient_cert_id} "
                f"expected={expected_recipient_cert_id}"
            )

        intercepted = bool(reasons)
        return InterceptionDecision(
            package_id=package_id,
            intercepted=intercepted,
            reasons=tuple(reasons),
            detail="; ".join(details),
            decided_at=now,
        )

    @staticmethod
    def query_events(
        events: tuple[AuditEvent, ...],
        query: AuditQuery,
    ) -> AuditQueryResult:
        """AC-6: filter ``events`` by ``query``. Pure function.

        The cursor is implemented as the ``record_hash`` of the last
        returned event. To paginate, pass ``query=cursor_next`` on the
        next call. When the result is shorter than ``query.limit``,
        ``cursor_next`` is empty.
        """
        if not isinstance(events, tuple) or not all(
            isinstance(e, AuditEvent) for e in events
        ):
            raise AuditEventValidationError(
                "events must be a tuple of AuditEvent"
            )
        if not isinstance(query, AuditQuery):
            raise AuditQueryValidationError(
                "query must be an AuditQuery instance"
            )

        # Skip past the cursor first (cursor is the record_hash of the
        # last event of the previous page).
        skipping = bool(query.cursor)
        filtered: list[AuditEvent] = []
        total_scanned = 0
        for event in events:
            total_scanned += 1
            if skipping:
                if event.record_hash == query.cursor:
                    skipping = False
                continue
            if not _event_matches(event, query):
                continue
            filtered.append(event)
            if len(filtered) >= query.limit:
                break

        cursor_next = filtered[-1].record_hash if len(filtered) >= query.limit else ""
        return AuditQueryResult(
            events=tuple(filtered),
            total_scanned=total_scanned,
            cursor_next=cursor_next,
        )

    @staticmethod
    def export_events(
        events: tuple[AuditEvent, ...],
        *,
        fmt: AuditExportFormat = AuditExportFormat.JSONL,
        now: str,
    ) -> AuditExportPayload:
        """AC-6: render events to bytes. Pure function, no IO.

        ``JSONL`` writes one JSON object per line + trailing newline,
        matching ``loop/tool-audit.jsonl`` layout. ``JSON`` writes one
        JSON array. ``digest_hex`` is ``SHA-256(content)`` so two
        identical exports on identical inputs are content-stable.
        """
        if not isinstance(events, tuple) or not all(
            isinstance(e, AuditEvent) for e in events
        ):
            raise AuditEventValidationError(
                "events must be a tuple of AuditEvent"
            )
        if not isinstance(fmt, AuditExportFormat):
            raise AuditEventValidationError(
                f"fmt must be AuditExportFormat; got {fmt!r}"
            )
        if not _ISO_UTC_Z.match(now):
            raise AuditEventValidationError(
                f"now must be ISO-8601 UTC 'Z'; got {now!r}"
            )

        rows = [_event_to_export_row(e) for e in events]
        if fmt == AuditExportFormat.JSONL:
            body = b"\n".join(
                json.dumps(r, ensure_ascii=False, sort_keys=True).encode("utf-8")
                for r in rows
            ) + b"\n"
        else:
            body = json.dumps(rows, ensure_ascii=False, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(body).hexdigest()
        return AuditExportPayload(
            format=fmt,
            content=body,
            byte_count=len(body),
            event_count=len(events),
            exported_at=now,
            digest_hex=digest,
        )

    @staticmethod
    def to_audit_record(decision: InterceptionDecision) -> dict:
        """Project an :class:`InterceptionDecision` to an audit dict.

        Mirrors US-11/12/13/8: EXCLUDES ``detail`` free text (kept only
        as a ``detail_hash`` for traceability) and includes reason codes,
        intercepted flag, package_id, and decided_at.
        """
        if not isinstance(decision, InterceptionDecision):
            raise AuditEventValidationError(
                "decision must be an InterceptionDecision"
            )
        return {
            "schema_version": "1.0",
            "domain": "coevo.audit_governance",
            "event_kind": "interception_decision",
            "package_id": decision.package_id,
            "intercepted": decision.intercepted,
            "reasons": [r.value for r in decision.reasons],
            "detail_hash": hashlib.sha256(decision.detail.encode("utf-8")).hexdigest(),
            "decided_at": decision.decided_at,
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _event_matches(event: AuditEvent, query: AuditQuery) -> bool:
    if query.actor and event.actor != query.actor:
        return False
    if query.source is not None and event.source != query.source:
        return False
    if query.action and event.action != query.action:
        return False
    if query.project_id and event.project_id != query.project_id:
        return False
    if query.task_id and event.task_id != query.task_id:
        return False
    if query.result is not None and event.result != query.result:
        return False
    if query.ts_from and event.ts < query.ts_from:
        return False
    if query.ts_to and event.ts > query.ts_to:
        return False
    return True


def _event_to_export_row(event: AuditEvent) -> dict:
    return {
        "ts": event.ts,
        "actor": event.actor,
        "source": event.source.value,
        "action": event.action,
        "project_id": event.project_id,
        "task_id": event.task_id,
        "result": event.result.value,
        "tool": event.tool,
        "fingerprint": event.fingerprint,
        "record_hash": event.record_hash,
    }

# ---------------------------------------------------------------------------
# Real-time audit stream (US-15-AC-2)
# ---------------------------------------------------------------------------
#
# Imported last: stream.py imports the AuditEvent types defined above.

from .stream import (  # noqa: E402
    AuditStreamError,
    AuditStreamHub,
    AuditSubscription,
    DEFAULT_MAX_QUEUED,
    DEFAULT_MAX_SUBSCRIBERS,
    DEFAULT_HISTORY_LEN,
)
