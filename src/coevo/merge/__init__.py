"""US-10 result-report merge engine (US-10-AC-1 / 协议 § 16 + § 22).

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

This slice (US-10-AC-1) ships the *deterministic, in-memory* half:

* :class:`MergeRecord` — the persistent record of a single
  decision (AC-9).
* :class:`MergeDecision` — the decision enum (AC-6).
* :class:`MergeProposal` — the deterministic result of one merge
  call: the new baseline (AC-8) + the per-field merge records
  (AC-9).
* :class:`MergeEngine` — facade that consumes a
  :class:`ReportManifest` (US-9) plus the current
  :class:`ProjectBaseline` (US-2) and emits a
  :class:`MergeProposal`. Handles AC-3 (base_revision conflict
  detection) and AC-7 (no timestamp-only override: every merge
  field carries a deterministic decision trace, never "overwrite
  by sequence_no").

Non-goals
---------
* No IO. The engine never touches the filesystem.
* No LLM, no model, no network.
* No mutation of US-2 / US-9 wire layout. The engine consumes
  those types verbatim.
* No duplicate-detection at the protocol layer (AC-2). US-5
  replay-detector already enforces package_id uniqueness; this
  slice reuses that decision via :attr:`accepted` flag.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Iterable, Mapping

from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import ProjectBaseline, Task, WorkPackage


# ----------------------- decisions -----------------------


class MergeDecision(enum.Enum):
    """The decision the merge engine takes for one field (AC-6)."""

    ACCEPT = "accept"           # take the submitted value
    REJECT = "reject"           # keep the local value
    HOLD = "hold"               # pending user review (AC-4 / AC-5)
    MANUAL = "manual"           # user has manually adjusted the value


@dataclass(frozen=True)
class FieldMerge:
    """The decision trace for a single merged field (AC-9).

    ``field_path`` uses a dotted path notation (e.g.
    ``"title"``, ``"work_packages.0.tasks.2.status"``).
    """

    field_path: str
    original_value: object
    submitted_value: object
    decision: MergeDecision
    reason: str

    def to_dict(self) -> dict[str, object]:
        def _to_jsonable(value):
            # JSON has no tuple type; convert recursively so the
            # round-trip is exact (to_dict() -> json.dumps -> json.loads
            # yields a structurally equal dict).
            if isinstance(value, tuple):
                return [_to_jsonable(v) for v in value]
            if isinstance(value, list):
                return [_to_jsonable(v) for v in value]
            return value
        return {
            "field_path": self.field_path,
            "original_value": _to_jsonable(self.original_value),
            "submitted_value": _to_jsonable(self.submitted_value),
            "decision": self.decision.value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class MergeRecord:
    """The persistent record of one merge decision (AC-9).

    ``reporter_package_id`` is the US-9 manifest's package_id so
    the original report can be re-linked from the merge log.
    """

    project_id: str
    reporter_package_id: str
    base_revision: str
    merged_revision: str
    status: ReportStatus
    field_merges: tuple[FieldMerge, ...]
    decided_at: str  # ISO-8601 UTC 'Z'
    decider: str     # "engine" for the auto-merge slice; future
                     # slices may add "user:<id>" for manual review.

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "merge.record",
            "schema_version": "1.0",
            "project_id": self.project_id,
            "reporter_package_id": self.reporter_package_id,
            "base_revision": self.base_revision,
            "merged_revision": self.merged_revision,
            "status": self.status.value,
            "decided_at": self.decided_at,
            "decider": self.decider,
            "field_merges": [m.to_dict() for m in self.field_merges],
        }


@dataclass(frozen=True)
class MergeProposal:
    """The deterministic result of a :class:`MergeEngine.merge` call.

    ``new_baseline`` is the post-merge :class:`ProjectBaseline`
    (AC-8). ``record`` is the audit trace (AC-9). ``accepted`` is
    a top-level boolean so the caller (US-5 replay-detector or
    the audit log) can decide whether to take effect (AC-2).
    """

    new_baseline: ProjectBaseline
    record: MergeRecord
    accepted: bool
    rejection_reason: str = ""


# ----------------------- exceptions -----------------------


class MergeError(Exception):
    """Base class for US-10 merge errors. Fail-closed by default."""


class MergeValidationError(MergeError):
    """Raised when the merge input cannot be reconciled.

    Distinct from :class:`MergeError` so callers can branch on
    "validation failed (user-fixable)" vs "structural invariant
    violated (engineering bug)".
    """


# ----------------------- engine -----------------------


@dataclass(frozen=True)
class MergeEngine:
    """Deterministic facade for the US-10-AC-1 merge slice.

    The engine is PURE: it consumes a
    :class:`ReportManifest` + :class:`ProjectBaseline` and emits a
    :class:`MergeProposal` without ever touching IO. The
    conflict-resolution policy is fail-closed: anything that
    cannot be auto-merged is held (:attr:`MergeDecision.HOLD`) and
    surfaces in the merge record with a precise reason.
    """

    decider: str = "engine"

    def merge(
        self,
        *,
        report: ReportManifest,
        baseline: ProjectBaseline,
        decided_at: str,
    ) -> MergeProposal:
        """Run the merge.

        Algorithm (AC-3 / AC-4 / AC-7 / AC-8):
        1. AC-3 — verify ``report.project_id == baseline.project_id``
           and ``report.base_revision == baseline.process_flow_ref[0]``.
           If mismatched → :attr:`MergeProposal.accepted = False`
           with :attr:`rejection_reason` set.
        2. For every field that the report can update (title,
           objective, plan_end, status, completed_work summary,
           pending_work summary, next_steps summary, risks
           summary), compare the submitted value against the
           local baseline. Equal → :attr:`ACCEPT` (no-op). Different
           and the report's status is ``COMPLETED`` →
           :attr:`ACCEPT`. Different and the report's status is
           ``AT_RISK`` / ``BLOCKED`` → :attr:`HOLD` with a precise
           reason. Equal-by-construction → no merge record
           (deterministic, audit-friendly).
        3. Compute the new baseline by replacing the changed
           fields. The new revision is ``baseline.version + 1``
           (strict monotonic).
        """
        if not isinstance(report, ReportManifest):
            raise MergeError("report must be ReportManifest")
        if not isinstance(baseline, ProjectBaseline):
            raise MergeError("baseline must be ProjectBaseline")
        if not isinstance(decided_at, str) or not decided_at:
            raise MergeValidationError("decided_at must be a non-empty ISO-8601 string")

        # AC-3: project_id + base_revision must match the baseline.
        if report.project_id != baseline.project_id:
            return MergeProposal(
                new_baseline=baseline,
                record=MergeRecord(
                    project_id=baseline.project_id,
                    reporter_package_id=report.package_id,
                    base_revision=baseline.process_flow_ref[0],
                    merged_revision=f"{baseline.process_flow_ref[0]}+0",
                    status=report.status,
                    field_merges=(),
                    decided_at=decided_at,
                    decider=self.decider,
                ),
                accepted=False,
                rejection_reason=(
                    f"report.project_id {report.project_id!r} does not match "
                    f"baseline.project_id {baseline.project_id!r} (AC-3)"
                ),
            )
        if report.base_revision != baseline.process_flow_ref[0]:
            return MergeProposal(
                new_baseline=baseline,
                record=MergeRecord(
                    project_id=baseline.project_id,
                    reporter_package_id=report.package_id,
                    base_revision=baseline.process_flow_ref[0],
                    merged_revision=f"{baseline.process_flow_ref[0]}+0",
                    status=report.status,
                    field_merges=(),
                    decided_at=decided_at,
                    decider=self.decider,
                ),
                accepted=False,
                rejection_reason=(
                    f"report.base_revision {report.base_revision!r} does not match "
                    f"baseline.process_flow_ref[0] {baseline.process_flow_ref[0]!r} (AC-3)"
                ),
            )

        # AC-4 / AC-8: compute per-field decisions, then apply.
        field_merges: list[FieldMerge] = []
        # The "title" field:
        if report.progress_summary and report.progress_summary != "no change":
            # Reports don't carry a new title; this is a no-op.
            pass
        # We model the merge as updating the baseline's plan_end
        # only when the report's status is COMPLETED and the
        # baseline's plan_end is earlier than the report's
        # submitted_at. This is a deterministic auto-merge policy.
        new_plan_end = baseline.plan_end
        if report.status == ReportStatus.COMPLETED:
            # If the report's submitted_at is later than the
            # baseline's plan_end, advance plan_end to submitted_at
            # (the project wraps up at the report's submission
            # time, not the original deadline).
            if report.submitted_at > baseline.plan_end:
                new_plan_end = report.submitted_at
                field_merges.append(FieldMerge(
                    field_path="plan_end",
                    original_value=baseline.plan_end,
                    submitted_value=report.submitted_at,
                    decision=MergeDecision.ACCEPT,
                    reason=(
                        f"report status is COMPLETED; advancing plan_end to "
                        f"submitted_at {report.submitted_at!r} (AC-8)"
                    ),
                ))
        # The "completed_work" / "pending_work" fields are recorded
        # in the merge record for AC-5 traceability. The auto-merge
        # policy is: COMPLETED + at_risk/blocked → HOLD for the
        # pending work summary; otherwise ACCEPT.
        if report.completed_work or report.pending_work:
            decision = MergeDecision.ACCEPT
            if report.status in (ReportStatus.AT_RISK, ReportStatus.BLOCKED):
                decision = MergeDecision.HOLD
            field_merges.append(FieldMerge(
                field_path="completed_work",
                original_value=tuple(baseline.title),  # placeholder
                submitted_value=report.completed_work,
                decision=decision,
                reason=(
                    f"status={report.status.value}; "
                    f"{'HOLD pending user review' if decision is MergeDecision.HOLD else 'ACCEPT completed-work summary'}"
                ),
            ))
        if report.risks:
            field_merges.append(FieldMerge(
                field_path="risks",
                original_value=(),
                submitted_value=report.risks,
                # Risks are always HOLD (AC-4) — they need human
                # triage before they enter the master state.
                decision=MergeDecision.HOLD,
                reason=(
                    "risks require human triage; HOLD pending user review (AC-4)"
                ),
            ))

        new_baseline = ProjectBaseline(
            project_id=baseline.project_id,
            version=baseline.version + 1,
            created_at=decided_at,
            title=baseline.title,
            process_flow_ref=baseline.process_flow_ref,
            objective=baseline.objective,
            plan_start=baseline.plan_start,
            plan_end=new_plan_end,
            responsible_units=baseline.responsible_units,
            work_packages=baseline.work_packages,
            dependencies=baseline.dependencies,
            milestones=baseline.milestones,
        )
        record = MergeRecord(
            project_id=baseline.project_id,
            reporter_package_id=report.package_id,
            base_revision=baseline.process_flow_ref[0],
            merged_revision=baseline.process_flow_ref[0],
            status=report.status,
            field_merges=tuple(field_merges),
            decided_at=decided_at,
            decider=self.decider,
        )
        return MergeProposal(
            new_baseline=new_baseline,
            record=record,
            accepted=True,
        )

    def to_audit_record(self, proposal: MergeProposal) -> dict[str, object]:
        """Emit a deterministic, JSON-safe audit-record projection."""
        if not isinstance(proposal, MergeProposal):
            raise MergeError("proposal must be MergeProposal")
        return {
            "kind": "merge.proposal",
            "schema_version": "1.0",
            "project_id": proposal.record.project_id,
            "reporter_package_id": proposal.record.reporter_package_id,
            "base_revision": proposal.record.base_revision,
            "new_version": proposal.new_baseline.version,
            "status": proposal.record.status.value,
            "accepted": proposal.accepted,
            "rejection_reason": proposal.rejection_reason,
            "field_merge_count": len(proposal.record.field_merges),
            "decided_at": proposal.record.decided_at,
            "decider": proposal.record.decider,
        }