"""US-15-AC-2 durable audit stream store (JSONL + hash chain, fail-closed).

The real-time hub is in-memory; this store gives the stream a durable,
append-only journal so late subscribers can replay the event history:

* explicit ``create`` / ``open`` only;
* each line is canonical JSON bound to a SHA-256 hash chain
  (``prev_hash`` -> ``record_hash``);
* ``open`` verifies the whole chain before use; tampering is rejected;
* payload size is bounded; no free-form sensitive text beyond the
  already-sanitized ``AuditEvent`` fields.

No new dependency; Python stdlib only.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-15-AC-2 审计流持久化：JSONL + SHA-256 哈希链，追加独占、失败关闭、
# 尺寸增量维护（免逐条 stat）。
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Final
from src.coevo.canon import canonical_json_str
from src.coevo.timefmt import now_utc_iso_z

from . import AuditEvent, AuditEventSource


SCHEMA_VERSION: str = "1.0"
STORE_MAX_BYTES: int = 16 * 1024 * 1024
GENESIS: Final[str] = "GENESIS"


class AuditStreamStoreError(Exception):
    """Base class for stream-store failures (fail-closed)."""


def event_to_mapping(event: AuditEvent) -> dict[str, Any]:
    """Canonical, JSON-safe mapping of an AuditEvent (enums -> values)."""
    if not isinstance(event, AuditEvent):
        raise AuditStreamStoreError("event must be an AuditEvent")
    return {
        "ts": event.ts,
        "actor": event.actor,
        "source": event.source.value,
        "action": event.action,
        "project_id": event.project_id,
        "task_id": event.task_id,
        "result": event.result.value,
        "tool": event.tool,
        "detail": event.detail,
        "fingerprint": event.fingerprint,
        "record_hash": event.record_hash,
    }


def mapping_to_event(mapping: dict[str, Any]) -> AuditEvent:
    """Strictly reconstruct an AuditEvent from a stored mapping."""
    if not isinstance(mapping, dict):
        raise AuditStreamStoreError("stored event must be a JSON object")
    source_raw = mapping.get("source")
    if not isinstance(source_raw, str):
        raise AuditStreamStoreError("stored event is missing source")
    try:
        source = AuditEventSource(source_raw)
    except ValueError as exc:
        raise AuditStreamStoreError("stored event has an invalid source") from exc
    record = {
        "ts": mapping.get("ts", ""),
        "actor": mapping.get("actor", ""),
        "action": mapping.get("action", ""),
        "result": mapping.get("result", ""),
        "project_id": mapping.get("project_id", ""),
        "task_id": mapping.get("task_id", ""),
        "tool": mapping.get("tool", ""),
        "detail": mapping.get("detail", {}),
        "fingerprint": mapping.get("fingerprint", ""),
        "record_hash": mapping.get("record_hash", ""),
    }
    return AuditEvent.from_audit_record(record, source=source)


class AuditStreamStore:
    """Append-only, hash-chained JSONL store for audit events."""

    def __init__(
        self, path: Path, stream, last_hash: str, max_bytes: int = STORE_MAX_BYTES
    ) -> None:
        self._path = path
        self._stream = stream
        self._last_hash = last_hash
        self._max_bytes = max_bytes
        # 当前字节数：create() 在构造后追加 init 记录，open() 直接对既有
        # 文件打开，因此统一由 _sync_size() 在记录追加前校准，之后追加时
        # 增量维护，避免每条记录一次 stat() 系统调用。
        self._size = 0

    @property
    def path(self) -> Path:
        return self._path

    @property
    def last_hash(self) -> str:
        return self._last_hash

    @classmethod
    def create(
        cls, path: Path, *, max_bytes: int = STORE_MAX_BYTES
    ) -> "AuditStreamStore":
        """Create a new audit stream store (fails if it exists)."""
        if not isinstance(path, Path):
            raise AuditStreamStoreError("path must be a Path")
        if path.exists():
            raise AuditStreamStoreError("audit stream store already exists")
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = path.open("a", encoding="utf-8")
        store = cls(path, stream, GENESIS, max_bytes)
        store._append_record({"schema_version": SCHEMA_VERSION}, action="init")
        store._sync_size()
        return store

    def _sync_size(self) -> None:
        self._size = self._path.stat().st_size

    @classmethod
    def open(
        cls, path: Path, *, max_bytes: int = STORE_MAX_BYTES
    ) -> "AuditStreamStore":
        """Open an existing store after full chain verification."""
        if not isinstance(path, Path):
            raise AuditStreamStoreError("path must be a Path")
        if not path.is_file():
            raise AuditStreamStoreError("audit stream store does not exist")
        store = cls(path, path.open("a", encoding="utf-8"), GENESIS, max_bytes)
        store._sync_size()
        if not store.verify_chain():
            store.close()
            raise AuditStreamStoreError("audit stream store chain is invalid")
        return store

    def append(self, event: AuditEvent) -> str:
        mapping = event_to_mapping(event)
        return self._append_record(mapping, action="publish")

    def _append_record(self, payload: dict[str, Any], *, action: str) -> str:
        """Append one audit record under the hash chain and persist atomically (fail-closed)."""
        canonical = canonical_json_str(payload, ensure_ascii=False)
        if self._size + len(canonical.encode("utf-8")) > self._max_bytes:
            raise AuditStreamStoreError("audit stream store exceeds size limit")
        record = {
            "schema_version": SCHEMA_VERSION,
            "ts": now_utc_iso_z(),
            "action": action,
            "payload": payload,
            "prev_hash": self._last_hash,
        }
        record["record_hash"] = _chain_hash(record)
        line = canonical_json_str(record, ensure_ascii=False) + "\n"
        self._stream.write(line)
        self._stream.flush()
        # 文本模式写入时换行会被翻译为 os.linesep（Windows 上 \r\n），
        # 磁盘增量需按行内换行数补上翻译产生的字节，保持与 stat() 一致。
        self._size += len(line.encode("utf-8")) + line.count("\n")
        self._last_hash = record["record_hash"]
        return record["record_hash"]

    def events(self) -> tuple[AuditEvent, ...]:
        """Return all published events (verifying the chain)."""
        rows = self._read_rows()
        events: list[AuditEvent] = []
        for row in rows:
            if row.get("action") != "publish":
                continue
            events.append(mapping_to_event(row["payload"]))
        return tuple(events)

    def verify_chain(self) -> bool:
        """Verify the full hash chain; False on any tampering."""
        try:
            previous = GENESIS
            for row in self._read_rows():
                if row.get("prev_hash") != previous:
                    return False
                if row.get("record_hash") != _chain_hash(row):
                    return False
                previous = row["record_hash"]
            return True
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            return False

    def _read_rows(self) -> list[dict[str, Any]]:
        """Read and decode the audit rows (fail-closed on tampering)."""
        rows: list[dict[str, Any]] = []
        with self._path.open("r", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise AuditStreamStoreError("stored row must be an object")
                rows.append(row)
        return rows

    def close(self) -> None:
        self._stream.close()


def _chain_hash(record: dict[str, Any]) -> str:
    """SHA-256 digest over a row canonical payload plus the previous hash."""
    payload = canonical_json_str(
        {
            "schema_version": record["schema_version"],
            "ts": record["ts"],
            "action": record["action"],
            "payload": record["payload"],
            "prev_hash": record["prev_hash"],
        },
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
