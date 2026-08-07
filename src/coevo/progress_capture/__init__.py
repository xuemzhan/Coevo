"""US-8 progress capture service facade.

Scope
-----
Consumes workspace + evidence inputs and emits a DRAFT :class:`ProgressCapture`
(AC-1..AC-8). Pure half of US-8:

* No IO, no LLM, no DB.
* No automatic task identification -- ``task_id`` is provided by the caller.
* The "report" output is a :class:`ProgressDraft` (NOT a US-9
  :class:`ReportManifest`). US-9 ReportBuilder is the consumer that
  converts a draft into a real wire package.
* All dataclasses are frozen + exact-type + ISO-8601 UTC `Z` time strings.
* ``requires_user_confirmation=True`` is FORCED by construction (AC-6);
  ``formally_accepted=False`` is the only starting state; only
  :meth:`ProgressCaptureService.accept` flips it to ``True``.
* Fail-closed on every malformed input.

AC mapping
----------
* AC-1 识别工作区文档/成果变化 -- :meth:`ProgressCaptureService.extract_progress`
  accepts 4 evidence kinds and emits one ProgressItem per evidence.
* AC-2 四类提取 -- :class:`ProgressItemKind` enum + :meth:`to_report_draft`
  bucketing.
* AC-3 进展关联成果证据 -- :attr:`ProgressItem.evidence_refs` >= 1 enforced
  at construction.
* AC-4 信息来源 + 置信度 -- :attr:`ProgressItem.source_kind` +
  :attr:`ProgressItem.confidence` enforced at construction; confidence
  must lie in [0.0, 1.0].
* AC-5 用户可修改或驳回 -- :meth:`revise` / :meth:`reject`.
* AC-6 用户确认 -- :attr:`requires_user_confirmation` is True by force;
  :attr:`formally_accepted` is False until :meth:`accept` is called.
* AC-7 不得仅根据文件修改时间判断 -- :class:`EvidenceKind` has NO
  ``FILE_MTIME_ONLY`` member; receiving an unknown kind (including any
  caller-supplied string equal to ``"file_mtime_only"``) is rejected at
  validation.
* AC-8 确认后可生成汇报数据 -- :meth:`to_report_draft` only fires after
  ``formally_accepted == True``; the draft binds every segment item back
  to its source :class:`ProgressItem.item_id`.

Non-goals
---------
* No file watcher / no real-time diff / no IPC.
* No automatic identification of task_id from text content.
* No import of US-9 ReportManifest (US-9 builder is the consumer, not
  the producer)."""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import Iterable
from src.coevo.workspace.models import WorkspaceEntry

from .models import (DOMAIN, EvidenceInput, EvidenceKind, EvidenceRef, FORBIDDEN_KIND_TOKENS, ItemOverride, ProgressCapture, ProgressCaptureConflictError, ProgressCaptureError, ProgressCaptureValidationError, ProgressDraft, ProgressItem, ProgressItemKind, ProgressItemStatus, SCHEMA_VERSION, _HEX_64, _SAFE_ID, _check_confidence, _check_hex64, _check_iso_utc, _check_non_empty_str, _check_safe_id)

from .service import (ProgressCaptureService, _classify, _make_capture_id, _make_item_id)

from .watcher import DEFAULT_MAX_EVENTS, DEFAULT_POLL_INTERVAL_SEC, DEFAULT_STABILITY_CHECKS, FileChangeEvent, FileEventKind, FileSnapshot, WorkspaceWatcher
