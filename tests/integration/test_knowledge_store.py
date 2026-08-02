"""Integration tests for US-14-AC-2 persistent knowledge store."""
from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from src.coevo.knowledge_base import (
    KnowledgeBaseFacade,
    KnowledgeBundle,
    KnowledgeStore,
    KnowledgeStoreConflictError,
    KnowledgeStoreError,
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


class KnowledgeStoreLifecycleTests(unittest.TestCase):
    def test_full_persistence_lifecycle(self):
        bundle = _bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "knowledge.db"
            store = KnowledgeStore.create(path)
            receipt = store.save(bundle, now=NOW)
            self.assertEqual(bundle.bundle_id, receipt["bundle_id"])
            self.assertEqual("false", receipt["idempotent"])
            self.assertTrue(store.verify_audit_chain())
            store.close()

            reopened = KnowledgeStore.open(path)
            try:
                loaded = reopened.load(bundle.bundle_id)
                self.assertEqual(bundle, loaded)
                self.assertEqual(1, len(reopened.list_by_project("PRJ001")))
                self.assertTrue(reopened.verify_audit_chain())
                # Idempotent re-save after reopen
                again = reopened.save(bundle, now=NOW)
                self.assertEqual("true", again["idempotent"])
            finally:
                reopened.close()

    def test_conflicting_bundle_is_rejected(self):
        bundle = _bundle()
        altered = replace(
            bundle,
            committed_at="2026-08-22T00:05:00Z",
            committed_by="USR001",
            formally_committed=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "knowledge.db"
            store = KnowledgeStore.create(path)
            try:
                store.save(bundle, now=NOW)
                with self.assertRaises(KnowledgeStoreConflictError):
                    store.save(altered, now=NOW)
            finally:
                store.close()

    def test_corrupt_database_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "knowledge.db"
            path.write_bytes(b"this is not a sqlite database")
            with self.assertRaises(KnowledgeStoreError):
                KnowledgeStore.open(path)

    def test_multiple_bundles_per_project(self):
        bundle = _bundle()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "knowledge.db"
            store = KnowledgeStore.create(path)
            try:
                store.save(bundle, now=NOW)
                rows = store.list_by_project("PRJ001")
                self.assertEqual(1, len(rows))
                self.assertEqual(bundle.bundle_id, rows[0]["bundle_id"])
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
