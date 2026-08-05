"""US-8-AC-2 real-time workspace file watcher (stdlib polling, fail-closed).

The watcher detects file changes in a workspace and emits bounded
:class:`FileChangeEvent` objects. Design constraints:

* No ``FILE_MTIME_ONLY`` signal: events carry digest + size + mtime, but
  the watcher never decides that a task is complete (AC-7). Consumers
  decide through :class:`ProgressCaptureService`.
* Path safety: relative paths are workspace-relative, symlinks are
  skipped, and every resolved file must stay under the root.
* Write stability: a change is emitted only after the same fingerprint
  (size, mtime, digest) is observed ``stability_checks`` consecutive
  scans, so half-written files do not produce events.
* Incremental digesting: files whose ``(size, mtime_ns)`` are unchanged
  since the previous scan reuse their stored digest, so a quiet
  workspace costs O(entries) metadata stat calls instead of re-hashing
  every file (an O(bytes) operation) on every poll. Content changes
  that preserve both size and mtime are out of scope for the reuse
  shortcut; callers that need byte-exact detection on every scan can
  set ``reuse_digest_on_unchanged=False`` (default True).
* Bounded event queue with optional background polling thread.

No new dependency; Python stdlib only.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-8-AC-2 工作区文件 watcher：轮询 + 摘要复用 + 符号链接跳过，失败关闭。
from __future__ import annotations

import enum
import hashlib
import mimetypes
import os
import re
import stat
import threading
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from . import (
    EvidenceInput,
    EvidenceKind,
    EvidenceRef,
    ProgressCaptureValidationError,
)


_ISO_UTC_Z: Final[re.Pattern[str]] = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
_HEX_64: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")

DEFAULT_POLL_INTERVAL_SEC: float = 1.0
DEFAULT_MAX_EVENTS: int = 256
DEFAULT_STABILITY_CHECKS: int = 2
DEFAULT_MAX_DIGEST_BYTES: int = 32 * 1024 * 1024
_CHUNK: int = 64 * 1024


def _now_utc_iso_z() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class FileEventKind(enum.Enum):
    """Closed set of raw file change kinds (never completion verdicts)."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    """A single observed file fingerprint (path, size, mtime, digest)."""

    relative_path: str
    size_bytes: int
    mtime_ns: int
    digest_hex: str
    media_type: str

    def __post_init__(self) -> None:
        _check_relative_path(self.relative_path)
        if not isinstance(self.size_bytes, int) or self.size_bytes < 0:
            raise ProgressCaptureValidationError("size_bytes must be non-negative")
        if not isinstance(self.mtime_ns, int) or self.mtime_ns < 0:
            raise ProgressCaptureValidationError("mtime_ns must be non-negative")
        if self.digest_hex and not _HEX_64.match(self.digest_hex):
            raise ProgressCaptureValidationError("digest_hex must be 64-hex or empty")
        if not isinstance(self.media_type, str) or not self.media_type:
            raise ProgressCaptureValidationError("media_type must be non-empty")


@dataclass(frozen=True, slots=True)
class FileChangeEvent:
    """A raw workspace file change (creation/modification/deletion)."""

    kind: FileEventKind
    relative_path: str
    size_bytes: int
    mtime_ns: int
    digest_hex: str
    media_type: str
    ts: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, FileEventKind):
            raise ProgressCaptureValidationError("kind must be a FileEventKind")
        _check_relative_path(self.relative_path)
        if not isinstance(self.size_bytes, int) or self.size_bytes < 0:
            raise ProgressCaptureValidationError("size_bytes must be non-negative")
        if not isinstance(self.mtime_ns, int) or self.mtime_ns < 0:
            raise ProgressCaptureValidationError("mtime_ns must be non-negative")
        if self.digest_hex and not _HEX_64.match(self.digest_hex):
            raise ProgressCaptureValidationError("digest_hex must be 64-hex or empty")
        if not isinstance(self.media_type, str) or not self.media_type:
            raise ProgressCaptureValidationError("media_type must be non-empty")
        if not isinstance(self.ts, str) or not _ISO_UTC_Z.match(self.ts):
            raise ProgressCaptureValidationError("ts must be ISO-8601 UTC Z")


def _check_relative_path(path: str) -> None:
    if (
        not isinstance(path, str)
        or not path
        or path.startswith("/")
        or "\\" in path
        or any(part in ("", ".", "..") for part in path.split("/"))
    ):
        raise ProgressCaptureValidationError(
            f"relative_path must be a safe workspace-relative path; got {path!r}"
        )


class WorkspaceWatcher:
    """Polling workspace watcher with bounded, stability-gated events."""

    def __init__(
        self,
        root: Path,
        *,
        poll_interval_sec: float = DEFAULT_POLL_INTERVAL_SEC,
        max_events: int = DEFAULT_MAX_EVENTS,
        stability_checks: int = DEFAULT_STABILITY_CHECKS,
        max_digest_bytes: int = DEFAULT_MAX_DIGEST_BYTES,
        allow_extensions: frozenset[str] | None = None,
        reuse_digest_on_unchanged: bool = True,
    ) -> None:
        if not isinstance(root, Path):
            raise ProgressCaptureValidationError("root must be a Path")
        try:
            resolved = root.resolve(strict=True)
        except OSError as exc:
            raise ProgressCaptureValidationError(
                f"watcher root must be an existing directory ({exc})"
            ) from exc
        if not resolved.is_dir():
            raise ProgressCaptureValidationError("watcher root must be a directory")
        if (
            not isinstance(poll_interval_sec, (int, float))
            or not 0.05 <= float(poll_interval_sec) <= 60.0
        ):
            raise ProgressCaptureValidationError(
                "poll_interval_sec must be between 0.05 and 60.0"
            )
        if not isinstance(max_events, int) or max_events < 1:
            raise ProgressCaptureValidationError("max_events must be a positive integer")
        if not isinstance(stability_checks, int) or stability_checks < 1:
            raise ProgressCaptureValidationError(
                "stability_checks must be a positive integer"
            )
        if not isinstance(max_digest_bytes, int) or max_digest_bytes <= 0:
            raise ProgressCaptureValidationError(
                "max_digest_bytes must be a positive integer"
            )
        if allow_extensions is not None and (
            not isinstance(allow_extensions, frozenset)
            or not all(
                isinstance(ext, str) and ext.startswith(".") for ext in allow_extensions
            )
        ):
            raise ProgressCaptureValidationError(
                "allow_extensions must be None or a frozenset of '.ext' strings"
            )
        if not isinstance(reuse_digest_on_unchanged, bool):
            raise ProgressCaptureValidationError(
                "reuse_digest_on_unchanged must be a bool"
            )
        self._root = resolved
        self._poll_interval_sec = float(poll_interval_sec)
        self._max_events = max_events
        self._stability_checks = stability_checks
        self._max_digest_bytes = max_digest_bytes
        self._allow_extensions = allow_extensions
        self._reuse_digest_on_unchanged = reuse_digest_on_unchanged
        self._snapshot: dict[str, FileSnapshot] = {}
        self._pending: dict[str, tuple[tuple[int, int, str], int]] = {}
        self._events: deque[FileChangeEvent] = deque(maxlen=max_events)
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._error_count = 0

    @property
    def root(self) -> Path:
        return self._root

    @property
    def error_count(self) -> int:
        return self._error_count

    def scan(self, now: str | None = None) -> tuple[FileChangeEvent, ...]:
        """Compare the filesystem to the last snapshot and emit events."""
        now = now or _now_utc_iso_z()
        if not _ISO_UTC_Z.match(now):
            raise ProgressCaptureValidationError("now must be ISO-8601 UTC Z")
        current = self._collect(self._snapshot)
        events: list[FileChangeEvent] = []
        for path in sorted(set(self._snapshot) | set(current)):
            old = self._snapshot.get(path)
            new = current.get(path)
            if new is None:
                self._snapshot.pop(path, None)
                self._pending.pop(path, None)
                if old is not None:
                    events.append(
                        FileChangeEvent(
                            FileEventKind.DELETED,
                            old.relative_path,
                            0,
                            old.mtime_ns,
                            "",
                            old.media_type,
                            now,
                        )
                    )
                continue
            fingerprint = (new.size_bytes, new.mtime_ns, new.digest_hex)
            entry = self._pending.get(path)
            if entry is None:
                if self._stability_checks <= 1:
                    self._snapshot[path] = new
                    kind = FileEventKind.CREATED if old is None else FileEventKind.MODIFIED
                    events.append(
                        FileChangeEvent(
                            kind,
                            new.relative_path,
                            new.size_bytes,
                            new.mtime_ns,
                            new.digest_hex,
                            new.media_type,
                            now,
                        )
                    )
                else:
                    self._pending[path] = (fingerprint, 1)
                continue
            if entry[0] == fingerprint:
                seen = entry[1] + 1
                if seen >= self._stability_checks:
                    self._pending.pop(path, None)
                    self._snapshot[path] = new
                    kind = FileEventKind.CREATED if old is None else FileEventKind.MODIFIED
                    events.append(
                        FileChangeEvent(
                            kind,
                            new.relative_path,
                            new.size_bytes,
                            new.mtime_ns,
                            new.digest_hex,
                            new.media_type,
                            now,
                        )
                    )
                else:
                    self._pending[path] = (fingerprint, seen)
            else:
                self._pending[path] = (fingerprint, 1)
        for event in events:
            self._events.append(event)
        return tuple(events)

    def drain(self) -> tuple[FileChangeEvent, ...]:
        """Return and clear the pending event queue."""
        pending = tuple(self._events)
        self._events.clear()
        return pending

    def reset(self) -> None:
        """Clear the snapshot, pending candidates, and event queue."""
        self._snapshot.clear()
        self._pending.clear()
        self._events.clear()

    def start(self) -> None:
        """Start the optional background polling thread."""
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="coevo-workspace-watcher",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the background polling thread (idempotent)."""
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join(timeout=self._poll_interval_sec * 2 + 1.0)
        self._thread = None

    def _run(self) -> None:
        while not self._stop_event.wait(self._poll_interval_sec):
            try:
                self.scan()
            except Exception:  # noqa: BLE001 - a scan failure never kills the watcher
                self._error_count += 1

    def build_evidence_input(
        self,
        event: FileChangeEvent,
        *,
        task_id: str,
        text: str,
        confidence: float,
        role: str | None = None,
    ) -> EvidenceInput:
        """Map a change event to a progress-capture evidence input.

        Deletion and digest-less events are rejected (fail-closed): a
        removed or oversized file cannot be completion evidence, and the
        watcher never emits a mtime-only signal.
        """
        if not isinstance(event, FileChangeEvent):
            raise ProgressCaptureValidationError("event must be a FileChangeEvent")
        if event.kind == FileEventKind.DELETED:
            raise ProgressCaptureValidationError(
                "deleted files cannot be completion evidence (AC-7)"
            )
        if not event.digest_hex:
            raise ProgressCaptureValidationError(
                "oversized files without a digest cannot be evidence"
            )
        if not isinstance(confidence, float) or not 0.0 <= confidence <= 1.0:
            raise ProgressCaptureValidationError("confidence must be in [0.0, 1.0]")
        is_text = event.media_type.startswith("text/")
        kind = (
            EvidenceKind.DOCUMENT_CONTENT if is_text else EvidenceKind.ARTIFACT_FILE
        )
        resolved_role = role or ("document" if is_text else "artifact")
        if resolved_role not in {"document", "feedback", "artifact", "dependency"}:
            raise ProgressCaptureValidationError(
                "role must be document/feedback/artifact/dependency"
            )
        evidence_ref = EvidenceRef(
            path=event.relative_path,
            role=resolved_role,
            media_type=event.media_type,
            digest_hex=event.digest_hex,
            size_bytes=event.size_bytes,
        )
        return EvidenceInput(
            task_id=task_id,
            kind=kind,
            source_ref=event.relative_path,
            text=text,
            confidence=confidence,
            evidence_refs=(evidence_ref,),
        )

    # -- internals ----------------------------------------------------------

    def _collect(
        self,
        previous: dict[str, FileSnapshot] | None = None,
    ) -> dict[str, FileSnapshot]:
        """Collect snapshots for the workspace tree.

        ``previous`` is the last observed snapshot; files whose
        ``(size, mtime_ns)`` pair is unchanged reuse the stored digest
        unless reuse was disabled at construction. The returned dict is
        byte-identical to a full re-hash for every file the caller can
        actually observe as changed (new, deleted, or size/mtime
        changed), so event semantics are preserved.
        """
        previous = previous if self._reuse_digest_on_unchanged else {}
        result: dict[str, FileSnapshot] = {}
        root = str(self._root)
        for dirpath, dirnames, filenames in os.walk(self._root, followlinks=False):
            dirnames[:] = [name for name in dirnames if not name.startswith(".")]
            rel_dir = os.path.relpath(dirpath, root).replace("\\", "/")
            for name in sorted(filenames):
                if name.startswith("."):
                    continue
                if (
                    self._allow_extensions is not None
                    and os.path.splitext(name)[1].lower()
                    not in self._allow_extensions
                ):
                    continue
                relative = name if rel_dir == "." else f"{rel_dir}/{name}"
                full_path = os.path.join(dirpath, name)
                try:
                    # 单次 lstat 同时完成符号链接判断与元数据读取，
                    # 替代原来的 is_symlink() + stat() 两次系统调用。
                    info = os.lstat(full_path)
                    if stat.S_ISLNK(info.st_mode):
                        continue
                    resolved = os.path.realpath(full_path)
                    if os.path.commonpath([resolved, root]) != root:
                        continue
                except (OSError, ValueError):
                    continue
                size = int(info.st_size)
                mtime_ns = int(info.st_mtime_ns)
                prior = previous.get(relative)
                if (
                    prior is not None
                    and prior.size_bytes == size
                    and prior.mtime_ns == mtime_ns
                ):
                    digest = prior.digest_hex
                else:
                    digest = self._digest(full_path, size)
                media = mimetypes.guess_type(name)[0] or "application/octet-stream"
                result[relative] = FileSnapshot(
                    relative,
                    size,
                    mtime_ns,
                    digest,
                    media,
                )
        return result

    def _digest(self, full: str, size: int) -> str:
        if size > self._max_digest_bytes:
            return ""
        hasher = hashlib.sha256()
        try:
            with open(full, "rb") as stream:
                for chunk in iter(lambda: stream.read(_CHUNK), b""):
                    hasher.update(chunk)
        except OSError:
            return ""
        return hasher.hexdigest()
