"""Shared strict JSON parsing guards (FRAMEWORK-OPTIMIZE-14).

Dependency-free leaf module (stdlib only).  ``reject_duplicate_pairs`` is the
single repository-wide ``object_pairs_hook`` that fails closed on duplicate
JSON keys; callers inject their own ``error_factory`` so the exception type
matches the surrounding module contract.
"""

from __future__ import annotations

from typing import Any, Callable


def reject_duplicate_pairs(
    pairs: list[tuple[str, Any]],
    *,
    error_factory: Callable[[str], Exception] = ValueError,
) -> dict[str, Any]:
    """Merge ``pairs`` into a dict, rejecting duplicate keys fail-closed."""

    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise error_factory(f"duplicate key {key!r}")
        out[key] = value
    return out
