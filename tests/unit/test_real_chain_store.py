"""SQLite real-chain store unit and rollback-resistance tests."""
from __future__ import annotations

import math
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.coevo.identity.audit_anchor import AuditAnchorError
from src.coevo.orchestrator.real_chain_store import (
    RealChainStore,
    RealChainStoreError,
    RealChainStoreRecoveryRequired,
    canonical_digest,
    canonical_json_bytes,
)
from tests.support_identity import TestFreshnessAuthority, TestSigner


NOW = "2026-08-01T04:00:00Z"


class CanonicalTests(unittest.TestCase):
    def test_canonical_and_rejections(self) -> None:
        self.assertEqual(canonical_json_bytes({"b": 2, "a": 1}), b'{"a":1,"b":2}')
        for value in ({"x": (1,)}, {1: "x"}, {"x": math.nan}):
            with self.assertRaises(RealChainStoreError):
                canonical_json_bytes(value)


class PersistentStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.signer = TestSigner()
        self.freshness = TestFreshnessAuthority()
        self.counter = 0

    def path(self) -> Path:
        self.counter += 1
        return Path(self.temporary.name) / f"store-{self.counter}.db"

    def create(self, path: Path | None = None) -> RealChainStore:
        return RealChainStore.create(
            path or self.path(), signer=self.signer, freshness=self.freshness,
        )

    def open(self, path: Path) -> RealChainStore:
        return RealChainStore.open(
            path, signer=self.signer, freshness=self.freshness,
        )

    @staticmethod
    def add_event(store: RealChainStore, event_id: str = "ev.1") -> str:
        digest = canonical_digest({"event": event_id})
        store.begin_dispatch(event_id, digest, "PRJ001", NOW)
        return digest

    def test_explicit_create_and_open_only(self) -> None:
        path = self.path()
        with self.assertRaises(RealChainStoreError):
            RealChainStore(path)
        with self.assertRaises(AuditAnchorError):
            self.open(path)
        store = self.create(path)
        store_id = store.store_id
        store.close()
        with self.assertRaises(AuditAnchorError):
            self.create(path)
        reopened = self.open(path)
        self.assertEqual(store_id, reopened.store_id)
        reopened.close()

    def test_hash_chain_and_checkpoint_persist(self) -> None:
        path = self.path()
        store = self.create(path)
        digest = self.add_event(store)
        store.record_attempt("ev.1", digest, "facade.0", "failure", NOW)
        self.assertTrue(store.verify_audit_chain())
        entries = store.audit_entries
        store_id = store.store_id
        store.close()
        reopened = self.open(path)
        self.assertEqual(store_id, reopened.store_id)
        reopened_entries = reopened.audit_entries
        self.assertEqual(entries, reopened_entries[:len(entries)])
        self.assertEqual(("recovery", "required"),
                         (reopened_entries[-1].action, reopened_entries[-1].result))
        reopened.close()

    def test_same_id_different_digest_conflicts_transactionally(self) -> None:
        store = self.create()
        digest = self.add_event(store)
        with self.assertRaises(RealChainStoreError):
            store.begin_dispatch("ev.1", "f" * 64, "PRJ001", NOW)
        self.assertEqual(digest, store.recovery_context("ev.1").event_digest)
        self.assertIn("digest_conflict", [entry.result for entry in store.audit_entries])
        store.close()

    def test_deleted_audit_tail_is_rejected(self) -> None:
        store = self.create()
        self.add_event(store)
        store.connection.execute(
            "DELETE FROM real_chain_audit WHERE sequence=(SELECT MAX(sequence) FROM real_chain_audit)"
        )
        with self.assertRaises(AuditAnchorError):
            _ = store.audit_entries
        store.close()

    def test_known_audit_corruption_blocks_business_operations(self) -> None:
        store = self.create()
        self.add_event(store)
        store.connection.execute(
            "UPDATE real_chain_audit SET result='forged' WHERE sequence=1"
        )
        with self.assertRaises(RealChainStoreError):
            store.begin_dispatch("ev.2", canonical_digest({"event": "ev.2"}),
                                 "PRJ001", NOW)
        self.assertIsNone(store.connection.execute(
            "SELECT event_id FROM real_chain_records WHERE event_id='ev.2'"
        ).fetchone())
        store.close()

    def test_record_and_metadata_tampering_are_rejected(self) -> None:
        for statement in (
            "UPDATE real_chain_records SET project_id='FORGED' WHERE event_id='ev.1'",
            "UPDATE real_chain_metadata SET store_id='forged-store' WHERE singleton=1",
            "UPDATE real_chain_metadata SET schema_version='9.9' WHERE singleton=1",
        ):
            with self.subTest(statement=statement):
                store = self.create()
                self.add_event(store)
                store.connection.execute(statement)
                expected = RealChainStoreError if "schema_version" in statement else AuditAnchorError
                with self.assertRaises(expected):
                    _ = store.store_id
                store.close()

    def test_bad_anchor_signature_is_rejected_on_open(self) -> None:
        path = self.path()
        store = self.create(path)
        store.anchor.signature.write_bytes(b"forged")
        store.close()
        with self.assertRaises(AuditAnchorError):
            self.open(path)

    def test_old_sqlite_snapshot_cannot_replace_newer_state(self) -> None:
        path = self.path()
        old = Path(self.temporary.name) / "old.db"
        store = self.create(path)
        first_digest = self.add_event(store, "ev.1")
        shutil.copy2(path, old)
        store.record_attempt("ev.1", first_digest, "facade.0", "failure", NOW)
        store.close()
        shutil.copy2(old, path)
        with self.assertRaises(AuditAnchorError):
            self.open(path)

    def test_old_anchor_cannot_replace_newer_signed_state(self) -> None:
        path = self.path()
        store = self.create(path)
        saved = []
        for artifact in (
            store.anchor.head, store.anchor.signature, store.anchor.marker_signature,
        ):
            copy = Path(str(artifact) + ".old")
            shutil.copy2(artifact, copy)
            saved.append((copy, artifact))
        self.add_event(store)
        store.close()
        for old, official in saved:
            shutil.copy2(old, official)
        with self.assertRaises(AuditAnchorError):
            self.open(path)

    def test_sqlite_and_signed_anchor_cannot_roll_back_together(self) -> None:
        path = self.path()
        old_database = Path(self.temporary.name) / "old-pair.db"
        store = self.create(path)
        self.add_event(store, "ev.1")
        shutil.copy2(path, old_database)
        saved = []
        for artifact in (
            store.anchor.head, store.anchor.signature, store.anchor.marker_signature,
        ):
            copy = Path(str(artifact) + ".pair-old")
            shutil.copy2(artifact, copy)
            saved.append((copy, artifact))
        self.add_event(store, "ev.2")
        store.close()
        shutil.copy2(old_database, path)
        for old, official in saved:
            shutil.copy2(old, official)
        with self.assertRaises(AuditAnchorError):
            self.open(path)

    def test_prepare_failure_rolls_back_sqlite_and_audit(self) -> None:
        store = self.create()
        before = store.audit_entries
        with patch.object(store.anchor, "prepare", side_effect=OSError("injected prepare")):
            with self.assertRaises(OSError):
                self.add_event(store)
        self.assertEqual(before, store.audit_entries)
        self.add_event(store)
        self.assertEqual(1, len([x for x in store.audit_entries if x.action == "dispatch"]))
        store.close()

    def test_promote_failure_requires_recovery_without_replaying_business(self) -> None:
        store = self.create()
        with patch.object(store.anchor, "promote", side_effect=OSError("injected promote")):
            with self.assertRaises(RealChainStoreRecoveryRequired):
                self.add_event(store)
        with self.assertRaises(RealChainStoreRecoveryRequired):
            _ = store.audit_entries
        store.recover()
        entries = store.audit_entries
        self.assertEqual(1, len([x for x in entries if x.action == "dispatch"]))
        self.assertEqual("DISPATCHING", store.recovery_context("ev.1").state)
        store.close()

    def test_before_and_after_audit_triggers_are_rejected_before_business_write(self) -> None:
        for timing in ("BEFORE", "AFTER"):
            with self.subTest(timing=timing):
                store = self.create()
                digest = self.add_event(store)
                before_state = store.connection.execute(
                    "SELECT state FROM real_chain_records WHERE event_id='ev.1'"
                ).fetchone()[0]
                before_count = store.connection.execute(
                    "SELECT COUNT(*) FROM real_chain_audit"
                ).fetchone()[0]
                store.connection.execute(
                    f"CREATE TRIGGER forged_{timing.lower()} {timing} INSERT ON real_chain_audit "
                    "BEGIN UPDATE real_chain_records SET state='ESCALATED' "
                    "WHERE event_id=NEW.event_id; END"
                )
                with self.assertRaises(RealChainStoreError):
                    store.record_attempt("ev.1", digest, "facade.0", "failure", NOW)
                self.assertEqual(before_state, store.connection.execute(
                    "SELECT state FROM real_chain_records WHERE event_id='ev.1'"
                ).fetchone()[0])
                self.assertEqual(before_count, store.connection.execute(
                    "SELECT COUNT(*) FROM real_chain_audit"
                ).fetchone()[0])
                store.close()

    def test_temp_trigger_and_operation_time_ddl_are_rejected_and_rolled_back(self) -> None:
        store = self.create()
        digest = self.add_event(store)
        store.connection.execute(
            "CREATE TEMP TRIGGER forged_temp AFTER INSERT ON real_chain_audit "
            "BEGIN UPDATE real_chain_records SET state='ESCALATED' "
            "WHERE event_id=NEW.event_id; END"
        )
        with self.assertRaises(RealChainStoreError):
            store.record_attempt("ev.1", digest, "facade.0", "failure", NOW)
        store.connection.execute("DROP TRIGGER forged_temp")
        before_count = store.connection.execute(
            "SELECT COUNT(*) FROM real_chain_audit"
        ).fetchone()[0]
        original_audit = store._audit

        def audit_then_inject(*args):
            original_audit(*args)
            store.connection.execute(
                "CREATE TRIGGER injected_during_write AFTER INSERT ON real_chain_audit "
                "BEGIN SELECT 1; END"
            )

        with patch.object(store, "_audit", side_effect=audit_then_inject):
            with self.assertRaises(RealChainStoreError):
                store.record_attempt("ev.1", digest, "facade.0", "failure", NOW)
        self.assertEqual(before_count, store.connection.execute(
            "SELECT COUNT(*) FROM real_chain_audit"
        ).fetchone()[0])
        self.assertIsNone(store.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='trigger' "
            "AND name='injected_during_write'"
        ).fetchone())
        store.close()

    def test_extra_table_view_and_index_are_rejected(self) -> None:
        statements = (
            "CREATE TABLE forged_table(value TEXT)",
            "CREATE VIEW forged_view AS SELECT event_id FROM real_chain_records",
            "CREATE INDEX forged_index ON real_chain_records(project_id)",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                store = self.create()
                store.connection.execute(statement)
                with self.assertRaises(RealChainStoreError):
                    _ = store.audit_entries
                store.close()

    def test_column_default_check_and_primary_key_ddl_changes_are_rejected(self) -> None:
        replacements = (
            ("event_digest TEXT NOT NULL", "event_digest BLOB NOT NULL"),
            ("held_snapshot TEXT NOT NULL DEFAULT ''", "held_snapshot TEXT NOT NULL DEFAULT 'x'"),
            ("CHECK(singleton=1)", "CHECK(singleton IN (1,2))"),
            ("event_id TEXT PRIMARY KEY", "event_id TEXT UNIQUE"),
        )
        for old, new in replacements:
            with self.subTest(change=(old, new)):
                path = self.path()
                store = self.create(path)
                store.close()
                connection = sqlite3.connect(path)
                table = "real_chain_metadata" if "singleton" in old else "real_chain_records"
                connection.execute("PRAGMA writable_schema=ON")
                connection.execute(
                    "UPDATE sqlite_master SET sql=replace(sql,?,?) WHERE type='table' AND name=?",
                    (old, new, table),
                )
                version = connection.execute("PRAGMA schema_version").fetchone()[0]
                connection.execute(f"PRAGMA schema_version={version + 1}")
                connection.execute("PRAGMA writable_schema=OFF")
                connection.commit()
                connection.close()
                with self.assertRaises(RealChainStoreError):
                    self.open(path)

    def test_legal_reopen_checkpoint_binds_schema_digest(self) -> None:
        path = self.path()
        store = self.create(path)
        expected = canonical_digest(store._schema_projection())
        head = json.loads(store.anchor.head.read_text(encoding="utf-8"))
        self.assertEqual(expected, head["checkpoint"]["schema_sha256"])
        store.close()
        reopened = self.open(path)
        self.assertEqual(expected, canonical_digest(reopened._schema_projection()))
        reopened.close()


if __name__ == "__main__":
    unittest.main()
