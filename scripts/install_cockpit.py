"""Offline install / upgrade / rollback / uninstall for the local Coevo cockpit.

This tool is the offline deployment surface for the production cockpit
(P0-1 / INSTALL-1). It installs a versioned runtime bundle under
``<install_root>/app/<version>``, records a SHA-256 integrity manifest
per version, keeps an install-history journal (``releases.json``) and an
atomically-switched ``current`` pointer, and verifies the manifest before
any pointer switch. It never touches data or log directories.

Design invariants (fail-closed):

* The version label must match ``^\\d+\\.\\d+\\.\\d+$`` (semantic, never a
  timestamp) and is used as a single safe path segment.
* Every copied file is hashed while copying; the manifest is written and
  re-verified before the ``current`` pointer moves.
* Install/upgrade write into ``app/<version>`` only; rollback re-verifies
  the previous version's manifest before switching; uninstall removes
  only the current version (data/log and other versions are preserved).
* All paths are resolved under ``<install_root>``; symlinks in the source
  are skipped (never followed); destructive operations are limited to
  ``app/``, ``manifests/``, ``releases.json`` and the ``current`` pointer.
* A single-instance lock prevents concurrent install/upgrade/rollback.

No new dependency: Python stdlib only (the runtime itself is stdlib-only).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Final


APP_DIR: Final[str] = "app"
MANIFEST_DIR: Final[str] = "manifests"
CURRENT_POINTER: Final[str] = "current"
RELEASES_FILE: Final[str] = "releases.json"
LOG_RELATIVE: Final[str] = "logs/install.log"
LOCK_RELATIVE: Final[str] = "install.lock"
STALE_LOCK_SECONDS: Final[int] = 600
RELEASES_SCHEMA: Final[str] = "1.0"
VERSION_RE: Final[re.Pattern[str]] = re.compile(r"^\d+\.\d+\.\d+$")
_VERSION_PY_RE: Final[re.Pattern[str]] = re.compile(
    r'^VERSION:\s*str\s*=\s*"([^"]+)"\s*$', re.MULTILINE
)

# Runtime bundle: everything needed to run the cockpit offline. The
# development tree (.tools, tests, loop, docs) is deliberately excluded.
BUNDLE_RELATIVES: Final[tuple[str, ...]] = (
    "src",
    "scripts/run_cockpit.py",
    "scripts/run_demo.py",
    "config",
    "README.md",
)
_SKIP_DIR_NAMES: Final[frozenset[str]] = frozenset({"__pycache__"})
_SKIP_FILE_SUFFIXES: Final[frozenset[str]] = frozenset({".pyc", ".pyo"})


class InstallerError(RuntimeError):
    """Raised when an install/upgrade/rollback operation fails (fail-closed)."""


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version_from_source(source_root: Path) -> str:
    version_path = source_root / "src" / "coevo" / "version.py"
    match = _VERSION_PY_RE.search(version_path.read_text(encoding="utf-8"))
    if match is None:
        raise InstallerError(
            f"cannot read VERSION from {version_path} (missing or malformed)"
        )
    return match.group(1)


def _validate_version(version: str) -> str:
    if not VERSION_RE.fullmatch(version):
        raise InstallerError(
            f"version must match ^\\d+\\.\\d+\\.\\d+$ (no timestamps); got {version!r}"
        )
    return version


def _resolve_install_root(install_root: Path) -> Path:
    try:
        resolved = install_root.resolve()
    except OSError as exc:
        raise InstallerError(f"install root cannot be resolved: {exc}") from exc
    return resolved


class InstallLock:
    """Exclusive-create lock with stale takeover (mirrors cockpit semantics)."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._fd: int | None = None

    def acquire(self) -> None:
        if self._fd is not None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._try_create():
            if not self._recover_stale() or not self._try_create():
                raise InstallerError(
                    f"another installer process is active ({self._path})"
                )

    def _try_create(self) -> bool:
        try:
            self._fd = os.open(
                str(self._path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
            os.write(self._fd, str(os.getpid()).encode("ascii"))
            return True
        except FileExistsError:
            return False

    def _recover_stale(self) -> bool:
        try:
            age = time.time() - self._path.stat().st_mtime
        except OSError:
            return False
        if age < STALE_LOCK_SECONDS:
            return False
        try:
            self._path.unlink()
            return True
        except OSError:
            return False

    def release(self) -> None:
        if self._fd is None:
            return
        try:
            os.close(self._fd)
        finally:
            self._fd = None
            try:
                self._path.unlink()
            except FileNotFoundError:
                pass

    def __enter__(self) -> "InstallLock":
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()


def _copy_bundle(source_root: Path, target: Path) -> dict[str, str]:
    """Copy the runtime bundle into ``target`` and return path->sha256."""
    manifest: dict[str, str] = {}

    def _copy_one(src: Path, dst: Path) -> None:
        if src.is_symlink():
            return
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with src.open("rb") as reader, dst.open("wb") as writer:
                for chunk in iter(lambda: reader.read(64 * 1024), b""):
                    digest.update(chunk)
                    writer.write(chunk)
            manifest[dst.relative_to(target).as_posix()] = digest.hexdigest()
        elif src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            for child in sorted(src.iterdir()):
                if child.is_dir() and child.name in _SKIP_DIR_NAMES:
                    continue
                if child.is_file() and child.suffix in _SKIP_FILE_SUFFIXES:
                    continue
                _copy_one(child, dst / child.name)

    for relative in BUNDLE_RELATIVES:
        src = (source_root / relative).resolve()
        if not src.exists():
            raise InstallerError(f"bundle path is missing in source: {relative}")
        _copy_one(src, target / relative)
    return manifest


def _write_manifest(install_root: Path, version: str, manifest: dict[str, str]) -> str:
    lines = [
        f"{manifest[path]}  {path}\n" for path in sorted(manifest)
    ]
    body = "".join(lines).encode("utf-8")
    manifest_dir = install_root / MANIFEST_DIR
    manifest_dir.mkdir(parents=True, exist_ok=True)
    target = manifest_dir / f"{version}.sha256"
    tmp = manifest_dir / f".{version}.{uuid.uuid4().hex}.tmp"
    with tmp.open("wb") as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, target)
    return _sha256_bytes(body)


def _verify_manifest(install_root: Path, version: str) -> str:
    """Re-hash the installed tree and compare against the manifest."""
    manifest_path = install_root / MANIFEST_DIR / f"{version}.sha256"
    try:
        body = manifest_path.read_bytes()
    except OSError as exc:
        raise InstallerError(f"manifest is missing for {version}: {exc}") from exc
    expected: dict[str, str] = {}
    for raw in body.decode("utf-8").splitlines():
        parts = raw.split("  ", 1)
        if len(parts) != 2:
            raise InstallerError(f"malformed manifest line: {raw!r}")
        expected[parts[1]] = parts[0]
    app_dir = install_root / APP_DIR / version
    actual: dict[str, str] = {}
    for path in sorted(app_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(app_dir)
        if any(part == "__pycache__" for part in relative.parts):
            continue  # runtime-generated bytecode is not part of the artifact
        if path.suffix in _SKIP_FILE_SUFFIXES:
            continue
        actual[relative.as_posix()] = _sha256_file(path)
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        changed = sorted(
            path for path in set(expected) & set(actual)
            if expected[path] != actual[path]
        )
        detail: list[str] = []
        if missing:
            detail.append(f"missing={missing[:5]}")
        if extra:
            detail.append(f"extra={extra[:5]}")
        if changed:
            detail.append(f"changed={changed[:5]}")
        raise InstallerError(
            f"integrity verification failed for {version}: " + "; ".join(detail)
        )
    return _sha256_bytes(body)


def _read_releases(install_root: Path) -> list[dict[str, object]]:
    path = install_root / RELEASES_FILE
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InstallerError(f"releases.json is corrupt: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != RELEASES_SCHEMA:
        raise InstallerError("releases.json has an unsupported schema")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise InstallerError("releases.json entries must be a list")
    return entries


def _write_releases(install_root: Path, entries: list[dict[str, object]]) -> None:
    payload = {
        "schema_version": RELEASES_SCHEMA,
        "entries": entries,
    }
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    tmp = install_root / f".{RELEASES_FILE}.{uuid.uuid4().hex}.tmp"
    with tmp.open("wb") as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, install_root / RELEASES_FILE)


def _write_pointer(install_root: Path, version: str) -> None:
    tmp = install_root / f".current-{uuid.uuid4().hex}.tmp"
    with tmp.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(version + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, install_root / CURRENT_POINTER)


def _read_pointer(install_root: Path) -> str:
    pointer = install_root / CURRENT_POINTER
    try:
        value = pointer.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise InstallerError(f"current pointer is unreadable: {exc}") from exc
    return _validate_version(value)


def _append_log(install_root: Path, action: str, version: str, result: str, detail: str = "") -> None:
    path = install_root / LOG_RELATIVE
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(
                json.dumps(
                    {
                        "ts": _now_iso(),
                        "action": action,
                        "version": version,
                        "result": result,
                        "detail": detail,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )
    except OSError:
        pass  # install log is best-effort; it must never fail the operation


def _install_or_upgrade(
    source_root: Path,
    install_root: Path,
    version: str,
    *,
    force: bool,
    action: str,
) -> None:
    source_root = source_root.resolve()
    install_root = _resolve_install_root(install_root)
    if source_root == install_root:
        raise InstallerError("install root must not equal the source root")
    version = _validate_version(version)
    if not (source_root / "src" / "coevo" / "version.py").is_file():
        raise InstallerError("source root is not a Coevo repository (missing src/coevo/version.py)")
    if not (source_root / "scripts" / "run_cockpit.py").is_file():
        raise InstallerError("source root is missing scripts/run_cockpit.py")

    target = install_root / APP_DIR / version
    if target.exists():
        if not force:
            raise InstallerError(
                f"version {version} is already installed at {target} "
                "(use --force to overwrite)"
            )
        shutil.rmtree(target)

    install_root.mkdir(parents=True, exist_ok=True)
    manifest = _copy_bundle(source_root, target)
    try:
        manifest_sha256 = _write_manifest(install_root, version, manifest)
        _verify_manifest(install_root, version)
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise

    entries = _read_releases(install_root)
    previous = _read_pointer(install_root) if (install_root / CURRENT_POINTER).exists() else None
    entries = [
        {**entry, "status": "archived"}
        for entry in entries
        if entry.get("version") != version
    ]
    entries.append(
        {
            "version": version,
            "action": action,
            "installed_at": _now_iso(),
            "previous": previous,
            "manifest_sha256": manifest_sha256,
            "status": "current",
        }
    )
    _write_releases(install_root, entries)
    _write_pointer(install_root, version)
    _append_log(install_root, action, version, "ok")


def _rollback(install_root: Path) -> None:
    install_root = _resolve_install_root(install_root)
    current = _read_pointer(install_root)
    entries = _read_releases(install_root)
    by_version = {str(entry.get("version")): entry for entry in entries}
    current_entry = by_version.get(current)
    if current_entry is None:
        raise InstallerError(f"no release record for current version {current}")
    previous = current_entry.get("previous")
    if not isinstance(previous, str) or not previous:
        raise InstallerError("no previous version available for rollback")
    _validate_version(previous)
    if not (install_root / APP_DIR / previous).is_dir():
        raise InstallerError(
            f"previous version {previous} is missing; refusing rollback"
        )
    _verify_manifest(install_root, previous)
    entries = [
        {**entry, "status": "archived" if entry.get("version") == current else entry.get("status")}
        for entry in entries
    ]
    entries.append(
        {
            "version": previous,
            "action": "rollback",
            "installed_at": _now_iso(),
            "previous": current,
            "manifest_sha256": by_version[previous].get("manifest_sha256"),
            "status": "current",
        }
    )
    _write_releases(install_root, entries)
    _write_pointer(install_root, previous)
    _append_log(install_root, "rollback", previous, "ok")


def _uninstall(install_root: Path, *, all_versions: bool) -> None:
    install_root = _resolve_install_root(install_root)
    if all_versions:
        for name in (APP_DIR, MANIFEST_DIR, RELEASES_FILE, CURRENT_POINTER):
            target = install_root / name
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            elif target.exists():
                target.unlink(missing_ok=True)
        _append_log(install_root, "uninstall-all", "", "ok")
        return
    current = _read_pointer(install_root)
    app_dir = install_root / APP_DIR / current
    manifest = install_root / MANIFEST_DIR / f"{current}.sha256"
    if app_dir.is_dir():
        shutil.rmtree(app_dir)
    manifest.unlink(missing_ok=True)
    pointer = install_root / CURRENT_POINTER
    if pointer.exists() and pointer.read_text(encoding="utf-8").strip() == current:
        pointer.unlink(missing_ok=True)
    _append_log(install_root, "uninstall", current, "ok")


def _check(install_root: Path) -> int:
    install_root = _resolve_install_root(install_root)
    try:
        current = _read_pointer(install_root)
        if not (install_root / APP_DIR / current).is_dir():
            raise InstallerError(f"current version {current} is missing")
        _verify_manifest(install_root, current)
        _read_releases(install_root)
        data_dir = install_root
        log_dir = install_root / "logs"
        if not data_dir.is_dir() or not log_dir.is_dir():
            raise InstallerError("data/log directories are missing")
    except InstallerError as exc:
        print(f"check failed: {exc}", file=sys.stderr)
        return 1
    print(f"check ok: current={current}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline install/upgrade/rollback/uninstall for Coevo cockpit"
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=("install", "upgrade", "rollback", "uninstall", "check"),
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Coevo repository root (default: this repository)",
    )
    parser.add_argument(
        "--install-root",
        type=Path,
        default=Path(
            os.environ.get("LOCALAPPDATA", str(Path.home()))
        )
        / "KaiwuAgent",
        help="installation root (default: %%LOCALAPPDATA%%\\KaiwuAgent)",
    )
    parser.add_argument("--version", default=None, help="semantic version label")
    parser.add_argument("--force", action="store_true", help="overwrite an existing version")
    parser.add_argument("--all", dest="all_versions", action="store_true", help="uninstall all versions")
    args = parser.parse_args(argv)

    install_root = _resolve_install_root(args.install_root)
    try:
        if args.action == "check":
            return _check(install_root)
        version = args.version or _version_from_source(args.source_root.resolve())
        _validate_version(version)
        with InstallLock(install_root / LOCK_RELATIVE) as lock:
            if args.action in ("install", "upgrade"):
                _install_or_upgrade(
                    args.source_root,
                    install_root,
                    version,
                    force=args.force,
                    action=args.action,
                )
                print(f"{args.action} ok: {version} -> {install_root}")
            elif args.action == "rollback":
                _rollback(install_root)
                print(f"rollback ok: current -> {_read_pointer(install_root)}")
            elif args.action == "uninstall":
                _uninstall(install_root, all_versions=args.all_versions)
                print("uninstall ok")
        return 0
    except InstallerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        try:
            _append_log(install_root, args.action, args.version or "", "failed", str(exc))
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
