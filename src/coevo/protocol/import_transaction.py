"""US-5 atomic-import transaction state machine (US-5-AC-3 / 协议 § 15).

Scope
-----
This module implements the 7-step transaction state machine from
协议 § 15 "原子导入":

    1. 在临时目录解密和检查；
    2. 建立待提交工作区；
    3. 完成全部文件写入；
    4. 完成数据库状态准备；
    5. 执行最终提交；
    6. 提交成功后切换为正式状态；
    7. 删除临时数据。

The state machine is **pure**: it tracks the seven steps in a
frozen :class:`ImportTransaction` record and emits the next step
deterministically. Side effects (filesystem writes, DB inserts)
are the caller's responsibility; the importer only enforces the
order and the rollback rule (协议 § 15 第二段).

Non-goals
---------
* No IO. The importer never touches the filesystem or any
  database — those are the persistence layer's job (see
  :mod:`.processed_package_store`).
* No model / LLM / network.
* No mutation of US-5-AC-1 / US-5-AC-2 wire layout.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Mapping

from .agent_package import AgentPackageError
from .package_builder import BuiltPackage
from .replay_detector import ProcessedPackage, ReplayDecision, ReplayOutcome


class AgentPackageImportError(AgentPackageError):
    """Base class for all US-5-AC-3 import errors."""


class AgentPackageImportValidationError(AgentPackageImportError):
    """Raised when validation fails (file size / forbidden type / etc.)."""


class AgentPackageImportConflictError(AgentPackageImportError):
    """Raised when the package's base_revision conflicts with current project master."""


class AgentPackageImportReplayError(AgentPackageImportError):
    """Raised when the replay detector refuses the package (non-ACCEPT outcome)."""


class ImportStep(enum.Enum):
    """The seven transaction steps from 协议 § 15."""

    QUARANTINE_RECEIVED = "quarantine_received"           # step 0: caller hands us bytes
    DECRYPT_AND_INSPECT = "decrypt_and_inspect"           # step 1
    PREPARE_WORKSPACE = "prepare_workspace"               # step 2
    WRITE_FILES = "write_files"                           # step 3
    PREPARE_DATABASE = "prepare_database"                 # step 4
    COMMIT = "commit"                                     # step 5
    PROMOTE = "promote"                                   # step 6
    CLEANUP = "cleanup"                                   # step 7
    COMMITTED = "committed"                               # terminal success
    ROLLED_BACK = "rolled_back"                           # terminal failure


_STEP_ORDER: tuple[ImportStep, ...] = (
    ImportStep.QUARANTINE_RECEIVED,
    ImportStep.DECRYPT_AND_INSPECT,
    ImportStep.PREPARE_WORKSPACE,
    ImportStep.WRITE_FILES,
    ImportStep.PREPARE_DATABASE,
    ImportStep.COMMIT,
    ImportStep.PROMOTE,
    ImportStep.CLEANUP,
    ImportStep.COMMITTED,
)


@dataclass(frozen=True)
class ImportTransaction:
    """A single package import transaction.

    The record is frozen; transitions produce new instances via
    :meth:`advance` (and :meth:`fail`). Callers persist these
    records alongside the audit log so the import is auditable.
    """

    package_id: str
    project_id: str
    base_revision: str | None  # 协议 § 16.2: manifest's base_revision
    current_revision: str | None  # 协议 § 16.3: receiver's current master
    step: ImportStep
    failure_reason: str = ""
    completed_steps: tuple[ImportStep, ...] = field(default_factory=tuple)

    def advance(self, to_step: ImportStep) -> "ImportTransaction":
        """Return a new transaction with the next step marked completed.

        Strictly monotonic: callers must pass a step that is *later*
        in :data:`_STEP_ORDER` than the current one. Skipping
        forward is allowed (e.g. DECRYPT_AND_INSPECT → COMMIT after
        the caller bundles steps); going backward raises.
        """
        current_idx = _STEP_ORDER.index(self.step)
        target_idx = _STEP_ORDER.index(to_step)
        if target_idx <= current_idx:
            raise AgentPackageImportError(
                f"cannot advance from {self.step.value} to {to_step.value}: "
                f"target is not strictly later than current"
            )
        if to_step == ImportStep.ROLLED_BACK:
            raise AgentPackageImportError(
                "use fail() to mark a transaction as rolled back"
            )
        # Push every intermediate step the caller skipped, so the
        # recorded ``completed_steps`` truly reflects the canonical
        # 7-step path (协议 § 15). Skipping forward is still allowed;
        # callers may bypass PREPARE_WORKSPACE / WRITE_FILES / etc.,
        # but the resulting history shows every step that was crossed.
        intermediate = _STEP_ORDER[current_idx:target_idx]
        return ImportTransaction(
            package_id=self.package_id,
            project_id=self.project_id,
            base_revision=self.base_revision,
            current_revision=self.current_revision,
            step=to_step,
            failure_reason=self.failure_reason,
            completed_steps=self.completed_steps + intermediate,
        )

    def fail(self, reason: str) -> "ImportTransaction":
        """Mark the transaction as failed and rolled back.

        The failure_reason is recorded verbatim in the audit log so
        receivers can correlate the rollback with a precise cause.
        """
        if not isinstance(reason, str) or not reason:
            raise AgentPackageImportError("failure reason must be a non-empty string")
        return ImportTransaction(
            package_id=self.package_id,
            project_id=self.project_id,
            base_revision=self.base_revision,
            current_revision=self.current_revision,
            step=ImportStep.ROLLED_BACK,
            failure_reason=reason,
            completed_steps=self.completed_steps,
        )


