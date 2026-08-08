"""Shared Windows PowerShell executable resolution (single source of truth).

``identity.certificates``, ``identity.audit_anchor`` (simple variant) and
``identity.private_keys``, ``crypto.cng_handle`` (locked-hash variant)
implemented the same resolver with per-module error classes.  This leaf
unifies both variants (FRAMEWORK-OPTIMIZE-16); callers inject their own
``error_factory`` so exception semantics stay byte-identical (jsonutil
pattern).  Stdlib-only, dependency-free.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Callable


def powershell_executable(*, error_factory: Callable[[str], Exception]) -> str:
    """Resolve the Windows PowerShell executable (unlocked simple variant).

    ``COEVO_POWERSHELL_PATH`` (must be absolute) wins; otherwise fall back to
    ``%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe`` when it
    exists.  Raises ``error_factory(...)`` when unavailable.
    """
    exe = os.environ.get("COEVO_POWERSHELL_PATH")
    if exe and Path(exe).is_absolute():
        return exe
    fallback = (
        Path(os.environ.get("SystemRoot", r"C:\Windows"))
        / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    )
    if fallback.is_file():
        return str(fallback)
    raise error_factory("Windows PowerShell is unavailable")


def locked_powershell_executable(
    lock_path: Path,
    *,
    error_factory: Callable[[str], Exception],
) -> str:
    """Resolve and verify Windows PowerShell against the locked toolchain.

    Reads ``toolchain-lock.json``'s
    ``tools.make_compatibility_shim.windows_powershell``; ``COEVO_POWERSHELL_PATH``
    (must be absolute) wins, otherwise ``%SystemRoot%/<relative>``.  The
    resolved executable must pass the locked size + SHA-256 integrity check
    (fail-closed).
    """
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        expected = lock["tools"]["make_compatibility_shim"]["windows_powershell"]
        expected_size = int(expected["size"])
        expected_sha256 = str(expected["sha256"])
        relative = str(expected["windows_directory_relative_path"])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise error_factory("locked Windows PowerShell metadata is unavailable") from exc
    configured = os.environ.get("COEVO_POWERSHELL_PATH")
    candidate = Path(configured) if configured else (
        Path(os.environ.get("SystemRoot", r"C:\Windows")) / relative
    )
    if not candidate.is_absolute():
        raise error_factory("Windows PowerShell path must be absolute")
    try:
        resolved = candidate.resolve(strict=True)
        stat = resolved.stat()
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    except OSError as exc:
        raise error_factory("Windows PowerShell is unavailable") from exc
    if stat.st_size != expected_size or digest != expected_sha256:
        raise error_factory("Windows PowerShell failed the locked integrity check")
    return str(resolved)


__all__ = ["powershell_executable", "locked_powershell_executable"]
