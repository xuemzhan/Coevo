"""Explicit domain event model (REVIEW2-8)."""

from .models import (
    DomainEvent,
    EventValidationError,
    event_order_key,
    validate_event_chain,
)

__all__ = [
    "DomainEvent",
    "EventValidationError",
    "event_order_key",
    "validate_event_chain",
]
