"""US-3-AC-2: SQLite-persistent redacted talent pool + redaction-on-import.

The :class:`TalentStore` persists the *redacted-only* field-minimum
contract (AC-2): talent_code / skill_tags / credentials /
current_task_count / max_parallel_tasks / availability /
redacted identity. Raw PII never enters the database; the only entry
point for raw identity attributes is :func:`talent_from_import`, which
delegates to :func:`src.coevo.talent.redaction.redact_identity`.

Guarantees (mirror the repository's established persistence posture)
--------------------------------------------------------------------
* Explicit :meth:`TalentStore.create` / :meth:`TalentStore.open` only;
  ``create`` refuses to overwrite an existing file and never creates
  implicitly from request data.
* Schema locked: ``meta.schema_version`` + ``meta.schema_sha256`` and
  exact DDL comparison on every open; extra objects / column drift are
  rejected (fail-closed).
* Tamper detection: append-only SHA-256 hash chain
  (``prev_hash`` / ``record_hash``) re-verified on every open plus
  ``PRAGMA integrity_check``.
* ``talent_code`` uniqueness enforced transactionally (``UNIQUE`` +
  ``BEGIN IMMEDIATE``).
* :meth:`TalentStore.snapshot` re-validates every row through the
  :class:`TalentPool` constructor (uniqueness, non-empty, pool match),
  so a corrupt database refuses to produce a pool.

Non-goals
---------
* No multi-process / multi-connection concurrency (one connection per
  store instance).
* No change to the US-3-AC-1 in-memory model or the recommender API.
* No new dependency -- Python stdlib only (``sqlite3`` / ``hashlib`` /
  ``json`` / ``uuid`` / ``datetime`` / ``pathlib``).
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-3-AC-2 SQLite 脱敏人才池持久化：哈希链 + 导入即脱敏 + 元数据缓存。
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Iterator

from .models import (
    AvailabilityWindow,
    SkillTag,
    Talent,
    TalentPool,
    TalentRecommenderError,
    TalentValidationError,
)
from .redaction import RedactedIdentity, redact_identity


SCHEMA_VERSION: str = "1.0"
GENESIS_HASH: str = "0" * 64

_DIGEST_HEX_LEN: int = 64
_FIELD_MAX_BYTES: int = 512
_LIST_MAX_ITEMS: int = 64
_COUNT_MAX: int = 1_000_000_000
_DISPLAY_MAX: int = 16
_SAFE_CODE_SET = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
)

_SCHEMA_DDL: Final[tuple[str, ...]] = (
    "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    "CREATE TABLE talents ("
    "seq INTEGER PRIMARY KEY, "
    "talent_code TEXT NOT NULL UNIQUE, "
    "skill_tags TEXT NOT NULL, "
    "credentials TEXT NOT NULL, "
    "current_task_count INTEGER NOT NULL, "
    "max_parallel_tasks INTEGER NOT NULL, "
    "availability_start TEXT NOT NULL, "
    "availability_end TEXT NOT NULL, "
    "identity_pool_code TEXT NOT NULL, "
    "display_hint TEXT NOT NULL, "
    "identity_hash TEXT NOT NULL, "
    "prev_hash TEXT NOT NULL, "
    "record_hash TEXT NOT NULL)",
)
_SCHEMA_SHA256: Final[str] = hashlib.sha256(
    "\n".join(_SCHEMA_DDL).encode("utf-8")
).hexdigest()

_META_KEYS: Final[tuple[str, ...]] = (
    "schema_version",
    "schema_sha256",
    "pool_code",
    "pool_schema_version",
    "record_count",
    "created_at",
)


class TalentStoreError(TalentRecommenderError):
    """Base class for persistent talent-store failures (fail-closed)."""


class TalentStoreIntegrityError(TalentStoreError):
    """The talent database is corrupt, tampered or schema-drifted."""


class TalentStoreDuplicateError(TalentStoreError):
    """A talent_code is already registered in the store."""


def _now_utc_iso_z() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _is_safe_id(value: str) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if not (value[0].isalpha() or value[0] == "_"):
        return False
    if len(value) > 64:
        return False
    return all(ch in _SAFE_CODE_SET for ch in value)


def _validate_iso_z(value: object, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TalentStoreError(f"{name} must be a non-empty string")
    if len(value.encode("utf-8")) > _FIELD_MAX_BYTES:
        raise TalentStoreError(f"{name} exceeds size limit")
    if not value.endswith("Z"):
        raise TalentStoreError(f"{name} must be ISO-8601 UTC ending with 'Z'")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TalentStoreError(f"{name} is not a valid ISO-8601 timestamp") from exc


def _validate_talent(
    talent: Talent,
    *,
    pool_code: str,
    pool_schema_version: str,
) -> None:
    """Store-level fail-closed validation before any row is persisted."""
    if not isinstance(talent, Talent):
        raise TalentStoreError("talent must be Talent")
    if not _is_safe_id(talent.talent_code):
        raise TalentStoreError("talent_code must be a safe-id")
    if not talent.skill_tags:
        raise TalentStoreError("skill_tags must be non-empty")
    if len(talent.skill_tags) > _LIST_MAX_ITEMS:
        raise TalentStoreError("skill_tags exceeds item limit")
    for tag in talent.skill_tags:
        if not isinstance(tag, SkillTag):
            raise TalentStoreError("skill_tags must be exact SkillTag")
        if len(tag.value.encode("utf-8")) > _FIELD_MAX_BYTES:
            raise TalentStoreError("skill_tag exceeds size limit")
    if len(talent.credentials) > _LIST_MAX_ITEMS:
        raise TalentStoreError("credentials exceeds item limit")
    for cred in talent.credentials:
        if not _is_safe_id(cred):
            raise TalentStoreError("credential must be a safe-id")
    if (
        not isinstance(talent.current_task_count, int)
        or isinstance(talent.current_task_count, bool)
        or talent.current_task_count < 0
        or talent.current_task_count > _COUNT_MAX
    ):
        raise TalentStoreError(
            "current_task_count must be an integer in [0, 1e9]"
        )
    if (
        not isinstance(talent.max_parallel_tasks, int)
        or isinstance(talent.max_parallel_tasks, bool)
        or talent.max_parallel_tasks < 1
        or talent.max_parallel_tasks > _COUNT_MAX
    ):
        raise TalentStoreError(
            "max_parallel_tasks must be an integer in [1, 1e9]"
        )
    if talent.current_task_count > talent.max_parallel_tasks:
        raise TalentStoreError(
            "current_task_count cannot exceed max_parallel_tasks"
        )
    _validate_iso_z(talent.availability.start, "availability.start")
    _validate_iso_z(talent.availability.end, "availability.end")
    identity = talent.redacted_identity
    if not isinstance(identity, RedactedIdentity):
        raise TalentStoreError("redacted_identity must be RedactedIdentity")
    if identity.pool_code != pool_code:
        raise TalentStoreError(
            f"identity pool_code {identity.pool_code!r} does not match store"
        )
    if (
        not isinstance(identity.identity_hash, str)
        or len(identity.identity_hash) != _DIGEST_HEX_LEN
        or any(ch not in "0123456789abcdef" for ch in identity.identity_hash)
    ):
        raise TalentStoreError(
            "identity_hash must be a 64-char lowercase hex digest"
        )
    if (
        not isinstance(identity.display_hint, str)
        or not identity.display_hint
        or len(identity.display_hint) > _DISPLAY_MAX
    ):
        raise TalentStoreError(
            "display_hint must be a non-empty string of at most 16 chars"
        )


def _record_hash(
    *,
    prev_hash: str,
    seq: int,
    talent: Talent,
    pool_code: str,
    pool_schema_version: str,
) -> str:
    identity = talent.redacted_identity
    payload = "|".join(
        (
            prev_hash,
            str(seq),
            talent.talent_code,
            json.dumps(
                [tag.value for tag in talent.skill_tags],
                separators=(",", ":"),
                sort_keys=True,
            ),
            json.dumps(
                list(talent.credentials),
                separators=(",", ":"),
                sort_keys=True,
            ),
            str(talent.current_task_count),
            str(talent.max_parallel_tasks),
            talent.availability.start,
            talent.availability.end,
            identity.pool_code,
            identity.display_hint,
            identity.identity_hash,
            pool_code,
            pool_schema_version,
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class TalentStore:
    """SQLite-backed persistent redacted talent pool (US-3-AC-2)."""

    def __init__(self, connection: sqlite3.Connection, path: Path) -> None:
        self._connection = connection
        self._path = path
        self._closed = False
        # pool 元数据在 create 时写入且不可变：首次读取后缓存，避免每次
        # register/pool_code 都执行一次 SQL 查询。
        self._pool_meta_cache: tuple[str, str] | None = None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def pool_code(self) -> str:
        self._ensure_open()
        return self._pool_meta()[0]

    # -- lifecycle ----------------------------------------------------------

    @classmethod
    def create(
        cls,
        path: Path,
        *,
        pool_code: str,
        pool_schema_version: str = "1.0",
    ) -> "TalentStore":
        """Create a new empty store for ``pool_code``; fails if it exists."""
        if not isinstance(path, Path):
            raise TalentStoreError("path must be a Path")
        if not _is_safe_id(pool_code):
            raise TalentStoreError("pool_code must be a safe-id")
        if pool_schema_version != "1.0":
            raise TalentStoreError(
                f"unsupported pool_schema_version {pool_schema_version!r}"
            )
        if path.exists():
            raise TalentStoreError("talent store already exists")
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(path))
        try:
            for statement in _SCHEMA_DDL:
                connection.execute(statement)
            meta = {
                "schema_version": SCHEMA_VERSION,
                "schema_sha256": _SCHEMA_SHA256,
                "pool_code": pool_code,
                "pool_schema_version": pool_schema_version,
                "record_count": "0",
                "created_at": _now_utc_iso_z(),
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
    def from_pool(cls, path: Path, pool: TalentPool) -> "TalentStore":
        """Create a store from an existing in-memory :class:`TalentPool`."""
        if not isinstance(pool, TalentPool):
            raise TalentStoreError("pool must be TalentPool")
        store = cls.create(
            path,
            pool_code=pool.pool_code,
            pool_schema_version=pool.schema_version,
        )
        try:
            for talent in pool.talents:
                store.register(talent)
        except Exception:
            store.close()
            try:
                path.unlink()
            except OSError:
                pass
            raise
        return store

    @classmethod
    def open(cls, path: Path) -> "TalentStore":
        """Open an existing store after schema + chain verification."""
        if not isinstance(path, Path):
            raise TalentStoreError("path must be a Path")
        if not path.is_file():
            raise TalentStoreError("talent store does not exist")
        connection = sqlite3.connect(str(path))
        try:
            cls._verify_integrity(connection)
            cls._verify_schema(connection)
            cls._verify_chain(connection)
            return cls(connection, path)
        except sqlite3.DatabaseError as exc:
            connection.close()
            raise TalentStoreError(
                "talent store file is corrupt or not a SQLite database"
            ) from exc
        except Exception:
            connection.close()
            raise

    def close(self) -> None:
        if self._closed:
            return
        self._connection.close()
        self._closed = True

    def __enter__(self) -> "TalentStore":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _ensure_open(self) -> None:
        if self._closed:
            raise TalentStoreError("talent store is closed")

    def _pool_meta(self) -> tuple[str, str]:
        if self._pool_meta_cache is None:
            meta = dict(
                self._connection.execute("SELECT key, value FROM meta").fetchall()
            )
            self._pool_meta_cache = (
                meta["pool_code"],
                meta["pool_schema_version"],
            )
        return self._pool_meta_cache

    # -- queries ------------------------------------------------------------

    def get(self, talent_code: str) -> Talent | None:
        """Fetch a talent by code from the SQLite pool."""
        self._ensure_open()
        if not isinstance(talent_code, str) or not talent_code:
            raise TalentStoreError("talent_code must be a string")
        row = self._connection.execute(
            "SELECT talent_code, skill_tags, credentials, current_task_count, "
            "max_parallel_tasks, availability_start, availability_end, "
            "identity_pool_code, display_hint, identity_hash "
            "FROM talents WHERE talent_code = ?",
            (talent_code,),
        ).fetchone()
        return _row_to_talent(row) if row is not None else None

    def iter_talents(self) -> Iterator[Talent]:
        """Iterate all talents in registration order."""
        self._ensure_open()
        cursor = self._connection.execute(
            "SELECT talent_code, skill_tags, credentials, current_task_count, "
            "max_parallel_tasks, availability_start, availability_end, "
            "identity_pool_code, display_hint, identity_hash "
            "FROM talents ORDER BY seq ASC"
        )
        for row in cursor:
            yield _row_to_talent(row)

    def __len__(self) -> int:
        self._ensure_open()
        row = self._connection.execute(
            "SELECT COUNT(*) FROM talents"
        ).fetchone()
        return int(row[0])

    # -- mutation -----------------------------------------------------------

    def register(self, talent: Talent) -> "TalentStore":
        """Atomically persist ``talent``; refuses duplicate talent_code."""
        self._ensure_open()
        pool_code, pool_schema_version = self._pool_meta()
        _validate_talent(
            talent,
            pool_code=pool_code,
            pool_schema_version=pool_schema_version,
        )
        connection = self._connection
        connection.execute("BEGIN IMMEDIATE")
        try:
            previous = connection.execute(
                "SELECT seq, record_hash FROM talents ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            seq = int(previous[0]) + 1 if previous is not None else 1
            prev_hash = previous[1] if previous is not None else GENESIS_HASH
            record_hash = _record_hash(
                prev_hash=prev_hash,
                seq=seq,
                talent=talent,
                pool_code=pool_code,
                pool_schema_version=pool_schema_version,
            )
            connection.execute(
                "INSERT INTO talents "
                "(seq, talent_code, skill_tags, credentials, current_task_count, "
                "max_parallel_tasks, availability_start, availability_end, "
                "identity_pool_code, display_hint, identity_hash, "
                "prev_hash, record_hash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    seq,
                    talent.talent_code,
                    json.dumps(
                        [tag.value for tag in talent.skill_tags],
                        separators=(",", ":"),
                        sort_keys=True,
                    ),
                    json.dumps(
                        list(talent.credentials),
                        separators=(",", ":"),
                        sort_keys=True,
                    ),
                    talent.current_task_count,
                    talent.max_parallel_tasks,
                    talent.availability.start,
                    talent.availability.end,
                    talent.redacted_identity.pool_code,
                    talent.redacted_identity.display_hint,
                    talent.redacted_identity.identity_hash,
                    prev_hash,
                    record_hash,
                ),
            )
            connection.execute(
                "UPDATE meta SET value = CAST((SELECT COUNT(*) FROM talents) "
                "AS TEXT) WHERE key = 'record_count'"
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise TalentStoreDuplicateError(
                f"talent_code {talent.talent_code!r} already registered"
            ) from exc
        except Exception:
            connection.rollback()
            raise
        return self

    # -- bridge -------------------------------------------------------------

    def snapshot(self) -> TalentPool:
        """Materialize the store as an in-memory :class:`TalentPool`.

        Re-validates uniqueness / non-empty / pool match through the
        ``TalentPool`` constructor (fail-closed on corrupt data).
        """
        self._ensure_open()
        pool_code, pool_schema_version = self._pool_meta()
        talents = tuple(self.iter_talents())
        return TalentPool(
            pool_code=pool_code,
            schema_version=pool_schema_version,
            talents=talents,
        )

    # -- verification (open-time, fail-closed) ------------------------------

    @staticmethod
    def _verify_integrity(connection: sqlite3.Connection) -> None:
        row = connection.execute("PRAGMA integrity_check").fetchone()
        if row is None or row[0] != "ok":
            raise TalentStoreIntegrityError("SQLite integrity_check failed")

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
            raise TalentStoreIntegrityError(
                "talent store schema object count mismatch"
            )
        found: dict[str, str] = {}
        for kind, name, sql in objects:
            if kind != "table":
                raise TalentStoreIntegrityError(
                    "talent store has a non-table object"
                )
            found[name] = str(sql)
        expected: dict[str, str] = {}
        for statement in _SCHEMA_DDL:
            table_name = statement.split("(", 1)[0].replace(
                "CREATE TABLE ", ""
            ).strip()
            expected[table_name] = statement
        if set(found) != set(expected):
            raise TalentStoreIntegrityError("talent store table set mismatch")
        for table_name, canonical in expected.items():
            if _normalize_sql(found[table_name]) != _normalize_sql(canonical):
                raise TalentStoreIntegrityError("talent store DDL drift detected")
        meta = dict(
            connection.execute("SELECT key, value FROM meta").fetchall()
        )
        if set(meta) != set(_META_KEYS):
            raise TalentStoreIntegrityError("talent store meta key set mismatch")
        if meta.get("schema_version") != SCHEMA_VERSION:
            raise TalentStoreIntegrityError(
                "talent store schema_version mismatch"
            )
        if meta.get("schema_sha256") != _SCHEMA_SHA256:
            raise TalentStoreIntegrityError(
                "talent store schema digest mismatch"
            )
        if not _is_safe_id(meta.get("pool_code", "")):
            raise TalentStoreIntegrityError("talent store pool_code is corrupt")
        if meta.get("pool_schema_version") != "1.0":
            raise TalentStoreIntegrityError(
                "talent store pool_schema_version is corrupt"
            )
        try:
            record_count = int(meta.get("record_count", ""))
        except ValueError as exc:
            raise TalentStoreIntegrityError(
                "talent store record_count is corrupt"
            ) from exc
        if record_count < 0:
            raise TalentStoreIntegrityError(
                "talent store record_count is negative"
            )

    @staticmethod
    def _verify_chain(connection: sqlite3.Connection) -> None:
        rows = connection.execute(
            "SELECT seq, talent_code, skill_tags, credentials, "
            "current_task_count, max_parallel_tasks, availability_start, "
            "availability_end, identity_pool_code, display_hint, "
            "identity_hash, prev_hash, record_hash "
            "FROM talents ORDER BY seq ASC"
        ).fetchall()
        meta = dict(
            connection.execute("SELECT key, value FROM meta").fetchall()
        )
        try:
            expected_count = int(meta.get("record_count", ""))
        except ValueError as exc:
            raise TalentStoreIntegrityError(
                "talent store record_count is corrupt"
            ) from exc
        if len(rows) != expected_count:
            raise TalentStoreIntegrityError(
                "talent store row count does not match meta.record_count"
            )
        pool_code = meta.get("pool_code", "")
        pool_schema_version = meta.get("pool_schema_version", "")
        previous = GENESIS_HASH
        for index, row in enumerate(rows, start=1):
            seq = int(row[0])
            if seq != index:
                raise TalentStoreIntegrityError(
                    "talent store sequence is not contiguous"
                )
            try:
                talent = _row_to_talent(row[1:11])
            except TalentValidationError as exc:
                raise TalentStoreIntegrityError(
                    "talent store row violates the field-minimum contract"
                ) from exc
            expected_hash = _record_hash(
                prev_hash=previous,
                seq=seq,
                talent=talent,
                pool_code=pool_code,
                pool_schema_version=pool_schema_version,
            )
            if row[11] != previous or row[12] != expected_hash:
                raise TalentStoreIntegrityError(
                    "talent store hash chain is invalid"
                )
            previous = row[12]


def _row_to_talent(row: tuple) -> Talent:
    (
        talent_code,
        skill_tags_raw,
        credentials_raw,
        current_task_count,
        max_parallel_tasks,
        availability_start,
        availability_end,
        identity_pool_code,
        display_hint,
        identity_hash,
    ) = row
    skill_tags = tuple(
        SkillTag(value)
        for value in json.loads(skill_tags_raw)
    )
    credentials = tuple(json.loads(credentials_raw))
    return Talent(
        talent_code=talent_code,
        skill_tags=skill_tags,
        credentials=credentials,
        current_task_count=int(current_task_count),
        max_parallel_tasks=int(max_parallel_tasks),
        availability=AvailabilityWindow(
            start=availability_start,
            end=availability_end,
        ),
        redacted_identity=RedactedIdentity(
            pool_code=identity_pool_code,
            display_hint=display_hint,
            identity_hash=identity_hash,
        ),
    )


def _normalize_sql(statement: str) -> str:
    return " ".join(str(statement).split())


def talent_from_import(
    *,
    talent_code: str,
    pool_code: str,
    raw_name: str,
    raw_email: str,
    org_code: str,
    skill_tags: tuple[str | SkillTag, ...],
    credentials: tuple[str, ...],
    current_task_count: int,
    max_parallel_tasks: int,
    availability: AvailabilityWindow,
) -> Talent:
    """Redact raw identity attributes and build a validated :class:`Talent`.

    This is the only sanctioned entry point for raw PII into the
    persistence slice: the returned :class:`Talent` carries only the
    redacted identity, and the raw inputs are never persisted.
    """
    identity = redact_identity(
        pool_code=pool_code,
        raw_name=raw_name,
        raw_email=raw_email,
        org_code=org_code,
    )
    tags = tuple(
        tag if isinstance(tag, SkillTag) else SkillTag(tag)
        for tag in skill_tags
    )
    return Talent(
        talent_code=talent_code,
        skill_tags=tags,
        credentials=tuple(credentials),
        current_task_count=current_task_count,
        max_parallel_tasks=max_parallel_tasks,
        availability=availability,
        redacted_identity=identity,
    )


__all__ = [
    "GENESIS_HASH",
    "SCHEMA_VERSION",
    "TalentStore",
    "TalentStoreDuplicateError",
    "TalentStoreError",
    "TalentStoreIntegrityError",
    "talent_from_import",
]
