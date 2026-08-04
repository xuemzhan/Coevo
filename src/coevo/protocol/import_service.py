"""US-5 package-import service facade (US-5-AC-3 / 协议 § 15 + § 17).

Scope
-----
This module ties the atomic-import transaction state machine
(:mod:`.import_transaction`) and the processed-package store
(:mod:`.processed_package_store`) together. The service is the
*external* face that other slices (the workspace module, the UI
layer, the audit emitter) call; the two underlying modules stay
in-memory and pure.

The service exposes one public method, :meth:`import_package`,
which takes a :class:`BuiltPackage` plus a pre-computed replay
decision and orchestrates the 7-step import transaction:

    1. DECRYPT_AND_INSPECT (validation of fixed header / envelope)
    2. PREPARE_WORKSPACE (caller-handled, tracked by tx)
    3. WRITE_FILES (caller-handled, tracked by tx)
    4. PREPARE_DATABASE (caller-handled, tracked by tx)
    5. COMMIT — atomic register into the store
    6. PROMOTE — record outcome as "committed"
    7. CLEANUP — terminal

The service never touches the filesystem or a real DB; it just
maintains the transaction + store invariant. Callers are
expected to perform the actual side effects for steps 2-4 in
their own layer (workspace / DB) and report success / failure
back to the service.

Non-goals
---------
* No IO. The service is in-memory + transactional.
* No LLM, no model, no network.
* No mutation of US-5-AC-1 / US-5-AC-2 wire layout.
"""
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 任务包原子导入门面（US-5 AC-3 / 协议 §15+§17）：import_package 以
# 重放决策 + 7 步事务状态机完成导入，失败回滚不留半态；成功返回
# ImportOutcome（COMMITTED + 已处理包登记）。

from __future__ import annotations

import dataclasses

from .agent_package import (
    AgentPackageError,
    AgentPackageFlags,
    EnvelopeHeader,
    encode_envelope,
)
from .import_transaction import (
    AgentPackageImportError,
    AtomicImporter,
    ImportStep,
    ImportTransaction,
)
from .package_builder import BuiltPackage
from .processed_package_store import (
    AgentPackageStoreDuplicateError,
    ProcessedPackageRecord,
    ProcessedPackageStore,
)
from .replay_detector import (
    ProcessedPackage,
    ReplayDecision,
)
from .sm2_sign import compute_sm3_digest
from .sm2_keywrap import encode_key_transport_bytes


@dataclasses.dataclass(frozen=True)
class ImportOutcome:
    """The result of an :meth:`PackageImportService.import_package` call.

    Carries the final :class:`ImportTransaction` plus the
    post-import :class:`ProcessedPackageStore` so callers can
    persist the new store state atomically alongside the audit
    log.
    """

    transaction: ImportTransaction
    store: ProcessedPackageStore
    record: ProcessedPackageRecord | None  # None when the import failed before COMMIT


