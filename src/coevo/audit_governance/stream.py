"""US-15-AC-2 real-time audit stream (push notifications / subscriptions).

An in-process publish/subscribe hub for :class:`AuditEvent`:

* subscribers register with a caller-supplied callback (push) and an
  optional per-subscriber filter; each subscription also keeps a bounded
  buffer for pull-style consumption;
* delivery is fail-isolated: a failing subscriber callback never blocks
  or raises into the publisher, and never affects other subscribers;
* buffers are bounded: on overflow the oldest buffered event is dropped
  and ``dropped`` is incremented -- drops are never silent;
* the hub keeps a bounded recent-event history for late readers;
* subscriptions are bounded, validated (actor safe-id, callback
  callable, positive queue size), and track their owner for audit
  governance.

The hub is in-memory: durable persistence remains the responsibility of
the existing audit-chain stores; this slice is the real-time channel.
No new dependency; Python stdlib only.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-15-AC-2 审计流：订阅/发布/重放内存历史，fail-isolated 投递；
# 持久化委托 AuditStreamStore。
from __future__ import annotations

import threading
import uuid
from collections import deque
from typing import Any, Callable, Final

from . import (
    AuditEvent,
    AuditEventValidationError,
    AuditGovernanceError,
)
from .stream_store import AuditStreamStore, AuditStreamStoreError


from src.coevo.ids import SAFE_ID as _SAFE_ID
_SUB_ID_PREFIX: Final[str] = "as-"

DEFAULT_MAX_QUEUED: int = 64
DEFAULT_MAX_SUBSCRIBERS: int = 64
DEFAULT_HISTORY_LEN: int = 256


class AuditStreamError(AuditGovernanceError):
    """Base class for audit stream failures (fail-closed by default)."""


class AuditSubscription:
    """A single auditor subscription with push callback + bounded buffer."""

    def __init__(
        self,
        subscription_id: str,
        actor: str,
        callback: Callable[[AuditEvent], None],
        event_filter: Callable[[AuditEvent], bool] | None,
        max_queued: int,
        hub: "AuditStreamHub",
    ) -> None:
        self.subscription_id = subscription_id
        self.actor = actor
        self._callback = callback
        self._event_filter = event_filter
        self._max_queued = max_queued
        self._hub = hub
        self._buffer: deque[AuditEvent] = deque(maxlen=max_queued)
        self._dropped = 0
        self._callback_errors = 0
        self._active = True
        self._lock = threading.Lock()

    @property
    def active(self) -> bool:
        return self._active

    @property
    def dropped(self) -> int:
        with self._lock:
            return self._dropped

    @property
    def callback_errors(self) -> int:
        with self._lock:
            return self._callback_errors

    @property
    def pending_count(self) -> int:
        with self._lock:
            return len(self._buffer)

    def matches(self, event: AuditEvent) -> bool:
        return self._event_filter is None or bool(self._event_filter(event))

    def deliver(self, event: AuditEvent) -> None:
        """Invoke the push callback and buffer the event (fail-isolated)."""
        try:
            self._callback(event)
        except Exception:  # noqa: BLE001 - one bad subscriber never breaks the stream
            with self._lock:
                self._callback_errors += 1
        with self._lock:
            if not self._active:
                return
            if len(self._buffer) == self._max_queued:
                self._buffer.popleft()
                self._dropped += 1
            self._buffer.append(event)

    def drain(self) -> tuple[AuditEvent, ...]:
        """Return and clear the buffered events (pull-style consumption)."""
        with self._lock:
            pending = tuple(self._buffer)
            self._buffer.clear()
            return pending

    def unsubscribe(self) -> None:
        """Deactivate this subscription (idempotent)."""
        self._hub.unsubscribe(self)

    def _deactivate(self) -> None:
        with self._lock:
            self._active = False
            self._buffer.clear()


class AuditStreamHub:
    """Thread-safe publish/subscribe hub for audit events."""

    def __init__(
        self,
        *,
        max_subscribers: int = DEFAULT_MAX_SUBSCRIBERS,
        history_len: int = DEFAULT_HISTORY_LEN,
        store: AuditStreamStore | None = None,
        authorizer: Any | None = None,
    ) -> None:
        if not isinstance(max_subscribers, int) or max_subscribers < 1:
            raise AuditStreamError("max_subscribers must be a positive integer")
        if not isinstance(history_len, int) or history_len < 1:
            raise AuditStreamError("history_len must be a positive integer")
        self._max_subscribers = max_subscribers
        self._lock = threading.RLock()
        self._subscriptions: dict[str, AuditSubscription] = {}
        self._history: deque[AuditEvent] = deque(maxlen=history_len)
        self._event_count = 0
        self._store = store
        self._authorizer = authorizer

    @property
    def subscriber_count(self) -> int:
        with self._lock:
            return len(self._subscriptions)

    @property
    def event_count(self) -> int:
        with self._lock:
            return self._event_count

    def subscribe(
        self,
        actor: str,
        callback: Callable[[AuditEvent], None],
        *,
        event_filter: Callable[[AuditEvent], bool] | None = None,
        max_queued: int = DEFAULT_MAX_QUEUED,
        permission: str = "audit:subscribe",
        replay: bool = False,
    ) -> AuditSubscription:
        """Register a subscriber; returns a handle to unsubscribe/drain."""
        if not isinstance(actor, str) or not _SAFE_ID.match(actor):
            raise AuditEventValidationError("actor must be a safe-id")
        if self._authorizer is not None:
            is_allowed = getattr(self._authorizer, "is_allowed", None)
            if not callable(is_allowed):
                raise AuditStreamError("authorizer must implement is_allowed")
            if not is_allowed(actor, permission):
                raise AuditStreamError(
                    f"subscription denied: {actor!r} lacks {permission!r}"
                )
        if not callable(callback):
            raise AuditEventValidationError("callback must be callable")
        if event_filter is not None and not callable(event_filter):
            raise AuditEventValidationError("event_filter must be callable or None")
        if not isinstance(max_queued, int) or max_queued < 1:
            raise AuditEventValidationError("max_queued must be a positive integer")
        with self._lock:
            if len(self._subscriptions) >= self._max_subscribers:
                raise AuditStreamError("audit stream subscriber limit reached")
            subscription = AuditSubscription(
                f"{_SUB_ID_PREFIX}{uuid.uuid4().hex}",
                actor,
                callback,
                event_filter,
                max_queued,
                self,
            )
            self._subscriptions[subscription.subscription_id] = subscription
        if replay and self._store is not None:
            for event in self._store.events():
                if subscription.matches(event):
                    subscription.deliver(event)
        return subscription

    def unsubscribe(self, subscription: AuditSubscription) -> None:
        """Deactivate and remove a subscription (idempotent)."""
        if not isinstance(subscription, AuditSubscription):
            raise AuditEventValidationError("subscription must be an AuditSubscription")
        with self._lock:
            existing = self._subscriptions.get(subscription.subscription_id)
            if existing is None or existing is not subscription:
                return
            del self._subscriptions[subscription.subscription_id]
            subscription._deactivate()

    def publish(self, event: AuditEvent) -> None:
        """Deliver an event to every matching subscriber (fail-isolated)."""
        if not isinstance(event, AuditEvent):
            raise AuditEventValidationError("publish requires an AuditEvent")
        if self._store is not None:
            try:
                self._store.append(event)
            except AuditStreamStoreError as exc:
                raise AuditStreamError(
                    f"audit stream persistence failed ({exc})"
                ) from exc
        with self._lock:
            subscribers = tuple(self._subscriptions.values())
            self._history.append(event)
            self._event_count += 1
        for subscription in subscribers:
            if subscription.active and subscription.matches(event):
                subscription.deliver(event)

    def recent_events(self, limit: int = DEFAULT_HISTORY_LEN) -> tuple[AuditEvent, ...]:
        """Return the most recent published events (newest last)."""
        if not isinstance(limit, int) or limit < 1:
            raise AuditStreamError("limit must be a positive integer")
        with self._lock:
            return tuple(self._history)[-limit:]
