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
* Revocation (AC-10) lives in a future slice."""

from __future__ import annotations

import enum
import datetime as dt
from dataclasses import dataclass, field, replace
from typing import Iterable, Mapping
from src.coevo.protocol.import_service import ImportOutcome
from src.coevo.protocol.import_transaction import ImportStep
from src.coevo.protocol.processed_package_store import AgentPackageStoreDuplicateError, ProcessedPackageRecord, ProcessedPackageStore
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import ProjectBaseline, Task, WorkPackage

from .models import (FieldMerge, MERGEABLE_PACKAGE_TYPES, MISSING, MergeCommitOutcome, MergeDecision, MergeError, MergeProposal, MergeRecord, MergeValidationError, _MissingSentinel, _is_missing, _master_revision)

from .engine import (MergeEngine)

from .receipt import BASELINE_DIGEST_ALGORITHM, BASELINE_SCHEMA, MergeCommitReceipt, MergeCommitReceiptError, MergeCommitReceiptStore, ReceiptSigningAuthority, append_signed_receipt, build_signed_merge_commit_receipt, canonical_baseline_digest
from .repository import MergeReceiptRepository

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
    "_master_revision",
]
