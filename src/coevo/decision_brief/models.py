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
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from src.coevo.risk import Risk, RiskKind, RiskReport, SourceKind
from ._util import (
    _ZERO_DIGEST,
    _digest as _util_digest,
    _encode_json as _util_encode_json,
    _is_link_or_reparse as _util_is_link_or_reparse,
    _parse_utc as _util_parse_utc,
    _safe_string as _util_safe_string,
    _stat_is_reparse as _stat_is_reparse,
)

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


def _is_link_or_reparse(path: Path) -> bool:
    return _util_is_link_or_reparse(path, error_factory=DecisionBriefValidationError)

def _safe_string(value: object, *, field: str, max_bytes: int) -> None:
    _util_safe_string(
        value,
        field=field,
        max_bytes=max_bytes,
        error_factory=DecisionBriefValidationError,
    )

def _digest(value: object, *, field: str) -> None:
    _util_digest(value, field=field, error_factory=DecisionBriefValidationError)

def _parse_utc(value: object, *, field: str) -> dt.datetime:
    return _util_parse_utc(
        value,
        field=field,
        error_factory=DecisionBriefValidationError,
        not_utc_message=f"{field} must be ISO-8601 UTC",
        invalid_message=f"{field} must be valid ISO-8601 UTC",
    )

def _encode_json(value: object, *, max_bytes: int) -> bytes:
    return _util_encode_json(
        value, max_bytes=max_bytes, error_factory=DecisionBriefValidationError
    )

# FRAMEWORK-OPTIMIZE-20: domain construction/validation helpers moved to `_build`
# (per-function lazy imports avoid a dataclass __post_init__ <-> helper cycle);
# the historical import surface is preserved by re-exporting here.
from ._build import (
    _brief_id,
    _build_content,
    _clone_brief,
    _clone_confirmation,
    _clone_content,
    _clone_risk_report,
    _latest_receipt,
    _make_version,
    _risk_conclusion,
    _validate_bound_risk,
    _validate_content_model,
    _validate_docx,
    _validate_stored_brief,
)
