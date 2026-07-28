"""US-10 result-report merge engine (US-10-AC-1 P1 fix + Round-2 / 协议 § 16 + § 17).

Scope
-----
US-10 specifies the receiver-side state-merge flow:

  AC-1  system validates report package identity / signature /
        integrity / base_revision
  AC-2  duplicate report packages do NOT take effect twice
  AC-3  compare member's referenced baseline against current
        project master revision
  AC-4  conflict-free content enters normal review
  AC-5  conflicting content shows original / local / submitted values
  AC-6  user can choose accept-submitted / keep-local / manual /
        hold / return
  AC-7  time-stamp must NOT be the sole override basis
  AC-8  merge produces a new project master revision
  AC-9  original report + merge record are permanently retained
  AC-10 merged results can be revoked by permission

This slice (US-10-AC-1 P1 fix + Round-2) ships the *deterministic,
in-memory* half:

* :class:`MergeDecision` -- the decision enum (AC-6).
* :class:`FieldMerge` -- the per-field decision trace (AC-5 / AC-9)
  carrying THREE values: ``original_value`` (member's reported
  baseline), ``current_value`` (receiver's current master), and
  ``submitted_value`` (the report's value). When the field does not
  exist in either side, the corresponding :data:`MISSING` sentinel
  is used (no fabrication, no per-field override of the wrong
  attribute).
* :class:`MergeRecord` -- the persistent record of a single merge
  decision (AC-9) carrying ``base_version`` / ``current_version`` /
  ``merged_version`` / ``decision_maker`` / ``has_conflict`` /
  ``store_post`` (the post-merge :class:`ProcessedPackageStore`).
* :class:`MergeProposal` -- the deterministic result of one merge
  call: the new baseline (AC-8) + the merge record (AC-9) +
  ``accepted`` (AC-2) + ``rejection_reason``.
* :class:`MergeEngine` -- facade that consumes a
  :class:`ReportManifest` (US-9) + the current
  :class:`ProjectBaseline` (US-2) + a verified :class:`ImportOutcome`
  (US-5 AC-3) and emits a :class:`MergeProposal`.

P1 fixes (2026-07-27, security review deleg_9746448c):
* P1: ``merge`` now requires a verified :class:`ImportOutcome` whose
  transaction step is ``COMMITTED``, whose package matches the
  report on identity / project / sender / recipient / package_type,
  and whose package_type is in
  ``{"RESULT_SUBMISSION", "TASK_PROGRESS"}``. Naked
  :class:`ReportManifest` is refused with ``MergeError``.
* P2: ``merge`` looks up ``package_id`` in
  :class:`ProcessedPackageStore` and refuses duplicates with
  ``accepted=False`` (no version bump). On success, the new record
  is registered into the returned store (atomic
  register = one transaction). The caller persists ``store_post``
  alongside the audit log.
* P3: ``submitted_at`` is recorded as metadata only. The
  ``submitted_at > plan_end`` automatic override of ``plan_end`` is
  REMOVED. Any field with a :attr:`MergeDecision.HOLD` decision
  forces ``accepted=False``; the proposal does not bump the master
  version. This is the only place where a model-driven timestamp
  was overriding a business field; removal eliminates the AC-7
  violation.
* P4: ``FieldMerge.current_value`` carries the receiver's current
  master value (三方 diff for AC-5). The default for missing fields
  is the explicit ``__missing__`` sentinel -- never an arbitrary
  field. ``MergeRecord.base_version`` / ``current_version`` /
  ``merged_version`` use the protocol ``<project_id>-R<NNNN>``
  format (``P4 revision format fix``). ``decision_maker`` records
  the human/system identifier that authorised the merge.

Round-2 P1 fix (2026-07-27, security review deleg_3af08415):
* AC-3 base_revision mismatch (US-10 AC-3 / 协议 § 16.3) emits a
  HOLD-with-conflict proposal (``accepted=False``,
  ``has_conflict=True``) instead of silent accept.
* ``decision_maker`` is no longer a constructor argument. It is
  derived from ``import_outcome.record.package.recipient_cert_id``
  (US-5 verified identity) so that an attacker controlling the
  engine ctor cannot forge the authority that authorises a
  project-master version update (强制约束 § 8.4). Callers MAY pass
  an ``authorized_recipient_certs`` set to additionally pin the
  updater to a project-specific white-list (e.g. the project
  owner's cert id from the project identity layer); a non-empty
  intersection is required for ``accepted=True``.

Non-goals
---------
* No IO. The engine never touches the filesystem.
* No LLM, no model, no network.
* No mutation of US-2 / US-5 / US-9 wire layout. The engine
  consumes those types verbatim.
* Revocation (AC-10) lives in a future slice.
"""
from __future__ import annotations

