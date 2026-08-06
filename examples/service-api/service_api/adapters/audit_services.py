from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from coevo_demo_utils import build_and_verify_package  # noqa: E402
from src.coevo.audit_governance import (  # noqa: E402
    AuditExportFormat,
    AuditQuery,
    SecurityAuditFacade,
)

from ._core import AUDITOR_CERT, OWNER_CERT, _require_param


def audit_query(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """按主体/动作/结果查询审计事件（US-15 AC-6）。"""
    query = AuditQuery(
        actor=str(request.params.get("actor", "")),
        action=str(request.params.get("action", "")),
        project_id=str(request.params.get("project_id", "")),
        limit=int(request.params.get("limit", 50)),
    )
    result = SecurityAuditFacade.query_events(
        tuple(ctx["audit_events"]), query
    )
    return {
        "total_scanned": result.total_scanned,
        "events": [
            {
                "ts": event.ts,
                "actor": event.actor,
                "action": event.action,
                "result": event.result.value,
                "project_id": event.project_id,
            }
            for event in result.events
        ],
    }
def audit_intercept(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """异常包拦截决策（US-15 AC-1）。"""
    decision = SecurityAuditFacade.evaluate_interception(
        package_id=_require_param(request, "package_id"),
        envelope_status=str(request.params.get("envelope_status", "ok")),
        signature_status=str(request.params.get("signature_status", "valid")),
        expiration_ts=str(request.params.get("expiration_ts", "")),
        now=request.ts,
        replay_status=str(request.params.get("replay_status", "new")),
        envelope_recipient_cert_id=_require_param(
            request, "envelope_recipient_cert_id"
        ),
        expected_recipient_cert_id=_require_param(
            request, "expected_recipient_cert_id"
        ),
    )
    return {
        "intercepted": decision.intercepted,
        "reasons": [reason.value for reason in decision.reasons],
        "detail": decision.detail,
    }
def audit_export(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """导出审计事件（JSONL/JSON，内容摘要 SHA-256 稳定可复验，US-15 AC-6）。"""
    fmt = AuditExportFormat(str(request.params.get("format", "jsonl")))
    payload = SecurityAuditFacade.export_events(
        tuple(ctx["audit_events"]), fmt=fmt, now=request.ts
    )
    return {
        "format": payload.format.value,
        "event_count": payload.event_count,
        "byte_count": payload.byte_count,
        "digest_hex": payload.digest_hex,
        "content_base64": base64.b64encode(payload.content).decode("ascii"),
    }
def audit_checkpoint(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """安全管理员导出加密审计检查点包（AUDIT_CHECKPOINT → 负责人）。"""
    baseline = ctx["project_state"].get("baseline")
    base_revision = (
        f"{baseline.project_id}-R{baseline.version:04d}"
        if baseline is not None
        else "PRJ001-R0001"
    )
    audit_digest = hashlib.sha256(
        "".join(event.ts + event.action for event in ctx["audit_events"]).encode(
            "utf-8"
        )
    ).hexdigest()
    content = json.dumps(
        {
            "audit_event_count": len(ctx["audit_events"]),
            "audit_digest": audit_digest,
            "checkpoint_note": "一致性 API 审计检查点",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    package, wire = build_and_verify_package(
        provider=ctx["provider"],
        sender_cert=AUDITOR_CERT,
        recipient_cert=OWNER_CERT,
        package_type="AUDIT_CHECKPOINT",
        project_id="PRJ001",
        task_id="",
        base_revision=base_revision,
        sequence_no=1,
        manifest={
            "event_id": "ev.audit.checkpoint",
            "project_id": "PRJ001",
            "task_id": "",
            "base_revision": base_revision,
            "payload_digest": "0" * 64,
        },
        content=content,
        signed_at=request.ts,
        expires_at="2027-08-01T00:00:00Z",
    )
    envelope = package.envelope
    export = ctx["runtime_dir"] / "outbox" / (
        f"AUDIT_CHECKPOINT_PRJ001_{envelope.package_id}.agent"
    )
    export.parent.mkdir(parents=True, exist_ok=True)
    export.write_bytes(wire)
    return {
        "package_id": envelope.package_id,
        "package_type": envelope.package_type,
        "audit_digest": audit_digest,
        "sha256": hashlib.sha256(wire).hexdigest(),
        "exported_path": str(export),
    }
