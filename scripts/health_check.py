"""OPS-1: offline production health check (stdlib only, fail-closed).

Runs a set of bounded checks against an installed Coevo cockpit and
prints a structured JSON report. Exit codes: 0 = ok, 1 = degraded
(warning), 2 = critical (a check failed).

Checks
------
* data / log directories exist and are writable;
* free disk space above ``--min-free-bytes`` (default 512 MiB);
* the cockpit ``/healthz`` endpoint answers 200 (when ``--cockpit-url``
  is given; default ``http://127.0.0.1:12701``);
* audit seal state via ``scripts/audit_seal.py verify``
  (``fully-sealed`` ok; unsealed tail = degraded; failure = critical);
* installed version consistency (install ``current`` pointer -> app
  version matches ``src/coevo/version.py`` in the installed bundle);
* single-instance lock is not stale (age < 10 minutes);
* a backup exists under ``--backup-root`` (default
  ``<install-root>\\backups``) and the newest backup manifest is at most
  ``--max-backup-age-days`` (default 7) old (OPS-3). A missing or stale
  backup is degraded (recovery posture), never critical;
* the python interpreter pin (``<install-root>\\python-path.txt``, OPS-2)
  exists, is absolute and points to an existing executable (OPS-5).
  A missing or invalid pin is degraded (the watchdog would silently fall
  back to PATH), never critical.

All checks are read-only; no state is modified. This script is meant
for monitoring hooks / scheduled checks, not for the quality gate.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


_VERSION_RE = re.compile(r'^VERSION:\s*str\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
_STALE_LOCK_SECONDS = 600


def _check(label: str, ok: bool, detail: str, level: str = "critical") -> dict[str, Any]:
    return {"name": label, "ok": ok, "level": level if not ok else "ok", "detail": detail}


def check_dirs(install_root: Path) -> dict[str, Any]:
    problems = []
    for name in ("", "logs"):
        target = install_root if not name else install_root / name
        if not target.is_dir():
            problems.append(f"{name or 'data'} dir missing")
            continue
        probe = target / ".health-probe"
        try:
            probe.write_text("probe", encoding="utf-8")
            probe.unlink()
        except OSError as exc:
            problems.append(f"{name or 'data'} dir not writable ({exc})")
    return _check(
        "dirs",
        not problems,
        "; ".join(problems) or "data/log dirs present and writable",
    )


def check_disk(install_root: Path, min_free_bytes: int) -> dict[str, Any]:
    try:
        usage = shutil.disk_usage(install_root)
    except OSError as exc:
        return _check("disk", False, f"cannot stat disk ({exc})")
    ok = usage.free >= min_free_bytes
    detail = (
        f"free={usage.free} min={min_free_bytes}"
        if ok
        else f"free={usage.free} below min={min_free_bytes}"
    )
    return _check("disk", ok, detail)


def check_cockpit(cockpit_url: str) -> dict[str, Any]:
    """Probe /healthz and verify the responder is really the cockpit.

    A 200 from a *different* service occupying the port must not count as
    healthy (AVAIL-2): the body must identify ``service=coevo-cockpit`` and
    ``status=ok``. Any unhealthy responder is degraded (availability
    warning), matching the documented semantics.
    """
    try:
        with urllib.request.urlopen(cockpit_url + "/healthz", timeout=3) as response:
            raw = response.read(4096).decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {}
            ok = (
                response.status == 200
                and payload.get("service") == "coevo-cockpit"
                and payload.get("status") == "ok"
            )
            detail = (
                f"healthz HTTP {response.status} "
                f"service={payload.get('service', '?')!r}"
            )
            return _check("cockpit", ok, detail, level="degraded")
    except Exception as exc:  # noqa: BLE001 - network/connection failures are degraded
        return _check("cockpit", False, f"unreachable ({exc})", level="degraded")


def check_audit(repo_root: Path, python: str | None = None) -> dict[str, Any]:
    interpreter = python or sys.executable
    script = repo_root / "scripts" / "audit_seal.py"
    try:
        result = subprocess.run(
            # --allow-tail: an unsealed tail (e.g. after loop_state/audit
            # writes that precede the next gate seal) is a degraded posture,
            # not a critical failure; genuine tamper still surfaces as an
            # error and stays critical. Matches the lint gate semantics.
            [interpreter, str(script), "verify", "--allow-tail"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        status = ""
        try:
            status = json.loads(result.stdout or "{}").get("status", "")
        except json.JSONDecodeError:
            pass
        if status == "fully-sealed":
            return _check("audit", True, "fully-sealed")
        if status == "valid-prefix-with-unsealed-tail":
            return _check("audit", True, "unsealed tail (run make quality to re-seal)", level="degraded")
        return _check(
            "audit",
            False,
            (result.stderr or result.stdout or "verify failed").strip()[:300],
        )
    except subprocess.TimeoutExpired:
        return _check("audit", False, "audit verify timed out")


def check_version(install_root: Path) -> dict[str, Any]:
    pointer = install_root / "current"
    if not pointer.is_file():
        return _check("version", False, "install root has no current pointer")
    version = pointer.read_text(encoding="utf-8").strip()
    version_py = install_root / "app" / version / "src" / "coevo" / "version.py"
    if not version_py.is_file():
        return _check("version", False, f"app/{version} bundle is incomplete")
    match = _VERSION_RE.search(version_py.read_text(encoding="utf-8"))
    if match is None:
        return _check("version", False, "version.py is malformed")
    return _check(
        "version",
        match.group(1) == version,
        f"pointer={version} source={match.group(1)}",
    )


def check_lock(install_root: Path) -> dict[str, Any]:
    lock = install_root / "cockpit.lock"
    if not lock.is_file():
        return _check("lock", True, "no lock file (not running or already released)")
    try:
        age = time.time() - lock.stat().st_mtime
    except OSError as exc:
        return _check("lock", False, f"cannot stat lock ({exc})")
    if age >= _STALE_LOCK_SECONDS:
        return _check("lock", False, f"stale lock (age {age:.0f}s >= {_STALE_LOCK_SECONDS}s)")
    return _check("lock", True, f"lock fresh (age {age:.0f}s)")


def _verify_backup(
    repo_root: Path, backup_root: Path, label: str
) -> str:
    """Run ``backup_state.py verify`` on one backup; return a short outcome."""
    script = repo_root / "scripts" / "backup_state.py"
    if not script.is_file():
        return "tool missing"
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--action",
                "verify",
                "--backup-root",
                str(backup_root),
                "--label",
                label,
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "timed out"
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return f"failed (exit {result.returncode})"
    if payload.get("ok") is True:
        return "ok"
    return f"failed (exit {result.returncode})"


def check_backup(
    backup_root: Path,
    max_age_days: int,
    *,
    verify: bool = False,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Latest backup freshness (OPS-3); optional integrity verify (OPS-6)."""
    backup_root = backup_root.resolve()
    if not backup_root.is_dir():
        return _check(
            "backup",
            False,
            f"no backup root: {backup_root}",
            level="degraded",
        )
    newest: tuple[str, datetime] | None = None
    for child in sorted(backup_root.iterdir()):
        if not child.is_dir():
            continue
        manifest = child / "manifest.json"
        if not manifest.is_file():
            continue
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            created = datetime.fromisoformat(
                str(payload.get("created_at", "")).replace("Z", "+00:00")
            )
        except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError):
            continue
        if newest is None or created > newest[1]:
            newest = (child.name, created)
    if newest is None:
        return _check(
            "backup",
            False,
            f"no valid backup manifests under {backup_root}",
            level="degraded",
        )
    label, created = newest
    now = datetime.now(UTC)
    if created > now + timedelta(days=1):
        return _check(
            "backup",
            False,
            f"latest backup '{label}' has an invalid future timestamp",
            level="degraded",
        )
    age_days = (now - created).total_seconds() / 86400
    if age_days > max_age_days:
        return _check(
            "backup",
            False,
            f"latest backup '{label}' is {age_days:.1f} days old "
            f"(max {max_age_days})",
            level="degraded",
        )
    detail = f"latest backup '{label}' is {age_days:.2f} days old"
    if verify and repo_root is not None:
        outcome = _verify_backup(repo_root, backup_root, label)
        if outcome != "ok":
            return _check(
                "backup",
                False,
                f"{detail}; integrity check failed ({outcome})",
                level="degraded",
            )
        detail += "; integrity=ok"
    return _check(
        "backup",
        True,
        detail,
    )