class AtomicImporter:
    """Pure-function atomic-importer state machine.

    No IO. Callers drive the 7-step transaction by calling
    :meth:`begin` and :meth:`advance`; persistence-side effects
    are the persistence layer's job. The importer's job is to
    enforce monotonicity, validate inputs, and emit audit-record
    projections.
    """

    def begin(
        self,
        *,
        package_id: str,
        project_id: str,
        base_revision: str | None = None,
        current_revision: str | None = None,
    ) -> ImportTransaction:
        """Begin a new transaction at step 0 (QUARANTINE_RECEIVED)."""
        if not isinstance(package_id, str) or not package_id:
            raise AgentPackageImportError("package_id must be a non-empty string")
        if not isinstance(project_id, str) or not project_id:
            raise AgentPackageImportError("project_id must be a non-empty string")
        for name, value in (("base_revision", base_revision), ("current_revision", current_revision)):
            if value is not None and (not isinstance(value, str) or not value):
                raise AgentPackageImportError(f"{name} must be a non-empty string or None")
        return ImportTransaction(
            package_id=package_id,
            project_id=project_id,
            base_revision=base_revision,
            current_revision=current_revision,
            step=ImportStep.QUARANTINE_RECEIVED,
        )

    def advance(
        self,
        transaction: ImportTransaction,
        *,
        to_step: ImportStep,
    ) -> ImportTransaction:
        """Advance the transaction to ``to_step``.

        Validates monotonicity. The persistence layer is expected
        to perform the side effects associated with each step
        (协议 § 15 第 1-7 步). The importer never touches the
        filesystem or DB; it only emits the next transaction
        state.
        """
        if not isinstance(transaction, ImportTransaction):
            raise AgentPackageImportError("transaction must be ImportTransaction")
        if not isinstance(to_step, ImportStep):
            raise AgentPackageImportError("to_step must be ImportStep")
        return transaction.advance(to_step)

    def fail(
        self,
        transaction: ImportTransaction,
        *,
        reason: str,
    ) -> ImportTransaction:
        """Mark the transaction as failed. The caller must perform
        the rollback steps from 协议 § 15 第二段: revert DB state,
        delete incomplete workspace, retain the raw .agent file,
        log the error, leave the package in quarantine.
        """
        if not isinstance(transaction, ImportTransaction):
            raise AgentPackageImportError("transaction must be ImportTransaction")
        return transaction.fail(reason)

    def check_replay(
        self,
        transaction: ImportTransaction,
        *,
        replay_decision: ReplayDecision,
    ) -> None:
        """Enforce 协议 § 17: the replay decision must be ACCEPT.

        Other outcomes (DUPLICATE_PACKAGE_ID, DUPLICATE_DIGEST,
        REPLAY_SEQUENCE, REVOKED_PACKAGE, INVALID_REFERENCE) are
        raised as :class:`AgentPackageImportReplayError`.
        """
        if not isinstance(transaction, ImportTransaction):
            raise AgentPackageImportError("transaction must be ImportTransaction")
        if not isinstance(replay_decision, ReplayDecision):
            raise AgentPackageImportError("replay_decision must be ReplayDecision")
        if replay_decision.outcome is not ReplayOutcome.ACCEPT:
            raise AgentPackageImportReplayError(
                f"replay detector refused import: {replay_decision.outcome.value} "
                f"({replay_decision.detail})"
            )

    def check_base_revision(
        self,
        transaction: ImportTransaction,
    ) -> None:
        """Enforce 协议 § 16.2 / § 16.3: base_revision must match
        current_revision (or current must be None for first import).

        If they differ the caller is in conflict-resolution mode
        (协议 § 16.4); a bare import without explicit acceptance
        is rejected with :class:`AgentPackageImportConflictError`.
        """
        if not isinstance(transaction, ImportTransaction):
            raise AgentPackageImportError("transaction must be ImportTransaction")
        if transaction.base_revision is None:
            # First import into an empty project: acceptable.
            return
        if transaction.current_revision is None:
            raise AgentPackageImportConflictError(
                f"package claims base_revision {transaction.base_revision!r} "
                "but receiver has no current project revision"
            )
        if transaction.base_revision != transaction.current_revision:
            raise AgentPackageImportConflictError(
                f"base_revision {transaction.base_revision!r} does not match "
                f"current project revision {transaction.current_revision!r}; "
                "caller must enter conflict-resolution flow (协议 § 16.4)"
            )

    def to_audit_record(
        self,
        transaction: ImportTransaction,
    ) -> dict[str, object]:
        """Emit a deterministic, JSON-safe audit-record projection.

        Same shape convention as US-1/2/3/5 audit helpers: no
        raw payload, only structural facts.
        """
        return {
            "kind": "agent_package.import",
            "schema_version": "1.0",
            "package_id": transaction.package_id,
            "project_id": transaction.project_id,
            "step": transaction.step.value,
            "completed_steps": [s.value for s in transaction.completed_steps],
            "base_revision": transaction.base_revision,
            "current_revision": transaction.current_revision,
            "failure_reason": transaction.failure_reason,
            "terminal": transaction.step in (ImportStep.COMMITTED, ImportStep.ROLLED_BACK),
        }