import enum
import datetime as dt
from dataclasses import dataclass, field, replace
from typing import Iterable, Mapping

from src.coevo.protocol.import_service import ImportOutcome
from src.coevo.protocol.import_transaction import ImportStep
from src.coevo.protocol.processed_package_store import (
    AgentPackageStoreDuplicateError,
    ProcessedPackageRecord,
    ProcessedPackageStore,
)
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import ProjectBaseline, Task, WorkPackage
from .receipt import (
    BASELINE_DIGEST_ALGORITHM,
    BASELINE_SCHEMA,
    MergeCommitReceipt,
    MergeCommitReceiptError,
    MergeCommitReceiptStore,
    ReceiptSigningAuthority,
    append_signed_receipt,
    build_signed_merge_commit_receipt,
)
from .repository import MergeReceiptRepository


# Sentinel for fields not present in a value. Exposed publicly so
# tests and downstream consumers can compare against it without
# inventing a magic string.
class _MissingSentinel:
    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "__missing__"


MISSING: _MissingSentinel = _MissingSentinel()


def _is_missing(value: object) -> bool:
    return value is MISSING


# Package types that are eligible for state-merge. The protocol
# defines many package types (协议 § 5) but only result-style ones
# carry state-merge data; task-assignment / change / meeting-decision
# etc. are handled by other slices.
MERGEABLE_PACKAGE_TYPES: frozenset[str] = frozenset({
    "RESULT_SUBMISSION",
    "TASK_PROGRESS",
})


# ----------------------- decisions -----------------------


class MergeDecision(enum.Enum):
    """The decision the merge engine takes for one field (AC-6)."""

    ACCEPT = "accept"           # take the submitted value
    REJECT = "reject"           # keep the local value
    HOLD = "hold"               # pending user review (AC-4 / AC-5)
    MANUAL = "manual"           # user has manually adjusted the value


# ----------------------- per-field record -----------------------


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


# ----------------------- merge record -----------------------


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


# ----------------------- merge proposal -----------------------


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


# ----------------------- exceptions -----------------------


class MergeError(Exception):
    """Base class for US-10 merge errors. Fail-closed by default."""


class MergeValidationError(MergeError):
    """Raised when the merge input cannot be reconciled.

    Distinct from :class:`MergeError` so callers can branch on
    "validation failed (user-fixable)" vs "structural invariant
    violated (engineering bug)".
    """


# ----------------------- version helpers -----------------------


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


# ----------------------- engine -----------------------


