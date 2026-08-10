"""Explicit domain event model (REVIEW2-8).

Offline-sync ordering must NEVER rely on wall-clock timestamps or file
system mtimes. This module defines the unified event shape and the
canonical ordering rule:

* within an aggregate, order is the strictly increasing
  ``client_sequence`` (per-writer counter);
* ``created_at`` is metadata only -- it never participates in ordering;
* ``causation_id`` must reference an event that precedes the current one
  in canonical order (acyclic by construction);
* ``correlation_id`` groups events belonging to one business unit.

Fail-closed: any unknown/duplicate/misordered/cyclic event set is rejected.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from src.coevo.ids import SAFE_ID
from src.coevo.timefmt import is_iso_utc_z


class EventValidationError(ValueError):
    """Raised when an event or event chain violates the model (fail-closed)."""


def _require_safe_id(value: str, label: str) -> None:
    if not isinstance(value, str) or not SAFE_ID.match(value):
        raise EventValidationError(f"{label} must be a safe-id; got {value!r}")


def _require_non_empty(value: str, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise EventValidationError(f"{label} must be a non-empty string")


@dataclass(frozen=True)
class DomainEvent:
    """The unified offline-sync event shape (REVIEW2-8)."""

    event_id: str
    aggregate_id: str
    aggregate_type: str
    base_revision: str
    actor: str
    operation: str
    payload: Mapping[str, object]
    created_at: str
    client_sequence: int
    correlation_id: str = ""
    causation_id: str = ""

    def __post_init__(self) -> None:
        _require_safe_id(self.event_id, "event_id")
        _require_safe_id(self.aggregate_id, "aggregate_id")
        _require_non_empty(self.aggregate_type, "aggregate_type")
        _require_non_empty(self.base_revision, "base_revision")
        _require_non_empty(self.actor, "actor")
        _require_non_empty(self.operation, "operation")
        if not isinstance(self.payload, Mapping):
            raise EventValidationError("payload must be a mapping")
        if not is_iso_utc_z(self.created_at):
            raise EventValidationError(
                "created_at must be ISO-8601 UTC with trailing Z "
                "(metadata only; never used for ordering)"
            )
        if (
            not isinstance(self.client_sequence, int)
            or isinstance(self.client_sequence, bool)
            or self.client_sequence < 0
        ):
            raise EventValidationError(
                "client_sequence must be a non-negative integer"
            )
        if self.correlation_id and not SAFE_ID.match(self.correlation_id):
            raise EventValidationError(
                f"correlation_id must be a safe-id; got {self.correlation_id!r}"
            )
        if self.causation_id and not SAFE_ID.match(self.causation_id):
            raise EventValidationError(
                f"causation_id must be a safe-id; got {self.causation_id!r}"
            )


def event_order_key(event: DomainEvent) -> tuple[str, int]:
    """Canonical ordering key: (aggregate_id, client_sequence).

    Wall-clock timestamps never participate (REVIEW2-8).
    """

    return (event.aggregate_id, event.client_sequence)


def validate_event_chain(
    events: Sequence[DomainEvent],
) -> tuple[DomainEvent, ...]:
    """Validate and canonically order an event set, fail-closed.

    Rules:
    * every member must be a :class:`DomainEvent`;
    * event_ids are unique;
    * within an aggregate, ``client_sequence`` is strictly increasing
      (created_at is ignored for ordering);
    * ``causation_id`` must reference an existing event that precedes
      the current event in canonical order (no self / no cycle).
    """

    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        raise EventValidationError("events must be a sequence of DomainEvent")
    ordered = sorted(events, key=event_order_key)
    seen_ids: set[str] = set()
    by_id: dict[str, DomainEvent] = {}
    for event in ordered:
        if not isinstance(event, DomainEvent):
            raise EventValidationError(
                f"chain member must be DomainEvent; got {type(event).__name__}"
            )
        if event.event_id in seen_ids:
            raise EventValidationError(
                f"duplicate event_id {event.event_id!r}"
            )
        seen_ids.add(event.event_id)
        by_id[event.event_id] = event
    position = {event.event_id: index for index, event in enumerate(ordered)}
    # Strictly increasing client_sequence per aggregate.
    previous: dict[str, int] = {}
    for event in ordered:
        last = previous.get(event.aggregate_id)
        if last is not None and event.client_sequence <= last:
            raise EventValidationError(
                f"aggregate {event.aggregate_id!r} client_sequence "
                f"{event.client_sequence} is not strictly increasing "
                f"(previous {last})"
            )
        previous[event.aggregate_id] = event.client_sequence
    # Causality must point strictly backwards in canonical order.
    for event in ordered:
        if not event.causation_id:
            continue
        cause = by_id.get(event.causation_id)
        if cause is None:
            raise EventValidationError(
                f"causation_id {event.causation_id!r} references an "
                "unknown event"
            )
        if position[cause.event_id] >= position[event.event_id]:
            raise EventValidationError(
                f"causation_id {event.causation_id!r} must precede "
                f"{event.event_id!r} in canonical order (self/cycle)"
            )
    return tuple(ordered)


__all__ = [
    "DomainEvent",
    "EventValidationError",
    "event_order_key",
    "validate_event_chain",
]
