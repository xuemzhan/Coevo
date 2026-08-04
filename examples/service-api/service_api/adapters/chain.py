from __future__ import annotations

import base64
import json
from typing import Any

from src.coevo.decision_brief import (  # noqa: E402
    BriefType,
    DecisionBriefService,
)
from src.coevo.knowledge_base import (  # noqa: E402
    KnowledgeBaseFacade,
    ReviewDecision,
    ReviewDecisionKind,
)
from src.coevo.protocol import (  # noqa: E402
    PackageImportService,
    ProcessedPackage,
    ProcessedPackageStore,
    ReplayDecision,
    ReplayOutcome,
    check_replay,
    parse_package_bytes,
)
from src.coevo.protocol.sm2_sign import compute_sm3_digest  # noqa: E402
from src.coevo.risk import merge_and_analyze  # noqa: E402
from src.coevo.supervision import SupervisionCoordinator  # noqa: E402

from ._core import OWNER_CERT, _require_param
from ..contract import ErrorCode, ServiceError  # noqa: E402


def merge_analyze(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """合并最近一次成果汇报并做风险预检（US-10/US-11）。"""
    state = ctx["project_state"]
    if state["baseline"] is None or state["report"] is None:
        raise ServiceError(
            ErrorCode.CONFLICT,
            "project_state missing baseline or report; run decomposition.propose "
            "and report.build first",
        )
    report = state["report"]["manifest"]
    merged_packages = ctx.setdefault("merged_packages", set())
    if report.package_id in merged_packages:
        raise ServiceError(
            ErrorCode.CONFLICT,
            f"report {report.package_id} already merged (AC-2 duplicate)",
        )
    wire = base64.b64decode(state["report"]["wire_base64"], validate=True)
    package = parse_package_bytes(wire)
    digest = compute_sm3_digest(wire)
    candidate = ProcessedPackage(
        package_id=package.envelope.package_id,
        package_digest=digest,
        sender_cert_id=report.sender_cert_id,
        recipient_cert_id=report.recipient_cert_id,
        project_id=report.project_id,
        sequence_no=report.sequence_no,
    )
    replay = check_replay(candidate=candidate, registry=())
    imported = PackageImportService().import_package(
        package=package,
        replay_decision=ReplayDecision(
            replay.outcome, replay.previous_sequence_no, replay.detail
        ),
        store=ProcessedPackageStore.empty(),
        base_revision=report.base_revision,
        current_revision=report.base_revision,
        processed_at=request.ts,
    )
    with ctx["store_lock"]:
        outcome = merge_and_analyze(
            engine=ctx["merge_engine"],
            import_outcome=imported,
            report=report,
            baseline=state["baseline"],
            store=ProcessedPackageStore.empty(),
            receipt_repository=ctx["receipt_repository"],
            decided_at=request.ts,
            now=request.ts,
            authorized_recipient_certs=frozenset({OWNER_CERT}),
        )
    if not outcome.commit.proposal.accepted or outcome.commit.receipt is None:
        raise ServiceError(
            ErrorCode.CONFLICT,
            f"merge rejected: {outcome.commit.proposal.rejection_reason}",
        )
    state["baseline"] = outcome.commit.proposal.new_baseline
    state["risk_report"] = outcome.risk_report
    state["receipt"] = outcome.commit.receipt
    merged_packages.add(report.package_id)
    return {
        "merged_version": outcome.commit.proposal.record.merged_version,
        "receipt_id": outcome.commit.receipt.receipt_id,
        "risk_kinds": (
            [risk.kind.value for risk in outcome.risk_report.risks]
            if outcome.risk_report else []
        ),
    }
def risk_analyze(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """返回最近一次合并后的风险报告明细（US-11）。"""
    report = ctx["project_state"].get("risk_report")
    if report is None:
        raise ServiceError(ErrorCode.CONFLICT, "no risk report in project_state")
    return {
        "project_id": report.project_id,
        "analysed_at": report.analysed_at,
        "coordination_meeting_recommended": report.coordination_meeting_recommended,
        "risks": [
            {
                "risk_id": risk.risk_id,
                "kind": risk.kind.value,
                "source": risk.source.value,
                "severity": risk.severity,
                "basis": risk.basis,
                "recommendation": risk.recommendation,
            }
            for risk in report.risks
        ],
    }
def supervision_coordinate(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """把已确认风险转为督办事项与会议提案（US-12）。"""
    report = ctx["project_state"].get("risk_report")
    if report is None:
        raise ServiceError(ErrorCode.CONFLICT, "no risk report in project_state")
    outcome = SupervisionCoordinator().coordinate(
        risk_report=report,
        project_recipient_cert_id=OWNER_CERT,
        now=request.ts,
    )
    return {
        "supervision_items": [
            {
                "item_id": item.item_id,
                "risk_kind": item.risk_kind.value,
                "due_at": item.due_at,
                "closing_condition": item.closing_condition,
            }
            for item in outcome.items
        ],
        "meeting_proposal_id": (
            outcome.meeting_proposal.proposal_id
            if outcome.meeting_proposal is not None else None
        ),
        "conclusion_count": len(outcome.conclusions),
    }
def brief_generate(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """负责人确认风险后生成决策简报（US-13，三类类型）。"""
    state = ctx["project_state"]
    if state["receipt"] is None or state["risk_report"] is None:
        raise ServiceError(ErrorCode.CONFLICT, "missing receipt or risk in project_state")
    brief_type = BriefType(str(_require_param(request, "brief_type")))
    confirmation = ctx["risk_confirmation_repository"].confirm(
        receipt_id=state["receipt"].receipt_id,
        receipt_repository=ctx["receipt_repository"],
        risk_report=state["risk_report"],
        confirmed_at=request.ts,
        confirmed_by=OWNER_CERT,
        event_id=f"brief.{request.request_id}",
    )
    kwargs: dict[str, Any] = {}
    if brief_type is BriefType.PERIODIC:
        kwargs.update(
            period_start=str(request.params.get("period_start", "")),
            period_end=str(request.params.get("period_end", "")),
        )
    if brief_type is BriefType.RISK_TOPIC:
        kwargs["topic_risk_ids"] = tuple(
            request.params.get("topic_risk_ids", [])
        )
    brief = DecisionBriefService().generate(
        receipt_id=state["receipt"].receipt_id,
        receipt_repository=ctx["receipt_repository"],
        risk_confirmation_id=confirmation.confirmation_id,
        risk_repository=ctx["risk_confirmation_repository"],
        brief_repository=ctx["brief_repository"],
        brief_type=brief_type,
        template_ref=ctx["template_ref"],
        template_approval_id=ctx["template_approval"].approval_id,
        template_registry=ctx["template_registry"],
        generated_at=request.ts,
        actor_id=OWNER_CERT,
        event_id=f"brief.{request.request_id}",
        **kwargs,
    )
    state["brief"] = brief
    return {
        "brief_id": brief.brief_id,
        "brief_type": brief.brief_type.value,
        "revision": brief.current.revision,
        "high_risk_count": len(brief.current.content.high_risk_items),
        "pending_decision_count": len(brief.current.content.pending_decisions),
    }
def knowledge_aggregate(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """汇总项目知识并生成复盘草稿/可复用模板（US-14）。"""
    state = ctx["project_state"]
    bundle = KnowledgeBaseFacade.aggregate(
        project_id=str(_require_param(request, "project_id")),
        baseline=request.params.get("baseline") or (
            {
                "title": state["baseline"].title,
                "summary": state["baseline"].objective,
                "stages": [wp.standard_stage for wp in state["baseline"].work_packages],
                "work_packages": [wp.work_package_id for wp in state["baseline"].work_packages],
            }
            if state["baseline"] is not None else None
        ),
        merge_records=tuple(request.params.get("merge_records", [])),
        risk_reports=tuple(request.params.get("risk_reports", [])),
        decision_briefs=tuple(request.params.get("decision_briefs", [])),
        meeting_conclusions=tuple(request.params.get("meeting_conclusions", [])),
        progress_captures=tuple(request.params.get("progress_captures", [])),
        model_summaries=tuple(request.params.get("model_summaries", [])),
        now=request.ts,
    )
    decisions = tuple(
        ReviewDecision(
            decision_id=f"rev.{index}",
            entry_id=entry.entry_id,
            decision=ReviewDecisionKind.APPROVE,
            decided_by=OWNER_CERT,
            reason="服务框架统一审批入库",
            decided_at=request.ts,
        )
        for index, entry in enumerate(bundle.entries)
    )
    committed = KnowledgeBaseFacade.review(
        bundle, decisions=decisions, now=request.ts
    )
    with ctx["store_lock"]:
        ctx["knowledge_store"].save(committed, now=request.ts)
    return {
        "bundle_id": committed.bundle_id,
        "entry_count": len(committed.entries),
        "reusable_template_count": len(committed.reusable_templates),
        "retrospective_sections": len(committed.retrospective.body_sections),
        "formally_committed": committed.formally_committed,
    }
