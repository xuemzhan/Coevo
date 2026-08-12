"""db_migration - shared SQLite schema migration framework (PRODUCT-REVIEW T-14).

Repositories persist ``schema_version`` in a singleton metadata table and
reject unknown versions. This module provides the versioned upgrade path:
ordered, per-version migrations applied inside transactions, with
fail-closed checks for unknown/newer versions and missing rows.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 共享 SQLite 迁移框架：元数据表 + 版本化迁移注册表 + 失败关闭。
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SchemaMigration:
    """One ordered schema upgrade step."""

    version: str
    description: str
    apply: Callable[[sqlite3.Connection], None]


class SchemaMigrationError(RuntimeError):
    """A schema version could not be resolved or upgraded."""


def read_schema_version(
    connection: sqlite3.Connection,
    *,
    metadata_table: str,
    singleton_col: str = "singleton",
    version_col: str = "schema_version",
) -> str:
    """Read the persisted schema version; missing metadata is fail-closed."""
    try:
        row = connection.execute(
            f"SELECT {version_col} FROM {metadata_table} "
            f"WHERE {singleton_col}=1"
        ).fetchone()
    except sqlite3.Error as exc:
        raise SchemaMigrationError(
            f"cannot read schema version from {metadata_table}: {exc}"
        ) from exc
    if row is None:
        raise SchemaMigrationError(f"metadata table {metadata_table} has no version row")
    version = str(row[0])
    if not version:
        raise SchemaMigrationError("schema version must be non-empty")
    return version


def apply_migrations(
    connection: sqlite3.Connection,
    *,
    metadata_table: str,
    expected_version: str,
    migrations: tuple[SchemaMigration, ...],
) -> str:
    """Upgrade the database to ``expected_version`` via ordered migrations.

    Versions are applied strictly in registration order; each migration runs
    in its own transaction. Unknown/newer current versions fail closed.
    """
    current = read_schema_version(
        connection, metadata_table=metadata_table
    )
    by_version = {m.version: m for m in migrations}
    pending = [
        m for m in migrations
        if _version_gt(m.version, current) and _version_le(m.version, expected_version)
    ]
    for migration in pending:
        if migration.version not in by_version:
            raise SchemaMigrationError(
                f"no migration registered for version {migration.version!r}"
            )
        connection.execute("BEGIN")
        try:
            migration.apply(connection)
            connection.execute(
                f"UPDATE {metadata_table} SET {_version_col(metadata_table)} = ? "
                "WHERE singleton=1",
                (migration.version,),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    final = read_schema_version(connection, metadata_table=metadata_table)
    if final != expected_version:
        raise SchemaMigrationError(
            f"schema ended at {final!r}, expected {expected_version!r}"
        )
    return final


def _version_col(metadata_table: str) -> str:
    # 元数据表统一使用 schema_version 列（由调用方保证）。
    del metadata_table
    return "schema_version"


def _version_gt(left: str, right: str) -> bool:
    return _version_key(left) > _version_key(right)


def _version_le(left: str, right: str) -> bool:
    return _version_key(left) <= _version_key(right)


def _version_key(version: str) -> tuple[int, ...]:
    parts = version.split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError as exc:
        raise SchemaMigrationError(
            f"schema version {version!r} is not numeric dotted"
        ) from exc
