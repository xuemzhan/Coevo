"""Domain construction / validation helpers for decision-brief models (FRAMEWORK-OPTIMIZE-20).

These helpers are not required by dataclass ``__post_init__`` and were moved out of ``models.py``
using per-function lazy imports so the dataclass <-> helper module cycle is avoided. The historical import surface
(``from .models import _build_content`` etc.) is preserved by ``models.py`` re-exporting this module at the bottom.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import zipfile
from pathlib import PurePosixPath
from src.coevo.merge.receipt import MergeCommitReceipt
from src.coevo.merge.repository import MergeReceiptRepository
from src.coevo.risk import Risk, RiskReport

def _latest_receipt(
    receipt_id: str,
    repository: MergeReceiptRepository,
    trusted_time: dt.datetime,
) -> MergeCommitReceipt:
    from .models import DecisionBriefValidationError, _safe_string
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
    from .models import DecisionBriefValidationError, _parse_utc, _validate_risk_report
    _validate_risk_report(report)
    if report.project_id != receipt.project_id:
        raise DecisionBriefValidationError("risk report project mismatch")
    if report.merge_reporter_package_id != receipt.package_id:
        raise DecisionBriefValidationError("risk report package mismatch")
    analysed = _parse_utc(report.analysed_at, field="analysed_at")
    committed = _parse_utc(receipt.commit_decided_at, field="commit_decided_at")
    if analysed < committed or analysed > trusted_time:
        raise DecisionBriefValidationError("risk analysis time is outside trusted bounds")

def _clone_risk_report(report: RiskReport) -> RiskReport:
    from .models import _validate_risk_report
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
    from .models import RiskConfirmation
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
    from .models import (
        BriefConclusion,
        BriefContent,
        BriefSourceKind,
        BriefType,
        DecisionBriefValidationError,
        HIGH_RISK_MIN_SEVERITY,
        SourceReference,
        _parse_utc,
        _stable_sources,
    )
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
    from .models import (
        BriefConclusion,
        BriefSourceKind,
        SourceReference,
        _stable_sources,
    )
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
    from .models import (
        BriefContent,
        BriefVersion,
        DecisionBriefValidationError,
        _content_digest,
        _version_digest_values,
    )
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

def _validate_stored_brief(brief: DecisionBrief) -> None:
    from .models import (
        BriefContent,
        BriefType,
        BriefVersion,
        DecisionBrief,
        DecisionBriefValidationError,
        WpsDocumentRequest,
        _ZERO_DIGEST,
        _content_digest,
        _safe_string,
        _version_digest,
    )
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
    from .models import (
        BriefConclusion,
        BriefContent,
        DecisionBriefValidationError,
        SourceReference,
    )
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
    from .models import BriefConclusion, BriefContent, SourceReference
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
    from .models import BriefVersion, DecisionBrief, WpsDocumentRequest
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
    from .models import BriefType
    digest = hashlib.sha256(
        f"{receipt.receipt_id}\0{brief_type.value}".encode("utf-8")
    ).hexdigest()[:24]
    return f"brief.{brief_type.value}.{digest}"

def _validate_docx(payload: bytes) -> None:
    from .models import (
        DecisionBriefValidationError,
        MAX_TEMPLATE_UNCOMPRESSED_BYTES,
        MAX_TEMPLATE_ZIP_ENTRIES,
    )
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
