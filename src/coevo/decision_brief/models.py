"""decision_brief.models - domain models, enums, errors and shared validation helpers for US-13 decision briefs."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-13 决策简报领域模型：简报/内容/模板/风险确认与全部校验；
# 候选风险须经负责人密钥确认绑定最新合并回执。

from __future__ import annotations

import datetime as dt
import enum
import hashlib
import json
import os
import stat
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from src.coevo.merge.receipt import MergeCommitReceipt
from src.coevo.merge.repository import MergeReceiptRepository
from src.coevo.risk import Risk, RiskKind, RiskReport, SourceKind

BRIEF_DOMAIN = "coevo.decision_brief"

BRIEF_SCHEMA = "1.0"

RISK_CONFIRMATION_DOMAIN = "coevo.risk.owner-confirmation"

WPS_TOOL_ID = "kaiwu.wps.document"

HIGH_RISK_MIN_SEVERITY = 4

MAX_RISK_COUNT = 256

MAX_AFFECTED_TASKS_PER_RISK = 128

MAX_RISK_STRING_BYTES = 16 * 1024

MAX_RISK_REPORT_BYTES = 1024 * 1024

MAX_CONCLUSIONS_PER_SECTION = 512

MAX_SOURCES_PER_CONCLUSION = 256

MAX_BRIEF_CONTENT_BYTES = 2 * 1024 * 1024

MAX_TEMPLATE_BYTES = 8 * 1024 * 1024

MAX_TEMPLATE_UNCOMPRESSED_BYTES = 32 * 1024 * 1024

MAX_TEMPLATE_ZIP_ENTRIES = 4096

_ZERO_DIGEST = "0" * 64

_REPARSE_POINT = 0x400

class DecisionBriefError(Exception):
    """Base class for fail-closed decision-brief errors."""

class DecisionBriefValidationError(DecisionBriefError):
    """The brief input or immutable model is invalid."""

class DecisionBriefConflictError(DecisionBriefError):
    """A CAS or idempotency condition rejected a state change."""

class BriefType(enum.Enum):
    STAGE = "stage"
    PERIODIC = "periodic"
    RISK_TOPIC = "risk_topic"

class BriefSourceKind(enum.Enum):
    TASK = "task"
    RESULT_PACKAGE = "result_package"
    RISK = "risk"
    MERGE_RECEIPT = "merge_receipt"

@dataclass(frozen=True, order=True)
class SourceReference:
    kind: BriefSourceKind
    reference_id: str

    def __post_init__(self) -> None:
        if type(self.kind) is not BriefSourceKind:
            raise DecisionBriefValidationError("source kind is not supported")
        _safe_string(self.reference_id, field="reference_id", max_bytes=1024)

@dataclass(frozen=True)
class BriefConclusion:
    conclusion_id: str
    text: str
    sources: tuple[SourceReference, ...]

    def __post_init__(self) -> None:
        _safe_string(self.conclusion_id, field="conclusion_id", max_bytes=1024)
        _safe_string(self.text, field="text", max_bytes=16 * 1024)
        if (
            type(self.sources) is not tuple
            or not self.sources
            or len(self.sources) > MAX_SOURCES_PER_CONCLUSION
            or any(type(source) is not SourceReference for source in self.sources)
        ):
            raise DecisionBriefValidationError("conclusion sources are invalid or oversized")
        if len(set(self.sources)) != len(self.sources):
            raise DecisionBriefValidationError("sources must not contain duplicates")
        if self.sources != tuple(sorted(self.sources, key=_source_sort_key)):
            raise DecisionBriefValidationError("sources must use stable order")

@dataclass(frozen=True)
class BriefContent:
    title: str
    overall_progress: tuple[BriefConclusion, ...]
    important_changes: tuple[BriefConclusion, ...]
    high_risk_items: tuple[BriefConclusion, ...]
    pending_decisions: tuple[BriefConclusion, ...]

    def __post_init__(self) -> None:
        _safe_string(self.title, field="title", max_bytes=4096)
        sections = self.sections
        if any(
            type(section) is not tuple
            or len(section) > MAX_CONCLUSIONS_PER_SECTION
            or any(type(item) is not BriefConclusion for item in section)
            for section in sections
        ):
            raise DecisionBriefValidationError("brief sections are invalid or oversized")
        if not self.overall_progress or not self.important_changes:
            raise DecisionBriefValidationError(
                "overall progress and important changes must be present"
            )
        ids = tuple(item.conclusion_id for section in sections for item in section)
        if len(set(ids)) != len(ids):
            raise DecisionBriefValidationError("conclusion IDs must be unique")
        _encode_json(_content_plain(self), max_bytes=MAX_BRIEF_CONTENT_BYTES)

    @property
    def sections(self) -> tuple[tuple[BriefConclusion, ...], ...]:
        """Return the brief content sections as a tuple."""
        return (
            self.overall_progress,
            self.important_changes,
            self.high_risk_items,
            self.pending_decisions,
        )

@dataclass(frozen=True)
class ApprovedTemplate:
    approval_id: str
    template_ref: str
    template_digest: str

    def __post_init__(self) -> None:
        _safe_string(self.approval_id, field="approval_id", max_bytes=1024)
        _validate_template_ref(self.template_ref)
        _digest(self.template_digest, field="template_digest")

@dataclass(frozen=True)
class RiskConfirmation:
    confirmation_id: str
    payload: bytes
    signature: bytes
    receipt_id: str
    snapshot_digest: str
    risk_digest: str
    confirmed_at: str
    confirmed_by: str
    report: RiskReport

    def __post_init__(self) -> None:
        _safe_string(self.confirmation_id, field="confirmation_id", max_bytes=1024)
        if type(self.payload) is not bytes or not self.payload:
            raise DecisionBriefValidationError("confirmation payload must be bytes")
        if type(self.signature) is not bytes or not self.signature:
            raise DecisionBriefValidationError("confirmation signature must be bytes")
        _safe_string(self.receipt_id, field="receipt_id", max_bytes=1024)
        _digest(self.snapshot_digest, field="snapshot_digest")
        _digest(self.risk_digest, field="risk_digest")
        _parse_utc(self.confirmed_at, field="confirmed_at")
        _safe_string(self.confirmed_by, field="confirmed_by", max_bytes=1024)
        if type(self.report) is not RiskReport:
            raise DecisionBriefValidationError("confirmation report must be exact RiskReport")
        if _risk_digest(self.report) != self.risk_digest:
            raise DecisionBriefValidationError("confirmed risk report digest mismatch")
        expected_payload = _encode_json({
            "domain": RISK_CONFIRMATION_DOMAIN,
            "schema_version": BRIEF_SCHEMA,
            "receipt_id": self.receipt_id,
            "snapshot_digest": self.snapshot_digest,
            "risk_digest": self.risk_digest,
            "confirmed_at": self.confirmed_at,
            "confirmed_by": self.confirmed_by,
        }, max_bytes=16 * 1024)
        if self.payload != expected_payload:
            raise DecisionBriefValidationError("risk confirmation payload mismatch")
        if hashlib.sha256(self.payload + self.signature).hexdigest() != self.confirmation_id:
            raise DecisionBriefValidationError("risk confirmation ID mismatch")

@dataclass(frozen=True)
class WpsDocumentRequest:
    brief_id: str
    source_revision: int
    template_ref: str
    template_approval_id: str
    template_digest: str
    tool_id: str = WPS_TOOL_ID
    operation: str = "generate_copy"
    save_mode: str = "new_version"
    output_format: str = "docx"
    macros_allowed: bool = False
    requires_user_confirmation: bool = True

    def __post_init__(self) -> None:
        _safe_string(self.brief_id, field="brief_id", max_bytes=1024)
        if (
            isinstance(self.source_revision, bool)
            or not isinstance(self.source_revision, int)
            or self.source_revision < 1
        ):
            raise DecisionBriefValidationError("source_revision must be >= 1")
        _validate_template_ref(self.template_ref)
        _safe_string(
            self.template_approval_id, field="template_approval_id", max_bytes=1024
        )
        _digest(self.template_digest, field="template_digest")
        if self.tool_id != WPS_TOOL_ID:
            raise DecisionBriefValidationError("unregistered WPS tool")
        if self.operation != "generate_copy" or self.save_mode != "new_version":
            raise DecisionBriefValidationError("WPS may only generate a new-version copy")
        if self.output_format != "docx" or self.macros_allowed is not False:
            raise DecisionBriefValidationError("WPS output must be macro-free DOCX")
        if self.requires_user_confirmation is not True:
            raise DecisionBriefValidationError("WPS requires user confirmation")

@dataclass(frozen=True)
class BriefVersion:
    revision: int
    created_at: str
    edited_by: str
    edit_reason: str
    source_receipt_id: str
    source_package_id: str
    content: BriefContent
    content_digest: str
    previous_version_digest: str
    version_digest: str
    requires_user_review: bool = True
    formally_released: bool = False

    def __post_init__(self) -> None:
        if (
            isinstance(self.revision, bool)
            or not isinstance(self.revision, int)
            or self.revision < 1
        ):
            raise DecisionBriefValidationError("revision must be >= 1")
        _parse_utc(self.created_at, field="created_at")
        _safe_string(self.edited_by, field="edited_by", max_bytes=1024)
        _safe_string(self.edit_reason, field="edit_reason", max_bytes=4096)
        _safe_string(self.source_receipt_id, field="source_receipt_id", max_bytes=1024)
        _safe_string(self.source_package_id, field="source_package_id", max_bytes=1024)
        if type(self.content) is not BriefContent:
            raise DecisionBriefValidationError("content must be exact BriefContent")
        for name in ("content_digest", "previous_version_digest", "version_digest"):
            _digest(getattr(self, name), field=name)
        if self.content_digest != _content_digest(self.content):
            raise DecisionBriefValidationError("brief content digest mismatch")
        if self.version_digest != _version_digest(self):
            raise DecisionBriefValidationError("brief version digest mismatch")
        if self.requires_user_review is not True or self.formally_released is not False:
            raise DecisionBriefValidationError("draft review/release policy was bypassed")

@dataclass(frozen=True)
class DecisionBrief:
    brief_id: str
    project_id: str
    brief_type: BriefType
    versions: tuple[BriefVersion, ...]
    wps_request: WpsDocumentRequest

    def __post_init__(self) -> None:
        _safe_string(self.brief_id, field="brief_id", max_bytes=1024)
        _safe_string(self.project_id, field="project_id", max_bytes=1024)
        if type(self.brief_type) is not BriefType:
            raise DecisionBriefValidationError("brief_type is not supported")
        if (
            type(self.versions) is not tuple
            or not self.versions
            or any(type(item) is not BriefVersion for item in self.versions)
        ):
            raise DecisionBriefValidationError("versions must contain exact BriefVersion")
        if tuple(item.revision for item in self.versions) != tuple(
            range(1, len(self.versions) + 1)
        ):
            raise DecisionBriefValidationError("brief revisions must be consecutive")
        previous = _ZERO_DIGEST
        for version in self.versions:
            if version.previous_version_digest != previous:
                raise DecisionBriefValidationError("brief version hash chain is invalid")
            previous = version.version_digest
        if type(self.wps_request) is not WpsDocumentRequest:
            raise DecisionBriefValidationError("wps_request must be exact WpsDocumentRequest")
        if (
            self.wps_request.brief_id != self.brief_id
            or self.wps_request.source_revision != self.current.revision
        ):
            raise DecisionBriefValidationError("WPS request does not bind current brief")

    @property
    def current(self) -> BriefVersion:
        return self.versions[-1]

    @property
    def head_digest(self) -> str:
        return self.current.version_digest

def _latest_receipt(
    receipt_id: str,
    repository: MergeReceiptRepository,
    trusted_time: dt.datetime,
) -> MergeCommitReceipt:
    _safe_string(receipt_id, field="receipt_id", max_bytes=1024)
    if type(repository) is not MergeReceiptRepository:
        raise DecisionBriefValidationError("authoritative receipt repository required")
    history = repository.verified_history(trusted_time=trusted_time)
    # 单遍扫描同时完成两件事：按 receipt_id 定位目标收据，并记录每个
    # 项目在历史中的最后一条收据（历史有序，后见者即“最新”）。原实现
    # 对同一份历史做了两遍线性扫描。
    receipt: MergeCommitReceipt | None = None
    project_latest: dict[str, MergeCommitReceipt] = {}
    for item in history:
        project_latest[item.project_id] = item
        if item.receipt_id == receipt_id:
            receipt = item
    if receipt is None:
        raise DecisionBriefValidationError("verified receipt is absent")
    if project_latest.get(receipt.project_id) is not receipt:
        raise DecisionBriefValidationError("latest confirmed project receipt required")
    expected = f"{receipt.project_id}-R{receipt.snapshot.baseline.version:04d}"
    if receipt.merged_revision != expected or receipt.baseline_digest != receipt.snapshot.digest:
        raise DecisionBriefValidationError("receipt snapshot binding is invalid")
    return receipt

def _validate_bound_risk(
    receipt: MergeCommitReceipt,
    report: RiskReport,
    trusted_time: dt.datetime,
) -> None:
    _validate_risk_report(report)
    if report.project_id != receipt.project_id:
        raise DecisionBriefValidationError("risk report project mismatch")
    if report.merge_reporter_package_id != receipt.package_id:
        raise DecisionBriefValidationError("risk report package mismatch")
    analysed = _parse_utc(report.analysed_at, field="analysed_at")
    committed = _parse_utc(receipt.commit_decided_at, field="commit_decided_at")
    if analysed < committed or analysed > trusted_time:
        raise DecisionBriefValidationError("risk analysis time is outside trusted bounds")

def _validate_risk_report(report: object) -> None:
    if type(report) is not RiskReport:
        raise DecisionBriefValidationError("risk report must be exact RiskReport")
    if len(report.risks) > MAX_RISK_COUNT:
        raise DecisionBriefValidationError("risk count exceeds policy")
    _safe_string(
        report.merge_reporter_package_id,
        field="risk.merge_reporter_package_id",
        max_bytes=MAX_RISK_STRING_BYTES,
    )
    _safe_string(
        report.project_id, field="risk.project_id", max_bytes=MAX_RISK_STRING_BYTES
    )
    analysed_at = _parse_utc(report.analysed_at, field="risk.analysed_at")
    if (
        type(report.coordination_meeting_recommended) is not bool
        or report.requires_owner_confirmation is not True
        or report.formally_released is not False
    ):
        raise DecisionBriefValidationError("risk report policy flags are invalid")
    risk_ids: list[str] = []
    for risk in report.risks:
        if type(risk) is not Risk:
            raise DecisionBriefValidationError("risk entries must be exact Risk")
        if (
            type(risk.kind) is not RiskKind
            or type(risk.source) is not SourceKind
            or isinstance(risk.severity, bool)
            or not isinstance(risk.severity, int)
            or not 1 <= risk.severity <= 5
            or type(risk.affected_tasks) is not tuple
            or not risk.affected_tasks
        ):
            raise DecisionBriefValidationError("risk shape is invalid")
        if len(risk.affected_tasks) > MAX_AFFECTED_TASKS_PER_RISK:
            raise DecisionBriefValidationError("affected task count exceeds policy")
        for name in (
            "risk_id", "basis", "recommendation", "suggested_deadline", "rationale"
        ):
            _safe_string(
                getattr(risk, name), field=f"risk.{name}", max_bytes=MAX_RISK_STRING_BYTES
            )
        for task_id in risk.affected_tasks:
            _safe_string(
                task_id, field="risk.affected_task", max_bytes=MAX_RISK_STRING_BYTES
            )
        if (
            len(set(risk.affected_tasks)) != len(risk.affected_tasks)
            or risk.affected_tasks != tuple(sorted(risk.affected_tasks))
            or _parse_utc(
                risk.suggested_deadline, field="risk.suggested_deadline"
            ) < analysed_at
        ):
            raise DecisionBriefValidationError("risk task/deadline ordering is invalid")
        risk_ids.append(risk.risk_id)
    if len(set(risk_ids)) != len(risk_ids) or risk_ids != sorted(risk_ids):
        raise DecisionBriefValidationError("risk IDs must be unique and ordered")
    _encode_json(report.to_dict(), max_bytes=MAX_RISK_REPORT_BYTES)

def _risk_digest(report: RiskReport) -> str:
    _validate_risk_report(report)
    return hashlib.sha256(
        _encode_json(report.to_dict(), max_bytes=MAX_RISK_REPORT_BYTES)
    ).hexdigest()

def _clone_risk_report(report: RiskReport) -> RiskReport:
    _validate_risk_report(report)
    risks = tuple(Risk(
        risk_id=item.risk_id,
        kind=item.kind,
        source=item.source,
        basis=item.basis,
        affected_tasks=tuple(item.affected_tasks),
        recommendation=item.recommendation,
        suggested_deadline=item.suggested_deadline,
        severity=item.severity,
        rationale=item.rationale,
    ) for item in report.risks)
    return RiskReport(
        merge_reporter_package_id=report.merge_reporter_package_id,
        project_id=report.project_id,
        analysed_at=report.analysed_at,
        risks=risks,
        coordination_meeting_recommended=report.coordination_meeting_recommended,
        requires_owner_confirmation=report.requires_owner_confirmation,
        formally_released=report.formally_released,
    )

def _clone_confirmation(item: RiskConfirmation) -> RiskConfirmation:
    return RiskConfirmation(
        confirmation_id=item.confirmation_id,
        payload=bytes(item.payload),
        signature=bytes(item.signature),
        receipt_id=item.receipt_id,
        snapshot_digest=item.snapshot_digest,
        risk_digest=item.risk_digest,
        confirmed_at=item.confirmed_at,
        confirmed_by=item.confirmed_by,
        report=_clone_risk_report(item.report),
    )

def _build_content(
    receipt: MergeCommitReceipt,
    report: RiskReport,
    brief_type: BriefType,
    *,
    period_start: str | None = None,
    period_end: str | None = None,
    topic_risk_ids: tuple[str, ...] | None = None,
) -> BriefContent:
    result = SourceReference(BriefSourceKind.RESULT_PACKAGE, receipt.package_id)
    receipt_source = SourceReference(BriefSourceKind.MERGE_RECEIPT, receipt.receipt_id)
    task = SourceReference(BriefSourceKind.TASK, receipt.task_id)
    changes = [BriefConclusion(
        conclusion_id="change.master_revision",
        text=f"Confirmed project master changed from {receipt.current_revision} to {receipt.merged_revision}.",
        sources=_stable_sources((result, receipt_source)),
    )]
    if receipt.completed_task_id is not None:
        changes.append(BriefConclusion(
            conclusion_id="change.completed_task",
            text=f"Task {receipt.completed_task_id} is confirmed complete.",
            sources=_stable_sources((
                SourceReference(BriefSourceKind.TASK, receipt.completed_task_id),
                result,
                receipt_source,
            )),
        ))
    # AC-5 type-specific parameters: fail closed on malformed values and
    # cross-type misuse. When omitted, the brief keeps the US-13-AC-1
    # label-only shape (backward compatible).
    if period_start is not None:
        _parse_utc(period_start, field="period_start")
    if period_end is not None:
        _parse_utc(period_end, field="period_end")
    if (
        period_start is not None
        and period_end is not None
        and period_end < period_start
    ):
        raise DecisionBriefValidationError(
            "period_end must be >= period_start"
        )
    topic_set: frozenset[str] | None = None
    if topic_risk_ids is not None:
        if (
            type(topic_risk_ids) is not tuple
            or not topic_risk_ids
            or any(type(item) is not str or not item for item in topic_risk_ids)
            or len(set(topic_risk_ids)) != len(topic_risk_ids)
        ):
            raise DecisionBriefValidationError(
                "topic_risk_ids must be a non-empty tuple of unique strings"
            )
        known = frozenset(risk.risk_id for risk in report.risks)
        unknown = sorted(set(topic_risk_ids) - known)
        if unknown:
            raise DecisionBriefValidationError(
                f"topic_risk_ids reference unknown risks: {unknown}"
            )
        topic_set = frozenset(topic_risk_ids)
    if brief_type is BriefType.PERIODIC:
        if topic_risk_ids is not None:
            raise DecisionBriefValidationError(
                "PERIODIC briefs cannot use topic_risk_ids"
            )
        if (period_start is None) != (period_end is None):
            raise DecisionBriefValidationError(
                "PERIODIC briefs require both period_start and period_end"
            )
    elif brief_type is BriefType.RISK_TOPIC:
        if period_start is not None or period_end is not None:
            raise DecisionBriefValidationError(
                "RISK_TOPIC briefs cannot use period bounds"
            )
        if topic_risk_ids is None:
            raise DecisionBriefValidationError(
                "RISK_TOPIC briefs require topic_risk_ids"
            )
    elif period_start is not None or period_end is not None or topic_risk_ids is not None:
        raise DecisionBriefValidationError(
            "STAGE briefs do not accept period or topic parameters"
        )
    severe = tuple(risk for risk in report.risks if risk.severity >= HIGH_RISK_MIN_SEVERITY)
    label = {
        BriefType.STAGE: "Stage decision brief",
        BriefType.PERIODIC: "Periodic decision report",
        BriefType.RISK_TOPIC: "Risk topic brief",
    }[brief_type]
    title = f"{label}: {receipt.snapshot.baseline.title}"
    if brief_type is BriefType.PERIODIC and period_start is not None:
        title = f"{title} ({period_start} -> {period_end})"
    if brief_type is BriefType.RISK_TOPIC and topic_set is not None:
        title = f"{title} [{', '.join(sorted(topic_set))}]"
    progress_text = (
        f"Project {receipt.project_id} is confirmed at {receipt.merged_revision}; "
        f"latest task status is {receipt.report_status.value}."
    )
    if brief_type is BriefType.PERIODIC and period_start is not None:
        progress_text = (
            f"Project {receipt.project_id} confirmed at {receipt.merged_revision} "
            f"for report period {period_start} to {period_end}; "
            f"latest task status is {receipt.report_status.value}."
        )
    progress = (BriefConclusion(
        conclusion_id="progress.confirmed",
        text=progress_text,
        sources=_stable_sources((task, result, receipt_source)),
    ),)
    if brief_type is BriefType.RISK_TOPIC and topic_set is not None:
        topic_risks = tuple(
            risk for risk in report.risks if risk.risk_id in topic_set
        )
        topic_severe = tuple(
            risk for risk in topic_risks
            if risk.severity >= HIGH_RISK_MIN_SEVERITY
        )
        return BriefContent(
            title=title,
            overall_progress=progress,
            important_changes=tuple(changes),
            high_risk_items=tuple(
                _risk_conclusion(risk, pending=False) for risk in topic_severe
            ),
            pending_decisions=tuple(
                _risk_conclusion(risk, pending=True) for risk in topic_risks
            ),
        )
    return BriefContent(
        title=title,
        overall_progress=progress,
        important_changes=tuple(changes),
        high_risk_items=tuple(_risk_conclusion(item, pending=False) for item in severe),
        pending_decisions=tuple(_risk_conclusion(item, pending=True) for item in severe),
    )

def _risk_conclusion(risk: Risk, *, pending: bool) -> BriefConclusion:
    sources = _stable_sources((
        SourceReference(BriefSourceKind.RISK, risk.risk_id),
        *(SourceReference(BriefSourceKind.TASK, item) for item in risk.affected_tasks),
    ))
    if pending:
        return BriefConclusion(
            conclusion_id=f"decision.{risk.risk_id}",
            text=f"Decision required for {risk.risk_id}: {risk.recommendation}",
            sources=sources,
        )
    return BriefConclusion(
        conclusion_id=f"risk.{risk.risk_id}",
        text=(
            f"High risk {risk.risk_id} ({risk.kind.value}, severity {risk.severity}) "
            f"affects {', '.join(risk.affected_tasks)}."
        ),
        sources=sources,
    )

def _make_version(**values: object) -> BriefVersion:
    content = values["content"]
    if type(content) is not BriefContent:
        # OPTIMIZE-2: an assert would be stripped under ``python -O``;
        # this is an internal type invariant that must stay fail-closed.
        raise DecisionBriefValidationError("version content must be BriefContent")
    content_digest = _content_digest(content)
    digest = _version_digest_values(
        revision=values["revision"],
        created_at=values["created_at"],
        edited_by=values["edited_by"],
        edit_reason=values["edit_reason"],
        source_receipt_id=values["source_receipt_id"],
        source_package_id=values["source_package_id"],
        content_digest=content_digest,
        previous_version_digest=values["previous_version_digest"],
    )
    return BriefVersion(
        **values,
        content_digest=content_digest,
        version_digest=digest,
    )

def _version_digest(version: BriefVersion) -> str:
    return _version_digest_values(
        revision=version.revision,
        created_at=version.created_at,
        edited_by=version.edited_by,
        edit_reason=version.edit_reason,
        source_receipt_id=version.source_receipt_id,
        source_package_id=version.source_package_id,
        content_digest=version.content_digest,
        previous_version_digest=version.previous_version_digest,
    )

def _version_digest_values(**values: object) -> str:
    return hashlib.sha256(_encode_json({
        "domain": BRIEF_DOMAIN,
        "schema_version": BRIEF_SCHEMA,
        **values,
    }, max_bytes=32 * 1024)).hexdigest()

def _content_digest(content: BriefContent) -> str:
    return hashlib.sha256(
        _encode_json(_content_plain(content), max_bytes=MAX_BRIEF_CONTENT_BYTES)
    ).hexdigest()

def _content_plain(content: BriefContent) -> dict[str, object]:
    names = ("overall_progress", "important_changes", "high_risk_items", "pending_decisions")
    return {
        "title": content.title,
        **{
            name: [
                {
                    "conclusion_id": item.conclusion_id,
                    "text": item.text,
                    "sources": [
                        {"kind": source.kind.value, "reference_id": source.reference_id}
                        for source in item.sources
                    ],
                }
                for item in getattr(content, name)
            ]
            for name in names
        },
    }

def _validate_stored_brief(brief: DecisionBrief) -> None:
    if type(brief) is not DecisionBrief:
        raise DecisionBriefValidationError("stored brief type is invalid")
    _safe_string(brief.brief_id, field="brief_id", max_bytes=1024)
    _safe_string(brief.project_id, field="project_id", max_bytes=1024)
    if type(brief.brief_type) is not BriefType or type(brief.versions) is not tuple:
        raise DecisionBriefValidationError("stored brief shape is invalid")
    previous = _ZERO_DIGEST
    for expected_revision, version in enumerate(brief.versions, start=1):
        if type(version) is not BriefVersion or version.revision != expected_revision:
            raise DecisionBriefValidationError("stored brief revisions are invalid")
        _validate_content_model(version.content)
        if (
            type(version.content) is not BriefContent
            or version.content_digest != _content_digest(version.content)
            or version.previous_version_digest != previous
            or version.version_digest != _version_digest(version)
            or version.requires_user_review is not True
            or version.formally_released is not False
        ):
            raise DecisionBriefValidationError("stored brief hash chain is invalid")
        previous = version.version_digest
    if not brief.versions or type(brief.wps_request) is not WpsDocumentRequest:
        raise DecisionBriefValidationError("stored brief request is invalid")
    WpsDocumentRequest(
        brief_id=brief.wps_request.brief_id,
        source_revision=brief.wps_request.source_revision,
        template_ref=brief.wps_request.template_ref,
        template_approval_id=brief.wps_request.template_approval_id,
        template_digest=brief.wps_request.template_digest,
        tool_id=brief.wps_request.tool_id,
        operation=brief.wps_request.operation,
        save_mode=brief.wps_request.save_mode,
        output_format=brief.wps_request.output_format,
        macros_allowed=brief.wps_request.macros_allowed,
        requires_user_confirmation=brief.wps_request.requires_user_confirmation,
    )
    if (
        brief.wps_request.brief_id != brief.brief_id
        or brief.wps_request.source_revision != brief.current.revision
    ):
        raise DecisionBriefValidationError("stored WPS request binding is invalid")

def _validate_content_model(content: object) -> None:
    if type(content) is not BriefContent:
        raise DecisionBriefValidationError("stored brief content type is invalid")
    for section in content.sections:
        if type(section) is not tuple:
            raise DecisionBriefValidationError("stored brief section type is invalid")
        for conclusion in section:
            if type(conclusion) is not BriefConclusion:
                raise DecisionBriefValidationError("stored conclusion type is invalid")
            sources = []
            for source in conclusion.sources:
                if type(source) is not SourceReference:
                    raise DecisionBriefValidationError("stored source type is invalid")
                sources.append(SourceReference(source.kind, source.reference_id))
            BriefConclusion(
                conclusion_id=conclusion.conclusion_id,
                text=conclusion.text,
                sources=tuple(sources),
            )
    BriefContent(
        title=content.title,
        overall_progress=content.overall_progress,
        important_changes=content.important_changes,
        high_risk_items=content.high_risk_items,
        pending_decisions=content.pending_decisions,
    )

def _clone_content(content: BriefContent) -> BriefContent:
    _validate_content_model(content)

    def clone_section(
        section: tuple[BriefConclusion, ...],
    ) -> tuple[BriefConclusion, ...]:
        return tuple(BriefConclusion(
            conclusion_id=item.conclusion_id,
            text=item.text,
            sources=tuple(SourceReference(source.kind, source.reference_id)
                          for source in item.sources),
        ) for item in section)

    return BriefContent(
        title=content.title,
        overall_progress=clone_section(content.overall_progress),
        important_changes=clone_section(content.important_changes),
        high_risk_items=clone_section(content.high_risk_items),
        pending_decisions=clone_section(content.pending_decisions),
    )

def _clone_brief(brief: DecisionBrief) -> DecisionBrief:
    _validate_stored_brief(brief)
    versions = tuple(BriefVersion(
        revision=item.revision,
        created_at=item.created_at,
        edited_by=item.edited_by,
        edit_reason=item.edit_reason,
        source_receipt_id=item.source_receipt_id,
        source_package_id=item.source_package_id,
        content=_clone_content(item.content),
        content_digest=item.content_digest,
        previous_version_digest=item.previous_version_digest,
        version_digest=item.version_digest,
        requires_user_review=item.requires_user_review,
        formally_released=item.formally_released,
    ) for item in brief.versions)
    request = brief.wps_request
    return DecisionBrief(
        brief_id=brief.brief_id,
        project_id=brief.project_id,
        brief_type=brief.brief_type,
        versions=versions,
        wps_request=WpsDocumentRequest(
            brief_id=request.brief_id,
            source_revision=request.source_revision,
            template_ref=request.template_ref,
            template_approval_id=request.template_approval_id,
            template_digest=request.template_digest,
            tool_id=request.tool_id,
            operation=request.operation,
            save_mode=request.save_mode,
            output_format=request.output_format,
            macros_allowed=request.macros_allowed,
            requires_user_confirmation=request.requires_user_confirmation,
        ),
    )

def _brief_id(receipt: MergeCommitReceipt, brief_type: BriefType) -> str:
    digest = hashlib.sha256(
        f"{receipt.receipt_id}\0{brief_type.value}".encode("utf-8")
    ).hexdigest()[:24]
    return f"brief.{brief_type.value}.{digest}"

def _stable_sources(sources: tuple[SourceReference, ...]) -> tuple[SourceReference, ...]:
    return tuple(sorted(set(sources), key=_source_sort_key))

def _content_sources(content: BriefContent) -> tuple[SourceReference, ...]:
    return tuple(
        source
        for section in content.sections
        for conclusion in section
        for source in conclusion.sources
    )

def _source_sort_key(source: SourceReference) -> tuple[str, str]:
    return source.kind.value, source.reference_id

def _validate_template_ref(value: object) -> None:
    _safe_string(value, field="template_ref", max_bytes=1024)
    if "\\" in value or ":" in value or value.startswith("/"):
        raise DecisionBriefValidationError("template_ref must be relative POSIX path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or path.suffix.lower() != ".docx"
    ):
        raise DecisionBriefValidationError("template_ref must be safe relative .docx")

def _validate_docx(payload: bytes) -> None:
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
            infos = archive.infolist()
            if len(infos) > MAX_TEMPLATE_ZIP_ENTRIES:
                raise DecisionBriefValidationError("template has too many ZIP entries")
            lowered = tuple(
                info.filename.replace("\\", "/").lower() for info in infos
            )
            if (
                len(set(lowered)) != len(lowered)
                or any(
                    len(name.encode("utf-8")) > 1024
                    or name.startswith("/")
                    or ".." in PurePosixPath(name).parts
                    for name in lowered
                )
            ):
                raise DecisionBriefValidationError("template ZIP names are unsafe")
            if (
                "[content_types].xml" not in lowered
                or "word/document.xml" not in lowered
            ):
                raise DecisionBriefValidationError("template is not a DOCX package")
            total = 0
            for info in infos:
                if info.is_dir():
                    continue
                total += info.file_size
                if total > MAX_TEMPLATE_UNCOMPRESSED_BYTES:
                    raise DecisionBriefValidationError("template expands beyond policy")
                if info.flag_bits & 0x1:
                    raise DecisionBriefValidationError("encrypted template is forbidden")
            metadata = b"".join(
                archive.read(info).lower()
                for info, name in zip(infos, lowered)
                if name in {
                    "[content_types].xml",
                    "_rels/.rels",
                    "word/_rels/document.xml.rels",
                }
            )
            if any(
                name.endswith("vbaproject.bin")
                or "/macros/" in f"/{name}/"
                or name.endswith(".docm")
                for name in lowered
            ) or b"macroenabled" in metadata or b"vbaproject" in metadata:
                raise DecisionBriefValidationError("template contains macros")
    except (zipfile.BadZipFile, OSError) as exc:
        raise DecisionBriefValidationError("template is not a valid DOCX ZIP") from exc

def _is_link_or_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError as exc:
        raise DecisionBriefValidationError("template path is unavailable") from exc
    return stat.S_ISLNK(info.st_mode) or _stat_is_reparse(info)

def _stat_is_reparse(info: os.stat_result) -> bool:
    return bool(getattr(info, "st_file_attributes", 0) & _REPARSE_POINT)

def _safe_string(value: object, *, field: str, max_bytes: int) -> None:
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        raise DecisionBriefValidationError(f"{field} must be a non-empty safe string")
    if len(value.encode("utf-8")) > max_bytes:
        raise DecisionBriefValidationError(f"{field} exceeds byte limit")

def _digest(value: object, *, field: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise DecisionBriefValidationError(f"{field} must be lowercase SHA-256")

def _parse_utc(value: object, *, field: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise DecisionBriefValidationError(f"{field} must be ISO-8601 UTC")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise DecisionBriefValidationError(f"{field} must be valid ISO-8601 UTC") from exc
    if parsed.utcoffset() != dt.timedelta(0):
        raise DecisionBriefValidationError(f"{field} must use UTC")
    return parsed

def _encode_json(value: object, *, max_bytes: int) -> bytes:
    try:
        payload = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        raise DecisionBriefValidationError("value is not canonical JSON") from exc
    if len(payload) > max_bytes:
        raise DecisionBriefValidationError("canonical payload exceeds byte limit")
    return payload
