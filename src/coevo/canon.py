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


def canonical_json_bytes(value: Any, *, ensure_ascii: bool = True) -> bytes:
    """Serialize ``value`` to canonical JSON bytes (sorted keys, compact)."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=ensure_ascii,
    ).encode("utf-8")


def canonical_digest(value: Any, *, ensure_ascii: bool = True) -> str:
    """Return the SHA-256 hex digest of the canonical JSON bytes."""

    return hashlib.sha256(
        canonical_json_bytes(value, ensure_ascii=ensure_ascii)
    ).hexdigest()
