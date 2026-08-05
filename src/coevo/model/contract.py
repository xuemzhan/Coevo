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
from typing import Protocol, runtime_checkable


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


__all__ = [
    "ModelError",
    "ModelProvider",
    "ModelUnavailableError",
    "ModelValidationError",
    "NullModelProvider",
    "parse_json_object",
]
