"""US-15 security audit governance facade (split from the package init)."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 安全审计门面（US-15）：
#   evaluate_interception()：把异常包的五类拦截原因集中判定为一次决策
#     （CORRUPTED/TAMPERED/EXPIRED/DUPLICATE/RECIPIENT_MISMATCH，按序
#     优先级短路），供导入前拦截层使用。
#   query_events()：按主体/动作/结果/项目/任务/时间过滤审计事件，带
#     limit 硬上限（10000）与 record_hash 游标分页；纯函数无 IO。
#   export_events()：导出 JSON/JSONL，内容摘要 SHA-256 稳定可复验。
#   关键不变量：AuditEvent 核心字段（ts/actor/source/action/result）强制
#     有效；project_id/task_id 允许为空字符串（过滤时空值不匹配非空条件），
#     审计投影排除敏感文本只保留哈希/计数。
from __future__ import annotations

import hashlib
import json

from .models import (
    _ISO_UTC_Z,
    _SAFE_ID,
    AuditEvent,
    AuditEventValidationError,
    AuditExportFormat,
    AuditExportPayload,
    AuditQuery,
    AuditQueryResult,
    AuditQueryValidationError,
    InterceptionDecision,
    InterceptionReason,
)

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
