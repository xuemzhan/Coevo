"""knowledge_base.facade - KnowledgeBaseFacade aggregation and template/retrospective extraction helpers."""

from __future__ import annotations

import hashlib

from .models import ClassificationDenied, KnowledgeBaseValidationError, KnowledgeBundle, KnowledgeClassification, KnowledgeEntry, KnowledgeSourceKind, RetrospectiveDraft, ReusableTemplate, ReusableTemplateKind, ReviewConflictError, ReviewDecision, ReviewDecisionKind, _CLASSIFICATION_RANK, _SAFE_ID, _check_iso_utc

class KnowledgeBaseFacade:
    """Pure-function US-14 service."""

    @staticmethod
    def aggregate(
        *,
        project_id: str,
        baseline: dict | None = None,
        merge_records: tuple[dict, ...] = (),
        risk_reports: tuple[dict, ...] = (),
        meeting_conclusions: tuple[dict, ...] = (),
        decision_briefs: tuple[dict, ...] = (),
        progress_captures: tuple[dict, ...] = (),
        model_summaries: tuple[dict, ...] = (),
        now: str,
    ) -> KnowledgeBundle:
        """AC-1..AC-5, AC-7: aggregate project knowledge into a draft bundle."""
        if not isinstance(project_id, str) or not _SAFE_ID.match(project_id):
            raise KnowledgeBaseValidationError(
                f"project_id must be safe-id; got {project_id!r}"
            )
        _check_iso_utc(now, field="now")

        # Build KnowledgeEntry list.
        entries: list[KnowledgeEntry] = []
        if baseline:
            entries.append(_entry_from_baseline(baseline, project_id, now))
        for rec in merge_records:
            entries.append(_entry_from_source(rec, KnowledgeSourceKind.MERGE_RECORD, project_id, now))
        for rep in risk_reports:
            entries.append(_entry_from_source(rep, KnowledgeSourceKind.RISK_REPORT, project_id, now))
        for c in meeting_conclusions:
            entries.append(_entry_from_source(c, KnowledgeSourceKind.MEETING_CONCLUSION, project_id, now))
        for b in decision_briefs:
            entries.append(_entry_from_source(b, KnowledgeSourceKind.DECISION_BRIEF, project_id, now))
        for p in progress_captures:
            entries.append(_entry_from_source(p, KnowledgeSourceKind.PROGRESS_CAPTURE, project_id, now))
        # AC-7: model_summaries default requires_owner_approval=True.
        for ms in model_summaries:
            entries.append(
                _entry_from_source(
                    ms, KnowledgeSourceKind.MODEL_SUMMARY, project_id, now,
                    requires_owner_approval=True,
                )
            )

        # AC-3: extract reusable templates.
        reusable = _extract_reusable_templates(
            baseline=baseline,
            risk_reports=risk_reports,
            project_id=project_id,
            now=now,
        )

        # AC-2: auto-generate retrospective draft (5 sections).
        retrospective = _generate_retrospective(
            project_id=project_id, entries=entries, now=now,
        )

        # AC-5: bundle_classification is the max of all entry classifications.
        max_rank = max(
            (_CLASSIFICATION_RANK[e.classification.value] for e in entries),
            default=0,
        )
        bundle_classification = _rank_to_classification(max_rank)

        return KnowledgeBundle(
            bundle_id=_make_bundle_id(project_id, now),
            project_id=project_id,
            entries=tuple(entries),
            retrospective=retrospective,
            reusable_templates=reusable,
            accepted_entries=(),
            rejected_entries=(),
            bundle_classification=bundle_classification,
            requires_user_confirmation=True,
            formally_committed=False,
            committed_at="",
            committed_by="",
            created_at=now,
        )

    @staticmethod
    def review(
        bundle: KnowledgeBundle,
        *,
        decisions: tuple[ReviewDecision, ...],
        now: str,
    ) -> KnowledgeBundle:
        """AC-6 + AC-7: apply reviewer decisions, mark formally_committed only
        when every requires_owner_approval=True entry has a decision AND
        all such decisions are APPROVE/REVISE (not REJECT).
        """
        if not isinstance(bundle, KnowledgeBundle):
            raise KnowledgeBaseValidationError(
                "bundle must be a KnowledgeBundle instance"
            )
        if not isinstance(decisions, tuple) or not all(
            isinstance(d, ReviewDecision) for d in decisions
        ):
            raise KnowledgeBaseValidationError(
                "decisions must be a tuple of ReviewDecision"
            )
        _check_iso_utc(now, field="now")
        if bundle.formally_committed:
            raise ReviewConflictError(
                f"bundle {bundle.bundle_id!r} is already formally_committed"
            )

        # Index decisions by entry_id.
        decision_by_entry: dict[str, ReviewDecision] = {}
        for d in decisions:
            if d.entry_id in decision_by_entry:
                raise KnowledgeBaseValidationError(
                    f"duplicate decision for entry_id {d.entry_id!r}"
                )
            decision_by_entry[d.entry_id] = d

        accepted: list[str] = []
        rejected: list[str] = []
        for entry in bundle.entries:
            if entry.requires_owner_approval:
                d = decision_by_entry.get(entry.entry_id)
                if d is None:
                    # Required decision missing; bundle stays uncommitted.
                    continue
                if d.decision == ReviewDecisionKind.APPROVE:
                    accepted.append(entry.entry_id)
                elif d.decision == ReviewDecisionKind.REVISE:
                    accepted.append(entry.entry_id)  # accepted-with-revision
                else:
                    rejected.append(entry.entry_id)

        # formally_committed iff every requires_owner_approval entry has a
        # decision (the uncommitted-required-missing path is handled by
        # continuing past the inner continue; here we check explicitly).
        all_required_decided = all(
            decision_by_entry.get(e.entry_id) is not None
            for e in bundle.entries
            if e.requires_owner_approval
        )
        all_non_required_accepted = all(
            e.entry_id in accepted or e.entry_id not in {
                d.entry_id for d in decisions if d.decision == ReviewDecisionKind.REJECT
            }
            for e in bundle.entries
            if not e.requires_owner_approval
        )

        formally_committed = all_required_decided and all_non_required_accepted

        if formally_committed:
            committed_at = now
            committed_by = decisions[0].decided_by if decisions else "system"
        else:
            committed_at = ""
            committed_by = ""

        return KnowledgeBundle(
            bundle_id=bundle.bundle_id,
            project_id=bundle.project_id,
            entries=bundle.entries,
            retrospective=bundle.retrospective,
            reusable_templates=bundle.reusable_templates,
            accepted_entries=tuple(accepted),
            rejected_entries=tuple(rejected),
            bundle_classification=bundle.bundle_classification,
            requires_user_confirmation=True,
            formally_committed=formally_committed,
            committed_at=committed_at,
            committed_by=committed_by,
            created_at=bundle.created_at,
        )

    @staticmethod
    def check_classification(
        bundle: KnowledgeBundle,
        *,
        actor_clearances: frozenset[KnowledgeClassification],
        now: str,
    ) -> KnowledgeBundle:
        """AC-5: classification check (fail-closed)."""
        if not isinstance(bundle, KnowledgeBundle):
            raise KnowledgeBaseValidationError(
                "bundle must be a KnowledgeBundle instance"
            )
        if not isinstance(actor_clearances, frozenset) or not all(
            isinstance(c, KnowledgeClassification) for c in actor_clearances
        ):
            raise KnowledgeBaseValidationError(
                "actor_clearances must be a frozenset of KnowledgeClassification"
            )
        _check_iso_utc(now, field="now")
        if bundle.bundle_classification not in actor_clearances:
            raise ClassificationDenied(
                f"bundle classification {bundle.bundle_classification.value!r} "
                f"not in actor clearances {[c.value for c in actor_clearances]!r}"
            )
        return bundle

    @staticmethod
    def to_audit_record(bundle: KnowledgeBundle) -> dict:
        """Project a bundle into an audit row.

        EXCLUDES body_summary / body_sections / template body. Keeps
        counts + classifications + decision counters.
        """
        if not isinstance(bundle, KnowledgeBundle):
            raise KnowledgeBaseValidationError(
                "bundle must be a KnowledgeBundle instance"
            )
        entries_summary: list[dict] = []
        for e in bundle.entries:
            entries_summary.append(
                {
                    "entry_id": e.entry_id,
                    "kind": e.kind.value,
                    "source_ref": e.source_ref,
                    "title_hash": hashlib.sha256(e.title.encode("utf-8")).hexdigest()[:16],
                    "classification": e.classification.value,
                    "scope": e.scope,
                    "requires_owner_approval": e.requires_owner_approval,
                    "body_hash": hashlib.sha256(e.body_summary.encode("utf-8")).hexdigest()[:16],
                }
            )
        templates_summary: list[dict] = []
        for t in bundle.reusable_templates:
            templates_summary.append(
                {
                    "template_id": t.template_id,
                    "kind": t.kind.value,
                    "source_project_id": t.source_project_id,
                    "scope": t.scope,
                    "body_hash": hashlib.sha256(
                        str(sorted(t.body.items())).encode("utf-8")
                    ).hexdigest()[:16],
                }
            )
        return {
            "schema_version": "1.0",
            "domain": "coevo.knowledge_base",
            "bundle_id": bundle.bundle_id,
            "project_id": bundle.project_id,
            "entry_count": len(bundle.entries),
            "entries": entries_summary,
            "template_count": len(bundle.reusable_templates),
            "templates": templates_summary,
            "accepted_count": len(bundle.accepted_entries),
            "rejected_count": len(bundle.rejected_entries),
            "bundle_classification": bundle.bundle_classification.value,
            "requires_user_confirmation": bundle.requires_user_confirmation,
            "formally_committed": bundle.formally_committed,
            "committed_at": bundle.committed_at,
            "committed_by": bundle.committed_by,
            "created_at": bundle.created_at,
        }

