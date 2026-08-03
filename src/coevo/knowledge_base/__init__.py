"""US-14 knowledge base service facade.

Scope
-----
Pure half of US-14: the *governance* layer that aggregates project
knowledge into a draft :class:`KnowledgeBundle`, applies reviewer
decisions (AC-6), and runs the classification check (AC-5). No
IO in the facade itself: disk persistence is provided by
:class:`KnowledgeStore` (US-14-AC-2, ``store.py``) and wired by the
composition layer. LLM-assisted template extraction is not
implemented (out of scope).

* No IO, no DB, no LLM, no scheduler.
* All dataclasses are frozen + exact-type + ISO-8601 UTC `Z` time strings.
* Pure function: same inputs yield identical :class:`KnowledgeBundle`.
* to_audit_record mirrors US-11/12/13/8/15/4/7 by EXCLUDING free-form
  body text (body_summary / body_sections / template body) and only
  keeping IDs, kinds, classifications, and counts.

AC mapping
----------
* AC-1 汇总 -- :meth:`KnowledgeBaseFacade.aggregate` consumes
  baseline + merge_records + risk_reports + meeting_conclusions +
  decision_briefs + progress_captures + model_summaries and emits
  one :class:`KnowledgeEntry` per input.
* AC-2 复盘报告草稿 -- :class:`RetrospectiveDraft` with five sections
  (总体进展 / 重要变化 / 高风险 / 待决策 / 最佳实践).
* AC-3 模板提取 -- :attr:`KnowledgeBundle.reusable_templates` is
  extracted from baseline (process_template + task_template) and
  risk_reports (risk_rule).
* AC-4 来源项目 + 适用范围 -- every :class:`KnowledgeEntry` carries
  ``source_ref`` + ``scope``; every :class:`ReusableTemplate` carries
  ``source_project_id`` + ``scope``.
* AC-5 密级检查 -- :meth:`KnowledgeBaseFacade.check_classification`
  raises :class:`ClassificationDenied` if actor_clearances do not
  include the bundle's :attr:`KnowledgeBundle.bundle_classification`.
* AC-6 用户审核 -- :meth:`KnowledgeBaseFacade.review` accepts
  :class:`ReviewDecision` tuples; APPROVE / REVISE / REJECT.
* AC-7 未经审核不得入库 -- :attr:`KnowledgeBundle.requires_user_confirmation`
  is FORCED True by construction; :attr:`formally_committed` is False
  by default; constructing with formally_committed=True without
  required metadata raises :class:`ValidationError`.

Non-goals
---------
* No IO / DB / LLM / scheduler.
* No mutation of any existing module.
* No new dependency."""

from __future__ import annotations

import enum
import hashlib
import re
from dataclasses import dataclass, field

from .models import (ClassificationDenied, KnowledgeBaseError, KnowledgeBaseValidationError, KnowledgeBundle, KnowledgeClassification, KnowledgeEntry, KnowledgeSourceKind, RetrospectiveDraft, ReusableTemplate, ReusableTemplateKind, ReviewConflictError, ReviewDecision, ReviewDecisionKind, _CLASSIFICATION_RANK, _ISO_UTC_Z, _SAFE_ID, _check_class, _check_iso_utc, _check_safe_id)

from .facade import (KnowledgeBaseFacade, _entry_from_baseline, _entry_from_source, _extract_reusable_templates, _generate_retrospective, _make_bundle_id, _make_entry_id, _make_template_id, _rank_to_classification, _source_index)

from .store import AUDIT_ACTION_STORE, KnowledgeStore, KnowledgeStoreConflictError, KnowledgeStoreError, bundle_to_payload, payload_to_bundle
