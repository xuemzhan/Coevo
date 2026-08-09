"""Shared id patterns and validators (FRAMEWORK-OPTIMIZE-11 / -13).

Dependency-free leaf module (stdlib only), symmetric to ``timefmt.py`` and
``canon.py``.  The repository-wide safe-id form is
``[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,63}`` (max 64 chars, no leading dot/dash).
Modules whose id grammar intentionally differs (e.g. task_flow requiring a
letter first char) keep their own pattern; see
``tests/unit/test_framework_optimize11.py``.
"""

from __future__ import annotations

import re

SAFE_ID: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")

HEX_64: re.Pattern[str] = re.compile(r"^[0-9a-f]{64}\Z")


def is_safe_id(value: object) -> bool:
    """Return True only for a non-empty safe-id string (fail-closed)."""

    return isinstance(value, str) and SAFE_ID.match(value) is not None


def is_hex_64(value: object) -> bool:
    """Return True only for a 64-char lowercase hex string (fail-closed)."""

    return isinstance(value, str) and HEX_64.match(value) is not None
