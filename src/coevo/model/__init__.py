"""Unified model-adapter layer (mandatory constraint 9.2).

Business slices depend on :class:`ModelProvider`; vendors are selected
by environment and never hard-coded into business logic. The default
is offline (``NullModelProvider``), so gates never need a network.
"""
from __future__ import annotations

import os

from .contract import (
    ModelError,
    ModelProvider,
    ModelUnavailableError,
    ModelValidationError,
    NullModelProvider,
    parse_json_object,
)
from .deepseek import DeepSeekProvider


def select_provider() -> ModelProvider:
    """Select a provider from ``COEVO_LLM_PROVIDER`` (default offline)."""
    provider = os.environ.get("COEVO_LLM_PROVIDER", "").strip().lower()
    if provider in ("", "none", "offline"):
        return NullModelProvider()
    if provider == "deepseek":
        return DeepSeekProvider()
    raise ModelError(f"unsupported model provider {provider!r}")


__all__ = [
    "DeepSeekProvider",
    "ModelError",
    "ModelProvider",
    "ModelUnavailableError",
    "ModelValidationError",
    "NullModelProvider",
    "parse_json_object",
    "select_provider",
]
