"""US-5 processed-package persistence store (US-5-AC-3 / 协议 § 17).

Scope
-----
协议 § 17 requires: "系统必须维护已处理包登记表,至少记录:
package_id / 包类型 / 发送方 / 接收方 / 项目编号 / 包序号 /
处理时间 / 处理结果 / 对应项目版本 / 原始文件摘要."

This module implements that registry as an in-memory store with
atomic commit semantics. The store is **pure** (no IO) and is
designed to be wrapped by an actual DB layer in a future slice
— the on-disk persistence shape is out of scope for AC-3 (the
wire-format / replay-detection logic is AC-2's scope).

The store exposes:
  * ``register(...)`` — atomically insert a :class:`ProcessedPackage`
    record; refuses duplicates by ``package_id`` (raises
    :class:`AgentPackageImportReplayError`) or ``package_digest``
    (raises :class:`AgentPackageImportReplayError`).
  * ``get(...)`` — read by ``package_id``.
  * ``by_digest(...)`` — read by ``package_digest``.
  * ``by_scope(...)`` — list records scoped to a (sender, recipient,
    project) tuple, ordered by ``sequence_no`` ascending.
  * ``revision_for(project_id)`` — return the highest known revision
    for a project (or None).

Non-goals
---------
* No IO, no DB. The store is in-memory.
* No LLM, no model, no network.
* No mutation of US-5-AC-1 / US-5-AC-2 wire layout.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .agent_package import AgentPackageError
from .replay_detector import ProcessedPackage


class AgentPackageStoreError(AgentPackageError):
    """Base class for processed-package store errors."""


class AgentPackageStoreDuplicateError(AgentPackageStoreError):
    """Raised when registering a duplicate package_id or package_digest."""


@dataclass(frozen=True)
class ProcessedPackageRecord:
    """协议 § 17 processed-package registry record.

    Carries the minimum data the protocol requires plus the
    processing outcome (the ``result`` field is recorded by the
    importer at COMMIT/PROMOTE time).
    """

    package: ProcessedPackage
    package_type: str  # 协议 § 5 enum
    processed_at: str  # ISO-8601 UTC 'Z'
    result: str        # "committed" / "rolled_back"
    revision: str      # 协议 § 16.1 project master revision at processing time


@dataclass(frozen=True)
class ProcessedPackageStore:
    """In-memory 协议 § 17 registry.

    All mutating operations are pure: ``register`` returns a new
    store instance rather than mutating in place. Callers can
    persist the new instance atomically (json.dumps + write to
    a DB in a future slice).
    """

    _records: tuple[ProcessedPackageRecord, ...] = field(default_factory=tuple)
    _by_id: tuple[tuple[str, int], ...] = field(default_factory=tuple)        # (id, idx)
    _by_digest: tuple[tuple[str, int], ...] = field(default_factory=tuple)     # (digest, idx)

    @classmethod
    def empty(cls) -> "ProcessedPackageStore":
        return cls(_records=tuple(), _by_id=tuple(), _by_digest=tuple())

    def get(self, package_id: str) -> ProcessedPackageRecord | None:
        for key, idx in self._by_id:
            if key == package_id:
                return self._records[idx]
        return None

    def by_digest(self, package_digest: str) -> ProcessedPackageRecord | None:
        for key, idx in self._by_digest:
            if key == package_digest:
                return self._records[idx]
        return None

    def by_scope(
        self,
        *,
        sender_cert_id: str,
        recipient_cert_id: str,
        project_id: str,
    ) -> tuple[ProcessedPackageRecord, ...]:
        """Return records for the given scope, sorted by sequence_no ASC."""
        out = [
            r
            for r in self._records
            if r.package.sender_cert_id == sender_cert_id
            and r.package.recipient_cert_id == recipient_cert_id
            and r.package.project_id == project_id
        ]
        out.sort(key=lambda r: r.package.sequence_no)
        return tuple(out)

    def revision_for(self, project_id: str) -> str | None:
        """Return the highest :attr:`ProcessedPackageRecord.revision` for a project.

        Used by :class:`PackageImportService` to check
        ``base_revision`` conflicts (协议 § 16.3). Returns ``None``
        when no record exists for the project.
        """
        out = [r for r in self._records if r.package.project_id == project_id]
        if not out:
            return None
        return max(r.revision for r in out)

    def register(
        self,
        record: ProcessedPackageRecord,
    ) -> "ProcessedPackageStore":
        """Atomically insert ``record``.

        Refuses duplicates by ``package_id`` (raises
        :class:`AgentPackageStoreDuplicateError`) and by
        ``package_digest`` (raises the same). The check + insert
        is a single atomic step from the caller's perspective.
        """
        if not isinstance(record, ProcessedPackageRecord):
            raise AgentPackageStoreError("record must be ProcessedPackageRecord")
        if self.get(record.package.package_id) is not None:
            raise AgentPackageStoreDuplicateError(
                f"package_id {record.package.package_id!r} already registered"
            )
        if self.by_digest(record.package.package_digest) is not None:
            raise AgentPackageStoreDuplicateError(
                f"package_digest {record.package.package_digest!r} already registered"
            )
        new_idx = len(self._records)
        return ProcessedPackageStore(
            _records=self._records + (record,),
            _by_id=self._by_id + ((record.package.package_id, new_idx),),
            _by_digest=self._by_digest + ((record.package.package_digest, new_idx),),
        )

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self):
        return iter(self._records)