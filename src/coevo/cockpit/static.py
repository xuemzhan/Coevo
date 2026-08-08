"""cockpit.static - bounded static asset cache and path policy for the local cockpit."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 静态资源路径策略与有界缓存：安全解析、mtime 失效、FIFO 淘汰。



from __future__ import annotations



import threading
from pathlib import Path
from typing import Final

from .models import CockpitValidationError
from src.coevo.relpath import is_safe_relative_path



STATIC_ALLOWED_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".html", ".css", ".js", ".png", ".svg", ".ico", ".txt", ".json", ".woff2",
})


STATIC_MAX_BYTES: Final[int] = 2 * 1024 * 1024


STATIC_CACHE_MAX_ENTRIES: int = 64


STATIC_CACHE_MAX_BYTES: int = 8 * 1024 * 1024


class _StaticAssetCache:
    """Bounded, mtime-validated cache for static assets.

    Repeated page loads currently re-read ``index.html`` / CSS / JS from
    disk on every request. This cache keeps the resolved bytes in memory
    and re-validates ``(mtime_ns, size)`` against the filesystem on each
    hit, so a file edited on disk is picked up on the next request while
    unchanged files avoid repeated reads. Thread-safe; bounded by entry
    count and total bytes (FIFO eviction).
    """

    def __init__(
        self,
        *,
        max_entries: int = STATIC_CACHE_MAX_ENTRIES,
        max_bytes: int = STATIC_CACHE_MAX_BYTES,
    ) -> None:
        if not isinstance(max_entries, int) or max_entries < 1:
            raise CockpitValidationError("max_entries must be a positive integer")
        if not isinstance(max_bytes, int) or max_bytes < 1:
            raise CockpitValidationError("max_bytes must be a positive integer")
        self._max_entries = max_entries
        self._max_bytes = max_bytes
        self._entries: dict[str, tuple[int, int, bytes]] = {}
        self._total_bytes = 0
        self._lock = threading.Lock()

    def get(self, path: Path) -> bytes | None:
        """Return cached bytes when the file is unchanged, else None."""
        try:
            stat = path.stat()
        except OSError:
            return None
        key = str(path)
        with self._lock:
            entry = self._entries.get(key)
        if (
            entry is not None
            and entry[0] == stat.st_mtime_ns
            and entry[1] == stat.st_size
        ):
            return entry[2]
        return None

    def put(self, path: Path, body: bytes) -> None:
        """Cache ``body`` for ``path`` after validating current stat."""
        if len(body) > self._max_bytes:
            return
        try:
            stat = path.stat()
        except OSError:
            return
        key = str(path)
        with self._lock:
            old = self._entries.pop(key, None)
            if old is not None:
                self._total_bytes -= len(old[2])
            self._entries[key] = (stat.st_mtime_ns, stat.st_size, body)
            self._total_bytes += len(body)
            while (
                len(self._entries) > self._max_entries
                or self._total_bytes > self._max_bytes
            ):
                oldest_key = next(iter(self._entries))
                removed = self._entries.pop(oldest_key)
                self._total_bytes -= len(removed[2])

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._entries)

    @property
    def total_bytes(self) -> int:
        with self._lock:
            return self._total_bytes


def resolve_static_path(static_root: Path, relative: str) -> Path | None:
    """Resolve a static asset inside the root, or return None (fail-closed)."""
    if not is_safe_relative_path(relative):
        return None
    try:
        root = static_root.resolve(strict=True)
        candidate = (root / relative).resolve(strict=False)
        candidate.relative_to(root)
    except (OSError, ValueError):
        return None
    if candidate.suffix.lower() not in STATIC_ALLOWED_EXTENSIONS:
        return None
    try:
        if not candidate.is_file() or candidate.stat().st_size > STATIC_MAX_BYTES:
            return None
    except OSError:
        return None
    return candidate