@dataclass(frozen=True)
class MergeEngine:
    def __init__(
        self, *, receipt_repository: MergeReceiptRepository | None = None,
        receipt_authority: ReceiptSigningAuthority | None = None,
    ) -> None:
        if (receipt_repository is None) != (receipt_authority is None):
            raise MergeError("receipt repository and authority must be composed together")
        object.__setattr__(self, "_receipt_repository", receipt_repository)
        object.__setattr__(self, "_receipt_authority", receipt_authority)

    """Deterministic facade for the US-10-AC-1 merge slice (P1 fix + Round-2).

    The engine is PURE: it consumes a verified
    :class:`ImportOutcome` + a :class:`ReportManifest` (US-9) + the
    current :class:`ProjectBaseline` (US-2) and emits a
    :class:`MergeProposal` without ever touching IO. The
    conflict-resolution policy is fail-closed: anything that
    cannot be reconciled is held (:attr:`MergeDecision.HOLD`) and
    surfaces in the merge record with a precise reason.

    Round-2 P4 fix (2026-07-27): ``decision_maker`` is no longer a
    constructor argument. It is derived from
    ``import_outcome.record.recipient_cert_id`` (US-5 verified
    identity) so that an attacker controlling the engine ctor
    cannot forge the authority that authorises a project-master
    version update (mandatory constraint section 8.4 "project
    master version update must be confirmed by an authorised
    person"). Callers MAY pass an ``authorized_recipient_certs``
    set to additionally pin the updater to a project-specific
    white-list (e.g. the project owner cert id from the project
    identity layer); a non-empty intersection is required for
    ``accepted=True``.

    Round-2 P1 fix: base_revision mismatch (US-10 AC-3 / protocol
    section 16.3) emits a HOLD-with-conflict proposal
    (``accepted=False``, ``has_conflict=True``) instead of silent
    accept. The conflict is shown in the merge record three way
    diff fields.
    """

    def merge(
        self,
        *,
        import_outcome: ImportOutcome,
        report: ReportManifest,
        baseline: ProjectBaseline,
        store: ProcessedPackageStore,
        decided_at: str,
        authorized_recipient_certs: "frozenset[str] | None" = None,
    ) -> MergeProposal:
        """Run the merge.

        Algorithm (AC-1 / AC-2 / AC-3 / AC-4 / AC-5 / AC-6 / AC-7 /
        AC-8 / AC-9 / P1 / P2 / P3 / P4 / Round-2 P1 / Round-2 P4):

        1. P1 -- validate ``import_outcome``: its transaction must
           have ``step == ImportStep.COMMITTED``; the record must be
           present; the record package must match the report on
           identity / project / sender / recipient / package_type.
           The package_type must be in :data:`MERGEABLE_PACKAGE_TYPES`.
        2. P2 -- check the store: a record with the same
           ``package_id`` already present -> ``accepted=False``,
           ``rejection_reason`` cites AC-2.
        3. AC-3 (Round-2 P1) -- ``report.project_id ==
           baseline.project_id`` AND the report base_revision
           matches the receiver current master revision
           (``<project_id>-R<NNNN>``). Mismatch emits a
           HOLD-with-conflict proposal (``accepted=False``,
           ``has_conflict=True``); strict-reject path remains for
           malformed inputs.
        4. Round-2 P4 -- derive ``decision_maker`` from
           ``import_outcome.record.package.recipient_cert_id``
           (US-5 verified). If ``authorized_recipient_certs`` was
           supplied, the recipient must be in it. Empty decision
           maker is rejected.
        5. AC-4 / AC-7 -- compute per-field decisions, then
           apply. ``submitted_at`` is recorded as metadata only;
           it does NOT drive any field decision. A HOLD anywhere
           -> ``accepted=False``, no version bump.
        6. AC-8 -- on full success the new baseline is
           ``baseline.version + 1``; the merged revision follows
           :func:`_master_revision` format.
        7. P2 -- register the new ProcessedPackageRecord in the
           store atomically and emit it via ``record.store_post``.
        """
        # ----- type / shape validation -----
        if not isinstance(import_outcome, ImportOutcome):
            raise MergeError("import_outcome must be ImportOutcome")
        if not isinstance(report, ReportManifest):
            raise MergeError("report must be ReportManifest")
        if not isinstance(baseline, ProjectBaseline):
            raise MergeError("baseline must be ProjectBaseline")
        if not isinstance(store, ProcessedPackageStore):
            raise MergeError("store must be ProcessedPackageStore")
        if not isinstance(decided_at, str) or not decided_at:
            raise MergeValidationError(
                "decided_at must be a non-empty ISO-8601 string"
            )

        # ----- P1: import_outcome must be COMMITTED and bind to the report -----
        if import_outcome.transaction is None:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    "import_outcome.transaction is None; refusing to "
                    "merge (transaction must be COMMITTED per AC-1 + P1)"
                ),
                import_outcome=import_outcome,
            )
        tx = import_outcome.transaction
        if tx.step is not ImportStep.COMMITTED:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"import_outcome.transaction.step is "
                    f"{tx.step.value!r}, not COMMITTED; refusing to "
                    f"merge (AC-1 + P1 verified-import binding)"
                ),
                import_outcome=import_outcome,
            )
        if import_outcome.record is None:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    "import_outcome.record is None; import did not "
                    "register a ProcessedPackageRecord (AC-1 + P1)"
                ),
                import_outcome=import_outcome,
            )
        rec_pkg = import_outcome.record.package
        if rec_pkg.package_id != report.package_id:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"import_outcome.package_id {rec_pkg.package_id!r} "
                    f"does not match report.package_id "
                    f"{report.package_id!r} (AC-1 + P1)"
                ),
                import_outcome=import_outcome,
            )
        if rec_pkg.project_id != report.project_id:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"import_outcome.project_id {rec_pkg.project_id!r} "
                    f"does not match report.project_id "
                    f"{report.project_id!r} (AC-1 + P1)"
                ),
                import_outcome=import_outcome,
            )
        if rec_pkg.sender_cert_id != report.sender_cert_id:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"import_outcome.sender_cert_id "
                    f"{rec_pkg.sender_cert_id!r} does not match "
                    f"report.sender_cert_id {report.sender_cert_id!r} "
                    f"(AC-1 + P1)"
                ),
                import_outcome=import_outcome,
            )
        if rec_pkg.recipient_cert_id != report.recipient_cert_id:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"import_outcome.recipient_cert_id "
                    f"{rec_pkg.recipient_cert_id!r} does not match "
                    f"report.recipient_cert_id "
                    f"{report.recipient_cert_id!r} (AC-1 + P1)"
                ),
                import_outcome=import_outcome,
            )
        if import_outcome.record.package_type not in MERGEABLE_PACKAGE_TYPES:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"package_type {import_outcome.record.package_type!r} "
                    f"is not in MERGEABLE_PACKAGE_TYPES "
                    f"{sorted(MERGEABLE_PACKAGE_TYPES)} (AC-1 + P1)"
                ),
                import_outcome=import_outcome,
            )

        # ----- P2: replay / duplicate gate -----
        if store.get(rec_pkg.package_id) is not None:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"package_id {rec_pkg.package_id!r} already "
                    f"registered in store; duplicate report is a "
                    f"no-op (AC-2 + P2)"
                ),
                import_outcome=import_outcome,
            )
        if store.by_digest(rec_pkg.package_digest) is not None:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"package_digest {rec_pkg.package_digest!r} "
                    f"already registered in store; duplicate content "
                    f"is a no-op (AC-2 + P2)"
                ),
                import_outcome=import_outcome,
            )

        # ----- AC-3: project_id match -----
        if report.project_id != baseline.project_id:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"report.project_id {report.project_id!r} does "
                    f"not match baseline.project_id "
                    f"{baseline.project_id!r} (AC-3)"
                ),
                import_outcome=import_outcome,
            )

        # ----- AC-3 / Round-2 P1: base_revision must equal receiver current master revision -----
        expected_base_revision = _master_revision(
            baseline.project_id, baseline.version
        )
        if report.base_revision != expected_base_revision:
            return self._hold_with_conflict(
                baseline, store, report, decided_at,
                reason=(
                    f"report.base_revision {report.base_revision!r} "
                    f"does not match receiver current master "
                    f"{expected_base_revision!r} (AC-3 + protocol "
                    f"section 16.3); project master update requires "
                    f"explicit user conflict resolution (section 16.4)"
                ),
                import_outcome=import_outcome,
            )

        # ----- decision_maker authority (Round-2 P4 / mandatory constraint 8.4) -----
        # decision_maker is derived from the verified ImportOutcome,
        # NEVER from the engine ctor. If a project-level allow-list
        # was supplied, the recipient_cert_id must be in it.
        decision_maker = rec_pkg.recipient_cert_id
        if not decision_maker:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    "import_outcome.record.recipient_cert_id is empty; "
                    "decision_maker cannot be established; refusing "
                    "to update project master revision (mandatory 8.4)"
                ),
                import_outcome=import_outcome,
            )
        if authorized_recipient_certs is not None:
            if decision_maker not in authorized_recipient_certs:
                return self._reject(
                    baseline, store, report, decided_at,
                    reason=(
                        f"decision_maker {decision_maker!r} is not in "
                        f"authorized_recipient_certs "
                        f"{sorted(authorized_recipient_certs)!r} "
                        f"(mandatory 8.4); project master update must "
                        f"be authorised by a listed recipient"
                    ),
                    import_outcome=import_outcome,
                )

        # ----- versions (P4 explicit revisions) -----
        base_version = _master_revision(baseline.project_id, baseline.version)
        current_version = base_version
        merged_version = _master_revision(baseline.project_id, baseline.version + 1)

        # ----- per-field merge (AC-4 / AC-5 / AC-7 / P3) -----
        field_merges: list[FieldMerge] = []
        has_conflict = False

        # Field: progress_summary (text; auto-merge ON_TRACK only)
        fm = self._merge_text_field(
            field_path="progress_summary",
            current_value=baseline.title,
            submitted_value=report.progress_summary,
            report=report,
        )
        if fm is not None:
            field_merges.append(fm)
            if fm.decision is MergeDecision.HOLD:
                has_conflict = True

        # Field: status (AC-4 risk / progress indicator)
        fm = self._merge_status_field(
            current_value=MISSING,
            submitted_value=report.status,
            report=report,
        )
        if fm is not None:
            field_merges.append(fm)
            if fm.decision is MergeDecision.HOLD:
                has_conflict = True

        # Field: completed_work (list of strings; auto-merge ON_TRACK)
        fm = self._merge_str_list_field(
            field_path="completed_work",
            current_value=MISSING,
            submitted_value=report.completed_work,
            report=report,
            hold_when_at_risk=True,
        )
        if fm is not None:
            field_merges.append(fm)
            if fm.decision is MergeDecision.HOLD:
                has_conflict = True

        # Field: pending_work (list of strings; always HOLD on non-empty)
        if report.pending_work:
            fm = FieldMerge(
                field_path="pending_work",
                original_value=MISSING,
                current_value=MISSING,
                submitted_value=report.pending_work,
                decision=MergeDecision.HOLD,
                reason=(
                    f"status={report.status.value}; pending_work "
                    f"requires user review before commit (AC-6)"
                ),
            )
            field_merges.append(fm)
            has_conflict = True

        # Field: next_steps (HOLD always when present)
        if report.next_steps:
            fm = FieldMerge(
                field_path="next_steps",
                original_value=MISSING,
                current_value=MISSING,
                submitted_value=report.next_steps,
                decision=MergeDecision.HOLD,
                reason="next_steps must be authorised by project owner (AC-6)",
            )
            field_merges.append(fm)
            has_conflict = True

        # Field: risks (always HOLD per AC-4)
        if report.risks:
            fm = FieldMerge(
                field_path="risks",
                original_value=MISSING,
                current_value=MISSING,
                submitted_value=report.risks,
                decision=MergeDecision.HOLD,
                reason=(
                    "risks require human triage; HOLD pending user "
                    "review (AC-4)"
                ),
            )
            field_merges.append(fm)
            has_conflict = True

        # P3: any HOLD -> accepted=False (no version bump)
        if has_conflict:
            record = MergeRecord(
                project_id=baseline.project_id,
                reporter_package_id=report.package_id,
                base_revision=report.base_revision,
                base_version=base_version,
                current_version=current_version,
                merged_version=current_version,
                status=report.status,
                field_merges=tuple(field_merges),
                decided_at=decided_at,
                decision_maker=decision_maker,
                has_conflict=True,
                store_post=store,
            )
            return MergeProposal(
                new_baseline=baseline,
                record=record,
                accepted=False,
                rejection_reason=(
                    "merge record contains HOLD decisions; refusing "
                    "to update project master revision until all "
                    "fields are accepted by the project owner (AC-6 + P3)"
                ),
            )

        # ----- AC-8 / P2: build new baseline + register record -----
        new_baseline = ProjectBaseline(
            project_id=baseline.project_id,
            version=baseline.version + 1,
            created_at=decided_at,
            title=baseline.title,
            process_flow_ref=baseline.process_flow_ref,
            objective=baseline.objective,
            plan_start=baseline.plan_start,
            plan_end=baseline.plan_end,
            responsible_units=baseline.responsible_units,
            work_packages=baseline.work_packages,
            dependencies=baseline.dependencies,
            milestones=baseline.milestones,
        )
        try:
            new_store = store.register(
                ProcessedPackageRecord(
                    package=rec_pkg,
                    package_type=import_outcome.record.package_type,
                    processed_at=decided_at,
                    result="committed",
                    revision=merged_version,
                )
            )
        except AgentPackageStoreDuplicateError as exc:
            return self._reject(
                baseline, store, report, decided_at,
                reason=(
                    f"concurrent register lost the race: {exc}; "
                    f"refusing double-commit (AC-2 + P2)"
                ),
                import_outcome=import_outcome,
            )

        record = MergeRecord(
            project_id=baseline.project_id,
            reporter_package_id=report.package_id,
            base_revision=report.base_revision,
            base_version=base_version,
            current_version=current_version,
            merged_version=merged_version,
            status=report.status,
            field_merges=tuple(field_merges),
            decided_at=decided_at,
            decision_maker=decision_maker,
            has_conflict=False,
            store_post=new_store,
        )
        return MergeProposal(
            new_baseline=new_baseline,
            record=record,
            accepted=True,
        )

    def merge_and_commit(
        self,
        *,
        import_outcome: ImportOutcome,
        report: ReportManifest,
        baseline: ProjectBaseline,
        store: ProcessedPackageStore,
        decided_at: str,
        authorized_recipient_certs: "frozenset[str] | None" = None,
    ) -> MergeCommitOutcome:
        """Atomically merge and register an authoritative content receipt."""
        if (
            type(self._receipt_repository) is not MergeReceiptRepository
            or type(self._receipt_authority) is not ReceiptSigningAuthority
        ):
            raise MergeError("merge engine lacks the system receipt composition")
        receipt_repository = self._receipt_repository
        receipt_authority = self._receipt_authority
        prior_history = receipt_repository.verified_history(
            trusted_time=dt.datetime.fromisoformat(
                decided_at.removesuffix("Z") + "+00:00"
            )
        )
        receipt_store = MergeCommitReceiptStore.empty()
        for historical in prior_history:
            receipt_store = append_signed_receipt(receipt_store, historical)
        proposal = self.merge(
            import_outcome=import_outcome,
            report=report,
            baseline=baseline,
            store=store,
            decided_at=decided_at,
            authorized_recipient_certs=authorized_recipient_certs,
        )
        if not proposal.accepted:
            return MergeCommitOutcome(
                proposal=proposal, receipt=None, receipt_store=receipt_store,
            )

        imported_record = import_outcome.record
        transaction = import_outcome.transaction
        if (
            imported_record is None
            or imported_record.result != "committed"
            or imported_record.package_type != report.package_type
            or imported_record.revision != report.base_revision
            or imported_record.package.sequence_no != report.sequence_no
            or transaction.package_id != report.package_id
            or transaction.project_id != report.project_id
            or transaction.base_revision != report.base_revision
            or transaction.current_revision != report.base_revision
        ):
            rolled_back = self._rollback_receipt_commit(
                proposal=proposal,
                baseline=baseline,
                store=store,
                reason="authoritative import facts do not bind to the report",
            )
            return MergeCommitOutcome(
                proposal=rolled_back, receipt=None, receipt_store=receipt_store,
            )

        if (
            not isinstance(proposal.record.field_merges, tuple)
            or any(
                not isinstance(field_merge, FieldMerge)
                or field_merge.decision
                not in (MergeDecision.ACCEPT, MergeDecision.MANUAL)
                for field_merge in proposal.record.field_merges
            )
        ):
            rolled_back = self._rollback_receipt_commit(
                proposal=proposal,
                baseline=baseline,
                store=store,
                reason="committed merge contains an untrusted field decision",
            )
            return MergeCommitOutcome(
                proposal=rolled_back, receipt=None, receipt_store=receipt_store,
            )

        status_merges = tuple(
            merge for merge in proposal.record.field_merges
            if isinstance(merge, FieldMerge) and merge.field_path == "status"
        )
        baseline_task_ids = {
            task.task_id
            for work_package in proposal.new_baseline.work_packages
            for task in work_package.tasks
        }
        if (
            len(status_merges) != 1
            or status_merges[0].decision
            not in (MergeDecision.ACCEPT, MergeDecision.MANUAL)
            or status_merges[0].submitted_value is not report.status
            or report.task_id not in baseline_task_ids
            or proposal.record.reporter_package_id != report.package_id
            or proposal.record.status is not report.status
            or proposal.record.decision_maker
            != imported_record.package.recipient_cert_id
        ):
            rolled_back = self._rollback_receipt_commit(
                proposal=proposal,
                baseline=baseline,
                store=store,
                reason=(
                    "committed merge lacks one accepted status field "
                    "or references an unknown task"
                ),
            )
            return MergeCommitOutcome(
                proposal=rolled_back, receipt=None, receipt_store=receipt_store,
            )

        package = imported_record.package
        if receipt_authority.signer_certificate_id != package.recipient_cert_id:
            rolled_back = self._rollback_receipt_commit(
                proposal=proposal, baseline=baseline, store=store,
                reason="receipt signer is not the verified merge recipient",
            )
            return MergeCommitOutcome(
                proposal=rolled_back, receipt=None, receipt_store=receipt_store,
            )
        status_decision = status_merges[0].decision.value
        completed_task_id = (
            report.task_id if report.status is ReportStatus.COMPLETED else None
        )
        try:
            trusted_time = dt.datetime.fromisoformat(
                decided_at.removesuffix("Z") + "+00:00"
            )
            def receipt_builder(store_id, store_sequence, previous_id, previous_hash):
                return build_signed_merge_commit_receipt(
                authority=receipt_authority,
                trusted_time=trusted_time,
                baseline=proposal.new_baseline,
                store_id=store_id, store_sequence=store_sequence,
                previous_receipt_id=previous_id,
                previous_receipt_hash=previous_hash,
                package_id=package.package_id,
                package_digest=package.package_digest,
                sender_cert_id=package.sender_cert_id,
                recipient_cert_id=package.recipient_cert_id,
                sequence_no=package.sequence_no,
                package_type=imported_record.package_type,
                import_processed_at=imported_record.processed_at,
                project_id=report.project_id,
                task_id=report.task_id,
                report_status=report.status,
                status_decision=status_decision,
                base_revision=proposal.record.base_revision,
                current_revision=proposal.record.current_version,
                merged_revision=proposal.record.merged_version,
                commit_decided_at=proposal.record.decided_at,
                decision_maker=proposal.record.decision_maker,
                baseline_digest_algorithm=BASELINE_DIGEST_ALGORITHM,
                baseline_schema=BASELINE_SCHEMA,
                completed_task_id=completed_task_id,
                )
            receipt = receipt_repository.commit(
                receipt_builder, trusted_time=trusted_time,
            )
            committed_receipts = append_signed_receipt(receipt_store, receipt)
        except (MergeCommitReceiptError, ValueError) as exc:
            rolled_back = self._rollback_receipt_commit(
                proposal=proposal,
                baseline=baseline,
                store=store,
                reason=f"receipt commit failed: {exc}",
            )
            return MergeCommitOutcome(
                proposal=rolled_back, receipt=None, receipt_store=receipt_store,
            )
        return MergeCommitOutcome(
            proposal=proposal,
            receipt=receipt,
            receipt_store=committed_receipts,
        )

    # ----- internal helpers -----

    def _rollback_receipt_commit(
        self,
        *,
        proposal: MergeProposal,
        baseline: ProjectBaseline,
        store: ProcessedPackageStore,
        reason: str,
    ) -> MergeProposal:
        record = replace(
            proposal.record,
            merged_version=proposal.record.current_version,
            has_conflict=True,
            store_post=store,
        )
        return MergeProposal(
            new_baseline=baseline,
            record=record,
            accepted=False,
            rejection_reason=reason,
        )

    def _reject(
        self,
        baseline: ProjectBaseline,
        store: ProcessedPackageStore,
        report: ReportManifest,
        decided_at: str,
        *,
        reason: str,
        import_outcome: "ImportOutcome | None" = None,
    ) -> MergeProposal:
        base_version = _master_revision(baseline.project_id, baseline.version)
        dm = ""
        if (
            import_outcome is not None
            and getattr(import_outcome, "record", None) is not None
        ):
            try:
                dm = import_outcome.record.package.recipient_cert_id
            except Exception:
                dm = ""
        record = MergeRecord(
            project_id=baseline.project_id,
            reporter_package_id=report.package_id,
            base_revision=report.base_revision,
            base_version=base_version,
            current_version=base_version,
            merged_version=base_version,
            status=report.status,
            field_merges=(),
            decided_at=decided_at,
            decision_maker=dm,
            has_conflict=True,
            store_post=store,
        )
        return MergeProposal(
            new_baseline=baseline,
            record=record,
            accepted=False,
            rejection_reason=reason,
        )

    def _hold_with_conflict(
        self,
        baseline: ProjectBaseline,
        store: ProcessedPackageStore,
        report: ReportManifest,
        decided_at: str,
        *,
        reason: str,
        import_outcome: "ImportOutcome | None" = None,
    ) -> MergeProposal:
        """Emit a HOLD-with-conflict proposal (AC-3 / protocol 16.3 + 16.4).

        Same shape as :meth:`_reject` but the rejection_reason is
        labelled as a "conflict" rather than a hard reject, and
        ``has_conflict=True`` signals the UI layer to render a
        three way diff for user resolution.
        """
        return self._reject(
            baseline, store, report, decided_at,
            reason=reason, import_outcome=import_outcome,
        )

    def _merge_text_field(
        self,
        *,
        field_path: str,
        current_value: object,
        submitted_value: object,
        report: ReportManifest,
    ) -> FieldMerge | None:
        if not submitted_value or submitted_value == "no change":
            return None
        decision = MergeDecision.ACCEPT
        if report.status in (ReportStatus.AT_RISK, ReportStatus.BLOCKED):
            decision = MergeDecision.HOLD
        return FieldMerge(
            field_path=field_path,
            original_value=MISSING,
            current_value=current_value if current_value is not None else MISSING,
            submitted_value=submitted_value,
            decision=decision,
            reason=(
                f"status={report.status.value}; "
                f"{'HOLD pending user review' if decision is MergeDecision.HOLD else 'ACCEPT text field'}"
            ),
        )

    def _merge_status_field(
        self,
        *,
        current_value: object,
        submitted_value: object,
        report: ReportManifest,
    ) -> FieldMerge | None:
        if submitted_value is None:
            return None
        decision = MergeDecision.ACCEPT
        if report.status in (ReportStatus.AT_RISK, ReportStatus.BLOCKED):
            decision = MergeDecision.HOLD
        return FieldMerge(
            field_path="status",
            original_value=MISSING,
            current_value=MISSING,
            submitted_value=submitted_value,
            decision=decision,
            reason=(
                f"status={report.status.value}; "
                f"{'HOLD pending user review' if decision is MergeDecision.HOLD else 'ACCEPT status'}"
            ),
        )

    def _merge_str_list_field(
        self,
        *,
        field_path: str,
        current_value: object,
        submitted_value: object,
        report: ReportManifest,
        hold_when_at_risk: bool,
    ) -> FieldMerge | None:
        if not submitted_value:
            return None
        decision = MergeDecision.ACCEPT
        if hold_when_at_risk and report.status in (
            ReportStatus.AT_RISK,
            ReportStatus.BLOCKED,
        ):
            decision = MergeDecision.HOLD
        return FieldMerge(
            field_path=field_path,
            original_value=MISSING,
            current_value=current_value,
            submitted_value=submitted_value,
            decision=decision,
            reason=(
                f"status={report.status.value}; "
                f"{'HOLD pending user review' if decision is MergeDecision.HOLD else 'ACCEPT list field'}"
            ),
        )

    def to_audit_record(self, proposal: MergeProposal) -> dict[str, object]:
        """Emit a deterministic, JSON-safe audit-record projection.

        Sensitive detail (``field_merges`` content, ``store_post``)
        is intentionally NOT included in the audit projection;
        the full record lives in :attr:`proposal.record` for
        callers that need the per-field trace.
        """
        if not isinstance(proposal, MergeProposal):
            raise MergeError("proposal must be MergeProposal")
        return {
            "kind": "merge.proposal",
            "schema_version": "1.0",
            "project_id": proposal.record.project_id,
            "reporter_package_id": proposal.record.reporter_package_id,
            "base_revision": proposal.record.base_revision,
            "base_version": proposal.record.base_version,
            "current_version": proposal.record.current_version,
            "merged_version": proposal.record.merged_version,
            "status": proposal.record.status.value,
            "accepted": proposal.accepted,
            "rejection_reason": proposal.rejection_reason,
            "has_conflict": proposal.record.has_conflict,
            "field_merge_count": len(proposal.record.field_merges),
            "decided_at": proposal.record.decided_at,
            "decision_maker": proposal.record.decision_maker,
        }


__all__ = [
    "FieldMerge",
    "MERGEABLE_PACKAGE_TYPES",
    "MISSING",
    "MergeDecision",
    "MergeEngine",
    "MergeError",
    "MergeCommitOutcome",
    "MergeCommitReceipt",
    "MergeCommitReceiptError",
    "MergeCommitReceiptStore",
    "MergeProposal",
    "MergeRecord",
    "MergeValidationError",
    "canonical_baseline_digest",
    "_hold_with_conflict",
    "_master_revision",
]