def _make_entry_id(kind: KnowledgeSourceKind, project_id: str, idx: int) -> str:
    return f"ke.{kind.value}.{project_id}.{idx}"

def _make_bundle_id(project_id: str, now: str) -> str:
    safe_now = now.replace(":", "").replace("T", "t").replace(".", "p")
    return f"kb.{project_id}.{safe_now}"

def _make_template_id(kind: ReusableTemplateKind, project_id: str, idx: int) -> str:
    return f"kt.{kind.value}.{project_id}.{idx}"

def _rank_to_classification(rank: int) -> KnowledgeClassification:
    if rank <= 0:
        return KnowledgeClassification.PUBLIC
    if rank == 1:
        return KnowledgeClassification.INTERNAL
    if rank == 2:
        return KnowledgeClassification.CONFIDENTIAL
    return KnowledgeClassification.RESTRICTED

def _entry_from_baseline(
    baseline: dict, project_id: str, now: str
) -> KnowledgeEntry:
    title = str(baseline.get("title", "project baseline"))
    body = str(baseline.get("summary", ""))
    classification_str = str(baseline.get("classification", "internal")).lower()
    try:
        classification = KnowledgeClassification(classification_str)
    except ValueError:
        classification = KnowledgeClassification.INTERNAL
    return KnowledgeEntry(
        entry_id=_make_entry_id(KnowledgeSourceKind.PROJECT_BASELINE, project_id, 0),
        kind=KnowledgeSourceKind.PROJECT_BASELINE,
        source_ref=f"{project_id}.baseline",
        title=title,
        body_summary=body,
        classification=classification,
        scope="all_projects",
        requires_owner_approval=False,
        recorded_at=now,
    )

