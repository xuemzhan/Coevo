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
  the producer).
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import Iterable

from src.coevo.workspace.models import WorkspaceEntry


SCHEMA_VERSION: str = "1.0"
DOMAIN: str = "coevo.progress_capture"

# 64-char lowercase hex, mirrors US-9 ReportArtifact.digest_hex.
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")

# safe-id: same alphabet as the rest of the codebase (US-2 / US-5).
_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")

# ISO-8601 UTC 'Z' -- strict format used everywhere else (US-9 / US-10 / US-13).
_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ProgressCaptureError(Exception):
    """Base class for all US-8 errors. Fail-closed by default."""


class ProgressCaptureValidationError(ProgressCaptureError):
    """An input field failed validation (user-fixable).

    Distinct from :class:`ProgressCaptureError` so callers can branch on
    "validation failed" vs "structural invariant violated".
    """


class ProgressCaptureConflictError(ProgressCaptureError):
    """An operation was inconsistent with the current capture state.

    Examples: calling :meth:`accept` after :meth:`reject` of every item;
    calling :meth:`to_report_draft` before :meth:`accept`.
    """


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class EvidenceKind(enum.Enum):
    """Closed set of evidence kinds accepted by US-8.

    NOTE: There is intentionally NO ``FILE_MTIME_ONLY`` member. AC-7
    forbids "only by file modification time" decisions, so the closed
    set excludes that channel. Callers that try to construct an input
    with kind == FILE_MTIME_ONLY (literal string or any other enum value
    outside this set) will be rejected at validation.
    """

    EXPLICIT_USER_TEXT = "explicit_user_text"
    DOCUMENT_CONTENT = "document_content"
    ARTIFACT_FILE = "artifact_file"
    TASK_DEPENDENCY_RESOLVED = "task_dependency_resolved"


# Closed string alias kept here so tests can assert "FILE_MTIME_ONLY is
# NOT a valid kind" without depending on enum internals.
FORBIDDEN_KIND_TOKENS: frozenset[str] = frozenset({
    "file_mtime_only",
    "FILE_MTIME_ONLY",
    "FileMtimeOnly",
    "mtime",
    "mtime_only",
    "file_mtime",
})


class ProgressItemKind(enum.Enum):
    """AC-2: 4 categories a progress item can fall into."""

    COMPLETED = "completed"
    PENDING = "pending"
    NEXT_STEP = "next_step"
    BLOCKER = "blocker"


