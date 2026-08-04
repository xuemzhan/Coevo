"""Unit tests for the durable audit stream store."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.coevo.audit_governance import (
    AuditEvent,
    AuditEventResult,
    AuditEventSource,
    AuditStreamStore,
    AuditStreamStoreError,
    AuditStreamHub,
)


NOW = "2026-08-22T00:00:00Z"


def _event(action: str = "import") -> AuditEvent:
    return AuditEvent(
        ts=NOW,
        actor="u.alice",
        source=AuditEventSource.IMPORT,
        action=action,
        project_id="PRJ001",
        task_id="t.1",
        result=AuditEventResult.OK,
        tool="PackageImportService",
    )


class AuditStreamStoreTests(unittest.TestCase):
    def _path(self, tmp: str) -> Path:
        return Path(tmp) / "stream.jsonl"

    def test_create_append_reopen_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._path(tmp)
            store = AuditStreamStore.create(path)
            store.append(_event("a"))
            store.append(_event("b"))
            store.close()

            reopened = AuditStreamStore.open(path)
            try:
                self.assertTrue(reopened.verify_chain())
                events = reopened.events()
                self.assertEqual(["a", "b"], [event.action for event in events])
                self.assertEqual(_event("a"), events[0])
            finally:
                reopened.close()

    def test_open_rejects_tampered_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._path(tmp)
            store = AuditStreamStore.create(path)
            store.append(_event("a"))
            store.append(_event("b"))
            store.close()
            text = path.read_text(encoding="utf-8")
            tampered = text.replace('"action":"publish"', '"action":"tampered"', 1)
            path.write_text(tampered, encoding="utf-8")
            with self.assertRaises(AuditStreamStoreError):
                AuditStreamStore.open(path)

    def test_verify_chain_detects_payload_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._path(tmp)
            store = AuditStreamStore.create(path)
            store.append(_event("a"))
            store.append(_event("b"))
            store.close()
            text = path.read_text(encoding="utf-8")
            tampered = text.replace('"t.1"', '"t.9"', 1)
            path.write_text(tampered, encoding="utf-8")
            with self.assertRaises(AuditStreamStoreError):
                AuditStreamStore.open(path)

    def test_size_cap_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._path(tmp)
            store = AuditStreamStore.create(path, max_bytes=512)
            with self.assertRaises(AuditStreamStoreError):
                for _ in range(50):
                    store.append(_event(f"event-{_}-" * 10))
            store.close()

    def test_tracked_size_stays_in_sync_with_disk(self):
        # 回归：增量维护的 _size 必须始终等于磁盘真实字节数，
        # 保证大小上限判定与 stat() 语义一致。
        with tempfile.TemporaryDirectory() as tmp:
            path = self._path(tmp)
            store = AuditStreamStore.create(path)
            try:
                self.assertEqual(path.stat().st_size, store._size)
                for index in range(20):
                    store.append(_event(f"sync-{index}"))
                    self.assertEqual(path.stat().st_size, store._size)
            finally:
                store.close()

    def test_store_backs_hub_persistence_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._path(tmp)
            store = AuditStreamStore.create(path)
            hub = AuditStreamHub(store=store)
            hub.publish(_event("one"))
            hub.publish(_event("two"))
            store.close()

            reopened = AuditStreamStore.open(path)
            second = AuditStreamHub(store=reopened)
            replayed: list[AuditEvent] = []
            second.subscribe("u.auditor", replayed.append, replay=True)
            self.assertEqual(["one", "two"], [event.action for event in replayed])
            reopened.close()


if __name__ == "__main__":
    unittest.main()
