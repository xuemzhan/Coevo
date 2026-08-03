"""Unit tests for PACKAGE-DB-1 persistent processed-package registry."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.coevo.protocol import (
    AgentPackageStoreDuplicateError,
    PackageStoreDb,
    PackageStoreDbError,
    PackageStoreDbIntegrityError,
    ProcessedPackage,
    ProcessedPackageRecord,
    ProcessedPackageStore,
)


NOW = "2026-08-03T00:00:00Z"


def _record(
    *,
    package_id: str = "pkg.001",
    package_digest: str = "a" * 64,
    sender_cert_id: str = "sender-001",
    recipient_cert_id: str = "recipient-001",
    project_id: str = "PRJ001",
    sequence_no: int = 1,
    package_type: str = "TASK_ASSIGNMENT",
    processed_at: str = NOW,
    result: str = "committed",
    revision: str = "PRJ001-R0001",
) -> ProcessedPackageRecord:
    return ProcessedPackageRecord(
        package=ProcessedPackage(
            package_id=package_id,
            package_digest=package_digest,
            sender_cert_id=sender_cert_id,
            recipient_cert_id=recipient_cert_id,
            project_id=project_id,
            sequence_no=sequence_no,
        ),
        package_type=package_type,
        processed_at=processed_at,
        result=result,
        revision=revision,
    )


class LifecycleTests(unittest.TestCase):
    def test_create_refuses_existing_path(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        self.addCleanup(store.close)
        with self.assertRaises(PackageStoreDbError):
            PackageStoreDb.create(path)

    def test_create_then_open_round_trip(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        self.assertEqual(len(store), 0)
        store.close()
        reopened = PackageStoreDb.open(path)
        self.assertEqual(len(reopened), 0)
        reopened.close()

    def test_open_missing_file_fails(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        with self.assertRaises(PackageStoreDbError):
            PackageStoreDb.open(Path(tmp) / "missing.db")

    def test_open_non_sqlite_file_fails(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "not-a-db.db"
        path.write_text("not a sqlite file", encoding="utf-8")
        with self.assertRaises(PackageStoreDbError):
            PackageStoreDb.open(path)

    def test_open_corrupt_sqlite_file_fails(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "corrupt.db"
        path.write_bytes(b"SQLite format 3\x00" + b"\x00" * 128)
        with self.assertRaises(PackageStoreDbError):
            PackageStoreDb.open(path)

    def test_close_is_idempotent_and_guards_use(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        store.close()
        store.close()
        with self.assertRaises(PackageStoreDbError):
            store.register(_record())
        with self.assertRaises(PackageStoreDbError):
            store.get("pkg.001")
        with self.assertRaises(PackageStoreDbError):
            store.snapshot()


class RegisterQueryTests(unittest.TestCase):
    def test_register_then_get_round_trip(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        self.addCleanup(store.close)
        record = _record()
        store.register(record)
        self.assertEqual(store.get("pkg.001"), record)
        self.assertEqual(store.by_digest("a" * 64), record)
        self.assertEqual(len(store), 1)

    def test_duplicate_package_id_rejected(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        self.addCleanup(store.close)
        store.register(_record())
        other = _record(
            package_digest="b" * 64,
            sequence_no=2,
            revision="PRJ001-R0002",
        )
        with self.assertRaises(AgentPackageStoreDuplicateError):
            store.register(other)
        self.assertEqual(len(store), 1)

    def test_duplicate_digest_rejected(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        self.addCleanup(store.close)
        store.register(_record())
        other = _record(
            package_id="pkg.002",
            sequence_no=2,
            revision="PRJ001-R0002",
        )
        with self.assertRaises(AgentPackageStoreDuplicateError):
            store.register(other)
        self.assertEqual(len(store), 1)

    def test_by_scope_sorted_by_sequence(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        self.addCleanup(store.close)
        store.register(
            _record(
                package_id="pkg.002",
                package_digest="b" * 64,
                sequence_no=2,
                revision="PRJ001-R0002",
            )
        )
        store.register(
            _record(
                package_id="pkg.001",
                package_digest="a" * 64,
                sequence_no=1,
            )
        )
        records = store.by_scope(
            sender_cert_id="sender-001",
            recipient_cert_id="recipient-001",
            project_id="PRJ001",
        )
        self.assertEqual(
            [r.package.package_id for r in records], ["pkg.001", "pkg.002"]
        )

    def test_revision_for_returns_highest(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        self.addCleanup(store.close)
        store.register(
            _record(
                package_id="pkg.001",
                package_digest="a" * 64,
                sequence_no=1,
                revision="PRJ001-R0001",
            )
        )
        store.register(
            _record(
                package_id="pkg.002",
                package_digest="b" * 64,
                sequence_no=2,
                revision="PRJ001-R0009",
            )
        )
        self.assertEqual(store.revision_for("PRJ001"), "PRJ001-R0009")
        self.assertIsNone(store.revision_for("OTHER"))

    def test_iter_records_returns_registration_order(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        self.addCleanup(store.close)
        first = _record()
        second = _record(
            package_id="pkg.002",
            package_digest="b" * 64,
            sequence_no=2,
            revision="PRJ001-R0002",
        )
        store.register(first)
        store.register(second)
        self.assertEqual(list(store.iter_records()), [first, second])

    def test_snapshot_matches_inmemory_store(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        self.addCleanup(store.close)
        store.register(_record())
        store.register(
            _record(
                package_id="pkg.002",
                package_digest="b" * 64,
                sequence_no=2,
                revision="PRJ001-R0002",
            )
        )
        snapshot = store.snapshot()
        self.assertIsInstance(snapshot, ProcessedPackageStore)
        self.assertEqual(len(snapshot), 2)
        self.assertEqual(snapshot.get("pkg.001"), _record())
        self.assertIsNotNone(snapshot.by_digest("b" * 64))
        self.assertEqual(snapshot.revision_for("PRJ001"), "PRJ001-R0002")


class ValidationTests(unittest.TestCase):
    def _fresh_store(self, tmp: str) -> PackageStoreDb:
        store = PackageStoreDb.create(Path(tmp) / "registry.db")
        self.addCleanup(store.close)
        return store

    def test_rejects_non_record(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = self._fresh_store(tmp)
        with self.assertRaises(PackageStoreDbError):
            store.register("not a record")

    def test_rejects_bad_digest_format(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = self._fresh_store(tmp)
        for digest in ("", "abc", "A" * 64, "g" + "a" * 63):
            with self.assertRaises(PackageStoreDbError):
                store.register(_record(package_digest=digest))

    def test_rejects_empty_identity_fields(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = self._fresh_store(tmp)
        for field in ("sender_cert_id", "recipient_cert_id", "project_id"):
            with self.assertRaises(PackageStoreDbError):
                store.register(_record(**{field: ""}))
        with self.assertRaises(PackageStoreDbError):
            store.register(_record(package_id=""))

    def test_rejects_bad_sequence_no(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = self._fresh_store(tmp)
        for sequence in (0, -1, 1_000_000_001, True):
            with self.assertRaises(PackageStoreDbError):
                store.register(_record(sequence_no=sequence))

    def test_rejects_unknown_package_type(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = self._fresh_store(tmp)
        with self.assertRaises(PackageStoreDbError):
            store.register(_record(package_type="MALWARE_PACKAGE"))

    def test_rejects_bad_timestamp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = self._fresh_store(tmp)
        for ts in ("", "2026-08-03T00:00:00", "not-a-timeZ", "2026-13-99T00:00:00Z"):
            with self.assertRaises(PackageStoreDbError):
                store.register(_record(processed_at=ts))

    def test_rejects_bad_result(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = self._fresh_store(tmp)
        with self.assertRaises(PackageStoreDbError):
            store.register(_record(result="maybe"))

    def test_rejects_empty_revision(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        store = self._fresh_store(tmp)
        with self.assertRaises(PackageStoreDbError):
            store.register(_record(revision=""))


class TamperDetectionTests(unittest.TestCase):
    @staticmethod
    def _registered_path(tmp: str) -> Path:
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        store.register(_record())
        store.register(
            _record(
                package_id="pkg.002",
                package_digest="b" * 64,
                sequence_no=2,
                revision="PRJ001-R0002",
            )
        )
        store.close()
        return path

    def test_value_tamper_detected_on_open(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "UPDATE processed_packages SET result = 'rolled_back' "
            "WHERE package_id = 'pkg.001'"
        )
        connection.commit()
        connection.close()
        with self.assertRaises(PackageStoreDbIntegrityError):
            PackageStoreDb.open(path)

    def test_digest_column_tamper_detected_on_open(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "UPDATE processed_packages SET package_digest = ? "
            "WHERE package_id = 'pkg.001'",
            ("c" * 64,),
        )
        connection.commit()
        connection.close()
        with self.assertRaises(PackageStoreDbIntegrityError):
            PackageStoreDb.open(path)

    def test_row_delete_detected_on_open(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "DELETE FROM processed_packages WHERE package_id = 'pkg.001'"
        )
        connection.commit()
        connection.close()
        with self.assertRaises(PackageStoreDbIntegrityError):
            PackageStoreDb.open(path)

    def test_last_row_delete_detected_on_open(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "DELETE FROM processed_packages WHERE package_id = 'pkg.002'"
        )
        connection.commit()
        connection.close()
        with self.assertRaises(PackageStoreDbIntegrityError):
            PackageStoreDb.open(path)

    def test_extra_table_detected_on_open(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute("CREATE TABLE smuggled (id INTEGER PRIMARY KEY)")
        connection.commit()
        connection.close()
        with self.assertRaises(PackageStoreDbIntegrityError):
            PackageStoreDb.open(path)

    def test_meta_schema_sha256_tamper_detected_on_open(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "UPDATE meta SET value = ? WHERE key = 'schema_sha256'",
            ("f" * 64,),
        )
        connection.commit()
        connection.close()
        with self.assertRaises(PackageStoreDbIntegrityError):
            PackageStoreDb.open(path)

    def test_meta_record_count_tamper_detected_on_open(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = self._registered_path(tmp)
        connection = sqlite3.connect(str(path))
        connection.execute(
            "UPDATE meta SET value = '99' WHERE key = 'record_count'"
        )
        connection.commit()
        connection.close()
        with self.assertRaises(PackageStoreDbIntegrityError):
            PackageStoreDb.open(path)


if __name__ == "__main__":
    unittest.main()
