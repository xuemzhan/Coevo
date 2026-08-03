"""Unit tests for US-3-AC-2: redacted talent-store persistence + import."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.coevo.talent import (
    AvailabilityWindow,
    RedactedIdentity,
    SkillTag,
    Talent,
    TalentPool,
    TalentStore,
    TalentStoreDuplicateError,
    TalentStoreError,
    TalentStoreIntegrityError,
    TalentValidationError,
    talent_from_import,
)


NOW = "2026-08-03T00:00:00Z"


def _identity(
    *,
    pool_code: str = "pool.1",
    identity_hash: str = "a" * 64,
    display_hint: str = "ab12cd34",
) -> RedactedIdentity:
    return RedactedIdentity(
        pool_code=pool_code,
        display_hint=display_hint,
        identity_hash=identity_hash,
    )


def _talent(
    *,
    talent_code: str = "t.1",
    pool_code: str = "pool.1",
    skill_tags: tuple[str, ...] = ("tech:python",),
    credentials: tuple[str, ...] = ("cert.pmp",),
    current_task_count: int = 1,
    max_parallel_tasks: int = 2,
    identity_hash: str = "a" * 64,
    display_hint: str = "ab12cd34",
) -> Talent:
    return Talent(
        talent_code=talent_code,
        skill_tags=tuple(SkillTag(tag) for tag in skill_tags),
        credentials=credentials,
        current_task_count=current_task_count,
        max_parallel_tasks=max_parallel_tasks,
        availability=AvailabilityWindow(
            "2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"
        ),
        redacted_identity=_identity(
            pool_code=pool_code,
            identity_hash=identity_hash,
            display_hint=display_hint,
        ),
    )


def _pool(*, talents: tuple[Talent, ...] = (_talent(),)) -> TalentPool:
    return TalentPool(
        pool_code="pool.1",
        schema_version="1.0",
        talents=talents,
    )


def _tmpdir(test: unittest.TestCase) -> str:
    td = tempfile.TemporaryDirectory()
    test.addCleanup(td.cleanup)
    return td.name


class LifecycleTests(unittest.TestCase):
    def test_create_refuses_existing_path(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        store = TalentStore.create(path, pool_code="pool.1")
        self.addCleanup(store.close)
        with self.assertRaises(TalentStoreError):
            TalentStore.create(path, pool_code="pool.1")

    def test_create_then_open_round_trip(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        store = TalentStore.create(path, pool_code="pool.1")
        self.assertEqual(len(store), 0)
        store.close()
        reopened = TalentStore.open(path)
        self.assertEqual(len(reopened), 0)
        self.assertEqual("pool.1", reopened.pool_code)
        reopened.close()

    def test_open_missing_file_fails(self):
        tmp = _tmpdir(self)
        with self.assertRaises(TalentStoreError):
            TalentStore.open(Path(tmp) / "missing.db")

    def test_open_non_sqlite_file_fails(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "not-a-db.db"
        path.write_text("not a sqlite file", encoding="utf-8")
        with self.assertRaises(TalentStoreError):
            TalentStore.open(path)

    def test_open_corrupt_sqlite_file_fails(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "corrupt.db"
        path.write_bytes(b"SQLite format 3\x00" + b"\x00" * 128)
        with self.assertRaises(TalentStoreError):
            TalentStore.open(path)

    def test_close_is_idempotent_and_guards_use(self):
        tmp = _tmpdir(self)
        store = TalentStore.create(Path(tmp) / "talent.db", pool_code="pool.1")
        store.close()
        store.close()
        with self.assertRaises(TalentStoreError):
            store.register(_talent())
        with self.assertRaises(TalentStoreError):
            store.snapshot()

    def test_create_rejects_bad_pool_code_and_schema_version(self):
        tmp = _tmpdir(self)
        with self.assertRaises(TalentStoreError):
            TalentStore.create(
                Path(tmp) / "bad1.db", pool_code="not a safe id!"
            )
        with self.assertRaises(TalentStoreError):
            TalentStore.create(
                Path(tmp) / "bad2.db",
                pool_code="pool.1",
                pool_schema_version="9.9",
            )


class RegisterQueryTests(unittest.TestCase):
    def test_register_then_get_round_trip(self):
        tmp = _tmpdir(self)
        store = TalentStore.create(Path(tmp) / "talent.db", pool_code="pool.1")
        self.addCleanup(store.close)
        talent = _talent()
        store.register(talent)
        self.assertEqual(store.get("t.1"), talent)
        self.assertEqual(len(store), 1)

    def test_duplicate_talent_code_rejected(self):
        tmp = _tmpdir(self)
        store = TalentStore.create(Path(tmp) / "talent.db", pool_code="pool.1")
        self.addCleanup(store.close)
        store.register(_talent())
        other = _talent(
            talent_code="t.1",
            skill_tags=("tech:go",),
            identity_hash="b" * 64,
        )
        with self.assertRaises(TalentStoreDuplicateError):
            store.register(other)
        self.assertEqual(len(store), 1)

    def test_iter_talents_returns_registration_order(self):
        tmp = _tmpdir(self)
        store = TalentStore.create(Path(tmp) / "talent.db", pool_code="pool.1")
        self.addCleanup(store.close)
        first = _talent()
        second = _talent(
            talent_code="t.2",
            skill_tags=("tech:go",),
            identity_hash="b" * 64,
        )
        store.register(first)
        store.register(second)
        self.assertEqual(list(store.iter_talents()), [first, second])

    def test_from_pool_and_snapshot_round_trip(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        pool = _pool(
            talents=(
                _talent(),
                _talent(
                    talent_code="t.2",
                    skill_tags=("tech:go",),
                    identity_hash="b" * 64,
                ),
            )
        )
        store = TalentStore.from_pool(path, pool)
        self.addCleanup(store.close)
        self.assertEqual(len(store), 2)
        snapshot = store.snapshot()
        self.assertIsInstance(snapshot, TalentPool)
        self.assertEqual(snapshot.pool_code, "pool.1")
        self.assertEqual(len(snapshot.talents), 2)
        self.assertEqual(snapshot.by_code("t.2"), pool.by_code("t.2"))


class ValidationTests(unittest.TestCase):
    def _fresh_store(self, tmp: str) -> TalentStore:
        store = TalentStore.create(Path(tmp) / "talent.db", pool_code="pool.1")
        self.addCleanup(store.close)
        return store

    def test_rejects_non_talent(self):
        tmp = _tmpdir(self)
        store = self._fresh_store(tmp)
        with self.assertRaises(TalentStoreError):
            store.register("not a talent")

    def test_rejects_bad_identity_hash(self):
        tmp = _tmpdir(self)
        store = self._fresh_store(tmp)
        for digest in ("", "abc", "A" * 64, "g" + "a" * 63):
            with self.assertRaises(TalentStoreError):
                store.register(
                    _talent(
                        identity_hash=digest,
                        talent_code=f"t.{digest[:4] or 'x'}",
                    )
                )

    def test_rejects_display_hint_too_long(self):
        tmp = _tmpdir(self)
        store = self._fresh_store(tmp)
        with self.assertRaises(TalentStoreError):
            store.register(
                _talent(
                    talent_code="t.longhint",
                    identity_hash="c" * 64,
                    display_hint="x" * 17,
                )
            )

    def test_rejects_identity_pool_code_mismatch(self):
        tmp = _tmpdir(self)
        store = self._fresh_store(tmp)
        with self.assertRaises(TalentStoreError):
            store.register(_talent(pool_code="other.pool"))

    def test_rejects_empty_skill_tags(self):
        tmp = _tmpdir(self)
        store = self._fresh_store(tmp)
        with self.assertRaises(TalentStoreError):
            store.register(_talent(skill_tags=()))


class ImportTests(unittest.TestCase):
    def test_talent_from_import_redacts_and_validates(self):
        talent = talent_from_import(
            talent_code="t.import.1",
            pool_code="pool.1",
            raw_name="Alice Zhang",
            raw_email="alice@example.com",
            org_code="org.1",
            skill_tags=("tech:python", "domain:audit"),
            credentials=("cert.pmp",),
            current_task_count=0,
            max_parallel_tasks=3,
            availability=AvailabilityWindow(
                "2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"
            ),
        )
        self.assertEqual("t.import.1", talent.talent_code)
        self.assertEqual("pool.1", talent.redacted_identity.pool_code)
        self.assertEqual(64, len(talent.redacted_identity.identity_hash))
        self.assertLessEqual(len(talent.redacted_identity.display_hint), 16)
        # raw PII must never survive in any field
        joined = repr(talent).lower()
        self.assertNotIn("alice", joined)
        self.assertNotIn("zhang", joined)

    def test_talent_from_import_is_deterministic(self):
        kwargs = dict(
            talent_code="t.import.1",
            pool_code="pool.1",
            raw_name="Alice Zhang",
            raw_email="alice@example.com",
            org_code="org.1",
            skill_tags=("tech:python",),
            credentials=(),
            current_task_count=0,
            max_parallel_tasks=2,
            availability=AvailabilityWindow(
                "2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"
            ),
        )
        first = talent_from_import(**kwargs)
        second = talent_from_import(**kwargs)
        self.assertEqual(
            first.redacted_identity.identity_hash,
            second.redacted_identity.identity_hash,
        )
        self.assertEqual(first, second)

    def test_talent_from_import_rejects_blank_raw_inputs(self):
        with self.assertRaises(TalentValidationError):
            talent_from_import(
                talent_code="t.import.1",
                pool_code="pool.1",
                raw_name="",
                raw_email="alice@example.com",
                org_code="org.1",
                skill_tags=("tech:python",),
                credentials=(),
                current_task_count=0,
                max_parallel_tasks=2,
                availability=AvailabilityWindow(
                    "2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"
                ),
            )

    def test_imported_talent_registers_in_store(self):
        tmp = _tmpdir(self)
        store = TalentStore.create(Path(tmp) / "talent.db", pool_code="pool.1")
        self.addCleanup(store.close)
        talent = talent_from_import(
            talent_code="t.import.1",
            pool_code="pool.1",
            raw_name="Alice Zhang",
            raw_email="alice@example.com",
            org_code="org.1",
            skill_tags=("tech:python",),
            credentials=("cert.pmp",),
            current_task_count=0,
            max_parallel_tasks=2,
            availability=AvailabilityWindow(
                "2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"
            ),
        )
        store.register(talent)
        self.assertEqual(store.get("t.import.1"), talent)


class TamperDetectionTests(unittest.TestCase):
    @staticmethod
    def _registered_path(tmp: str) -> Path:
        path = Path(tmp) / "talent.db"
        store = TalentStore.create(path, pool_code="pool.1")
        store.register(_talent())
        store.register(
            _talent(
                talent_code="t.2",
                skill_tags=("tech:go",),
                identity_hash="b" * 64,
            )
        )
        store.close()
        return path

    def test_value_tamper_detected_on_open(self):
        tmp = _tmpdir(self)
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "UPDATE talents SET current_task_count = 9 "
            "WHERE talent_code = 't.1'"
        )
        connection.commit()
        connection.close()
        with self.assertRaises(TalentStoreIntegrityError):
            TalentStore.open(path)

    def test_row_delete_detected_on_open(self):
        tmp = _tmpdir(self)
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "DELETE FROM talents WHERE talent_code = 't.2'"
        )
        connection.commit()
        connection.close()
        with self.assertRaises(TalentStoreIntegrityError):
            TalentStore.open(path)

    def test_extra_table_detected_on_open(self):
        tmp = _tmpdir(self)
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute("CREATE TABLE smuggled (id INTEGER PRIMARY KEY)")
        connection.commit()
        connection.close()
        with self.assertRaises(TalentStoreIntegrityError):
            TalentStore.open(path)

    def test_meta_record_count_tamper_detected_on_open(self):
        tmp = _tmpdir(self)
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "UPDATE meta SET value = '99' WHERE key = 'record_count'"
        )
        connection.commit()
        connection.close()
        with self.assertRaises(TalentStoreIntegrityError):
            TalentStore.open(path)


if __name__ == "__main__":
    unittest.main()