def check_pin(install_root: Path) -> dict[str, Any]:
    """Python interpreter pin integrity (OPS-5)."""
    pin = install_root / "python-path.txt"
    if not pin.is_file():
        return _check(
            "pin",
            False,
            "python pin missing (run register-autostart.ps1 -Action PinPython)",
            level="degraded",
        )
    try:
        value = pin.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return _check("pin", False, f"python pin unreadable ({exc})", level="degraded")
    if not value:
        return _check("pin", False, "python pin is empty", level="degraded")
    if not Path(value).is_absolute():
        return _check(
            "pin",
            False,
            f"python pin is not an absolute path: {value}",
            level="degraded",
        )
    if not Path(value).is_file():
        return _check(
            "pin",
            False,
            f"python pin target is missing: {value}",
            level="degraded",
        )
    return _check("pin", True, f"python pin ok: {value}")


def build_report(
    *,
    install_root: Path,
    repo_root: Path,
    cockpit_url: str,
    min_free_bytes: int,
    audit_python: str | None,
    backup_root: Path | None = None,
    max_backup_age_days: int = 7,
    verify_backups: bool = False,
) -> dict[str, Any]:
    checks = [
        check_dirs(install_root),
        check_disk(install_root, min_free_bytes),
        check_version(install_root),
        check_lock(install_root),
        check_cockpit(cockpit_url),
        check_audit(repo_root, audit_python),
        check_pin(install_root),
        check_backup(
            backup_root or install_root / "backups",
            max_backup_age_days,
            verify=verify_backups,
            repo_root=repo_root,
        ),
    ]
    critical = [c for c in checks if not c["ok"] and c["level"] == "critical"]
    degraded = [c for c in checks if not c["ok"] and c["level"] == "degraded"]
    status = "ok" if not critical and not degraded else ("degraded" if not critical else "critical")
    return {
        "ok": not critical and not degraded,
        "status": status,
        "install_root": str(install_root),
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo production health check")
    parser.add_argument(
        "--install-root",
        type=Path,
        default=Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "KaiwuAgent",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--cockpit-url", default="http://127.0.0.1:12701")
    parser.add_argument("--min-free-bytes", type=int, default=512 * 1024 * 1024)
    parser.add_argument("--audit-python", default=None)
    parser.add_argument("--backup-root", type=Path, default=None)
    parser.add_argument("--max-backup-age-days", type=int, default=7)
    parser.add_argument(
        "--verify-backups",
        action="store_true",
        help=(
            "run backup_state.py verify on the newest backup (integrity "
            "hash check; OPS-6)"
        ),
    )
    args = parser.parse_args(argv)
    if args.max_backup_age_days < 1:
        print("error: --max-backup-age-days must be a positive integer", file=sys.stderr)
        return 2
    report = build_report(
        install_root=args.install_root.resolve(),
        repo_root=args.repo_root.resolve(),
        cockpit_url=args.cockpit_url,
        min_free_bytes=args.min_free_bytes,
        audit_python=args.audit_python,
        backup_root=args.backup_root,
        max_backup_age_days=args.max_backup_age_days,
        verify_backups=args.verify_backups,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if report["status"] == "ok" else (1 if report["status"] == "degraded" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
