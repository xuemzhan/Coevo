"""OPS-2 / BACKUP-1: scripted backup, verify, restore of Coevo runtime state.

Pure-stdlib tool for the offline production state that is NOT part of
the re-installable app bundle:

* cockpit runtime state: ``cockpit-state.json``, ``cockpit-access.jsonl``,
  ``current`` pointer, ``releases.json``, ``manifests/*``, wrapped-key
  registry (``wrapped-keys.json`` when present);
* audit chain: ``loop/tool-audit.jsonl``, ``loop/audit-head.json``,
  ``loop/audit-head.p7s``, ``loop/audit-signing*.json``,
  ``loop/audit-signing-public*.cer``, ``loop/audit-checkpoint.json``.

Each backup is written to ``<backup-root>/<label>/`` with a SHA-256
manifest (``manifest.json``). ``verify`` re-checks every file;
``restore`` verifies first, refuses while the cockpit single-instance
lock is fresh (a live process may be writing state), and keeps a
``.pre-restore-<ts>`` copy of every replaced file.

Fail-closed: manifest paths must be relative and resolve inside the
install root (no ``..``, no absolute paths, no reparse escapes).
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
from typing import Any, Final


MANIFEST_SCHEMA: Final[str] = "1.0"
_LABEL_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._-]+$")
_STALE_LOCK_SECONDS: Final[int] = 600

# Relative paths (to the install root) that are backed up when present.
STATE_FILES: Final[tuple[str, ...]] = (
    "cockpit-state.json",
    "cockpit-access.jsonl",
    "current",
    "releases.json",
    "wrapped-keys.json",
    "manifests",
    "loop/tool-audit.jsonl",
    "loop/audit-head.json",
    "loop/audit-head.p7s",
    "loop/audit-checkpoint.json",
    "loop/audit-signing.json",
    "loop/audit-signing-public.cer",
)


class BackupError(RuntimeError):
    """Base class for backup/restore failures (fail-closed)."""


class BackupValidationError(BackupError, ValueError):
    """A path, label, or manifest is malformed."""


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(relative: str, install_root: Path) -> Path:
    if not isinstance(relative, str) or not relative:
        raise BackupValidationError("manifest path must be a non-empty string")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise BackupValidationError(f"unsafe manifest path: {relative!r}")
    resolved = (install_root / candidate).resolve()
    try:
        resolved.relative_to(install_root.resolve())
    except ValueError as exc:
        raise BackupValidationError(f"manifest path escapes install root: {relative!r}") from exc
    return resolved


def _validate_label(label: str) -> str:
    if not isinstance(label, str) or not _LABEL_RE.fullmatch(label):
        raise BackupValidationError(
            "label must match ^[A-Za-z0-9._-]+$ (no path separators)"
        )
    return label


def _collect_files(install_root: Path) -> tuple[str, ...]:
    """Return existing state-file relative paths (directories expanded)."""
    found: list[str] = []
    for relative in STATE_FILES:
        source = _safe_relative(relative, install_root)
        if source.is_dir():
            for child in sorted(source.rglob("*")):
                if child.is_file() and not child.is_symlink():
                    found.append(child.relative_to(install_root).as_posix())
        elif source.is_file() and not source.is_symlink():
            found.append(relative)
        else:
            continue
    # Historical signer archives / heads (any thumbprint).
    for pattern in ("loop/audit-signing-*.json", "loop/audit-signing-public-*.cer",
                    "loop/audit-head-*.json", "loop/audit-head-*.p7s"):
        for child in sorted(install_root.glob(pattern)):
            if child.is_file() and not child.is_symlink():
                found.append(child.relative_to(install_root).as_posix())
    return tuple(dict.fromkeys(found))


def backup(
    install_root: Path,
    backup_root: Path,
    label: str,
) -> dict[str, Any]:
    install_root = install_root.resolve()
    backup_root = backup_root.resolve()
    label = _validate_label(label)
    target = backup_root / label
    if target.exists():
        raise BackupValidationError(f"backup label already exists: {label}")
    target.mkdir(parents=True, exist_ok=False)
    entries: list[dict[str, Any]] = []
    skipped: list[str] = []
    for relative in _collect_files(install_root):
        source = _safe_relative(relative, install_root)
        if not source.is_file():
            skipped.append(relative)
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        entries.append(
            {
                "path": relative,
                "size": destination.stat().st_size,
                "sha256": _sha256_file(destination),
            }
        )
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "label": label,
        "created_at": _now_iso(),
        "files": entries,
        "skipped": sorted(skipped),
    }
    _write_manifest(target, manifest)
    return manifest


def _write_manifest(target: Path, manifest: dict[str, Any]) -> None:
    body = json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    tmp = target / f".manifest.{uuid.uuid4().hex}.tmp"
    with tmp.open("wb") as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, target / "manifest.json")


def _read_manifest(target: Path) -> dict[str, Any]:
    path = target / "manifest.json"
    if not path.is_file():
        raise BackupValidationError(f"backup has no manifest: {target}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BackupValidationError("backup manifest is not valid JSON") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise BackupValidationError("backup manifest schema mismatch")
    return manifest


def verify(backup_root: Path, label: str) -> dict[str, Any]:
    backup_root = backup_root.resolve()
    label = _validate_label(label)
    target = backup_root / label
    if not target.is_dir():
        raise BackupValidationError(f"backup not found: {label}")
    manifest = _read_manifest(target)
    problems: list[str] = []
    for entry in manifest.get("files", []):
        relative = entry.get("path")
        if not isinstance(relative, str):
            problems.append("manifest entry missing path")
            continue
        try:
            resolved = _safe_relative(relative, target)
        except BackupValidationError as exc:
            problems.append(str(exc))
            continue
        if not resolved.is_file():
            problems.append(f"missing: {relative}")
            continue
        size = entry.get("size")
        digest = entry.get("sha256")
        if size != resolved.stat().st_size or digest != _sha256_file(resolved):
            problems.append(f"hash/size mismatch: {relative}")
    return {
        "ok": not problems,
        "label": label,
        "files": len(manifest.get("files", [])),
        "problems": problems,
    }


def _lock_fresh(install_root: Path) -> bool:
    lock = install_root / "cockpit.lock"
    if not lock.is_file():
        return False
    try:
        return time.time() - lock.stat().st_mtime < _STALE_LOCK_SECONDS
    except OSError:
        return True


def restore(install_root: Path, backup_root: Path, label: str) -> dict[str, Any]:
    install_root = install_root.resolve()
    backup_root = backup_root.resolve()
    label = _validate_label(label)
    if _lock_fresh(install_root):
        raise BackupValidationError(
            "refusing to restore while the cockpit is running (fresh lock present)"
        )
    result = verify(backup_root, label)
    if not result["ok"]:
        raise BackupValidationError("backup verification failed; refusing restore")
    target = backup_root / label
    manifest = _read_manifest(target)
    pre = install_root / f".pre-restore-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    pre.mkdir(parents=True, exist_ok=True)
    restored: list[str] = []
    for entry in manifest.get("files", []):
        relative = str(entry["path"])
        source = _safe_relative(relative, target)
        destination = _safe_relative(relative, install_root)
        if destination.exists():
            pre_dest = pre / relative
            pre_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, pre_dest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored.append(relative)
    return {"ok": True, "label": label, "restored": restored, "pre_restore": str(pre)}


def list_backups(backup_root: Path) -> list[dict[str, Any]]:
    backup_root = backup_root.resolve()
    if not backup_root.is_dir():
        return []
    result = []
    for child in sorted(backup_root.iterdir()):
        if not child.is_dir():
            continue
        try:
            manifest = _read_manifest(child)
        except BackupValidationError:
            continue
        result.append(
            {
                "label": child.name,
                "created_at": manifest.get("created_at", ""),
                "files": len(manifest.get("files", [])),
            }
        )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo state backup/restore tool")
    parser.add_argument("--action", required=True, choices=("backup", "verify", "restore", "list"))
    parser.add_argument(
        "--install-root",
        type=Path,
        default=Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "KaiwuAgent",
    )
    parser.add_argument("--backup-root", type=Path, default=None)
    parser.add_argument("--label", default=None)
    args = parser.parse_args(argv)
    install_root = args.install_root.resolve()
    backup_root = (
        args.backup_root.resolve()
        if args.backup_root is not None
        else install_root / "backups"
    )
    try:
        if args.action == "list":
            print(json.dumps(list_backups(backup_root), ensure_ascii=False, indent=2))
            return 0
        label = args.label or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        if args.action == "backup":
            manifest = backup(install_root, backup_root, label)
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
        elif args.action == "verify":
            result = verify(backup_root, label)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["ok"] else 1
        else:
            result = restore(install_root, backup_root, label)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except BackupValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
