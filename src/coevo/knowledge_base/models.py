"""knowledge_base.models - US-14 knowledge-base domain models, enums, errors and shared validators."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-14 知识库领域模型：知识条目/分类/可复用模板/复盘草稿与全部校验。

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")

from src.coevo.timefmt import is_iso_utc_z

_CLASSIFICATION_RANK: dict[str, int] = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3,
}

class KnowledgeBaseError(Exception):
    """Base class for all US-14 errors. Fail-closed by default."""

class KnowledgeBaseValidationError(KnowledgeBaseError):
    """An input field or construct failed validation (user-fixable)."""

class ClassificationDenied(KnowledgeBaseError):
    """Actor's clearance is insufficient for the bundle's classification.

    Distinct from :class:`KnowledgeBaseValidationError` so callers can
    branch on "needs reclassification" vs "needs input fix".
    """

class ReviewConflictError(KnowledgeBaseError):
    """An operation was inconsistent with the current bundle state."""

class KnowledgeClassification(enum.Enum):
    """AC-5 closed set of knowledge classification levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class KnowledgeSourceKind(enum.Enum):
    """AC-1 + AC-7 closed set of source kinds.

    MODEL_SUMMARY entries default ``requires_owner_approval=True`` to
    satisfy AC-7: 未经审核的模型总结不得进入正式知识库。
    """

    PROJECT_BASELINE = "project_baseline"
    MERGE_RECORD = "merge_record"
    RISK_REPORT = "risk_report"
    MEETING_CONCLUSION = "meeting_conclusion"
    DECISION_BRIEF = "decision_brief"
    PROGRESS_CAPTURE = "progress_capture"
    MODEL_SUMMARY = "model_summary"

class ReusableTemplateKind(enum.Enum):
    """AC-3 closed set of reusable template kinds."""

    PROCESS_TEMPLATE = "process_template"
    TASK_TEMPLATE = "task_template"
    RISK_RULE = "risk_rule"

class ReviewDecisionKind(enum.Enum):
    """AC-6 closed set of reviewer decisions."""

    APPROVE = "approve"
    REVISE = "revise"
    REJECT = "reject"

@dataclass(frozen=True)
class ReusableTemplate:
    """AC-3: an extracted reusable template."""

    template_id: str
    kind: ReusableTemplateKind
    source_project_id: str
    scope: str
    body: dict
    extracted_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.template_id, str) or not _SAFE_ID.match(self.template_id):
            raise KnowledgeBaseValidationError(
                f"template_id must be safe-id; got {self.template_id!r}"
            )
        if not isinstance(self.kind, ReusableTemplateKind):
            raise KnowledgeBaseValidationError(
                f"kind must be ReusableTemplateKind; got {self.kind!r}"
            )
        if not isinstance(self.source_project_id, str) or not _SAFE_ID.match(self.source_project_id):
            raise KnowledgeBaseValidationError(
                f"source_project_id must be safe-id; got {self.source_project_id!r}"
            )
        if not isinstance(self.scope, str) or not self.scope:
            raise KnowledgeBaseValidationError("scope must be a non-empty string")
        if not isinstance(self.body, dict):
            raise KnowledgeBaseValidationError("body must be a dict")
        if not is_iso_utc_z(self.extracted_at):
            raise KnowledgeBaseValidationError(
                f"extracted_at must be ISO-8601 UTC 'Z'; got {self.extracted_at!r}"
            )