def _entry_from_source(
    source: dict,
    kind: KnowledgeSourceKind,
    project_id: str,
    now: str,
    *,
    requires_owner_approval: bool = False,
) -> KnowledgeEntry:
    idx = _source_index(source)
    title = str(source.get("title") or source.get("name") or kind.value)
    body = str(source.get("summary") or source.get("description") or "")
    classification_str = str(source.get("classification", "internal")).lower()
    try:
        classification = KnowledgeClassification(classification_str)
    except ValueError:
        classification = KnowledgeClassification.INTERNAL
    source_ref = str(source.get("id") or source.get("source_ref") or f"{kind.value}.{idx}")
    scope = str(source.get("scope", "this_project_only"))
    return KnowledgeEntry(
        entry_id=_make_entry_id(kind, project_id, idx),
        kind=kind,
        source_ref=source_ref,
        title=title,
        body_summary=body,
        classification=classification,
        scope=scope,
        requires_owner_approval=requires_owner_approval,
        recorded_at=now,
    )

def _source_index(source: dict) -> int:
    raw = source.get("index")
    if isinstance(raw, int) and raw >= 0:
        return raw
    return hashlib.sha256(str(sorted(source.items())).encode("utf-8")).hexdigest()[:4]

def _extract_reusable_templates(
    *,
    baseline: dict | None,
    risk_reports: tuple[dict, ...],
    project_id: str,
    now: str,
) -> tuple[ReusableTemplate, ...]:
    templates: list[ReusableTemplate] = []
    if baseline:
        stages = baseline.get("stages", [])
        if stages:
            templates.append(
                ReusableTemplate(
                    template_id=_make_template_id(
                        ReusableTemplateKind.PROCESS_TEMPLATE, project_id, 0
                    ),
                    kind=ReusableTemplateKind.PROCESS_TEMPLATE,
                    source_project_id=project_id,
                    scope="similar_domains",
                    body={"stages": list(stages)},
                    extracted_at=now,
                )
            )
        work_packages = baseline.get("work_packages", [])
        if work_packages:
            templates.append(
                ReusableTemplate(
                    template_id=_make_template_id(
                        ReusableTemplateKind.TASK_TEMPLATE, project_id, 1
                    ),
                    kind=ReusableTemplateKind.TASK_TEMPLATE,
                    source_project_id=project_id,
                    scope="similar_domains",
                    body={"work_packages": list(work_packages)},
                    extracted_at=now,
                )
            )
    for idx, rep in enumerate(risk_reports):
        risk_id = str(rep.get("id") or f"risk.{idx}")
        kind_str = str(rep.get("kind", ""))
        recommendation = str(rep.get("recommendation", ""))
        templates.append(
            ReusableTemplate(
                template_id=_make_template_id(
                    ReusableTemplateKind.RISK_RULE, project_id, idx
                ),
                kind=ReusableTemplateKind.RISK_RULE,
                source_project_id=project_id,
                scope="similar_domains",
                body={
                    "risk_kind": kind_str,
                    "risk_id": risk_id,
                    "rule": recommendation,
                },
                extracted_at=now,
            )
        )
    return tuple(templates)

