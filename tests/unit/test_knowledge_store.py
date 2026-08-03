"""Unit tests for US-14-AC-2 persistent knowledge bundle store."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from src.coevo.knowledge_base import (
    KnowledgeBaseFacade,
    KnowledgeBaseValidationError,
    KnowledgeBundle,
    KnowledgeStore,
    KnowledgeStoreConflictError,
    KnowledgeStoreError,
    bundle_to_payload,
    payload_to_bundle,
)


NOW = "2026-08-22T00:00:00Z"


def _bundle() -> KnowledgeBundle:
    return KnowledgeBaseFacade.aggregate(
        project_id="PRJ001",
        baseline={
            "title": "PRJ001 baseline",
            "summary": "initial baseline summary",
            "stages": ["plan", "execute", "review"],
            "work_packages": ["wp.1", "wp.2"],
        },
        merge_records=({"id": "mr.1", "title": "merge wp.1", "summary": "merged"},),
        risk_reports=(
            {"id": "r.1", "kind": "DEADLINE_OVERRUN", "recommendation": "add buffer"},
        ),
        meeting_conclusions=({"id": "mc.1", "title": "align on X"},),
        decision_briefs=(),
        progress_captures=(),
        model_summaries=({"id": "ms.1", "title": "LLM summary"},),
        now=NOW,
    )


class PayloadRoundTripTests(unittest.TestCase):
    def test_round_trip_preserves_bundle(self):
        bundle = _bundle()
        decoded = payload_to_bundle(bundle_to_payload(bundle))
        self.assertEqual(bundle, decoded)

    def test_unknown_type_marker_is_rejected(self):
        payload = bundle_to_payload(_bundle())
        data = json.loads(payload)
        data["bundle"]["$type"] = "Bogus"
        with self.assertRaises(KnowledgeBaseValidationError):
            payload_to_bundle(json.dumps(data))

    def test_unknown_field_is_rejected(self):
        payload = bundle_to_payload(_bundle())
        data = json.loads(payload)
        data["bundle"]["v"]["surprise"] = 1
        with self.assertRaises(KnowledgeBaseValidationError):
            payload_to_bundle(json.dumps(data))

    def test_invalid_enum_value_is_rejected(self):
        payload = bundle_to_payload(_bundle())
        data = json.loads(payload)
        bundle = data["bundle"]["v"]
        bundle["bundle_classification"] = {"$enum": "KnowledgeClassification", "v": "top_secret"}
        with self.assertRaises(KnowledgeBaseValidationError):
            payload_to_bundle(json.dumps(data))

    def test_invalid_top_level_fields_are_rejected(self):
        with self.assertRaises(KnowledgeBaseValidationError):
            payload_to_bundle('{"schema_version":"1.0"}')
        with self.assertRaises(KnowledgeBaseValidationError):
            payload_to_bundle('{"schema_version":"2.0","bundle":{}}')
        with self.assertRaises(KnowledgeBaseValidationError):
            payload_to_bundle("{not json")


class KnowledgeStoreTests(unittest.TestCase):
    def _store_path(self, tmp: str) -> Path:
        return Path(tmp) / "kb" / "store.db"

    def test_create_save_reopen_load_round_trip(self):
        bundle = _bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            store.save(bundle, now=NOW)
            store.close()

            reopened = KnowledgeStore.open(path)
            try:
                loaded = reopened.load(bundle.bundle_id)
                self.assertEqual(bundle, loaded)
                self.assertTrue(reopened.verify_audit_chain())
            finally:
                reopened.close()

    def test_save_is_idempotent_on_identical_digest(self):
        bundle = _bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            try:
                first = store.save(bundle, now=NOW)
                second = store.save(bundle, now=NOW)
                self.assertEqual("false", first["idempotent"])
                self.assertEqual("true", second["idempotent"])
                self.assertEqual(1, len(store.list_by_project("PRJ001")))
            finally:
                store.close()

    def test_same_id_different_digest_is_rejected(self):
        bundle = _bundle()
        altered = replace(
            bundle,
            committed_at="2026-08-22T00:05:00Z",
            committed_by="USR001",
            formally_committed=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            try:
                store.save(bundle, now=NOW)
                with self.assertRaises(KnowledgeStoreConflictError):
                    store.save(altered, now=NOW)
            finally:
                store.close()

    def test_load_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            try:
                self.assertIsNone(store.load("kb.missing"))
            finally:
                store.close()

    def test_corrupt_payload_is_rejected_on_load(self):
        bundle = _bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            store.save(bundle, now=NOW)
            store.close()

            connection = sqlite3.connect(str(path))
            connection.execute("UPDATE bundles SET payload = '{broken'")
            connection.commit()
            connection.close()

            reopened = KnowledgeStore.open(path)
            try:
                with self.assertRaises(KnowledgeStoreError):
                    reopened.load(bundle.bundle_id)
            finally:
                reopened.close()

    def test_schema_digest_tamper_is_rejected_on_open(self):
        bundle = _bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            store.save(bundle, now=NOW)
            store.close()
            connection = sqlite3.connect(str(path))
            connection.execute("UPDATE meta SET value = 'deadbeef' WHERE key = 'schema_sha256'")
            connection.commit()
            connection.close()
            with self.assertRaises(KnowledgeStoreError):
                KnowledgeStore.open(path)

    def test_extra_table_is_rejected_on_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            store.close()
            connection = sqlite3.connect(str(path))
            connection.execute("CREATE TABLE sneaky (id TEXT PRIMARY KEY)")
            connection.commit()
            connection.close()
            with self.assertRaises(KnowledgeStoreError):
                KnowledgeStore.open(path)

    def test_ddl_drift_is_rejected_on_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            store.close()
            connection = sqlite3.connect(str(path))
            connection.execute("ALTER TABLE bundles ADD COLUMN extra TEXT")
            connection.commit()
            connection.close()
            with self.assertRaises(KnowledgeStoreError):
                KnowledgeStore.open(path)

    def test_audit_chain_detects_tampering(self):
        bundle = _bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            store.save(bundle, now=NOW)
            store.close()
            connection = sqlite3.connect(str(path))
            connection.execute("UPDATE audit SET digest = '0' * 64")
            connection.commit()
            connection.close()
            with self.assertRaises(KnowledgeStoreError):
                KnowledgeStore.open(path)

    def test_create_existing_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            KnowledgeStore.create(path).close()
            with self.assertRaises(KnowledgeStoreError):
                KnowledgeStore.create(path)

    def test_open_missing_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(KnowledgeStoreError):
                KnowledgeStore.open(Path(tmp) / "absent.db")

    def test_list_by_project_returns_metadata(self):
        bundle = _bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._store_path(tmp)
            store = KnowledgeStore.create(path)
            try:
                store.save(bundle, now=NOW)
                rows = store.list_by_project("PRJ001")
                self.assertEqual(1, len(rows))
                self.assertEqual(bundle.bundle_id, rows[0]["bundle_id"])
                self.assertEqual("false", rows[0]["committed"])
                self.assertEqual(0, len(store.list_by_project("OTHER")))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
