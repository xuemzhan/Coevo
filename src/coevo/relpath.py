"""Shared safe relative-path predicate (single source of truth).

``progress_capture.watcher``, ``cockpit.static`` and ``cockpit.wps``
implemented the same "safe workspace-relative path" check with slightly
different local copies.  This leaf is the single source of truth
(FRAMEWORK-OPTIMIZE-15): fail-closed, stdlib-only, dependency-free.

Semantics that intentionally stay independent (documented in the slice):
``workspace.paths._has_parent_traversal`` (POSIX+Windows dialect scan for
composed paths) and ``model.config``'s single-file ``prompts_file`` check.
"""
from __future__ import annotations


def is_safe_relative_path(value: object) -> bool:
    """Return True only for a non-empty relative path without traversal.

    Rejects (fail-closed):
    * non-string / empty values;
    * leading ``/`` (absolute) or any ``\\`` (Windows separator abuse);
    * a NUL byte (never a valid Windows path component);
    * empty, ``.`` or ``..`` segments.

    The NUL rejection is a strictness unification: ``cockpit.static`` already
    rejected NUL; the other call sites never accepted a NUL path as valid
    (the filesystem layer would fail later), so no legal input changes.
    """
    if not isinstance(value, str) or not value:
        return False
    if value.startswith("/") or "\\" in value or "\x00" in value:
        return False
    return not any(part in ("", ".", "..") for part in value.split("/"))


__all__ = ["is_safe_relative_path"]
