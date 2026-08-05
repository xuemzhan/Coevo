"""Records archiving policy helpers (pure, testable).

Loop records grow linearly (VERIFICATION.md, DECISIONS.md, tool-audit
JSONL). This module implements the *planning* half of the archiving
policy; ``scripts/archive_records.py`` applies it. All functions are
pure: they never touch the filesystem.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 记录归档策略助手：VERIFICATION/DECISIONS/审计行分段与归档计划，纯函数。
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any


_VERIFICATION_HEADER = re.compile(r"^(\d{4}-\d{2}-\d{2}T[^\s]+Z)")
_DECISIONS_HEADER = re.compile(r"^(\d{4}-\d{2}-\d{2})")
_AUDIT_TS = re.compile(r'"ts"\s*:\s*"(\d{4}-\d{2}-\d{2}T[^"]+Z)"')


def _parse_ts(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(UTC)


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
    size_bytes = len(text.encode("utf-8"))
    if size_bytes > size_threshold_bytes:
        # Enforce the size cap (policy: "保留 N 条（或 ≤ 容量）"): drop the
        # oldest kept sections until the remaining tail fits, never emptying
        # the record. This makes the documented size trigger actually bite.
        moved = 0
        while len(keep) > 1 and len("\n".join(keep).encode("utf-8")) > size_threshold_bytes:
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
