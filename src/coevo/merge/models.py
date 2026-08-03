"""merge.models - domain models, enums, sentinels and errors for US-10 (merged from the former package __init__)."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from src.coevo.protocol.processed_package_store import ProcessedPackageStore
from src.coevo.report import ReportStatus
from src.coevo.task_decomposition import ProjectBaseline
from .receipt import MergeCommitReceipt, MergeCommitReceiptStore

class _MissingSentinel:
    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "__missing__"

MISSING: _MissingSentinel = _MissingSentinel()

def _is_missing(value: object) -> bool:
    return value is MISSING

MERGEABLE_PACKAGE_TYPES: frozenset[str] = frozenset({
    "RESULT_SUBMISSION",
    "TASK_PROGRESS",
})

class MergeDecision(enum.Enum):
    """The decision the merge engine takes for one field (AC-6)."""

    ACCEPT = "accept"           # take the submitted value
    REJECT = "reject"           # keep the local value
    HOLD = "hold"               # pending user review (AC-4 / AC-5)
    MANUAL = "manual"

@dataclass(frozen=True)
class FieldMerge:
    """The decision trace for a single merged field (AC-5 / AC-9).

    Carries the THREE values needed for 协议 § 16.4 conflict display:

    * ``original_value`` -- the value in the report's referenced
      baseline (== the member's snapshot at submit time). May be
      :data:`MISSING` when the report does not carry a comparable
      field.
    * ``current_value`` -- the value in the receiver's CURRENT
      master revision (三方 diff, P4). May be :data:`MISSING` when
      the receiver has no comparable field.
    * ``submitted_value`` -- the value the report claims. May be
      :data:`MISSING` when the report has no value (e.g. empty
      risks list).
    * ``decision`` -- one of :class:`MergeDecision`. The decision
      applies in the order: HOLD (force hold) > MANUAL (caller
      pre-decided) > REJECT (keep local) > ACCEPT (take submitted).
    * ``reason`` -- a non-empty explanation. AC-7 forbids pure
      timestamp override; the reason must cite a protocol /
      story identifier (e.g. ``"(AC-8)"``) when a model-driven
      inference was applied.
    """

    field_path: str
    original_value: object
    current_value: object
    submitted_value: object
    decision: MergeDecision
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.field_path, str) or not self.field_path:
            raise ValueError("field_path must be a non-empty string")
        if not isinstance(self.decision, MergeDecision):
            raise ValueError("decision must be a MergeDecision")
        if not isinstance(self.reason, str) or not self.reason:
            raise ValueError("reason must be a non-empty string")

    def to_dict(self) -> dict[str, object]:
        def _to_jsonable(value):
            # JSON has no tuple / enum / MISSING-sentinel type;
            # convert recursively so the round-trip is exact
            # (to_dict() -> json.dumps -> json.loads yields a
            # structurally equal dict).
            if _is_missing(value):
                return None  # explicit null = "no value"
            if isinstance(value, enum.Enum):
                return value.value
            if isinstance(value, tuple):
                return [_to_jsonable(v) for v in value]
            if isinstance(value, list):
                return [_to_jsonable(v) for v in value]
            return value
        return {
            "field_path": self.field_path,
            "original_value": _to_jsonable(self.original_value),
            "current_value": _to_jsonable(self.current_value),
            "submitted_value": _to_jsonable(self.submitted_value),
            "decision": self.decision.value,
            "reason": self.reason,
        }

@dataclass(frozen=True)
class MergeRecord:
    """The persistent record of one merge decision (AC-9).

    ``reporter_package_id`` is the US-9 manifest's package_id so the
    original report can be re-linked from the merge log.

    The record carries the three explicit project master revisions
    (P4) plus the authorised decision-maker (AC-6 / 强制约束 § 8.4
    "项目主版本更新必须由有权人员确认"). ``store_post`` is the
    :class:`ProcessedPackageStore` AFTER the merge has registered
    the package; on a HOLD or duplicate-reject proposal the store
    is unchanged.
    """

    project_id: str
    reporter_package_id: str
    base_revision: str
    base_version: str
    current_version: str
    merged_version: str
    status: ReportStatus
    field_merges: tuple[FieldMerge, ...]
    decided_at: str  # ISO-8601 UTC 'Z'
    decision_maker: str
    has_conflict: bool
    store_post: ProcessedPackageStore

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "merge.record",
            "schema_version": "1.0",
            "project_id": self.project_id,
            "reporter_package_id": self.reporter_package_id,
            "base_revision": self.base_revision,
            "base_version": self.base_version,
            "current_version": self.current_version,
            "merged_version": self.merged_version,
            "status": self.status.value,
            "decided_at": self.decided_at,
            "decision_maker": self.decision_maker,
            "has_conflict": self.has_conflict,
            "field_merges": [m.to_dict() for m in self.field_merges],
            "store_post_length": len(self.store_post),
        }

@dataclass(frozen=True)
class MergeProposal:
    """The deterministic result of a :class:`MergeEngine.merge` call.

    ``new_baseline`` is the post-merge :class:`ProjectBaseline`
    (AC-8) -- equal to the input baseline when ``accepted`` is
    False (rejection / HOLD / duplicate).

    ``record`` is the audit trace (AC-9) and is always populated
    so the caller can emit a uniform audit log entry.

    ``accepted`` is a top-level boolean so the caller (US-5
    replay-detector or the audit log) can decide whether to take
    effect (AC-2). When False, ``rejection_reason`` carries the
    precise reason (AC-3 / AC-6).
    """

    new_baseline: ProjectBaseline
    record: MergeRecord
    accepted: bool
    rejection_reason: str = ""

@dataclass(frozen=True)
class MergeCommitOutcome:
    """Atomic result of merge plus authoritative receipt registration."""

    proposal: MergeProposal
    receipt: MergeCommitReceipt | None
    receipt_store: MergeCommitReceiptStore

    def __post_init__(self) -> None:
        if not isinstance(self.proposal, MergeProposal):
            raise ValueError("proposal must be MergeProposal")
        if not isinstance(self.receipt_store, MergeCommitReceiptStore):
            raise ValueError("receipt_store must be MergeCommitReceiptStore")
        if self.proposal.accepted:
            if self.receipt is None:
                raise ValueError("accepted commit outcome requires a receipt")
            if self.receipt_store.get(self.receipt.receipt_id) != self.receipt:
                raise ValueError("accepted receipt must be registered")
        elif self.receipt is not None:
            raise ValueError("failed commit outcome must not carry a receipt")

class MergeError(Exception):
    """Base class for US-10 merge errors. Fail-closed by default."""

class MergeValidationError(MergeError):
    """Raised when the merge input cannot be reconciled.

    Distinct from :class:`MergeError` so callers can branch on
    "validation failed (user-fixable)" vs "structural invariant
    violated (engineering bug)".
    """

def _master_revision(project_id: str, version_number: int) -> str:
    """Render a project master revision in the protocol § 16.1 format.

    ``<project_id>-R<NNNN>`` (zero-padded to 4 digits; the format
    is a token rule, not a numerical invariant).
    """
    if not isinstance(project_id, str) or not project_id:
        raise ValueError("project_id must be a non-empty string")
    if not isinstance(version_number, int) or version_number < 0:
        raise ValueError("version_number must be a non-negative integer")
    return f"{project_id}-R{version_number:04d}"
