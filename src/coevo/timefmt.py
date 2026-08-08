"""Shared ISO-8601 UTC timestamp helpers (FRAMEWORK-GAPS-6 / OPTIMIZE-2).

Dependency-free leaf module (stdlib only) so both the framework layer and
product modules can import it without import cycles.  The pattern is
``\\Z``-anchored (no trailing-newline bypass), accepts optional fractional
seconds, validates the calendar, and fails closed on non-string input.
``now_utc_iso_z`` is the single repository-wide UTC timestamp generator
(FRAMEWORK-OPTIMIZE-2); product modules must not reimplement it.
"""

from __future__ import annotations

import datetime as _datetime
import re

_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z\Z")


def now_utc_iso_z() -> str:
    """Return the current UTC time as an ISO-8601 ``Z`` string.

    Format is ``YYYY-MM-DDTHH:MM:SS.ffffffZ`` (fractional seconds preserved),
    identical to the previous per-module ``now_utc_iso_z`` implementations
    that this helper consolidates.
    """

    return _datetime.datetime.now(_datetime.UTC).isoformat().replace(
        "+00:00", "Z"
    )


def is_iso_utc_z(value: object) -> bool:
    """Return True for strict ISO-8601 UTC timestamps with trailing Z."""

    if not isinstance(value, str):
        return False
    if not _ISO_UTC_Z.match(value):
        return False
    try:
        base = value[:-1].split(".")[0] + "Z"
        _datetime.datetime.strptime(base, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True
