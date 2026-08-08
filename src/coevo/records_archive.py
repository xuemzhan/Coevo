"""Records archiving policy helpers (pure, testable).

Loop records grow linearly (VERIFICATION.md, DECISIONS.md, tool-audit
JSONL). This module is the single source of truth for the archiving
*policy* (record kind thresholds) and the *planning* half of the
archiving workflow; ``scripts/archive_records.py`` applies it. All
functions are pure: they never touch the filesystem.
"""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any


POLICY: dict[str, dict[str, int]] = {
    "verification": {"keep_recent": 30, "min_age_days": 30, "size": 500_000},
    "decisions": {"keep_recent": 20, "min_age_days": 90, "size": 500_000},
    "audit": {"keep_recent": 2000, "min_age_days": 30, "size": 5_000_000},
}

# Kinds the generic archive tool may touch. The audit chain
# (``loop/tool-audit.jsonl``) is append-only and seal-protected: trimming it
# would invalidate the signed audit head without a dedicated re-anchor flow
# (RECORDS-ARCHIVE-3), so it is deliberately excluded here and the tool
# refuses to archive it.
ARCHIVABLE_KINDS: tuple[str, ...] = ("verification", "decisions")


def archivable(kind: str) -> bool:
    """Return whether ``kind`` is actionable by the generic archive tool."""
    return kind in ARCHIVABLE_KINDS


_VERIFICATION_HEADER = re.compile(r"^(\d{4}-\d{2}-\d{2}T[^\s]+Z)")
_DECISIONS_HEADER = re.compile(r"^(\d{4}-\d{2}-\d{2})")
_AUDIT_TS = re.compile(r'"ts"\s*:\s*"(\d{4}-\d{2}-\d{2}T[^"]+Z)"')


def _parse_ts(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(UTC)


def over_policy_size(kind: str, text: str) -> bool:
    """Return whether ``text`` exceeds the archiving size cap for ``kind``.

    Pure and fail-closed: unknown kinds and non-string text raise instead
    of silently returning a permissive result.
    """
    if kind not in POLICY:
        raise ValueError(f"unknown kind {kind!r}")
    if not isinstance(text, str):
        raise TypeError(f"text must be str, got {type(text).__name__}")
    return len(text.encode("utf-8")) > POLICY[kind]["size"]


def split_verification_sections(text: str) -> list[tuple[str, str]]:
    """Split VERIFICATION.md into (header_ts, block) pairs in order."""
    blocks = re.split(r"(?m)^## ", text)
    result: list[tuple[str, str]] = []
    for block in blocks:
        if not block.strip():
            continue
        header_line = block.splitlines()[0]
        match = _VERIFICATION_HEADER.match(header_line)
        if match is None:
            continue
        result.append((match.group(1), "## " + block))
    return result


def split_decisions_sections(text: str) -> list[tuple[str, str]]:
    """Split DECISIONS.md into (date, section) pairs in order."""
    blocks = re.split(r"(?m)^## ", text)
    result: list[tuple[str, str]] = []
    for block in blocks:
        if not block.strip():
            continue
        header_line = block.splitlines()[0]
        match = _DECISIONS_HEADER.match(header_line)
        if match is None:
            continue
        result.append((match.group(1), "## " + block))
    return result


def split_audit_lines(text: str) -> list[tuple[str, str]]:
    """Split tool-audit JSONL into (ts, line) pairs in order."""
    result: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = record.get("ts") if isinstance(record, dict) else None
        if isinstance(ts, str) and _AUDIT_TS.search(line):
            result.append((ts, line))
    return result


def archive_plan(
    text: str,
    *,
    kind: str,
    now: str,
    keep_recent: int,
    min_age_days: int,
    size_threshold_bytes: int,
    size_bytes: int | None = None,
    size_tail_budget_bytes: int = 64_000,
) -> dict[str, Any]:
    """Return {keep, archive, reason} given current content and policy."""
    if kind == "verification":
        sections = split_verification_sections(text)
    elif kind == "decisions":
        sections = split_decisions_sections(text)
    elif kind == "audit":
        sections = split_audit_lines(text)
    else:
        raise ValueError(f"unknown kind {kind!r}")
    now_dt = _parse_ts(now)
    keep: list[str] = []
    archive: list[str] = []
    reason = ""
    for index, (ts, content) in enumerate(sections):
        try:
            age_days = (now_dt - _parse_ts(ts)).total_seconds() / 86400.0
        except (ValueError, TypeError):
            age_days = 0.0
        if index >= len(sections) - keep_recent:
            keep.append(content)
        elif age_days > min_age_days:
            archive.append(content)
        else:
            keep.append(content)
    if size_bytes is None:
        size_bytes = len(text.encode("utf-8"))
    effective_threshold = max(1, size_threshold_bytes - size_tail_budget_bytes)
    if size_bytes > size_threshold_bytes:
        # Enforce the size cap (policy: "保留 N 条（或 ≤ 容量）"): drop the
        # oldest kept sections until the remaining tail fits under the cap
        # with headroom for gate output and the trailing newline, never
        # emptying the record. This makes the documented size trigger
        # actually bite and keeps --check green after --apply.
        moved = 0
        while (
            len(keep) > 1
            and len("\n".join(keep).encode("utf-8")) > effective_threshold
        ):
            archive.insert(0, keep.pop(0))
            moved += 1
        reason = f"size {size_bytes} > {size_threshold_bytes} bytes"
        if moved:
            reason += f"; size-trimmed {moved} kept section(s)"
    kept_text = "\n".join(keep)
    if archive:
        reason = f"archived {len(archive)} old section(s); " + reason
    return {
        "kind": kind,
        "keep": kept_text,
        "archive": "\n".join(archive),
        "archived_sections": len(archive),
        "reason": reason.strip("; "),
    }
