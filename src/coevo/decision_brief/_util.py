"""Pure utility helpers for the decision-brief models (FRAMEWORK-OPTIMIZE-19).

Dependency-free (no imports of the domain modules); raising helpers take an
``error_factory`` so callers keep their exact exception class and message.
``models.py`` imports these and exposes thin wrappers with the historical
signatures, so the existing import surface is unchanged.
"""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Callable

from src.coevo.timefmt import parse_iso_utc


_ZERO_DIGEST: str = "0" * 64
_REPARSE_POINT: int = 0x400


def _stat_is_reparse(info: os.stat_result) -> bool:
    return bool(getattr(info, "st_file_attributes", 0) & _REPARSE_POINT)


def _is_link_or_reparse(
    path: Path,
    *,
    error_factory: Callable[[str], Exception],
) -> bool:
    """Detect symbolic-link/reparse-point semantics for a Path (used by template path guards)."""
    try:
        info = path.lstat()
    except OSError as exc:
        raise error_factory("template path is unavailable") from exc
    return stat.S_ISLNK(info.st_mode) or _stat_is_reparse(info)


def _safe_string(
    value: object,
    *,
    field: str,
    max_bytes: int,
    error_factory: Callable[[str], Exception],
) -> None:
    """Fail-closed bounds check for a string field (type, non-empty, byte cap)."""
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        raise error_factory(f"{field} must be a non-empty safe string")
    if len(value.encode("utf-8")) > max_bytes:
        raise error_factory(f"{field} exceeds byte limit")


def _digest(
    value: object,
    *,
    field: str,
    error_factory: Callable[[str], Exception],
) -> None:
    """Validate a lowercase SHA-256 hex digest (fail-closed)."""
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise error_factory(f"{field} must be lowercase SHA-256")


def _parse_utc(
    value: object,
    *,
    field: str,
    error_factory: Callable[[str], Exception],
    not_utc_message: str,
    invalid_message: str,
) -> "object":
    """Parse an ISO-8601 UTC string into a timezone-aware datetime (fail-closed on non-UTC or malformed input)."""
    return parse_iso_utc(
        value,
        error_factory=error_factory,
        not_utc_message=not_utc_message,
        invalid_message=invalid_message,
    )


def _encode_json(
    value: object,
    *,
    max_bytes: int,
    error_factory: Callable[[str], Exception],
) -> bytes:
    """Encode a value to canonical JSON bytes under a byte budget (fail-closed)."""
    try:
        payload = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        raise error_factory("value is not canonical JSON") from exc
    if len(payload) > max_bytes:
        raise error_factory("canonical payload exceeds byte limit")
    return payload
