"""US-14-AC-2 persistent knowledge bundle store (SQLite, fail-closed).

The store persists :class:`KnowledgeBundle` snapshots as canonical JSON
with a locked schema and a hash-chained audit trail:

* explicit :meth:`create` / :meth:`open` only -- no implicit database
  creation from request data;
* schema digest locked in ``meta`` and re-verified on every open;
  extra tables/views/triggers/indexes and any DDL drift are rejected;
* idempotent save (same bundle_id + digest) and conflict rejection
  (same bundle_id, different digest);
* strict deserialization: unknown types/fields, bad enums, corrupted
  JSON or digest mismatches all raise instead of silently degrading;
* append-only hash-chained audit rows (ids + digests only, no free-form
  knowledge content).

No new dependency; Python stdlib only.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-14-AC-2 知识包持久化（SQLite）：JSON 载荷编解码 + 校验 + 原子提交。
from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from . import (
    KnowledgeBundle,
    KnowledgeClassification,
    KnowledgeEntry,
    KnowledgeSourceKind,
    KnowledgeBaseValidationError,
    ReusableTemplate,
    ReusableTemplateKind,
    RetrospectiveDraft,
    ReviewDecision,
    ReviewDecisionKind,
)


SCHEMA_VERSION: str = "1.0"
PAYLOAD_MAX_BYTES: int = 8 * 1024 * 1024
AUDIT_ACTION_STORE: str = "store"
AUDIT_GENESIS: str = "GENESIS"

_SCHEMA_DDL: Final[tuple[str, ...]] = (
    "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    "CREATE TABLE bundles ("
    "bundle_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, "
    "created_at TEXT NOT NULL, committed INTEGER NOT NULL, "
    "classification TEXT NOT NULL, sha256 TEXT NOT NULL, "
    "payload TEXT NOT NULL, stored_at TEXT NOT NULL)",
    "CREATE TABLE audit ("
    "audit_id TEXT PRIMARY KEY, ts TEXT NOT NULL, action TEXT NOT NULL, "
    "bundle_id TEXT NOT NULL, digest TEXT NOT NULL, "
    "prev_hash TEXT NOT NULL, record_hash TEXT NOT NULL)",
)
_SCHEMA_SHA256: Final[str] = hashlib.sha256(
    "\n".join(_SCHEMA_DDL).encode("utf-8")
).hexdigest()

_TYPE_REGISTRY: Final[dict[str, type]] = {
    "KnowledgeBundle": KnowledgeBundle,
    "KnowledgeEntry": KnowledgeEntry,
    "RetrospectiveDraft": RetrospectiveDraft,
    "ReusableTemplate": ReusableTemplate,
    "ReviewDecision": ReviewDecision,
    "KnowledgeClassification": KnowledgeClassification,
    "KnowledgeSourceKind": KnowledgeSourceKind,
    "ReusableTemplateKind": ReusableTemplateKind,
    "ReviewDecisionKind": ReviewDecisionKind,
}


class KnowledgeStoreError(Exception):
    """Base class for knowledge store failures (fail-closed by default)."""


class KnowledgeStoreConflictError(KnowledgeStoreError):
    """A different bundle already exists under the same bundle_id."""


def _now_utc_iso_z() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Strict canonical (de)serialization
# ---------------------------------------------------------------------------


def _encode(value: Any) -> Any:
    if isinstance(value, enum.Enum):
        return {"$enum": type(value).__name__, "v": value.value}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            "$type": type(value).__name__,
            "v": {
                field.name: _encode(getattr(value, field.name))
                for field in dataclasses.fields(value)
            },
        }
    if isinstance(value, tuple):
        return {"$tuple": [_encode(item) for item in value]}
    if isinstance(value, list):
        return {"$list": [_encode(item) for item in value]}
    if isinstance(value, dict):
        return {str(key): _encode(item) for key, item in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise KnowledgeBaseValidationError(
        f"cannot serialize value of type {type(value).__name__}"
    )


def _decode(value: Any) -> Any:
    if isinstance(value, dict):
        if "$enum" in value:
            marker = value.get("$enum")
            payload = value.get("v")
            if not isinstance(marker, str) or marker not in _TYPE_REGISTRY:
                raise KnowledgeBaseValidationError("unknown enum marker")
            cls = _TYPE_REGISTRY[marker]
            if not issubclass(cls, enum.Enum):
                raise KnowledgeBaseValidationError("marker is not an enum type")
            try:
                return cls(payload)
            except ValueError as exc:
                raise KnowledgeBaseValidationError(
                    f"invalid enum value for {marker}"
                ) from exc
        if "$type" in value:
            marker = value.get("$type")
            fields = value.get("v")
            if (
                not isinstance(marker, str)
                or marker not in _TYPE_REGISTRY
                or not isinstance(fields, dict)
            ):
                raise KnowledgeBaseValidationError("invalid type marker")
            cls = _TYPE_REGISTRY[marker]
            if not dataclasses.is_dataclass(cls):
                raise KnowledgeBaseValidationError("marker is not a dataclass")
            expected = {field.name for field in dataclasses.fields(cls)}
            if set(fields) != expected:
                raise KnowledgeBaseValidationError(
                    f"field set mismatch for {marker}"
                )
            kwargs = {key: _decode(item) for key, item in fields.items()}
            try:
                return cls(**kwargs)
            except TypeError as exc:
                raise KnowledgeBaseValidationError(
                    f"cannot construct {marker}"
                ) from exc
        if "$tuple" in value:
            items = value.get("$tuple")
            if not isinstance(items, list):
                raise KnowledgeBaseValidationError("invalid tuple marker")
            return tuple(_decode(item) for item in items)
        if "$list" in value:
            items = value.get("$list")
            if not isinstance(items, list):
                raise KnowledgeBaseValidationError("invalid list marker")
            return [_decode(item) for item in items]
        return {str(key): _decode(item) for key, item in value.items()}
    return value


def bundle_to_payload(bundle: KnowledgeBundle) -> str:
    """Canonical JSON payload for a bundle (schema_version + encoded bundle)."""
    if not isinstance(bundle, KnowledgeBundle):
        raise KnowledgeBaseValidationError("bundle must be a KnowledgeBundle")
    return json.dumps(
        {
            "schema_version": SCHEMA_VERSION,
            "bundle": _encode(bundle),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def payload_to_bundle(payload: str) -> KnowledgeBundle:
    """Strictly parse a stored payload back into a KnowledgeBundle."""
    if not isinstance(payload, str) or not payload:
        raise KnowledgeBaseValidationError("payload must be a non-empty string")
    if len(payload.encode("utf-8")) > PAYLOAD_MAX_BYTES:
        raise KnowledgeBaseValidationError("payload exceeds size limit")
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise KnowledgeBaseValidationError("payload is not valid JSON") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "bundle"}:
        raise KnowledgeBaseValidationError("payload top-level fields are invalid")
    if data["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeBaseValidationError("unsupported payload schema_version")
    bundle = _decode(data["bundle"])
    if not isinstance(bundle, KnowledgeBundle):
        raise KnowledgeBaseValidationError("payload does not decode to a bundle")
    return bundle


# ---------------------------------------------------------------------------
# SQLite store
# ---------------------------------------------------------------------------


class KnowledgeStore:
    """SQLite-backed persistent knowledge bundle store."""

    def __init__(self, connection: sqlite3.Connection, path: Path) -> None:
        self._connection = connection
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    @classmethod
    def create(cls, path: Path) -> "KnowledgeStore":
        """Create a new store at ``path`` (fails if it already exists)."""
        if not isinstance(path, Path):
            raise KnowledgeStoreError("path must be a Path")
        if path.exists():
            raise KnowledgeStoreError("knowledge store already exists")
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(path))
        try:
            for statement in _SCHEMA_DDL:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                ("schema_version", SCHEMA_VERSION),
            )
            connection.execute(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                ("schema_sha256", _SCHEMA_SHA256),
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
    def open(cls, path: Path) -> "KnowledgeStore":
        """Open an existing store after schema + audit verification."""
        if not isinstance(path, Path):
            raise KnowledgeStoreError("path must be a Path")
        if not path.is_file():
            raise KnowledgeStoreError("knowledge store does not exist")
        connection = sqlite3.connect(str(path))
        try:
            cls._verify_schema(connection)
            store = cls(connection, path)
            if not store.verify_audit_chain():
                raise KnowledgeStoreError("knowledge store audit chain is invalid")
            return store
        except sqlite3.DatabaseError as exc:
            connection.close()
            raise KnowledgeStoreError(
                "knowledge store file is corrupt or not a SQLite database"
            ) from exc
        except Exception:
            connection.close()
            raise

    def save(
        self,
        bundle: KnowledgeBundle,
        *,
        now: str | None = None,
    ) -> dict[str, str]:
        """Persist a bundle atomically; idempotent on identical digest."""
        now = now or _now_utc_iso_z()
        payload = bundle_to_payload(bundle)
        if len(payload.encode("utf-8")) > PAYLOAD_MAX_BYTES:
            raise KnowledgeStoreError("bundle payload exceeds size limit")
        digest = _digest_text(payload)
        with self._connection:
            row = self._connection.execute(
                "SELECT sha256 FROM bundles WHERE bundle_id = ?",
                (bundle.bundle_id,),
            ).fetchone()
            if row is not None:
                if row[0] == digest:
                    return {"bundle_id": bundle.bundle_id, "digest": digest, "idempotent": "true"}
                raise KnowledgeStoreConflictError(
                    f"bundle {bundle.bundle_id!r} already exists with a different digest"
                )
            self._connection.execute(
                "INSERT INTO bundles "
                "(bundle_id, project_id, created_at, committed, classification, "
                " sha256, payload, stored_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    bundle.bundle_id,
                    bundle.project_id,
                    bundle.created_at,
                    1 if bundle.formally_committed else 0,
                    bundle.bundle_classification.value,
                    digest,
                    payload,
                    now,
                ),
            )
            previous = self._connection.execute(
                "SELECT record_hash FROM audit ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            prev_hash = previous[0] if previous is not None else AUDIT_GENESIS
            audit_id = f"kb-{uuid.uuid4().hex}"
            record_hash = _digest_text(
                "|".join((prev_hash, audit_id, now, AUDIT_ACTION_STORE,
                          bundle.bundle_id, digest))
            )
            self._connection.execute(
                "INSERT INTO audit "
                "(audit_id, ts, action, bundle_id, digest, prev_hash, record_hash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (audit_id, now, AUDIT_ACTION_STORE, bundle.bundle_id, digest,
                 prev_hash, record_hash),
            )
        return {"bundle_id": bundle.bundle_id, "digest": digest, "idempotent": "false"}

    def load(self, bundle_id: str) -> KnowledgeBundle | None:
        """Load a bundle, verifying digest and strict payload structure."""
        row = self._connection.execute(
            "SELECT sha256, payload FROM bundles WHERE bundle_id = ?",
            (bundle_id,),
        ).fetchone()
        if row is None:
            return None
        stored_sha256, payload = row
        if _digest_text(payload) != stored_sha256:
            raise KnowledgeStoreError("stored bundle digest mismatch")
        try:
            return payload_to_bundle(payload)
        except KnowledgeBaseValidationError as exc:
            raise KnowledgeStoreError("stored bundle payload is corrupt") from exc

    def list_by_project(self, project_id: str) -> tuple[dict[str, str], ...]:
        """Return stored bundle metadata for a project (bounded, ordered)."""
        rows = self._connection.execute(
            "SELECT bundle_id, created_at, committed, classification "
            "FROM bundles WHERE project_id = ? ORDER BY created_at",
            (project_id,),
        ).fetchmany(1000)
        return tuple(
            {
                "bundle_id": bundle_id,
                "created_at": created_at,
                "committed": "true" if committed else "false",
                "classification": classification,
            }
            for bundle_id, created_at, committed, classification in rows
        )

    def verify_audit_chain(self) -> bool:
        """Recompute the audit hash chain; False on any tampering."""
        rows = self._connection.execute(
            "SELECT audit_id, ts, action, bundle_id, digest, prev_hash, record_hash "
            "FROM audit ORDER BY rowid"
        ).fetchall()
        previous = AUDIT_GENESIS
        for audit_id, ts, action, bundle_id, digest, prev_hash, record_hash in rows:
            if prev_hash != previous:
                return False
            expected = _digest_text(
                "|".join((previous, audit_id, ts, action, bundle_id, digest))
            )
            if record_hash != expected:
                return False
            previous = record_hash
        return True

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "KnowledgeStore":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- schema verification ------------------------------------------------

    @staticmethod
    def _verify_schema(connection: sqlite3.Connection) -> None:
        rows = connection.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE type IN ('table', 'view', 'trigger', 'index') "
            "ORDER BY type, name"
        ).fetchall()
        # SQLite records implicit PRIMARY KEY indexes (sqlite_autoindex_*);
        # they are reserved-named, cannot be user-created, and are skipped.
        objects = [
            row for row in rows if not str(row[1]).startswith("sqlite_autoindex_")
        ]
        if len(objects) != len(_SCHEMA_DDL):
            raise KnowledgeStoreError("knowledge store schema object count mismatch")
        found: dict[str, str] = {}
        expected: dict[str, str] = {}
        for kind, name, sql in objects:
            if kind != "table":
                raise KnowledgeStoreError("knowledge store has a non-table object")
            found[name] = str(sql)
        for statement in _SCHEMA_DDL:
            table_name = statement.split("(", 1)[0].replace(
                "CREATE TABLE ", ""
            ).strip()
            expected[table_name] = statement
        if set(found) != set(expected):
            raise KnowledgeStoreError("knowledge store table set mismatch")
        for table_name, canonical in expected.items():
            if _normalize_sql(found[table_name]) != _normalize_sql(canonical):
                raise KnowledgeStoreError("knowledge store DDL drift detected")
        meta = dict(
            connection.execute("SELECT key, value FROM meta").fetchall()
        )
        if meta.get("schema_version") != SCHEMA_VERSION:
            raise KnowledgeStoreError("knowledge store schema_version mismatch")
        if meta.get("schema_sha256") != _SCHEMA_SHA256:
            raise KnowledgeStoreError("knowledge store schema digest mismatch")


def _normalize_sql(statement: str) -> str:
    return " ".join(str(statement).split())
