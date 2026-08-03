"""PACKAGE-DB-1 persistent processed-package registry (协议 § 17).

SQLite-backed, fail-closed persistence for the processed-package
registry previously implemented purely in-memory in
:mod:`.processed_package_store`. The in-memory store is unchanged
and remains the shared read model for the pure facades; this module
adds the on-disk persistence layer with the same record shape.

Guarantees
----------
* Explicit :meth:`PackageStoreDb.create` / :meth:`PackageStoreDb.open`
  only — no implicit database creation from request data, and
  ``create`` refuses to overwrite an existing file.
* Schema locked: ``meta.schema_version`` + ``meta.schema_sha256`` and
  exact DDL comparison on every open; extra tables / views /
  triggers / indexes and column drift are rejected (fail-closed).
* Tamper detection: append-only hash chain over every registry row
  (``prev_hash`` / ``record_hash``), re-verified on every open.
  Any edit, deletion, reordering or hash mismatch refuses to open;
  ``PRAGMA integrity_check`` guards structural corruption.
* Duplicate / replay detection survives restarts: UNIQUE constraints
  on ``package_id`` and ``package_digest``, enforced transactionally
  (协议 § 17 情况 1 / 2); sequence-regression detection remains the
  replay detector's job over the persisted snapshot.
* Strict row validation on register (types, formats, closed result
  set, ISO-8601 UTC timestamps) — malformed input raises instead of
  silently degrading.

Non-goals
---------
* No multi-process / multi-connection concurrency: one connection per
  store instance, guarded by ``BEGIN IMMEDIATE``.
* No change to US-5-AC-1 / US-5-AC-2 wire layout and no change to the
  in-memory :class:`ProcessedPackageStore` API.
* No new dependency — Python stdlib only (``sqlite3`` / ``hashlib`` /
  ``json`` / ``uuid`` / ``pathlib`` / ``datetime``).
* External anchoring (signed checkpoints on a separate audit node) is
  out of scope; the global audit seal already provides that layer.
"""
from __future__ import annotations

import hashlib
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Iterator

from .agent_package import PACKAGE_TYPES
from .processed_package_store import (
    AgentPackageStoreDuplicateError,
    AgentPackageStoreError,
    ProcessedPackageRecord,
    ProcessedPackageStore,
)


SCHEMA_VERSION: str = "1.0"
GENESIS_HASH: str = "0" * 64
RESULT_COMMITTED: str = "committed"
RESULT_ROLLED_BACK: str = "rolled_back"
RESULT_VALUES: frozenset[str] = frozenset((RESULT_COMMITTED, RESULT_ROLLED_BACK))

_DIGEST_HEX_LEN: int = 64
_FIELD_MAX_BYTES: int = 512
_SEQ_MAX: int = 1_000_000_000

