"""Unit tests for US-15-AC-2 real-time audit stream."""
from __future__ import annotations

import unittest

from src.coevo.audit_governance import (
    AuditEvent,
    AuditEventResult,
    AuditEventSource,
    AuditEventValidationError,
    AuditStreamError,
    AuditStreamHub,
)


NOW = "2026-08-22T00:00:00Z"
NOW2 = "2026-08-22T00:01:00Z"


def _event(
    *,
    action: str = "import",
    actor: str = "u.alice",
    project_id: str = "PRJ001",
    ts: str = NOW,
) -> AuditEvent:
    return AuditEvent(
        ts=ts,
        actor=actor,
        source=AuditEventSource.IMPORT,
        action=action,
        project_id=project_id,
        task_id="",
        result=AuditEventResult.OK,
        tool="PackageImportService",
    )


def _collector() -> tuple[list[AuditEvent], object]:
    received: list[AuditEvent] = []

    def callback(event: AuditEvent) -> None:
        received.append(event)

    return received, callback


class AuditStreamHubTests(unittest.TestCase):
    def test_push_delivery_to_all_subscribers(self):
        hub = AuditStreamHub()
        first, cb1 = _collector()
        second, cb2 = _collector()
        sub1 = hub.subscribe("u.auditor", cb1)
        sub2 = hub.subscribe("u.auditor2", cb2)
        event = _event()
        hub.publish(event)
        self.assertEqual([event], first)
        self.assertEqual([event], second)
        self.assertEqual(1, hub.event_count)
        self.assertEqual(2, hub.subscriber_count)
        sub1.unsubscribe()
        self.assertEqual(1, hub.subscriber_count)

    def test_filter_limits_delivery(self):
        hub = AuditStreamHub()
        received, callback = _collector()
        hub.subscribe(
            "u.auditor",
            callback,
            event_filter=lambda event: event.action == "merge",
        )
        hub.publish(_event(action="import"))
        hub.publish(_event(action="merge"))
        self.assertEqual(["merge"], [event.action for event in received])

    def test_unsubscribe_stops_delivery(self):
        hub = AuditStreamHub()
        received, callback = _collector()
        subscription = hub.subscribe("u.auditor", callback)
        hub.publish(_event())
        subscription.unsubscribe()
        hub.publish(_event(ts=NOW2))
        self.assertEqual(1, len(received))
        self.assertFalse(subscription.active)

    def test_bounded_buffer_tracks_drops(self):
        hub = AuditStreamHub()
        received, callback = _collector()
        subscription = hub.subscribe("u.auditor", callback, max_queued=2)
        events = [_event(action=f"a{index}") for index in range(5)]
        for event in events:
            hub.publish(event)
        self.assertEqual(5, len(received))  # push never misses
        self.assertEqual(2, subscription.pending_count)
        self.assertGreaterEqual(subscription.dropped, 3)
        drained = subscription.drain()
        self.assertEqual(2, len(drained))
        self.assertEqual(0, subscription.pending_count)

    def test_failing_callback_is_isolated(self):
        hub = AuditStreamHub()
        received, good_callback = _collector()

        def broken_callback(event: AuditEvent) -> None:
            raise RuntimeError("boom")

        bad = hub.subscribe("u.bad", broken_callback)
        good = hub.subscribe("u.good", good_callback)
        hub.publish(_event())
        self.assertEqual(1, len(received))
        self.assertEqual(1, bad.callback_errors)
        self.assertEqual(0, good.callback_errors)

    def test_recent_events_history_is_bounded(self):
        hub = AuditStreamHub(history_len=3)
        for index in range(5):
            hub.publish(_event(action=f"a{index}"))
        recent = hub.recent_events()
        self.assertEqual(3, len(recent))
        self.assertEqual(["a2", "a3", "a4"], [event.action for event in recent])
        self.assertEqual(5, hub.event_count)

    def test_invalid_subscription_arguments_are_rejected(self):
        hub = AuditStreamHub()
        with self.assertRaises(AuditEventValidationError):
            hub.subscribe("bad actor!", lambda event: None)
        with self.assertRaises(AuditEventValidationError):
            hub.subscribe("u.auditor", "not callable")  # type: ignore[arg-type]
        with self.assertRaises(AuditEventValidationError):
            hub.subscribe("u.auditor", lambda event: None, max_queued=0)
        with self.assertRaises(AuditEventValidationError):
            hub.subscribe(
                "u.auditor",
                lambda event: None,
                event_filter="not callable",  # type: ignore[arg-type]
            )

    def test_publish_rejects_non_audit_event(self):
        hub = AuditStreamHub()
        with self.assertRaises(AuditEventValidationError):
            hub.publish({"not": "an event"})  # type: ignore[arg-type]

    def test_subscriber_limit_is_enforced(self):
        hub = AuditStreamHub(max_subscribers=2)
        hub.subscribe("u.a", lambda event: None)
        hub.subscribe("u.b", lambda event: None)
        with self.assertRaises(AuditStreamError):
            hub.subscribe("u.c", lambda event: None)

    def test_invalid_hub_arguments_are_rejected(self):
        with self.assertRaises(AuditStreamError):
            AuditStreamHub(max_subscribers=0)
        with self.assertRaises(AuditStreamError):
            AuditStreamHub(history_len=0)


if __name__ == "__main__":
    unittest.main()
