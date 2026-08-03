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
* single-instance lock is not stale (age < 10 minutes).

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
    try:
        with urllib.request.urlopen(cockpit_url + "/healthz", timeout=3) as response:
            ok = response.status == 200
            return _check("cockpit", ok, f"healthz HTTP {response.status}")
    except Exception as exc:  # noqa: BLE001 - network/connection failures are degraded
        return _check("cockpit", False, f"unreachable ({exc})", level="degraded")


def check_audit(repo_root: Path, python: str | None = None) -> dict[str, Any]:
    interpreter = python or sys.executable
    script = repo_root / "scripts" / "audit_seal.py"
    try:
        result = subprocess.run(
            [interpreter, str(script), "verify"],
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


def build_report(
    *,
    install_root: Path,
    repo_root: Path,
    cockpit_url: str,
    min_free_bytes: int,
    audit_python: str | None,
) -> dict[str, Any]:
    checks = [
        check_dirs(install_root),
        check_disk(install_root, min_free_bytes),
        check_version(install_root),
        check_lock(install_root),
        check_cockpit(cockpit_url),
        check_audit(repo_root, audit_python),
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
    args = parser.parse_args(argv)
    report = build_report(
        install_root=args.install_root.resolve(),
        repo_root=args.repo_root.resolve(),
        cockpit_url=args.cockpit_url,
        min_free_bytes=args.min_free_bytes,
        audit_python=args.audit_python,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if report["status"] == "ok" else (1 if report["status"] == "degraded" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
