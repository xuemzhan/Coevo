from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from coevo_demo_utils import build_and_verify_package, encrypt_and_verify  # noqa: E402
from src.coevo.cockpit import (  # noqa: E402
    MilestoneSummary,
    RoleView,
    TaskSummary,
    WorkspaceView,
)
from src.coevo.progress_capture import (  # noqa: E402
    EvidenceInput,
    EvidenceKind,
    EvidenceRef,
    ProgressCaptureService,
)
from src.coevo.protocol import (  # noqa: E402
    PackageImportService,
    ProcessedPackage,
    ProcessedPackageStore,
    ReplayDecision,
    ReplayOutcome,
    build_envelope_template,
    check_replay,
    open_encrypted_package,
    parse_package_bytes,
)
from src.coevo.protocol.sm2_sign import compute_sm3_digest  # noqa: E402
from src.coevo.report import ReportManifest, ReportStatus  # noqa: E402
from src.coevo.workspace.init_service import WorkspaceInitService  # noqa: E402
from src.coevo.workspace.models import WorkspaceEntry, WorkspaceRegistry  # noqa: E402

from ._core import _cert_handle, _require_param, _require_safe_id
from ..contract import ErrorCode, ServiceError  # noqa: E402


def package_build(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """构建并回读校验一个加密任务包（US-5）。"""
    sender_cert = _require_safe_id(
        _require_param(request, "sender_cert_id"), "sender_cert_id"
    )
    recipient_cert = _require_safe_id(
        _require_param(request, "recipient_cert_id"), "recipient_cert_id"
    )
    project_id = _require_safe_id(_require_param(request, "project_id"), "project_id")
    package_type = _require_param(request, "package_type")
    content = json.dumps(
        _require_param(request, "content"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    package, wire = build_and_verify_package(
        provider=ctx["provider"],
        sender_cert=sender_cert,
        recipient_cert=recipient_cert,
        package_type=package_type,
        project_id=project_id,
        task_id=str(request.params.get("task_id", "t.1")),
        base_revision=str(request.params.get("base_revision", "PRJ001-R0001")),
        sequence_no=int(_require_param(request, "sequence_no")),
        manifest=_require_param(request, "manifest"),
        content=content,
        signed_at=request.ts,
        expires_at=request.params.get("expires_at", "2027-08-01T00:00:00Z"),
    )
    envelope = package.envelope
    export = ctx["runtime_dir"] / "outbox" / (
        f"{envelope.package_type}_{envelope.project_id}_{envelope.package_id}.agent"
    )
    export.parent.mkdir(parents=True, exist_ok=True)
    export.write_bytes(wire)
    return {
        "package_id": envelope.package_id,
        "package_type": envelope.package_type,
        "sha256": hashlib.sha256(wire).hexdigest(),
        "wire_base64": base64.b64encode(wire).decode("ascii"),
        "exported_path": str(export),
    }
def workspace_init(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """离线导入加密任务包并初始化项目/角色工作区（US-6）。"""
    package_base64 = _require_param(request, "package_base64")
    role_id = _require_param(request, "role_id")
    base_revision = _require_param(request, "base_revision")
    wire = base64.b64decode(package_base64, validate=True)
    package = parse_package_bytes(wire)
    opened = open_encrypted_package(
        package,
        provider=ctx["provider"],
        recipient_handle=_cert_handle(
            ctx["provider"], package.envelope.recipient_cert_id, "recipient"
        ),
        sender_handle=_cert_handle(
            ctx["provider"], package.envelope.sender_cert_id, "sender"
        ),
    )
    workspaces = ctx.setdefault("workspaces", {})
    workspace_key = (package.envelope.project_id, role_id)
    if workspace_key in workspaces:
        raise ServiceError(
            ErrorCode.CONFLICT,
            f"workspace {workspace_key} already initialized (AC-7)",
        )
    digest = compute_sm3_digest(wire)
    candidate = ProcessedPackage(
        package_id=package.envelope.package_id,
        package_digest=digest,
        sender_cert_id=package.envelope.sender_cert_id,
        recipient_cert_id=package.envelope.recipient_cert_id,
        project_id=package.envelope.project_id,
        sequence_no=package.envelope.sequence_no,
    )
    replay = check_replay(candidate=candidate, registry=())
    if replay.outcome is not ReplayOutcome.ACCEPT:
        raise ServiceError(
            ErrorCode.CONFLICT, f"replay gate rejected: {replay.outcome.value}"
        )
    imported = PackageImportService().import_package(
        package=package,
        replay_decision=ReplayDecision(
            replay.outcome, replay.previous_sequence_no, replay.detail
        ),
        store=ProcessedPackageStore.empty(),
        base_revision=base_revision,
        current_revision=base_revision,
        processed_at=request.ts,
    )
    if imported.transaction.step.value != "committed":
        raise ServiceError(ErrorCode.CONFLICT, "import did not commit")
    init_service = WorkspaceInitService(
        quarantine_root=str(ctx["runtime_dir"] / "quarantine"),
        workspace_root=str(ctx["workspace_root"]),
    )
    init = init_service.init_from_import(
        imported, WorkspaceRegistry.empty(), role_id=role_id,
        revision=imported.record.revision,
    )
    if not init.created or init.entry is None:
        raise ServiceError(
            ErrorCode.CONFLICT, f"workspace init rejected: {init.failure_reason}"
        )
    workspaces[workspace_key] = init.entry
    Path(init.paths.workspace.as_posix()).mkdir(parents=True, exist_ok=True)
    return {
        "project_id": init.entry.project_id,
        "role_id": init.entry.role_id,
        "package_id": init.entry.package_id,
        "revision": init.entry.revision,
        "workspace_path": init.paths.workspace.as_posix(),
    }
def cockpit_snapshot(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """生成驾驶舱项目/角色视图快照（US-7 纯投影）。"""
    workspace = WorkspaceView(
        _require_param(request, "project_id"),
        str(request.params.get("title", "项目")),
        tuple(request.params.get("roles", [])),
        int(request.params.get("task_count", 0)),
        int(request.params.get("milestone_count", 0)),
        int(request.params.get("artifact_count", 0)),
    )
    role_views = [
        RoleView(
            str(role.get("role_id", "")),
            workspace.project_id,
            str(role.get("display_name", "")),
            tuple(
                TaskSummary(
                    str(task["task_id"]), str(task["title"]),
                    str(task.get("status", "in_progress")),
                    str(task.get("due_at", "")),
                    str(task.get("assignee_role_id", "")),
                )
                for task in role.get("tasks", [])
            ),
            (),
            (),
        )
        for role in request.params.get("role_views", [])
    ]
    return {
        "project_id": workspace.project_id,
        "task_count": workspace.task_count,
        "role_view_count": len(role_views),
    }
def progress_extract(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """从成果证据识别进展（US-8，产出 PROPOSED 待确认）。"""
    workspace = WorkspaceEntry(
        _require_param(request, "project_id"),
        _require_param(request, "role_id"),
        str(request.params.get("package_id", "pkg.input")),
        str(request.params.get("revision", "PRJ001-R0001")),
    )
    evidence = _require_param(request, "evidence")
    inputs = tuple(
        EvidenceInput(
            task_id=str(item["task_id"]),
            kind=EvidenceKind(str(item["kind"])),
            source_ref=str(item["source_ref"]),
            text=str(item["text"]),
            confidence=float(item["confidence"]),
            evidence_refs=tuple(
                EvidenceRef(
                    path=str(ref["path"]),
                    role=str(ref.get("role", "document")),
                    media_type=str(ref.get("media_type", "text/markdown")),
                    digest_hex=str(ref["digest_hex"]),
                    size_bytes=int(ref["size_bytes"]),
                )
                for ref in item["evidence_refs"]
            ),
        )
        for item in evidence
    )
    capture = ProgressCaptureService.extract_progress(
        workspace, inputs, now=request.ts
    )
    return {
        "capture_id": capture.capture_id,
        "item_count": len(capture.progress_items),
        "requires_user_confirmation": capture.requires_user_confirmation,
        "items": [
            {
                "item_id": item.item_id,
                "task_id": item.task_id,
                "kind": item.kind.value,
                "status": item.status.value,
                "confidence": item.confidence,
            }
            for item in capture.progress_items
        ],
    }
def report_build(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """生成真实加密成果汇报包（US-9）并暂存到项目状态供合并。"""
    manifest = _require_param(request, "manifest")
    sender_cert = manifest["sender_cert_id"]
    recipient_cert = manifest["recipient_cert_id"]
    envelope = build_envelope_template(
        sender_cert_id=sender_cert,
        recipient_cert_id=recipient_cert,
        project_id=manifest["project_id"],
        package_type="RESULT_SUBMISSION",
        sequence_no=int(manifest["sequence_no"]),
        payload_length=0,
        created_at=request.ts,
        expires_at="2027-08-01T00:00:00Z",
    )
    report = ReportManifest(
        schema_version="1.0",
        package_id=envelope.package_id,
        package_type="RESULT_SUBMISSION",
        project_id=manifest["project_id"],
        task_id=manifest["task_id"],
        base_revision=manifest["base_revision"],
        sequence_no=int(manifest["sequence_no"]),
        submitted_at=request.ts,
        sender_user_id=str(manifest.get("sender_user_id", "U-MEMBER")),
        sender_client_id=str(manifest.get("sender_client_id", "CLI-MEMBER")),
        sender_organization_id=str(manifest.get("sender_organization_id", "ORG")),
        sender_cert_id=sender_cert,
        recipient_user_id=str(manifest.get("recipient_user_id", "U-PM")),
        recipient_client_id=str(manifest.get("recipient_client_id", "CLI-PM")),
        recipient_organization_id=str(manifest.get("recipient_organization_id", "ORG")),
        recipient_cert_id=recipient_cert,
        status=ReportStatus(str(manifest["status"])),
        progress_summary=str(manifest.get("progress_summary", "")),
        completed_work=tuple(manifest.get("completed_work", [])),
        pending_work=tuple(manifest.get("pending_work", [])),
        next_steps=tuple(manifest.get("next_steps", [])),
        risks=tuple(manifest.get("risks", [])),
        artifacts=(),
    )
    content = json.dumps(
        {
            "progress_summary": report.progress_summary,
            "completed_work": list(report.completed_work),
            "status": report.status.value,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    package, wire = encrypt_and_verify(
        envelope=envelope,
        manifest={
            "schema_version": "1.0",
            "package_id": report.package_id,
            "package_type": report.package_type,
            "project_id": report.project_id,
            "task_id": report.task_id,
            "base_revision": report.base_revision,
            "sequence_no": report.sequence_no,
            "status": report.status.value,
            "sender_cert_id": sender_cert,
            "recipient_cert_id": recipient_cert,
        },
        content=content,
        provider=ctx["provider"],
        sender_cert=sender_cert,
        recipient_cert=recipient_cert,
        signed_at=request.ts,
    )
    ctx["project_state"]["report"] = {
        "wire_base64": base64.b64encode(wire).decode("ascii"),
        "manifest": report,
    }
    return {
        "package_id": report.package_id,
        "package_type": report.package_type,
        "sha256": hashlib.sha256(wire).hexdigest(),
    }
