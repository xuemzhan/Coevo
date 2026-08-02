"""Integration tests for US-15-AC-2 real-time audit stream."""
from __future__ import annotations

import threading
import unittest

from src.coevo.audit_governance import (
    AuditEvent,
    AuditEventResult,
    AuditEventSource,
    AuditEventValidationError,
    AuditStreamHub,
)


NOW = "2026-08-22T00:00:00Z"


def _record(**overrides) -> dict:
    base = {
        "ts": NOW,
        "actor": "u.alice",
        "action": "import",
        "result": "ok",
        "project_id": "PRJ001",
        "task_id": "t.1",
        "tool": "PackageImportService",
    }
    base.update(overrides)
    return base


class AuditStreamIntegrationTests(unittest.TestCase):
    def test_from_audit_record_to_subscriber_push(self):
        hub = AuditStreamHub()
        received: list[AuditEvent] = []
        hub.subscribe("u.auditor", received.append)
        event = AuditEvent.from_audit_record(
            _record(action="package.intercept", result="blocked"),
            source=AuditEventSource.VERIFY,
        )
        hub.publish(event)
        self.assertEqual(1, len(received))
        delivered = received[0]
        self.assertEqual(event, delivered)
        self.assertEqual("package.intercept", delivered.action)
        self.assertIs(AuditEventResult.BLOCKED, delivered.result)
        self.assertIs(AuditEventSource.VERIFY, delivered.source)
        self.assertEqual("PRJ001", delivered.project_id)

    def test_subscriber_can_filter_by_source_and_result(self):
        hub = AuditStreamHub()
        received: list[AuditEvent] = []
        hub.subscribe(
            "u.auditor",
            received.append,
            event_filter=lambda event: (
                event.source == AuditEventSource.REPLAY
                and event.result == AuditEventResult.BLOCKED
            ),
        )
        hub.publish(
            AuditEvent.from_audit_record(
                _record(action="replay.import", result="blocked"),
                source=AuditEventSource.REPLAY,
            )
        )
        hub.publish(
            AuditEvent.from_audit_record(
                _record(action="merge.accept", result="ok"),
                source=AuditEventSource.MERGE,
            )
        )
        self.assertEqual(1, len(received))
        self.assertEqual("replay.import", received[0].action)

    def test_concurrent_publishers_deliver_all_events(self):
        hub = AuditStreamHub()
        received: list[AuditEvent] = []
        lock = threading.Lock()

        def collect(event: AuditEvent) -> None:
            with lock:
                received.append(event)

        hub.subscribe("u.auditor", collect)

        def publisher(start: int) -> None:
            for index in range(25):
                hub.publish(
                    AuditEvent.from_audit_record(
                        _record(
                            ts="2026-08-22T00:00:00Z",
                            action=f"thread.{start}.{index}",
                            result="ok",
                        ),
                        source=AuditEventSource.STATE,
                    )
                )

        threads = [threading.Thread(target=publisher, args=(i,)) for i in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
        self.assertEqual(100, hub.event_count)
        self.assertEqual(100, len(received))
        self.assertEqual(100, len(hub.recent_events()))

    def test_publish_rejects_non_audit_event(self):
        hub = AuditStreamHub()
        with self.assertRaises(AuditEventValidationError):
            hub.publish(_record())  # type: ignore[arg-type]

    def test_subscription_requires_safe_actor(self):
        hub = AuditStreamHub()
        with self.assertRaises(AuditEventValidationError):
            hub.subscribe("not safe", lambda event: None)


if __name__ == "__main__":
    unittest.main()