@dataclass(frozen=True)
class KnowledgeEntry:
    """AC-1 + AC-4: a single piece of project knowledge."""

    entry_id: str
    kind: KnowledgeSourceKind
    source_ref: str
    title: str
    body_summary: str
    classification: KnowledgeClassification
    scope: str
    requires_owner_approval: bool
    recorded_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.entry_id, str) or not _SAFE_ID.match(self.entry_id):
            raise KnowledgeBaseValidationError(
                f"entry_id must be safe-id; got {self.entry_id!r}"
            )
        if not isinstance(self.kind, KnowledgeSourceKind):
            raise KnowledgeBaseValidationError(
                f"kind must be KnowledgeSourceKind; got {self.kind!r}"
            )
        if not isinstance(self.source_ref, str) or not self.source_ref:
            raise KnowledgeBaseValidationError("source_ref must be a non-empty string")
        if not isinstance(self.title, str) or not self.title:
            raise KnowledgeBaseValidationError("title must be a non-empty string")
        if not isinstance(self.body_summary, str):
            raise KnowledgeBaseValidationError("body_summary must be a string")
        if not isinstance(self.classification, KnowledgeClassification):
            raise KnowledgeBaseValidationError(
                f"classification must be KnowledgeClassification; got {self.classification!r}"
            )
        if not isinstance(self.scope, str) or not self.scope:
            raise KnowledgeBaseValidationError("scope must be a non-empty string")
        if not isinstance(self.requires_owner_approval, bool):
            raise KnowledgeBaseValidationError(
                "requires_owner_approval must be bool"
            )
        if not is_iso_utc_z(self.recorded_at):
            raise KnowledgeBaseValidationError(
                f"recorded_at must be ISO-8601 UTC 'Z'; got {self.recorded_at!r}"
            )

@dataclass(frozen=True)
class ReviewDecision:
    """AC-6: a single reviewer decision on a :class:`KnowledgeEntry`."""

    decision_id: str
    entry_id: str
    decision: ReviewDecisionKind
    decided_by: str
    reason: str
    decided_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.decision_id, str) or not _SAFE_ID.match(self.decision_id):
            raise KnowledgeBaseValidationError(
                f"decision_id must be safe-id; got {self.decision_id!r}"
            )
        if not isinstance(self.entry_id, str) or not _SAFE_ID.match(self.entry_id):
            raise KnowledgeBaseValidationError(
                f"entry_id must be safe-id; got {self.entry_id!r}"
            )
        if not isinstance(self.decision, ReviewDecisionKind):
            raise KnowledgeBaseValidationError(
                f"decision must be ReviewDecisionKind; got {self.decision!r}"
            )
        if not isinstance(self.decided_by, str) or not _SAFE_ID.match(self.decided_by):
            raise KnowledgeBaseValidationError(
                f"decided_by must be safe-id; got {self.decided_by!r}"
            )
        if not isinstance(self.reason, str):
            raise KnowledgeBaseValidationError("reason must be a string")
        if not is_iso_utc_z(self.decided_at):
            raise KnowledgeBaseValidationError(
                f"decided_at must be ISO-8601 UTC 'Z'; got {self.decided_at!r}"
            )

@dataclass(frozen=True)
class RetrospectiveDraft:
    """AC-2: the auto-generated retrospective draft."""

    draft_id: str
    project_id: str
    title: str
    body_sections: tuple[str, ...]
    sources: tuple[str, ...]
    generated_at: str
    requires_user_review: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.draft_id, str) or not _SAFE_ID.match(self.draft_id):
            raise KnowledgeBaseValidationError(
                f"draft_id must be safe-id; got {self.draft_id!r}"
            )
        if not isinstance(self.project_id, str) or not _SAFE_ID.match(self.project_id):
            raise KnowledgeBaseValidationError(
                f"project_id must be safe-id; got {self.project_id!r}"
            )
        if not isinstance(self.title, str) or not self.title:
            raise KnowledgeBaseValidationError("title must be a non-empty string")
        if not isinstance(self.body_sections, tuple) or not all(
            isinstance(s, str) and s for s in self.body_sections
        ):
            raise KnowledgeBaseValidationError(
                "body_sections must be a tuple of non-empty strings"
            )
        if not isinstance(self.sources, tuple) or not all(
            isinstance(s, str) and s for s in self.sources
        ):
            raise KnowledgeBaseValidationError(
                "sources must be a tuple of non-empty strings"
            )
        if not is_iso_utc_z(self.generated_at):
            raise KnowledgeBaseValidationError(
                f"generated_at must be ISO-8601 UTC 'Z'; got {self.generated_at!r}"
            )
        if not isinstance(self.requires_user_review, bool):
            raise KnowledgeBaseValidationError("requires_user_review must be bool")
        # AC-2 + AC-7: requires_user_review is FORCED True.
        if not self.requires_user_review:
            raise KnowledgeBaseValidationError(
                "RetrospectiveDraft.requires_user_review must be True (AC-7 fail-closed)"
            )

