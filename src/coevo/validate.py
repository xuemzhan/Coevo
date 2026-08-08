"""Shared model-input validation helpers (single source of truth).

``risk.models`` and ``supervision.models`` duplicated ``_non_empty`` with the
same message and different exception classes.  This leaf unifies the shared
pattern (FRAMEWORK-OPTIMIZE-18) using the ``error_factory`` convention so
each caller keeps its exact exception class and message (jsonutil pattern).
"""
from __future__ import annotations

from typing import Callable


def non_empty_string(
    value: object,
    *,
    error_factory: Callable[[str], Exception],
    field: str,
) -> None:
    """Raise ``error_factory(f"{field} must be a non-empty string")`` for
    non-string / empty / whitespace-only values (fail-closed)."""
    if not isinstance(value, str) or not value.strip():
        raise error_factory(f"{field} must be a non-empty string")


__all__ = ["non_empty_string"]
