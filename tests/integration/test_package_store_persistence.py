"""Integration tests for PACKAGE-DB-1: cross-restart persistence of the
协议 § 17 processed-package registry."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.coevo.protocol import (
    AgentPackageStoreDuplicateError,
    PackageStoreDb,
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
    sequence_no: int = 1,
    project_id: str = "PRJ001",
    revision: str = "PRJ001-R0001",
) -> ProcessedPackageRecord:
    return ProcessedPackageRecord(
        package=ProcessedPackage(
            package_id=package_id,
            package_digest=package_digest,
            sender_cert_id="sender-001",
            recipient_cert_id="recipient-001",
            project_id=project_id,
            sequence_no=sequence_no,
        ),
        package_type="TASK_ASSIGNMENT",
        processed_at=NOW,
        result="committed",
        revision=revision,
    )


class CrossRestartPersistenceTests(unittest.TestCase):
    def test_registered_records_survive_restart(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        self.addCleanup(store.close)
        record = _record()
        store.register(record)
        store.close()

        reopened = PackageStoreDb.open(path)
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.get("pkg.001"), record)
        self.assertEqual(reopened.by_digest("a" * 64), record)
        self.assertEqual(len(reopened), 1)

    def test_duplicate_package_id_detected_across_restart(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        self.addCleanup(store.close)
        store.register(_record())
        store.close()

        reopened = PackageStoreDb.open(path)
        self.addCleanup(reopened.close)
        with self.assertRaises(AgentPackageStoreDuplicateError):
            reopened.register(
                _record(
                    package_id="pkg.001",
                    package_digest="b" * 64,
                    sequence_no=2,
                    revision="PRJ001-R0002",
                )
            )

    def test_duplicate_digest_detected_across_restart(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        self.addCleanup(store.close)
        store.register(_record())
        store.close()

        reopened = PackageStoreDb.open(path)
        self.addCleanup(reopened.close)
        with self.assertRaises(AgentPackageStoreDuplicateError):
            reopened.register(
                _record(
                    package_id="pkg.002",
                    package_digest="a" * 64,
                    sequence_no=2,
                    revision="PRJ001-R0002",
                )
            )

    def test_scope_and_revision_queries_after_restart(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        self.addCleanup(store.close)
        store.register(_record())
        store.register(
            _record(
                package_id="pkg.002",
                package_digest="b" * 64,
                sequence_no=2,
                revision="PRJ001-R0009",
            )
        )
        store.close()

        reopened = PackageStoreDb.open(path)
        self.addCleanup(reopened.close)
        records = reopened.by_scope(
            sender_cert_id="sender-001",
            recipient_cert_id="recipient-001",
            project_id="PRJ001",
        )
        self.assertEqual(
            [r.package.package_id for r in records], ["pkg.001", "pkg.002"]
        )
        self.assertEqual(reopened.revision_for("PRJ001"), "PRJ001-R0009")

    def test_tampered_file_is_refused_on_reopen(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        self.addCleanup(store.close)
        store.register(_record())
        store.close()

        connection = sqlite3.connect(str(path))
        connection.execute(
            "UPDATE processed_packages SET sequence_no = 999 "
            "WHERE package_id = 'pkg.001'"
        )
        connection.commit()
        connection.close()

        with self.assertRaises(PackageStoreDbIntegrityError):
            PackageStoreDb.open(path)

    def test_snapshot_after_restart_supports_inmemory_facades(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
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
        store.close()

        reopened = PackageStoreDb.open(path)
        self.addCleanup(reopened.close)
        snapshot = reopened.snapshot()
        self.assertIsInstance(snapshot, ProcessedPackageStore)
        self.assertEqual(len(snapshot), 2)
        with self.assertRaises(AgentPackageStoreDuplicateError):
            snapshot.register(_record())
        self.assertEqual(snapshot.revision_for("PRJ001"), "PRJ001-R0002")

    def test_append_after_reopen_extends_persisted_registry(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = tmp_dir.name
        path = Path(tmp) / "registry.db"
        store = PackageStoreDb.create(path)
        self.addCleanup(store.close)
        store.register(_record())
        store.close()

        reopened = PackageStoreDb.open(path)
        self.addCleanup(reopened.close)
        reopened.register(
            _record(
                package_id="pkg.002",
                package_digest="b" * 64,
                sequence_no=2,
                revision="PRJ001-R0002",
            )
        )
        reopened.close()

        reopened_again = PackageStoreDb.open(path)
        self.addCleanup(reopened_again.close)
        self.assertEqual(len(reopened_again), 2)
        self.assertIsNotNone(reopened_again.get("pkg.002"))


if __name__ == "__main__":
    unittest.main()
