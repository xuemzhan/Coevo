"""PRODUCT-REVIEW T-14: shared SQLite schema migration framework."""
from __future__ import annotations

import sqlite3
import unittest


from src.coevo.db_migration import (
    SchemaMigration,
    SchemaMigrationError,
    apply_migrations,
    read_schema_version,
)


def _make_connection(version: str = "1.0") -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE app_metadata("
        "singleton INTEGER PRIMARY KEY CHECK(singleton=1), schema_version TEXT NOT NULL)"
    )
    conn.execute(
        "INSERT INTO app_metadata(singleton, schema_version) VALUES(1, ?)",
        (version,),
    )
    conn.execute("CREATE TABLE items(id INTEGER PRIMARY KEY, value TEXT)")
    conn.commit()
    return conn


class DbMigrationTests(unittest.TestCase):
    def test_read_version(self):
        conn = _make_connection("1.0")
        self.assertEqual("1.0", read_schema_version(conn, metadata_table="app_metadata"))

    def test_missing_metadata_is_fail_closed(self):
        conn = sqlite3.connect(":memory:")
        with self.assertRaises(SchemaMigrationError):
            read_schema_version(conn, metadata_table="app_metadata")

    def test_upgrade_1_0_to_1_1_preserves_data(self):
        conn = _make_connection("1.0")
        conn.execute("INSERT INTO items(value) VALUES('keep-me')")
        conn.commit()

        def _add_column(c):
            c.execute("ALTER TABLE items ADD COLUMN kind TEXT NOT NULL DEFAULT ''")

        final = apply_migrations(
            conn,
            metadata_table="app_metadata",
            expected_version="1.1",
            migrations=(
                SchemaMigration("1.1", "add kind column", _add_column),
            ),
        )
        self.assertEqual("1.1", final)
        self.assertEqual(
            "keep-me",
            conn.execute("SELECT value FROM items WHERE id=1").fetchone()[0],
        )
        self.assertEqual(
            "1.1",
            conn.execute(
                "SELECT schema_version FROM app_metadata WHERE singleton=1"
            ).fetchone()[0],
        )

    def test_unknown_newer_version_is_rejected(self):
        conn = _make_connection("9.9")
        with self.assertRaises(SchemaMigrationError):
            apply_migrations(
                conn,
                metadata_table="app_metadata",
                expected_version="1.0",
                migrations=(),
            )

    def test_empty_migrations_is_noop_at_current_version(self):
        conn = _make_connection("1.0")
        final = apply_migrations(
            conn,
            metadata_table="app_metadata",
            expected_version="1.0",
            migrations=(),
        )
        self.assertEqual("1.0", final)

    def test_failed_migration_rolls_back_version(self):
        conn = _make_connection("1.0")

        def _boom(c):
            c.execute("ALTER TABLE missing_table ADD COLUMN x TEXT")

        with self.assertRaises(sqlite3.OperationalError):
            apply_migrations(
                conn,
                metadata_table="app_metadata",
                expected_version="1.1",
                migrations=(
                    SchemaMigration("1.1", "boom", _boom),
                ),
            )
        self.assertEqual(
            "1.0",
            conn.execute(
                "SELECT schema_version FROM app_metadata WHERE singleton=1"
            ).fetchone()[0],
        )


if __name__ == "__main__":
    unittest.main()
