"""decision_brief.service - DecisionBriefService facade and its private helpers."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 决策简报服务（US-13）：
#   generate()：只消费“最新 verified 合并回执”与“负责人密钥签名的风险
#     确认”，二者缺一即拒绝；支持 STAGE/PERIODIC/RISK_TOPIC 三种类型，
#     内容逐结论绑定 task/result/risk/receipt 来源，保证可追溯。
#   revise()：修订走 CAS（revision + head_digest），旧事件重放拒绝，
#     修订历史以内容哈希链保存（AC-7）。
#   模板治理：ApprovedTemplateRegistry 每次实际复验受控 DOCX；生成的
#     WPS 请求只创建新版本副本并强制人工确认，不自动执行宏。
#   关键不变量：风险确认必须由项目负责人证书身份签署且与回执绑定；
#     未经确认的风险不得进入简报。

from __future__ import annotations

from src.coevo.merge.repository import MergeReceiptRepository

from .models import BRIEF_SCHEMA, BriefContent, BriefType, DecisionBrief, DecisionBriefValidationError, WpsDocumentRequest, _ZERO_DIGEST, _brief_id, _build_content, _content_sources, _latest_receipt, _make_version, _parse_utc, _safe_string, _validate_bound_risk

from .repositories import ApprovedTemplateRegistry, DecisionBriefRepository, RiskConfirmationRepository

class DecisionBriefService:
    """Generate and revise review-required decision-brief drafts."""

    def generate(
        self,
        *,
        receipt_id: str,
        receipt_repository: MergeReceiptRepository,
        risk_confirmation_id: str,
        risk_repository: RiskConfirmationRepository,
        brief_repository: DecisionBriefRepository,
        brief_type: BriefType,
        template_ref: str,
        template_approval_id: str,
        template_registry: ApprovedTemplateRegistry,
        generated_at: str,
        actor_id: str,
        event_id: str,
        period_start: str | None = None,
        period_end: str | None = None,
        topic_risk_ids: tuple[str, ...] | None = None,
    ) -> DecisionBrief:
        generated_time = _parse_utc(generated_at, field="generated_at")
        _safe_string(actor_id, field="actor_id", max_bytes=1024)
        if type(risk_repository) is not RiskConfirmationRepository:
            raise DecisionBriefValidationError("authoritative risk repository required")
        if type(brief_repository) is not DecisionBriefRepository:
            raise DecisionBriefValidationError("authoritative brief repository required")
        if type(template_registry) is not ApprovedTemplateRegistry:
            raise DecisionBriefValidationError("approved template registry required")
        if type(brief_type) is not BriefType:
            raise DecisionBriefValidationError("brief_type is not supported")
        receipt = _latest_receipt(receipt_id, receipt_repository, generated_time)
        confirmation = risk_repository.verified(
            risk_confirmation_id, receipt=receipt, trusted_time=generated_time
        )
        _validate_bound_risk(receipt, confirmation.report, generated_time)
        approval = template_registry.verify(
            approval_id=template_approval_id, template_ref=template_ref
        )
        brief_id = _brief_id(receipt, brief_type)
        content = _build_content(
            receipt,
            confirmation.report,
            brief_type,
            period_start=period_start,
            period_end=period_end,
            topic_risk_ids=topic_risk_ids,
        )
        initial = _make_version(
            revision=1,
            created_at=generated_at,
            edited_by=actor_id,
            edit_reason="generated from latest owner-confirmed project state",
            source_receipt_id=receipt.receipt_id,
            source_package_id=receipt.package_id,
            content=content,
            previous_version_digest=_ZERO_DIGEST,
        )
        brief = DecisionBrief(
            brief_id=brief_id,
            project_id=receipt.project_id,
            brief_type=brief_type,
            versions=(initial,),
            wps_request=WpsDocumentRequest(
                brief_id=brief_id,
                source_revision=1,
                template_ref=template_ref,
                template_approval_id=approval.approval_id,
                template_digest=approval.template_digest,
            ),
        )
        return brief_repository.create(brief, event_id=event_id)

    def revise(
        self,
        *,
        brief_id: str,
        brief_repository: DecisionBriefRepository,
        content: BriefContent,
        editor_id: str,
        edit_reason: str,
        edited_at: str,
        expected_revision: int,
        expected_head_digest: str,
        event_id: str,
        template_registry: ApprovedTemplateRegistry,
    ) -> DecisionBrief:
        if type(brief_repository) is not DecisionBriefRepository:
            raise DecisionBriefValidationError("authoritative brief repository required")
        if type(template_registry) is not ApprovedTemplateRegistry:
            raise DecisionBriefValidationError("exact template registry is required")
        return brief_repository.revise(
            brief_id=brief_id,
            content=content,
            editor_id=editor_id,
            edit_reason=edit_reason,
            edited_at=edited_at,
            expected_revision=expected_revision,
            expected_head_digest=expected_head_digest,
            event_id=event_id,
            template_registry=template_registry,
        )

    def to_audit_record(self, brief: DecisionBrief) -> dict[str, object]:
        if type(brief) is not DecisionBrief:
            raise DecisionBriefValidationError("brief must be exact DecisionBrief")
        content = brief.current.content
        return {
            "kind": "decision_brief.draft",
            "schema_version": BRIEF_SCHEMA,
            "brief_id": brief.brief_id,
            "project_id": brief.project_id,
            "brief_type": brief.brief_type.value,
            "revision": brief.current.revision,
            "head_digest": brief.head_digest,
            "source_receipt_id": brief.current.source_receipt_id,
            "source_package_id": brief.current.source_package_id,
            "source_count": len(set(_content_sources(content))),
            "high_risk_count": len(content.high_risk_items),
            "pending_decision_count": len(content.pending_decisions),
            "requires_user_review": True,
            "formally_released": False,
        }
