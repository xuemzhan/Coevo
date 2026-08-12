"""sync.store - node sync outbox and reconciliation (PRODUCT-REVIEW T-12).

Offline-first implementation of the sync-protocol contract
(``docs/architecture/sync-protocol.md`` / ``src/coevo/sync/contract.py``):

* ``SyncOutbox``: append-only per-node chain with hash linkage, monotonic
  sequence and replay protection; persisted as canonical JSON lines.
* ``SyncReconciler``: read-only reconciliation between the local chain and
  an incoming chain (validates order/linkage, detects new/replay/gap events).
* ``export_bundle`` / ``load_bundle``: file-based transport (like ``.agent``
  packages) so the same envelope format can later ride a controlled-network
  transport without changing the wire contract.

No network calls; the online-mode transport remains DESIGNED
(``online-mode-scope.md``).
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 同步出站队列 + 对账：离线优先（文件包），不违反全程离线约束。
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contract import (
    SyncContractError,
    SyncEnvelope,
    envelope_digest,
    validate_chain,
    validate_envelope,
)


_GENESIS: str = "0" * 64


@dataclass(frozen=True)
class SyncRecord:
    """One persisted envelope plus its canonical digest."""

    envelope: SyncEnvelope
    digest: str


class SyncOutbox:
    """Append-only per-node outgoing chain with linkage and replay checks."""

    def __init__(self, path: Path) -> None:
        if not isinstance(path, Path):
            raise SyncContractError("outbox path must be a Path")
        self._path = path
        self._records: list[SyncRecord] = []
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        raw = self._path.read_bytes()
        if not raw:
            return
        envelopes: list[SyncEnvelope] = []
        for line in raw.decode("utf-8").splitlines():
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SyncContractError("outbox contains invalid JSON") from exc
            envelopes.append(validate_envelope(data))
        digests = validate_chain(envelopes)
        self._records = [
            SyncRecord(envelope=env, digest=digest)
            for env, digest in zip(envelopes, digests)
        ]

    @property
    def records(self) -> tuple[SyncRecord, ...]:
        return tuple(self._records)

    @property
    def head_digest(self) -> str:
        return self._records[-1].digest if self._records else _GENESIS

    def append(self, data: Mapping[str, Any]) -> SyncRecord:
        """Append one envelope, enforcing linkage/order/replay."""
        envelope = validate_envelope(data)
        if self._records and self._records[0].envelope.source_node != envelope.source_node:
            raise SyncContractError("outbox is bound to a single source_node")
        expected_sequence = len(self._records) + 1
        if envelope.sequence != expected_sequence:
            raise SyncContractError(
                f"sequence {envelope.sequence} != expected {expected_sequence}"
            )
        previous = self.head_digest
        if envelope.previous_hash != previous:
            raise SyncContractError("envelope breaks outbox hash linkage")
        if any(record.envelope.event_id == envelope.event_id for record in self._records):
            raise SyncContractError(
                f"replay detected for event {envelope.event_id!r}"
            )
        digest = envelope_digest(envelope)
        record = SyncRecord(envelope=envelope, digest=digest)
        self._records.append(record)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as stream:
            stream.write(
                json.dumps(
                    {
                        "schema_version": envelope.schema_version,
                        "source_node": envelope.source_node,
                        "event_id": envelope.event_id,
                        "sequence": envelope.sequence,
                        "created_at": envelope.created_at,
                        "payload_digest": envelope.payload_digest,
                        "previous_hash": envelope.previous_hash,
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )
        return record


@dataclass(frozen=True)
class ReconcileResult:
    """Read-only reconciliation summary for an incoming chain."""

    ok: bool
    incoming_count: int
    new_events: tuple[str, ...]
    replay_events: tuple[str, ...]
    gaps: tuple[int, ...]
    detail: str = ""


class SyncReconciler:
    """Reconcile an incoming chain against the local outbox (no mutation)."""

    @staticmethod
    def reconcile(outbox: SyncOutbox, incoming: Sequence[Mapping[str, Any]]) -> ReconcileResult:
        envelopes = [validate_envelope(item) for item in incoming]
        try:
            validate_chain(envelopes)
        except SyncContractError as exc:
            return ReconcileResult(
                ok=False,
                incoming_count=len(envelopes),
                new_events=(),
                replay_events=(),
                gaps=(),
                detail=str(exc),
            )
        local_events = {
            record.envelope.event_id for record in outbox.records
        }
        local_sequences = {
            record.envelope.sequence for record in outbox.records
        }
        new_events = [
            env.event_id for env in envelopes if env.event_id not in local_events
        ]
        replay_events = [
            env.event_id for env in envelopes if env.event_id in local_events
        ]
        gaps = [
            index
            for index in range(1, len(envelopes) + 1)
            if index not in local_sequences
        ]
        return ReconcileResult(
            ok=True,
            incoming_count=len(envelopes),
            new_events=tuple(new_events),
            replay_events=tuple(replay_events),
            gaps=tuple(gaps),
        )


def export_bundle(path: Path, outbox: SyncOutbox) -> None:
    """Write the outbox chain as a canonical JSON bundle."""
    payload = [
        {
            "schema_version": record.envelope.schema_version,
            "source_node": record.envelope.source_node,
            "event_id": record.envelope.event_id,
            "sequence": record.envelope.sequence,
            "created_at": record.envelope.created_at,
            "payload_digest": record.envelope.payload_digest,
            "previous_hash": record.envelope.previous_hash,
        }
        for record in outbox.records
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def load_bundle(path: Path) -> tuple[SyncEnvelope, ...]:
    """Load and validate a bundle; any tamper fails closed."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncContractError(f"bundle is unreadable: {exc}") from exc
    if not isinstance(data, list):
        raise SyncContractError("bundle must be a JSON array of envelopes")
    envelopes = tuple(validate_envelope(item) for item in data)
    validate_chain(list(envelopes))
    return envelopes
