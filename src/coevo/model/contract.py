"""Unified model-adapter contract (mandatory constraint 9.2).

The business layer MUST NOT bind to a single vendor: everything goes
through :class:`ModelProvider`. Providers are replaceable and the
default is offline (``NullModelProvider`` raises
:class:`ModelUnavailableError`), so every quality gate stays green
without a network or an API key.

Model output is **never** a formal state: callers consume it as a
draft suggestion and route it through the existing human-confirmation
boundaries (see ``task_decomposition.agent``).
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 统一模型适配器契约（强制约束 9.2）：NullModelProvider 离线兜底。
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Mapping
from typing import Protocol, runtime_checkable

from src.coevo.timefmt import is_iso_utc_z


class ModelError(Exception):
    """Base class for model-adapter failures (fail-closed)."""


class ModelUnavailableError(ModelError):
    """No provider configured / no API key / offline mode."""


class ModelValidationError(ModelError):
    """The provider response is malformed, oversized or out of schema."""


@runtime_checkable
class ModelProvider(Protocol):
    """A single replaceable chat-completion provider."""

    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int,
        timeout_seconds: float,
    ) -> str:
        """Return the assistant message content, fail-closed on errors."""
        ...


class NullModelProvider:
    """Offline default: always unavailable (gates never touch a network)."""

    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int,
        timeout_seconds: float,
    ) -> str:
        """Complete a model request with a provider."""
        raise ModelUnavailableError(
            "no model provider configured (offline mode)"
        )


def parse_json_object(text: str, *, max_bytes: int) -> dict[str, object]:
    """Parse a bounded JSON object from a provider response, fail-closed."""
    if not isinstance(text, str) or not text.strip():
        raise ModelValidationError("model response is empty")
    encoded = text.encode("utf-8")
    if len(encoded) > max_bytes:
        raise ModelValidationError(
            f"model response exceeds {max_bytes} bytes"
        )
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ModelValidationError("model response is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ModelValidationError("model response must be a JSON object")
    return parsed


@dataclass(frozen=True)
class SuggestionEvidence:
    """A traceable reference supporting a draft suggestion (REVIEW2-7)."""

    kind: str
    source: str
    digest: str

    def __post_init__(self) -> None:
        for label, value in (
            ("kind", self.kind),
            ("source", self.source),
            ("digest", self.digest),
        ):
            if not isinstance(value, str) or not value:
                raise ModelValidationError(
                    f"evidence.{label} must be a non-empty string"
                )


@dataclass(frozen=True)
class DraftSuggestion:
    """The ONLY shape a model output may enter the business layer as.

    A draft is never formal state: it must be routed through a
    human-confirmation boundary before any state write. ``requires_
    confirmation`` defaults to True and cannot be silently disabled
    (REVIEW2-7).
    """

    source: str
    content: Mapping[str, object]
    evidence: tuple[SuggestionEvidence, ...] = ()
    confidence: float = 0.0
    requires_confirmation: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source:
            raise ModelValidationError("source must be a non-empty string")
        if not isinstance(self.content, Mapping):
            raise ModelValidationError("content must be a mapping")
        if not isinstance(self.confidence, (int, float)) or isinstance(
            self.confidence, bool
        ):
            raise ModelValidationError("confidence must be a float")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ModelValidationError(
                f"confidence must be within [0, 1]; got {self.confidence!r}"
            )
        if not isinstance(self.requires_confirmation, bool):
            raise ModelValidationError("requires_confirmation must be a bool")


@dataclass(frozen=True)
class ConfirmedStateChange:
    """The ONLY shape a formal state write API may accept (REVIEW2-7).

    Carries the human authorisation (who/when), the originating draft and
    the exact field changes. Raw dicts and unconfirmed drafts are rejected
    by :func:`ensure_confirmed_state_change`.
    """

    confirmed_by: str
    confirmed_at: str
    source_draft_id: str
    changes: Mapping[str, object]

    def __post_init__(self) -> None:
        for label, value in (
            ("confirmed_by", self.confirmed_by),
            ("confirmed_at", self.confirmed_at),
            ("source_draft_id", self.source_draft_id),
        ):
            if not isinstance(value, str) or not value:
                raise ModelValidationError(
                    f"{label} must be a non-empty string"
                )
        if not is_iso_utc_z(self.confirmed_at):
            raise ModelValidationError(
                "confirmed_at must be ISO-8601 UTC with trailing Z"
            )
        if not isinstance(self.changes, Mapping) or not self.changes:
            raise ModelValidationError(
                "changes must be a non-empty mapping"
            )


def ensure_confirmed_state_change(change: object) -> ConfirmedStateChange:
    """Fail-closed guard: only ConfirmedStateChange may reach a state write.

    Rejects raw dicts and unconfirmed :class:`DraftSuggestion` objects so a
    model output can never bypass the human-confirmation boundary
    (REVIEW2-7).
    """

    if not isinstance(change, ConfirmedStateChange):
        raise ModelValidationError(
            "formal state writes require a ConfirmedStateChange; "
            f"got {type(change).__name__}"
        )
    # Re-validate so a tampered/incorrectly-constructed instance fails closed.
    return ConfirmedStateChange(
        confirmed_by=change.confirmed_by,
        confirmed_at=change.confirmed_at,
        source_draft_id=change.source_draft_id,
        changes=dict(change.changes),
    )


__all__ = [
    "ConfirmedStateChange",
    "DraftSuggestion",
    "ModelError",
    "ModelProvider",
    "ModelUnavailableError",
    "ModelValidationError",
    "NullModelProvider",
    "SuggestionEvidence",
    "ensure_confirmed_state_change",
    "parse_json_object",
]