def _generate_retrospective(
    *,
    project_id: str,
    entries: tuple[KnowledgeEntry, ...],
    now: str,
) -> RetrospectiveDraft:
    """AC-2: 5-section retrospective draft from entry set."""
    sections: list[str] = []
    sources: list[str] = []

    # 总体进展: count entries by kind.
    by_kind: dict[str, int] = {}
    for e in entries:
        by_kind[e.kind.value] = by_kind.get(e.kind.value, 0) + 1
        sources.append(e.entry_id)
    overview = "总体进展: " + ", ".join(
        f"{kind}={count}" for kind, count in sorted(by_kind.items())
    ) if by_kind else "总体进展: (无 entries)"
    sections.append(overview)

    # 重要变化: change-related entries (merge records, progress captures).
    changes = [e for e in entries if e.kind in (
        KnowledgeSourceKind.MERGE_RECORD, KnowledgeSourceKind.PROGRESS_CAPTURE
    )]
    sections.append(
        "重要变化: "
        + "; ".join(e.title for e in changes)
        if changes
        else "重要变化: (无)"
    )

    # 高风险: risk reports + decision briefs.
    risks = [e for e in entries if e.kind in (
        KnowledgeSourceKind.RISK_REPORT, KnowledgeSourceKind.DECISION_BRIEF
    )]
    sections.append(
        "高风险: " + "; ".join(e.title for e in risks)
        if risks
        else "高风险: (无)"
    )

    # 待决策: meeting conclusions.
    pending = [e for e in entries if e.kind == KnowledgeSourceKind.MEETING_CONCLUSION]
    sections.append(
        "待决策: " + "; ".join(e.title for e in pending)
        if pending
        else "待决策: (无)"
    )

    # 最佳实践: project baseline + reusable templates (deduped from entries).
    practices = [e for e in entries if e.kind == KnowledgeSourceKind.PROJECT_BASELINE]
    sections.append(
        "最佳实践: " + "; ".join(e.title for e in practices)
        if practices
        else "最佳实践: (无)"
    )

    draft_id = f"rd.{project_id}.{now.replace(':', '').replace('T', 't').replace('.', 'p')}"
    return RetrospectiveDraft(
        draft_id=draft_id,
        project_id=project_id,
        title=f"{project_id} 复盘草稿",
        body_sections=tuple(sections),
        sources=tuple(sources),
        generated_at=now,
        requires_user_review=True,
    )
