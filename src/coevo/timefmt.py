"""Shared ISO-8601 UTC timestamp validator (FRAMEWORK-GAPS-6).

Dependency-free leaf module (stdlib only) so both the framework layer and
product modules can import it without import cycles.  The pattern is
``\\Z``-anchored (no trailing-newline bypass), accepts optional fractional
seconds, validates the calendar, and fails closed on non-string input.
"""

from __future__ import annotations

import datetime as _datetime
import re

_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z\Z")


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