@dataclass(frozen=True)
class KnowledgeBundle:
    """Final US-14 output."""

    bundle_id: str
    project_id: str
    entries: tuple[KnowledgeEntry, ...]
    retrospective: RetrospectiveDraft
    reusable_templates: tuple[ReusableTemplate, ...]
    accepted_entries: tuple[str, ...]
    rejected_entries: tuple[str, ...]
    bundle_classification: KnowledgeClassification
    requires_user_confirmation: bool
    formally_committed: bool
    committed_at: str
    committed_by: str
    created_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.bundle_id, str) or not _SAFE_ID.match(self.bundle_id):
            raise KnowledgeBaseValidationError(
                f"bundle_id must be safe-id; got {self.bundle_id!r}"
            )
        if not isinstance(self.project_id, str) or not _SAFE_ID.match(self.project_id):
            raise KnowledgeBaseValidationError(
                f"project_id must be safe-id; got {self.project_id!r}"
            )
        if not isinstance(self.entries, tuple) or not all(
            isinstance(e, KnowledgeEntry) for e in self.entries
        ):
            raise KnowledgeBaseValidationError(
                "entries must be a tuple of KnowledgeEntry"
            )
        if not isinstance(self.retrospective, RetrospectiveDraft):
            raise KnowledgeBaseValidationError(
                "retrospective must be a RetrospectiveDraft"
            )
        if not isinstance(self.reusable_templates, tuple) or not all(
            isinstance(t, ReusableTemplate) for t in self.reusable_templates
        ):
            raise KnowledgeBaseValidationError(
                "reusable_templates must be a tuple of ReusableTemplate"
            )
        for label, value in (
            ("accepted_entries", self.accepted_entries),
            ("rejected_entries", self.rejected_entries),
        ):
            if not isinstance(value, tuple) or not all(
                isinstance(s, str) and _SAFE_ID.match(s) for s in value
            ):
                raise KnowledgeBaseValidationError(
                    f"{label} must be a tuple of safe-id"
                )
        # No entry can be both accepted and rejected.
        overlap = set(self.accepted_entries) & set(self.rejected_entries)
        if overlap:
            raise KnowledgeBaseValidationError(
                f"entries cannot be both accepted and rejected: {sorted(overlap)}"
            )
        if not isinstance(self.bundle_classification, KnowledgeClassification):
            raise KnowledgeBaseValidationError(
                f"bundle_classification must be KnowledgeClassification; "
                f"got {self.bundle_classification!r}"
            )
        # AC-7 fail-closed: requires_user_confirmation MUST be True.
        if not self.requires_user_confirmation:
            raise KnowledgeBaseValidationError(
                "KnowledgeBundle.requires_user_confirmation must be True (AC-7 fail-closed)"
            )
        if self.formally_committed:
            if not self.committed_at or not self.committed_by:
                raise KnowledgeBaseValidationError(
                    "formally_committed=True requires committed_at and committed_by"
                )
            _check_iso_utc(self.committed_at, field="committed_at")
            _check_safe_id(self.committed_by, field="committed_by")
        else:
            if self.committed_at or self.committed_by:
                raise KnowledgeBaseValidationError(
                    "formally_committed=False requires empty committed_at and committed_by"
                )
        _check_iso_utc(self.created_at, field="created_at")

def _check_safe_id(value: object, *, field: str) -> None:
    if not isinstance(value, str) or not _SAFE_ID.match(value):
        raise KnowledgeBaseValidationError(
            f"{field} must be safe-id; got {value!r}"
        )

def _check_iso_utc(value: object, *, field: str) -> None:
    if not is_iso_utc_z(value):
        raise KnowledgeBaseValidationError(
            f"{field} must be ISO-8601 UTC 'Z'; got {value!r}"
        )

def _check_class(value: object, *, field: str, klass: type) -> None:
    if not isinstance(value, klass):
        raise KnowledgeBaseValidationError(
            f"{field} must be {klass.__name__}; got {value!r}"
        )
