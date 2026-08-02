"""progress_capture.models - US-8 progress-capture domain models, enums, errors and shared validators."""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from src.coevo.workspace.models import WorkspaceEntry

SCHEMA_VERSION: str = "1.0"

DOMAIN: str = "coevo.progress_capture"

_HEX_64 = re.compile(r"^[0-9a-f]{64}$")

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")

_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")

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
