"""Shared canonical JSON serialization and SHA-256 digest (FRAMEWORK-OPTIMIZE-3).

Dependency-free leaf module (stdlib only), symmetric to ``timefmt.py``, so
both the framework layer and product modules can import it without import
cycles.  The canonical form matches the repository-wide convention: sorted
keys, compact separators ``(",", ":")``, no trailing newline, optional ASCII
safe escaping.  Product audit/hash-chain callers MUST NOT reimplement the
digest inline (guarded by tests/unit/test_framework_optimize3.py).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_bytes(
    value: Any,
    *,
    ensure_ascii: bool = True,
    allow_nan: bool = False,
    trailing_newline: bool = False,
) -> bytes:
    """Serialize ``value`` to canonical JSON bytes (sorted keys, compact).

    ``allow_nan`` defaults to False so non-finite floats (NaN/Infinity) are
    rejected (fail-closed) instead of being emitted as non-standard JSON
    (FRAMEWORK-OPTIMIZE-5).
    """

    return canonical_json_str(
        value,
        ensure_ascii=ensure_ascii,
        allow_nan=allow_nan,
        trailing_newline=trailing_newline,
    ).encode("utf-8")


def canonical_json_str(
    value: Any,
    *,
    ensure_ascii: bool = True,
    allow_nan: bool = False,
    trailing_newline: bool = False,
) -> str:
    """Serialize ``value`` to canonical JSON text (sorted keys, compact).

    String variant of :func:`canonical_json_bytes` (FRAMEWORK-OPTIMIZE-9) for
    product modules that store canonical JSON as ``str``; byte semantics are
    identical after UTF-8 encoding.
    """

    text = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=ensure_ascii,
        allow_nan=allow_nan,
    )
    return text + "\n" if trailing_newline else text


def canonical_digest(
    value: Any,
    *,
    ensure_ascii: bool = True,
    allow_nan: bool = False,
    trailing_newline: bool = False,
) -> str:
    """Return the SHA-256 hex digest of the canonical JSON bytes."""

    return hashlib.sha256(
        canonical_json_bytes(
            value,
            ensure_ascii=ensure_ascii,
            allow_nan=allow_nan,
            trailing_newline=trailing_newline,
        )
    ).hexdigest()
