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
from typing import Callable

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


def parse_iso_utc(
    value: object,
    *,
    error_factory: Callable[[str], Exception],
    not_utc_message: str,
    invalid_message: str,
) -> _datetime.datetime:
    """Parse an ISO-8601 UTC ``Z`` string, raising ``error_factory`` on failure.

    Unifies the per-module ``_parse_utc`` copies (FRAMEWORK-OPTIMIZE-17).
    Callers pass their own exception class and exact messages so behavior is
    byte-identical to the original implementations:

    * non-string / missing trailing ``Z`` -> ``error_factory(not_utc_message)``;
    * malformed timestamp -> ``error_factory(invalid_message)``;
    * non-zero UTC offset -> ``error_factory(not_utc_message)`` (unreachable in
      practice because ``Z`` is replaced by ``+00:00``, kept for parity).
    """
    if not isinstance(value, str) or not value.endswith("Z"):
        raise error_factory(not_utc_message)
    try:
        parsed = _datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise error_factory(invalid_message) from exc
    if parsed.utcoffset() != _datetime.timedelta(0):
        raise error_factory(not_utc_message)
    return parsed