_SCHEMA_DDL: Final[tuple[str, ...]] = (
    "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    "CREATE TABLE processed_packages ("
    "seq INTEGER PRIMARY KEY, "
    "package_id TEXT NOT NULL UNIQUE, "
    "package_digest TEXT NOT NULL UNIQUE, "
    "sender_cert_id TEXT NOT NULL, "
    "recipient_cert_id TEXT NOT NULL, "
    "project_id TEXT NOT NULL, "
    "sequence_no INTEGER NOT NULL, "
    "package_type TEXT NOT NULL, "
    "processed_at TEXT NOT NULL, "
    "result TEXT NOT NULL, "
    "revision TEXT NOT NULL, "
    "prev_hash TEXT NOT NULL, "
    "record_hash TEXT NOT NULL)",
)
_SCHEMA_SHA256: Final[str] = hashlib.sha256(
    "\n".join(_SCHEMA_DDL).encode("utf-8")
).hexdigest()

_META_KEYS: Final[tuple[str, ...]] = (
    "schema_version",
    "schema_sha256",
    "store_id",
    "created_at",
    "record_count",
)


class PackageStoreDbError(AgentPackageStoreError):
    """Base class for persistent registry failures (fail-closed)."""


class PackageStoreDbIntegrityError(PackageStoreDbError):
    """The database is corrupt, tampered or schema-drifted; refused to open."""


def _now_utc_iso_z() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _validate_record(record: ProcessedPackageRecord) -> None:
    """Strict fail-closed validation before any row is persisted."""
    if not isinstance(record, ProcessedPackageRecord):
        raise PackageStoreDbError("record must be ProcessedPackageRecord")
    package = record.package
    if not isinstance(package.package_id, str) or not package.package_id:
        raise PackageStoreDbError("package_id must be a non-empty string")
    if len(package.package_id.encode("utf-8")) > _FIELD_MAX_BYTES:
        raise PackageStoreDbError("package_id exceeds size limit")
    if (
        not isinstance(package.package_digest, str)
        or len(package.package_digest) != _DIGEST_HEX_LEN
        or any(ch not in "0123456789abcdef" for ch in package.package_digest)
    ):
        raise PackageStoreDbError(
            "package_digest must be a 64-char lowercase hex digest"
        )
    for name, value in (
        ("sender_cert_id", package.sender_cert_id),
        ("recipient_cert_id", package.recipient_cert_id),
        ("project_id", package.project_id),
    ):
        if not isinstance(value, str) or not value:
            raise PackageStoreDbError(f"{name} must be a non-empty string")
        if len(value.encode("utf-8")) > _FIELD_MAX_BYTES:
            raise PackageStoreDbError(f"{name} exceeds size limit")
    if (
        not isinstance(package.sequence_no, int)
        or isinstance(package.sequence_no, bool)
        or package.sequence_no < 1
        or package.sequence_no > _SEQ_MAX
    ):
        raise PackageStoreDbError("sequence_no must be an integer in [1, 1e9]")
    if record.package_type not in PACKAGE_TYPES:
        raise PackageStoreDbError(
            f"package_type {record.package_type!r} is not in the protocol enum"
        )
    _validate_iso_z(record.processed_at, "processed_at")
    if record.result not in RESULT_VALUES:
        raise PackageStoreDbError(
            f"result {record.result!r} is not in {sorted(RESULT_VALUES)!r}"
        )
    if not isinstance(record.revision, str) or not record.revision:
        raise PackageStoreDbError("revision must be a non-empty string")
    if len(record.revision.encode("utf-8")) > _FIELD_MAX_BYTES:
        raise PackageStoreDbError("revision exceeds size limit")


def _validate_iso_z(value: object, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise PackageStoreDbError(f"{name} must be a non-empty string")
    if len(value.encode("utf-8")) > _FIELD_MAX_BYTES:
        raise PackageStoreDbError(f"{name} exceeds size limit")
    if not value.endswith("Z"):
        raise PackageStoreDbError(f"{name} must be ISO-8601 UTC ending with 'Z'")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PackageStoreDbError(f"{name} is not a valid ISO-8601 timestamp") from exc


def _record_hash(
    *,
    prev_hash: str,
    seq: int,
    record: ProcessedPackageRecord,
) -> str:
    package = record.package
    payload = "|".join(
        (
            prev_hash,
            str(seq),
            package.package_id,
            package.package_digest,
            package.sender_cert_id,
            package.recipient_cert_id,
            package.project_id,
            str(package.sequence_no),
            record.package_type,
            record.processed_at,
            record.result,
            record.revision,
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class PackageStoreDb:
    """SQLite-backed persistent 协议 § 17 processed-package registry."""

    def __init__(self, connection: sqlite3.Connection, path: Path) -> None:
        self._connection = connection
        self._path = path
        self._closed = False

    @property
    def path(self) -> Path:
        return self._path

    # -- lifecycle ----------------------------------------------------------

    @classmethod
    def create(cls, path: Path) -> "PackageStoreDb":
        """Create a new registry at ``path``; fails if it already exists."""
        if not isinstance(path, Path):
            raise PackageStoreDbError("path must be a Path")
        if path.exists():
            raise PackageStoreDbError("package store already exists")
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(path))
        try:
            for statement in _SCHEMA_DDL:
                connection.execute(statement)
            meta = {
                "schema_version": SCHEMA_VERSION,
                "schema_sha256": _SCHEMA_SHA256,
                "store_id": uuid.uuid4().hex,
                "created_at": _now_utc_iso_z(),
                "record_count": "0",
            }
            connection.executemany(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                tuple(meta.items()),
            )
            connection.commit()
        except Exception:
            connection.close()
            try:
                path.unlink()
            except OSError:
                pass
            raise
        return cls(connection, path)

    @classmethod
    def open(cls, path: Path) -> "PackageStoreDb":
        """Open an existing registry after schema + chain verification."""
        if not isinstance(path, Path):
            raise PackageStoreDbError("path must be a Path")
        if not path.is_file():
            raise PackageStoreDbError("package store does not exist")
        connection = sqlite3.connect(str(path))
        try:
            cls._verify_integrity(connection)
            cls._verify_schema(connection)
            cls._verify_chain(connection)
            return cls(connection, path)
        except sqlite3.DatabaseError as exc:
            connection.close()
            raise PackageStoreDbError(
                "package store file is corrupt or not a SQLite database"
            ) from exc
        except Exception:
            connection.close()
            raise

    def close(self) -> None:
        if self._closed:
            return
        self._connection.close()
        self._closed = True

    def __enter__(self) -> "PackageStoreDb":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _ensure_open(self) -> None:
        if self._closed:
            raise PackageStoreDbError("package store is closed")

    # -- queries ------------------------------------------------------------

    def get(self, package_id: str) -> ProcessedPackageRecord | None:
        self._ensure_open()
        if not isinstance(package_id, str):
            raise PackageStoreDbError("package_id must be a string")
        row = self._connection.execute(
            "SELECT package_id, package_digest, sender_cert_id, recipient_cert_id, "
            "project_id, sequence_no, package_type, processed_at, result, revision "
            "FROM processed_packages WHERE package_id = ?",
            (package_id,),
        ).fetchone()
        return _row_to_record(row) if row is not None else None

    def by_digest(self, package_digest: str) -> ProcessedPackageRecord | None:
        self._ensure_open()
        if not isinstance(package_digest, str):
            raise PackageStoreDbError("package_digest must be a string")
        row = self._connection.execute(
            "SELECT package_id, package_digest, sender_cert_id, recipient_cert_id, "
            "project_id, sequence_no, package_type, processed_at, result, revision "
            "FROM processed_packages WHERE package_digest = ?",
            (package_digest,),
        ).fetchone()
        return _row_to_record(row) if row is not None else None

    def by_scope(
        self,
        *,
        sender_cert_id: str,
        recipient_cert_id: str,
        project_id: str,
    ) -> tuple[ProcessedPackageRecord, ...]:
        self._ensure_open()
        rows = self._connection.execute(
            "SELECT package_id, package_digest, sender_cert_id, recipient_cert_id, "
            "project_id, sequence_no, package_type, processed_at, result, revision "
            "FROM processed_packages "
            "WHERE sender_cert_id = ? AND recipient_cert_id = ? AND project_id = ? "
            "ORDER BY sequence_no ASC",
            (sender_cert_id, recipient_cert_id, project_id),
        ).fetchall()
        return tuple(_row_to_record(row) for row in rows)

    def revision_for(self, project_id: str) -> str | None:
        self._ensure_open()
        row = self._connection.execute(
            "SELECT MAX(revision) FROM processed_packages WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        return row[0] if row is not None and row[0] is not None else None

    def iter_records(self) -> Iterator[ProcessedPackageRecord]:
        self._ensure_open()
        cursor = self._connection.execute(
            "SELECT package_id, package_digest, sender_cert_id, recipient_cert_id, "
            "project_id, sequence_no, package_type, processed_at, result, revision "
            "FROM processed_packages ORDER BY seq ASC"
        )
        for row in cursor:
            yield _row_to_record(row)

    def __len__(self) -> int:
        self._ensure_open()
        row = self._connection.execute(
            "SELECT COUNT(*) FROM processed_packages"
        ).fetchone()
        return int(row[0])

    # -- mutation -----------------------------------------------------------

    def register(self, record: ProcessedPackageRecord) -> "PackageStoreDb":
        """Atomically persist ``record``; refuses duplicates by
        ``package_id`` or ``package_digest`` (协议 § 17 情况 1 / 2).

        Raises :class:`AgentPackageStoreDuplicateError` on duplicates
        (same exception as the in-memory store) so existing facades
        keep their catch behaviour. Returns ``self`` for chaining.
        """
        self._ensure_open()
        _validate_record(record)
        connection = self._connection
        connection.execute("BEGIN IMMEDIATE")
        try:
            previous = connection.execute(
                "SELECT seq, record_hash FROM processed_packages "
                "ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            seq = int(previous[0]) + 1 if previous is not None else 1
            prev_hash = previous[1] if previous is not None else GENESIS_HASH
            record_hash = _record_hash(
                prev_hash=prev_hash, seq=seq, record=record
            )
            connection.execute(
                "INSERT INTO processed_packages "
                "(seq, package_id, package_digest, sender_cert_id, recipient_cert_id, "
                "project_id, sequence_no, package_type, processed_at, result, "
                "revision, prev_hash, record_hash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    seq,
                    record.package.package_id,
                    record.package.package_digest,
                    record.package.sender_cert_id,
                    record.package.recipient_cert_id,
                    record.package.project_id,
                    record.package.sequence_no,
                    record.package_type,
                    record.processed_at,
                    record.result,
                    record.revision,
                    prev_hash,
                    record_hash,
                ),
            )
            connection.execute(
                "UPDATE meta SET value = CAST((SELECT COUNT(*) FROM processed_packages) AS TEXT) "
                "WHERE key = 'record_count'"
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise AgentPackageStoreDuplicateError(
                "package_id or package_digest already registered"
            ) from exc
        except Exception:
            connection.rollback()
            raise
        return self

    # -- bridge -------------------------------------------------------------

    def snapshot(self) -> ProcessedPackageStore:
        """Materialize the persisted registry as the pure in-memory
        :class:`ProcessedPackageStore` for the existing facades.
        """
        self._ensure_open()
        store = ProcessedPackageStore.empty()
        for record in self.iter_records():
            store = store.register(record)
        return store

    # -- verification (open-time, fail-closed) ------------------------------

    @staticmethod
    def _verify_integrity(connection: sqlite3.Connection) -> None:
        row = connection.execute("PRAGMA integrity_check").fetchone()
        if row is None or row[0] != "ok":
            raise PackageStoreDbIntegrityError("SQLite integrity_check failed")

    @staticmethod
    def _verify_schema(connection: sqlite3.Connection) -> None:
        rows = connection.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE type IN ('table', 'view', 'trigger', 'index') "
            "ORDER BY type, name"
        ).fetchall()
        objects = [
            row for row in rows if not str(row[1]).startswith("sqlite_autoindex_")
        ]
        if len(objects) != len(_SCHEMA_DDL):
            raise PackageStoreDbIntegrityError(
                "package store schema object count mismatch"
            )
        found: dict[str, str] = {}
        expected: dict[str, str] = {}
        for kind, name, sql in objects:
            if kind != "table":
                raise PackageStoreDbIntegrityError(
                    "package store has a non-table object"
                )
            found[name] = str(sql)
        for statement in _SCHEMA_DDL:
            table_name = statement.split("(", 1)[0].replace(
                "CREATE TABLE ", ""
            ).strip()
            expected[table_name] = statement
        if set(found) != set(expected):
            raise PackageStoreDbIntegrityError("package store table set mismatch")
        for table_name, canonical in expected.items():
            if _normalize_sql(found[table_name]) != _normalize_sql(canonical):
                raise PackageStoreDbIntegrityError(
                    "package store DDL drift detected"
                )
        meta = dict(
            connection.execute("SELECT key, value FROM meta").fetchall()
        )
        if set(meta) != set(_META_KEYS):
            raise PackageStoreDbIntegrityError(
                "package store meta key set mismatch"
            )
        if meta.get("schema_version") != SCHEMA_VERSION:
            raise PackageStoreDbIntegrityError(
                "package store schema_version mismatch"
            )
        if meta.get("schema_sha256") != _SCHEMA_SHA256:
            raise PackageStoreDbIntegrityError(
                "package store schema digest mismatch"
            )
        try:
            record_count = int(meta.get("record_count", ""))
        except ValueError as exc:
            raise PackageStoreDbIntegrityError(
                "package store record_count is corrupt"
            ) from exc
        if record_count < 0:
            raise PackageStoreDbIntegrityError(
                "package store record_count is negative"
            )

    @staticmethod
    def _verify_chain(connection: sqlite3.Connection) -> None:
        rows = connection.execute(
            "SELECT seq, package_id, package_digest, sender_cert_id, "
            "recipient_cert_id, project_id, sequence_no, package_type, "
            "processed_at, result, revision, prev_hash, record_hash "
            "FROM processed_packages ORDER BY seq ASC"
        ).fetchall()
        meta = dict(
            connection.execute("SELECT key, value FROM meta").fetchall()
        )
        try:
            expected_count = int(meta.get("record_count", ""))
        except ValueError as exc:
            raise PackageStoreDbIntegrityError(
                "package store record_count is corrupt"
            ) from exc
        if len(rows) != expected_count:
            raise PackageStoreDbIntegrityError(
                "package store row count does not match meta.record_count"
            )
        previous = GENESIS_HASH
        for index, row in enumerate(rows, start=1):
            seq = int(row[0])
            if seq != index:
                raise PackageStoreDbIntegrityError(
                    "package store sequence is not contiguous"
                )
            record = _row_to_record(row[1:11])
            expected_hash = _record_hash(
                prev_hash=previous, seq=seq, record=record
            )
            if row[11] != previous or row[12] != expected_hash:
                raise PackageStoreDbIntegrityError(
                    "package store hash chain is invalid"
                )
            previous = row[12]


def _row_to_record(row: tuple) -> ProcessedPackageRecord:
    from .replay_detector import ProcessedPackage

    (
        package_id,
        package_digest,
        sender_cert_id,
        recipient_cert_id,
        project_id,
        sequence_no,
        package_type,
        processed_at,
        result,
        revision,
    ) = row
    return ProcessedPackageRecord(
        package=ProcessedPackage(
            package_id=package_id,
            package_digest=package_digest,
            sender_cert_id=sender_cert_id,
            recipient_cert_id=recipient_cert_id,
            project_id=project_id,
            sequence_no=int(sequence_no),
        ),
        package_type=package_type,
        processed_at=processed_at,
        result=result,
        revision=revision,
    )


def _normalize_sql(statement: str) -> str:
    return " ".join(str(statement).split())


__all__ = [
    "GENESIS_HASH",
    "RESULT_COMMITTED",
    "RESULT_ROLLED_BACK",
    "SCHEMA_VERSION",
    "PackageStoreDb",
    "PackageStoreDbError",
    "PackageStoreDbIntegrityError",
]
