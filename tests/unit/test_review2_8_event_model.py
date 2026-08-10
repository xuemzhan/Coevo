"""REVIEW2-8: explicit domain event model guard tests.

Contract (docs/architecture/event-model.md):

* ordering within an aggregate is the strictly increasing
  client_sequence -- created_at is metadata only and never orders events;
* causation_id must reference a preceding event (no self / no cycle);
* duplicate event_ids, unknown causation and non-strict sequences are
  rejected fail-closed.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.events import (
    DomainEvent,
    EventValidationError,
    event_order_key,
    validate_event_chain,
)

ROOT = Path(__file__).resolve().parents[2]


def _event(
    event_id: str,
    *,
    aggregate_id: str = "agg.1",
    client_sequence: int = 1,
    created_at: str = "2026-08-10T00:00:00Z",
    causation_id: str = "",
) -> DomainEvent:
    return DomainEvent(
        event_id=event_id,
        aggregate_id=aggregate_id,
        aggregate_type="task",
        base_revision="PRJ001-R0001",
        actor="u.pm",
        operation="update",
        payload={"field": "status"},
        created_at=created_at,
        client_sequence=client_sequence,
        correlation_id="corr.1",
        causation_id=causation_id,
    )


class EventModelTests(unittest.TestCase):
    def test_construction_validates_fail_closed(self) -> None:
        with self.assertRaises(EventValidationError):
            _event("bad id!").event_id  # noqa: B018
        with self.assertRaises(EventValidationError):
            DomainEvent(
                event_id="ev.1",
                aggregate_id="agg.1",
                aggregate_type="task",
                base_revision="PRJ001-R0001",
                actor="u.pm",
                operation="update",
                payload={},
                created_at="2026-08-10T00:00:00",  # no trailing Z
                client_sequence=1,
            )
        with self.assertRaises(EventValidationError):
            DomainEvent(
                event_id="ev.1",
                aggregate_id="agg.1",
                aggregate_type="task",
                base_revision="PRJ001-R0001",
                actor="u.pm",
                operation="update",
                payload={},
                created_at="2026-08-10T00:00:00Z",
                client_sequence=-1,
            )

    def test_ordering_uses_client_sequence_not_created_at(self) -> None:
        # created_at is reversed relative to the sequence: ordering must
        # still follow client_sequence (1 before 2).
        first = _event(
            "ev.1", client_sequence=1, created_at="2026-08-10T02:00:00Z"
        )
        second = _event(
            "ev.2", client_sequence=2, created_at="2026-08-10T01:00:00Z"
        )
        ordered = validate_event_chain((second, first))
        self.assertEqual(
            [event.event_id for event in ordered],
            ["ev.1", "ev.2"],
        )
        self.assertEqual(event_order_key(first), ("agg.1", 1))

    def test_duplicate_event_id_rejected(self) -> None:
        with self.assertRaises(EventValidationError):
            validate_event_chain((_event("ev.1"), _event("ev.1")))

    def test_non_strict_sequence_rejected(self) -> None:
        with self.assertRaises(EventValidationError):
            validate_event_chain(
                (
                    _event("ev.1", client_sequence=1),
                    _event("ev.2", client_sequence=1),
                )
            )

    def test_out_of_order_arrival_is_reordered_by_sequence(self) -> None:
        # Out-of-order arrival (2 then 1) is valid: canonical ordering
        # re-sequences by client_sequence, not by arrival or timestamps.
        ordered = validate_event_chain(
            (
                _event("ev.2", client_sequence=2),
                _event("ev.1", client_sequence=1),
            )
        )
        self.assertEqual(
            [event.event_id for event in ordered],
            ["ev.1", "ev.2"],
        )

    def test_causation_must_precede(self) -> None:
        good = validate_event_chain(
            (
                _event("ev.1", client_sequence=1),
                _event("ev.2", client_sequence=2, causation_id="ev.1"),
            )
        )
        self.assertEqual(len(good), 2)
        with self.assertRaises(EventValidationError):
            validate_event_chain(
                (
                    _event("ev.1", client_sequence=1),
                    _event("ev.2", client_sequence=2, causation_id="ev.2"),
                )
            )
        with self.assertRaises(EventValidationError):
            validate_event_chain(
                (
                    _event("ev.1", client_sequence=1),
                    _event("ev.2", client_sequence=2, causation_id="missing"),
                )
            )

    def test_causation_cycle_rejected(self) -> None:
        with self.assertRaises(EventValidationError):
            validate_event_chain(
                (
                    _event("ev.1", client_sequence=1, causation_id="ev.2"),
                    _event("ev.2", client_sequence=2, causation_id="ev.1"),
                )
            )

    def test_doc_exists(self) -> None:
        text = (ROOT / "docs" / "architecture" / "event-model.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("client_sequence", text)
        self.assertIn("causation_id", text)
        self.assertIn("created_at", text)


if __name__ == "__main__":
    unittest.main()