@dataclasses.dataclass(frozen=True)
class PackageImportService:
    """Deterministic facade for the US-5-AC-3 atomic-import slice.

    No internal state — every method is a pure function of its
    arguments. The store is supplied by the caller (or starts
    empty via :attr:`DEFAULT_EMPTY_STORE`).
    """

    importer: AtomicImporter = dataclasses.field(default_factory=AtomicImporter)

    def import_package(
        self,
        *,
        package: BuiltPackage,
        replay_decision: ReplayDecision,
        store: ProcessedPackageStore,
        base_revision: str | None = None,
        current_revision: str | None = None,
        processed_at: str | None = None,
    ) -> ImportOutcome:
        """Run the 7-step import transaction.

        ``replay_decision`` is supplied by the caller (typically
        via :func:`replay_detector.check_replay`). ``store`` is the
        caller's current 协议 § 17 registry. ``base_revision``
        and ``current_revision`` are 协议 § 16.2 / § 16.3 fields;
        pass ``current_revision=None`` for a brand-new project.

        On success returns ``ImportOutcome`` with
        ``transaction.step == ImportStep.COMMITTED`` and
        ``store`` updated with the new record. On failure returns
        ``ImportOutcome`` with
        ``transaction.step == ImportStep.ROLLED_BACK`` and
        ``store`` unchanged (atomic rollback at the store level).
        """
        if not isinstance(package, BuiltPackage):
            raise AgentPackageImportError("package must be BuiltPackage")
        if not isinstance(replay_decision, ReplayDecision):
            raise AgentPackageImportError("replay_decision must be ReplayDecision")
        if not isinstance(store, ProcessedPackageStore):
            raise AgentPackageImportError("store must be ProcessedPackageStore")

        env = package.envelope
        tx = self.importer.begin(
            package_id=env.package_id,
            project_id=env.project_id,
            base_revision=base_revision,
            current_revision=current_revision,
        )

        def _record(
            processed_at_str: str,
            result: str,
            revision: str,
        ) -> ProcessedPackageRecord:
            return ProcessedPackageRecord(
                package=ProcessedPackage(
                    package_id=env.package_id,
                    package_digest=compute_sm3_digest(package.to_bytes()),
                    sender_cert_id=env.sender_cert_id,
                    recipient_cert_id=env.recipient_cert_id,
                    project_id=env.project_id,
                    sequence_no=env.sequence_no,
                ),
                package_type=env.package_type,
                processed_at=processed_at_str,
                result=result,
                revision=revision,
            )

        try:
            tx = self.importer.advance(tx, to_step=ImportStep.DECRYPT_AND_INSPECT)
            # Caller-side validation: fixed-header consistency (fail-closed).
            _check_fixed_header_consistency(package)
            tx = self.importer.advance(tx, to_step=ImportStep.PREPARE_WORKSPACE)
            tx = self.importer.advance(tx, to_step=ImportStep.WRITE_FILES)
            tx = self.importer.advance(tx, to_step=ImportStep.PREPARE_DATABASE)
            self.importer.check_replay(tx, replay_decision=replay_decision)
            self.importer.check_base_revision(tx)
            if base_revision is None and current_revision is None:
                raise AgentPackageImportError(
                    "refusing to import without an explicit revision: neither "
                    "base_revision nor current_revision was supplied (protocol "
                    "16.2/16.3); the receiver must not fabricate a project "
                    "master revision"
                )
            tx = self.importer.advance(tx, to_step=ImportStep.COMMIT)
            timestamp = processed_at or _now_utc_iso_z()
            revision = current_revision or base_revision
            record = _record(timestamp, "committed", revision)
            new_store = store.register(record)
            tx = self.importer.advance(tx, to_step=ImportStep.PROMOTE)
            tx = self.importer.advance(tx, to_step=ImportStep.CLEANUP)
            tx = self.importer.advance(tx, to_step=ImportStep.COMMITTED)
            return ImportOutcome(transaction=tx, store=new_store, record=record)
        except AgentPackageError as exc:
            tx = self.importer.fail(tx, reason=str(exc))
            return ImportOutcome(transaction=tx, store=store, record=None)


DEFAULT_EMPTY_STORE: ProcessedPackageStore = ProcessedPackageStore.empty()


def _now_utc_iso_z() -> str:
    import datetime as dt
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def _check_fixed_header_consistency(package: BuiltPackage) -> None:
    """Fail-closed caller-side fixed-header length validation.

    The fixed header (protocol § 7.1) declares three lengths; each
    must match the actual encoded block it describes. A mismatch
    means the object was assembled inconsistently or tampered
    with, so the import is rejected instead of silently
    continuing (the previous placeholder silently accepted any
    mismatch).
    """
    env_bytes = encode_envelope(package.envelope)
    key_bytes = encode_key_transport_bytes(package.key_block)
    payload_bytes = (
        package.payload_block.header
        + package.payload_block.nonce
        + package.payload_block.ciphertext
        + package.payload_block.tag
    )
    fixed = package.fixed_header
    if (
        fixed.header_length != len(env_bytes)
        or fixed.key_block_length != len(key_bytes)
        or fixed.payload_length != len(payload_bytes)
    ):
        raise AgentPackageError(
            "fixed header length fields do not match package blocks: "
            f"header_length={fixed.header_length} vs {len(env_bytes)}, "
            f"key_block_length={fixed.key_block_length} vs {len(key_bytes)}, "
            f"payload_length={fixed.payload_length} vs {len(payload_bytes)}"
        )