class ProgressItemStatus(enum.Enum):
    """Lifecycle state of a single progress item (AC-5)."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REVISED = "revised"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceInput:
    """Raw input to :meth:`ProgressCaptureService.extract_progress`.

    This is what the caller hands the service: a workspace-relative
    locator, the kind, the source text/reference, the per-evidence
    confidence, and the chain back to an evidence artifact. ``task_id``
    is required so the service never auto-identifies tasks.
    """

    task_id: str
    kind: EvidenceKind
    source_ref: str
    text: str
    confidence: float
    evidence_refs: tuple["EvidenceRef", ...]

    def __post_init__(self) -> None:
        _check_safe_id(self.task_id, field="task_id")
        if not isinstance(self.kind, EvidenceKind):
            raise ProgressCaptureValidationError(
                f"evidence kind must be an EvidenceKind enum; got {self.kind!r}"
            )
        _check_non_empty_str(self.source_ref, field="source_ref")
        _check_non_empty_str(self.text, field="text")
        _check_confidence(self.confidence)
        if not isinstance(self.evidence_refs, tuple) or not self.evidence_refs:
            raise ProgressCaptureValidationError(
                "evidence_refs must be a non-empty tuple (AC-3)"
            )
        if not all(isinstance(r, EvidenceRef) for r in self.evidence_refs):
            raise ProgressCaptureValidationError(
                "evidence_refs must all be EvidenceRef instances"
            )


@dataclass(frozen=True)
class EvidenceRef:
    """AC-3: a single piece of evidence bound to a :class:`ProgressItem`.

    Mirrors the US-9 :class:`ReportArtifact` shape so the eventual
    US-9 builder can re-use these refs without re-validation. The path
    is workspace-relative and rejects ``..`` traversal.
    """

    path: str
    role: str
    media_type: str
    digest_hex: str
    size_bytes: int

    def __post_init__(self) -> None:
        _check_non_empty_str(self.path, field="path")
        if ".." in self.path.split("/") or self.path.startswith("/"):
            raise ProgressCaptureValidationError(
                f"evidence path must be a non-traversing workspace-relative path; got {self.path!r}"
            )
        if self.role not in {"document", "feedback", "artifact", "dependency"}:
            raise ProgressCaptureValidationError(
                f"evidence role must be one of document/feedback/artifact/dependency; got {self.role!r}"
            )
        _check_non_empty_str(self.media_type, field="media_type")
        _check_hex64(self.digest_hex, field="digest_hex")
        if not isinstance(self.size_bytes, int) or self.size_bytes < 0:
            raise ProgressCaptureValidationError(
                "size_bytes must be a non-negative integer"
            )


@dataclass(frozen=True)
class ItemOverride:
    """AC-5: a single reviewer edit applied to a :class:`ProgressItem`."""

    target_path: str
    original_value: object
    edited_value: object
    reason: str
    edited_at: str

    def __post_init__(self) -> None:
        _check_non_empty_str(self.target_path, field="target_path")
        _check_non_empty_str(self.reason, field="reason")
        _check_iso_utc(self.edited_at, field="edited_at")


@dataclass(frozen=True)
class ProgressItem:
    """AC-1..AC-5: a single recognized progress change.

    Immutable. Mutations (revise / reject / accept) return a new
    :class:`ProgressCapture` carrying updated items.
    """

    item_id: str
    workspace_project_id: str
    task_id: str
    kind: ProgressItemKind
    text: str
    source_kind: EvidenceKind
    source_ref: str
    confidence: float
    evidence_refs: tuple[EvidenceRef, ...]
    status: ProgressItemStatus
    overrides: tuple[ItemOverride, ...] = field(default_factory=tuple)
    created_at: str = ""

    def __post_init__(self) -> None:
        _check_safe_id(self.item_id, field="item_id")
        _check_safe_id(self.workspace_project_id, field="workspace_project_id")
        _check_safe_id(self.task_id, field="task_id")
        if not isinstance(self.kind, ProgressItemKind):
            raise ProgressCaptureValidationError(
                f"item kind must be ProgressItemKind; got {self.kind!r}"
            )
        _check_non_empty_str(self.text, field="text")
        if not isinstance(self.source_kind, EvidenceKind):
            raise ProgressCaptureValidationError(
                f"source_kind must be EvidenceKind; got {self.source_kind!r}"
            )
        _check_non_empty_str(self.source_ref, field="source_ref")
        _check_confidence(self.confidence)
        if not isinstance(self.evidence_refs, tuple) or not self.evidence_refs:
            raise ProgressCaptureValidationError(
                "evidence_refs must be a non-empty tuple (AC-3)"
            )
        if not all(isinstance(r, EvidenceRef) for r in self.evidence_refs):
            raise ProgressCaptureValidationError(
                "evidence_refs must all be EvidenceRef instances"
            )
        if not isinstance(self.status, ProgressItemStatus):
            raise ProgressCaptureValidationError(
                f"status must be ProgressItemStatus; got {self.status!r}"
            )
        if not isinstance(self.overrides, tuple) or not all(
            isinstance(o, ItemOverride) for o in self.overrides
        ):
            raise ProgressCaptureValidationError(
                "overrides must be a tuple of ItemOverride"
            )
        if self.status == ProgressItemStatus.REVISED and not self.overrides:
            raise ProgressCaptureValidationError(
                "REVISED items must carry at least one override"
            )
        if self.status == ProgressItemStatus.REJECTED and not self.overrides:
            # We require REJECTED to record the reason in an override so the
            # audit projection can recover it without leaking item text.
            raise ProgressCaptureValidationError(
                "REJECTED items must carry at least one override (reason)"
            )
        if self.created_at:
            _check_iso_utc(self.created_at, field="created_at")


@dataclass(frozen=True)
class ProgressCapture:
    """AC-6/AC-8: a single draft capturing the recognized progress.

    ``requires_user_confirmation`` is True by force (AC-6). ``formally_accepted``
    is False until :meth:`ProgressCaptureService.accept` is called.
    """

    schema_version: str
    capture_id: str
    workspace: WorkspaceEntry
    progress_items: tuple[ProgressItem, ...]
    requires_user_confirmation: bool
    formally_accepted: bool
    accepted_at: str
    accepted_by: str
    created_at: str

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ProgressCaptureValidationError(
                f"unsupported schema_version {self.schema_version!r}; only {SCHEMA_VERSION!r}"
            )
        _check_safe_id(self.capture_id, field="capture_id")
        if not isinstance(self.workspace, WorkspaceEntry):
            raise ProgressCaptureValidationError(
                "workspace must be a WorkspaceEntry instance"
            )
        if not isinstance(self.progress_items, tuple) or not all(
            isinstance(i, ProgressItem) for i in self.progress_items
        ):
            raise ProgressCaptureValidationError(
                "progress_items must be a tuple of ProgressItem"
            )
        if not self.requires_user_confirmation:
            # AC-6: the gate cannot be bypassed by construction.
            raise ProgressCaptureValidationError(
                "requires_user_confirmation must be True (AC-6 fail-closed)"
            )
        if self.formally_accepted:
            # Only the service's accept() path can set this True; the model
            # cannot fabricate a formally_accepted capture directly.
            if not self.accepted_at or not self.accepted_by:
                raise ProgressCaptureValidationError(
                    "formally_accepted=True requires accepted_at and accepted_by"
                )
            _check_iso_utc(self.accepted_at, field="accepted_at")
            _check_safe_id(self.accepted_by, field="accepted_by")
        else:
            if self.accepted_at or self.accepted_by:
                raise ProgressCaptureValidationError(
                    "formally_accepted=False must have empty accepted_at and accepted_by"
                )
        _check_iso_utc(self.created_at, field="created_at")
        # Every item must reference the same workspace.project_id.
        for item in self.progress_items:
            if item.workspace_project_id != self.workspace.project_id:
                raise ProgressCaptureValidationError(
                    f"item {item.item_id!r} workspace_project_id {item.workspace_project_id!r} "
                    f"does not match workspace.project_id {self.workspace.project_id!r}"
                )


@dataclass(frozen=True)
class ProgressDraft:
    """AC-8: a formally-accepted capture flattened for US-9 consumption.

    NOT a :class:`src.coevo.report.models.ReportManifest`. US-9
    ReportBuilder is the only consumer; it converts a ProgressDraft into
    a real ReportManifest (with sender/recipient identities, signature,
    base_revision, etc.).
    """

    draft_id: str
    workspace_project_id: str
    workspace_task_id: str
    completed_work: tuple[str, ...]
    pending_work: tuple[str, ...]
    next_steps: tuple[str, ...]
    blockers: tuple[str, ...]
    source_progress_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _check_safe_id(self.draft_id, field="draft_id")
        _check_safe_id(self.workspace_project_id, field="workspace_project_id")
        _check_safe_id(self.workspace_task_id, field="workspace_task_id")
        for name in ("completed_work", "pending_work", "next_steps", "blockers"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or not all(
                isinstance(x, str) and x for x in value
            ):
                raise ProgressCaptureValidationError(
                    f"{name} must be a tuple of non-empty strings"
                )
        if not isinstance(self.source_progress_ids, tuple) or not all(
            isinstance(x, str) and x for x in self.source_progress_ids
        ):
            raise ProgressCaptureValidationError(
                "source_progress_ids must be a tuple of non-empty strings"
            )


# ---------------------------------------------------------------------------
# Service facade
# ---------------------------------------------------------------------------


class ProgressCaptureService:
    """Pure-function facade over the US-8 data model.

    All public methods return new dataclass instances; no IO / DB / LLM /
    scheduling. The service is fully deterministic for a given
    ``(workspace, evidence_inputs, now)`` triple and the resulting
    ``capture_id`` is content-stable.
    """

    @staticmethod
    def extract_progress(
        workspace: WorkspaceEntry,
        evidence_inputs: Iterable[EvidenceInput],
        *,
        now: str,
    ) -> ProgressCapture:
        """AC-1..AC-4 + AC-7: parse inputs into a draft capture.

        Fails closed on:

        * workspace not a :class:`WorkspaceEntry`
        * any evidence_inputs item with kind == FILE_MTIME_ONLY (forbidden
          by AC-7)
        * any evidence_inputs item with confidence outside [0.0, 1.0]
        * any evidence_inputs item with empty evidence_refs
        * any evidence_ref path that traverses outside the workspace
        * ``now`` not in strict ISO-8601 UTC ``Z`` form
        """
        if not isinstance(workspace, WorkspaceEntry):
            raise ProgressCaptureValidationError(
                "workspace must be a WorkspaceEntry instance"
            )
        _check_iso_utc(now, field="now")

        inputs = tuple(evidence_inputs)
        for idx, ev in enumerate(inputs):
            if not isinstance(ev, EvidenceInput):
                raise ProgressCaptureValidationError(
                    f"evidence_inputs[{idx}] must be an EvidenceInput instance"
                )

        items: list[ProgressItem] = []
        for idx, ev in enumerate(inputs):
            item = ProgressItem(
                item_id=_make_item_id(workspace.project_id, ev.task_id, idx),
                workspace_project_id=workspace.project_id,
                task_id=ev.task_id,
                kind=_classify(ev),
                text=ev.text,
                source_kind=ev.kind,
                source_ref=ev.source_ref,
                confidence=ev.confidence,
                evidence_refs=ev.evidence_refs,
                status=ProgressItemStatus.PROPOSED,
                overrides=(),
                created_at=now,
            )
            items.append(item)

        capture_id = _make_capture_id(workspace.project_id, now, len(items))

        return ProgressCapture(
            schema_version=SCHEMA_VERSION,
            capture_id=capture_id,
            workspace=workspace,
            progress_items=tuple(items),
            requires_user_confirmation=True,
            formally_accepted=False,
            accepted_at="",
            accepted_by="",
            created_at=now,
        )

    @staticmethod
    def revise(
        capture: ProgressCapture,
        item_id: str,
        *,
        new_text: str | None = None,
        new_kind: ProgressItemKind | None = None,
        new_confidence: float | None = None,
        reason: str,
        now: str,
    ) -> ProgressCapture:
        """AC-5: replace item fields and append an override."""
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        _check_iso_utc(now, field="now")
        _check_non_empty_str(reason, field="reason")
        if new_text is None and new_kind is None and new_confidence is None:
            raise ProgressCaptureValidationError(
                "revise requires at least one of new_text/new_kind/new_confidence"
            )
        if new_confidence is not None:
            _check_confidence(new_confidence)

        new_items: list[ProgressItem] = []
        found = False
        for item in capture.progress_items:
            if item.item_id != item_id:
                new_items.append(item)
                continue
            found = True
            if item.status == ProgressItemStatus.REJECTED:
                raise ProgressCaptureConflictError(
                    f"cannot revise REJECTED item {item_id!r}"
                )
            if item.status == ProgressItemStatus.ACCEPTED and capture.formally_accepted:
                raise ProgressCaptureConflictError(
                    f"cannot revise ACCEPTED item {item_id!r} on a formally_accepted capture"
                )
            new_overrides = item.overrides
            replaced_text = item.text
            replaced_kind = item.kind
            replaced_confidence = item.confidence
            if new_text is not None:
                _check_non_empty_str(new_text, field="new_text")
                new_overrides = new_overrides + (
                    ItemOverride(
                        target_path="text",
                        original_value=item.text,
                        edited_value=new_text,
                        reason=reason,
                        edited_at=now,
                    ),
                )
                replaced_text = new_text
            if new_kind is not None:
                if not isinstance(new_kind, ProgressItemKind):
                    raise ProgressCaptureValidationError(
                        f"new_kind must be ProgressItemKind; got {new_kind!r}"
                    )
                new_overrides = new_overrides + (
                    ItemOverride(
                        target_path="kind",
                        original_value=item.kind,
                        edited_value=new_kind,
                        reason=reason,
                        edited_at=now,
                    ),
                )
                replaced_kind = new_kind
            if new_confidence is not None:
                new_overrides = new_overrides + (
                    ItemOverride(
                        target_path="confidence",
                        original_value=item.confidence,
                        edited_value=new_confidence,
                        reason=reason,
                        edited_at=now,
                    ),
                )
                replaced_confidence = new_confidence
            new_items.append(
                ProgressItem(
                    item_id=item.item_id,
                    workspace_project_id=item.workspace_project_id,
                    task_id=item.task_id,
                    kind=replaced_kind,
                    text=replaced_text,
                    source_kind=item.source_kind,
                    source_ref=item.source_ref,
                    confidence=replaced_confidence,
                    evidence_refs=item.evidence_refs,
                    status=ProgressItemStatus.REVISED,
                    overrides=new_overrides,
                    created_at=item.created_at,
                )
            )
        if not found:
            raise ProgressCaptureValidationError(
                f"item_id {item_id!r} not present in capture"
            )
        return ProgressCapture(
            schema_version=capture.schema_version,
            capture_id=capture.capture_id,
            workspace=capture.workspace,
            progress_items=tuple(new_items),
            requires_user_confirmation=True,
            formally_accepted=False,
            accepted_at="",
            accepted_by="",
            created_at=capture.created_at,
        )

    @staticmethod
    def reject(
        capture: ProgressCapture,
        item_id: str,
        *,
        reason: str,
        now: str,
    ) -> ProgressCapture:
        """AC-5: mark item as REJECTED with a reason-bearing override."""
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        _check_iso_utc(now, field="now")
        _check_non_empty_str(reason, field="reason")

        new_items: list[ProgressItem] = []
        found = False
        for item in capture.progress_items:
            if item.item_id != item_id:
                new_items.append(item)
                continue
            found = True
            if item.status == ProgressItemStatus.REJECTED:
                raise ProgressCaptureConflictError(
                    f"item {item_id!r} is already REJECTED"
                )
            override = ItemOverride(
                target_path="status",
                original_value=item.status,
                edited_value=ProgressItemStatus.REJECTED,
                reason=reason,
                edited_at=now,
            )
            new_items.append(
                ProgressItem(
                    item_id=item.item_id,
                    workspace_project_id=item.workspace_project_id,
                    task_id=item.task_id,
                    kind=item.kind,
                    text=item.text,
                    source_kind=item.source_kind,
                    source_ref=item.source_ref,
                    confidence=item.confidence,
                    evidence_refs=item.evidence_refs,
                    status=ProgressItemStatus.REJECTED,
                    overrides=item.overrides + (override,),
                    created_at=item.created_at,
                )
            )
        if not found:
            raise ProgressCaptureValidationError(
                f"item_id {item_id!r} not present in capture"
            )
        return ProgressCapture(
            schema_version=capture.schema_version,
            capture_id=capture.capture_id,
            workspace=capture.workspace,
            progress_items=tuple(new_items),
            requires_user_confirmation=True,
            formally_accepted=False,
            accepted_at="",
            accepted_by="",
            created_at=capture.created_at,
        )

    @staticmethod
    def accept(
        capture: ProgressCapture,
        *,
        accepted_by: str,
        now: str,
    ) -> ProgressCapture:
        """AC-6: flip formally_accepted to True; stamp accepted_by/at."""
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        if capture.formally_accepted:
            raise ProgressCaptureConflictError(
                f"capture {capture.capture_id!r} is already formally_accepted"
            )
        _check_safe_id(accepted_by, field="accepted_by")
        _check_iso_utc(now, field="now")

        new_items = tuple(
            ProgressItem(
                item_id=item.item_id,
                workspace_project_id=item.workspace_project_id,
                task_id=item.task_id,
                kind=item.kind,
                text=item.text,
                source_kind=item.source_kind,
                source_ref=item.source_ref,
                confidence=item.confidence,
                evidence_refs=item.evidence_refs,
                status=(
                    ProgressItemStatus.ACCEPTED
                    if item.status
                    in (ProgressItemStatus.PROPOSED, ProgressItemStatus.REVISED)
                    else item.status
                ),
                overrides=item.overrides,
                created_at=item.created_at,
            )
            for item in capture.progress_items
        )
        return ProgressCapture(
            schema_version=capture.schema_version,
            capture_id=capture.capture_id,
            workspace=capture.workspace,
            progress_items=new_items,
            requires_user_confirmation=True,
            formally_accepted=True,
            accepted_at=now,
            accepted_by=accepted_by,
            created_at=capture.created_at,
        )

    @staticmethod
    def to_report_draft(capture: ProgressCapture) -> ProgressDraft:
        """AC-8: flatten an accepted capture into a US-9-bound draft.

        Raises :class:`ProgressCaptureConflictError` if the capture is
        not yet formally accepted. REJECTED items are excluded from
        every segment; the draft binds every segment entry back to its
        source :class:`ProgressItem.item_id`.
        """
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        if not capture.formally_accepted:
            raise ProgressCaptureConflictError(
                f"capture {capture.capture_id!r} is not formally_accepted; "
                "call accept() before to_report_draft()"
            )

        # All non-rejected items, segmented by kind.
        completed: list[str] = []
        pending: list[str] = []
        next_steps: list[str] = []
        blockers: list[str] = []
        ids: list[str] = []
        for item in capture.progress_items:
            if item.status == ProgressItemStatus.REJECTED:
                continue
            ids.append(item.item_id)
            if item.kind == ProgressItemKind.COMPLETED:
                completed.append(item.item_id)
            elif item.kind == ProgressItemKind.PENDING:
                pending.append(item.item_id)
            elif item.kind == ProgressItemKind.NEXT_STEP:
                next_steps.append(item.item_id)
            elif item.kind == ProgressItemKind.BLOCKER:
                blockers.append(item.item_id)

        # task_id is the same for every item (AC-1 contract).
        task_ids = {item.task_id for item in capture.progress_items}
        workspace_task_id = next(iter(task_ids)) if task_ids else ""

        draft_id = "pd." + capture.capture_id[len("pc."):] + ".1"
        return ProgressDraft(
            draft_id=draft_id,
            workspace_project_id=capture.workspace.project_id,
            workspace_task_id=workspace_task_id,
            completed_work=tuple(completed),
            pending_work=tuple(pending),
            next_steps=tuple(next_steps),
            blockers=tuple(blockers),
            source_progress_ids=tuple(ids),
        )

    @staticmethod
    def to_audit_record(capture: ProgressCapture) -> dict:
        """Project a capture into a JSON-safe audit record.

        Mirrors US-11/12/13: includes counts + status flags, EXCLUDES
        ``text``, ``confidence`` numeric values, and ``override.reason``
        free text. Sensitive business phrasing is never written into the
        audit chain.
        """
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        items_summary: list[dict] = []
        for item in capture.progress_items:
            items_summary.append(
                {
                    "item_id": item.item_id,
                    "task_id": item.task_id,
                    "kind": item.kind.value,
                    "source_kind": item.source_kind.value,
                    "evidence_ref_count": len(item.evidence_refs),
                    "override_count": len(item.overrides),
                    "status": item.status.value,
                }
            )
        return {
            "schema_version": SCHEMA_VERSION,
            "domain": DOMAIN,
            "capture_id": capture.capture_id,
            "workspace_project_id": capture.workspace.project_id,
            "workspace_role_id": capture.workspace.role_id,
            "workspace_revision": capture.workspace.revision,
            "item_count": len(capture.progress_items),
            "items": items_summary,
            "requires_user_confirmation": capture.requires_user_confirmation,
            "formally_accepted": capture.formally_accepted,
            "accepted_by": capture.accepted_by if capture.formally_accepted else "",
            "accepted_at": capture.accepted_at if capture.formally_accepted else "",
            "created_at": capture.created_at,
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _check_non_empty_str(value: object, *, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise ProgressCaptureValidationError(
            f"{field} must be a non-empty string"
        )


def _check_safe_id(value: object, *, field: str) -> None:
    _check_non_empty_str(value, field=field)
    if not _SAFE_ID.match(value):  # type: ignore[arg-type]
        raise ProgressCaptureValidationError(
            f"{field} must match safe-id; got {value!r}"
        )


def _check_hex64(value: object, *, field: str) -> None:
    _check_non_empty_str(value, field=field)
    if not _HEX_64.match(value):  # type: ignore[arg-type]
        raise ProgressCaptureValidationError(
            f"{field} must be 64-char lowercase hex; got {value!r}"
        )


def _check_iso_utc(value: object, *, field: str) -> None:
    _check_non_empty_str(value, field=field)
    if not _ISO_UTC_Z.match(value):  # type: ignore[arg-type]
        raise ProgressCaptureValidationError(
            f"{field} must be ISO-8601 UTC with 'Z' suffix; got {value!r}"
        )


def _check_confidence(value: object) -> None:
    if not isinstance(value, (int, float)):
        raise ProgressCaptureValidationError(
            f"confidence must be a number in [0.0, 1.0]; got {value!r}"
        )
    if isinstance(value, bool):
        raise ProgressCaptureValidationError(
            "confidence must be a number; bool is not accepted"
        )
    if not (0.0 <= float(value) <= 1.0):
        raise ProgressCaptureValidationError(
            f"confidence must lie in [0.0, 1.0]; got {value!r}"
        )


def _classify(ev: EvidenceInput) -> ProgressItemKind:
    """Map an :class:`EvidenceInput` to a :class:`ProgressItemKind`.

    Pure heuristic that follows AC-1/AC-2: TASK_DEPENDENCY_RESOLVED is
    always a NEXT_STEP, ARTIFACT_FILE is always COMPLETED,
    DOCUMENT_CONTENT is COMPLETED unless the text contains a "blocker"
    cue (case-insensitive), and EXPLICIT_USER_TEXT is COMPLETED unless
    the text contains "pending"/"next"/"blocker" cues.
    """
    text_lc = ev.text.lower()
    if ev.kind == EvidenceKind.TASK_DEPENDENCY_RESOLVED:
        return ProgressItemKind.NEXT_STEP
    if ev.kind == EvidenceKind.ARTIFACT_FILE:
        return ProgressItemKind.COMPLETED
    if "blocker" in text_lc or "blocked" in text_lc or "stuck" in text_lc:
        return ProgressItemKind.BLOCKER
    if "next" in text_lc or "upcoming" in text_lc or "todo" in text_lc:
        return ProgressItemKind.NEXT_STEP
    if "pending" in text_lc or "wip" in text_lc or "in progress" in text_lc:
        return ProgressItemKind.PENDING
    return ProgressItemKind.COMPLETED


def _make_item_id(project_id: str, task_id: str, index: int) -> str:
    return f"pc.{project_id}.{task_id}.{index}"


def _make_capture_id(project_id: str, now: str, item_count: int) -> str:
    # content-stable id: workspace project + safe-id-encoded UTC timestamp
    # + item count. ISO-8601 colons and "T" are replaced so the id matches
    # the project-wide safe-id regex (mirrors US-2/5/9/10/13 naming).
    safe_now = now.replace(":", "").replace("T", "t").replace(".", "p")
    return f"pc.{project_id}.{safe_now}.{item_count}"


# ---------------------------------------------------------------------------
# Real-time workspace watcher (US-8-AC-2)
# ---------------------------------------------------------------------------
#
# Imported last: watcher.py imports the evidence types defined above.

from .watcher import (  # noqa: E402
    DEFAULT_MAX_EVENTS,
    DEFAULT_POLL_INTERVAL_SEC,
    DEFAULT_STABILITY_CHECKS,
    FileChangeEvent,
    FileEventKind,
    FileSnapshot,
    WorkspaceWatcher,
)
