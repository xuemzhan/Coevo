"""RELEASE-1: pre-release readiness check (stdlib, fail-closed).

Runs the checks an operator wants before cutting a release and prints a
structured JSON report. Exit codes: 0 = ready, 1 = warnings (degraded),
2 = critical (do not release).

Checks
------
* git working tree is clean;
* ``src/coevo/version.py`` is semantic and (when ``--expect-version`` is
  given) matches it;
* audit seal is ``fully-sealed`` (unsealed tail = warning, failure =
  critical);
* ``secret_scan.py`` reports no findings;
* the traceability matrix is consistent (no dangling entries);
* ``loop/STATE.json`` is ``done`` with no blocking issue;
* no backlog item is ``in-progress`` (``ready`` items = warning:
  explicitly deferred).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


_VERSION_RE = re.compile(r'^VERSION:\s*str\s*=\s*"(\d+\.\d+\.\d+)"\s*$', re.MULTILINE)
FORBIDDEN_TRACKED_ARTIFACTS = re.compile(
    r"(^|/)(__pycache__($|/)|[^/]*\.pyc$|[^/]*\.db(-wal|-shm)?$|"
    r"[^/]*\.pdb$|helper\.exe$|private-key-handles-[^/]*\.json$)",
    re.IGNORECASE,
)


def _run(repo_root: Path, command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )


def check_git_clean(repo_root: Path) -> dict[str, Any]:
    result = _run(repo_root, ["git", "status", "--porcelain"])
    dirty = [line for line in result.stdout.splitlines() if line.strip()]
    return {
        "name": "git_clean",
        "ok": not dirty,
        "level": "ok" if not dirty else "critical",
        "detail": "clean" if not dirty else f"{len(dirty)} uncommitted change(s)",
    }


def check_version(repo_root: Path, expect_version: str | None) -> dict[str, Any]:
    version_py = repo_root / "src" / "coevo" / "version.py"
    if not version_py.is_file():
        return {"name": "version", "ok": False, "level": "critical", "detail": "version.py missing"}
    match = _VERSION_RE.search(version_py.read_text(encoding="utf-8"))
    if match is None:
        return {"name": "version", "ok": False, "level": "critical", "detail": "version.py malformed"}
    actual = match.group(1)
    if expect_version is not None and actual != expect_version:
        return {
            "name": "version",
            "ok": False,
            "level": "critical",
            "detail": f"expected {expect_version}, got {actual}",
        }
    return {"name": "version", "ok": True, "level": "ok", "detail": actual}


def check_audit(repo_root: Path, python: str | None = None) -> dict[str, Any]:
    result = _run(
        repo_root,
        [python or sys.executable, str(repo_root / "scripts" / "audit_seal.py"), "verify"],
    )
    status = ""
    try:
        status = json.loads(result.stdout or "{}").get("status", "")
    except json.JSONDecodeError:
        pass
    if status == "fully-sealed":
        return {"name": "audit", "ok": True, "level": "ok", "detail": "fully-sealed"}
    if status == "valid-prefix-with-unsealed-tail":
        return {
            "name": "audit",
            "ok": True,
            "level": "warning",
            "detail": "unsealed tail (re-seal before release)",
        }
    return {
        "name": "audit",
        "ok": False,
        "level": "critical",
        "detail": (result.stderr or result.stdout or "verify failed").strip()[:200],
    }


def check_secret_scan(repo_root: Path, python: str | None = None) -> dict[str, Any]:
    result = _run(
        repo_root,
        [python or sys.executable, str(repo_root / "scripts" / "secret_scan.py")],
    )
    return {
        "name": "secret_scan",
        "ok": result.returncode == 0,
        "level": "ok" if result.returncode == 0 else "critical",
        "detail": "clean" if result.returncode == 0 else result.stdout.strip()[:200],
    }


def check_traceability(repo_root: Path, python: str | None = None) -> dict[str, Any]:
    result = _run(
        repo_root,
        [python or sys.executable, str(repo_root / "scripts" / "traceability_check.py")],
    )
    return {
        "name": "traceability",
        "ok": result.returncode == 0,
        "level": "ok" if result.returncode == 0 else "critical",
        "detail": "consistent" if result.returncode == 0 else result.stderr.strip()[:200],
    }


def check_state(repo_root: Path) -> dict[str, Any]:
    state_path = repo_root / "loop" / "STATE.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"name": "state", "ok": False, "level": "critical", "detail": str(exc)}
    status = state.get("status")
    blocking = state.get("blocking_issue")
    if status != "done" or blocking:
        return {
            "name": "state",
            "ok": False,
            "level": "critical",
            "detail": f"status={status} blocking={blocking!r}",
        }
    return {"name": "state", "ok": True, "level": "ok", "detail": f"done ({state.get('current_item')})"}


def check_backlog(repo_root: Path) -> dict[str, Any]:
    backlog = repo_root / "loop" / "BACKLOG.yaml"
    text = backlog.read_text(encoding="utf-8")
    in_progress = len(re.findall(r"(?m)^\s+status:\s*in-progress\s*$", text))
    ready = len(re.findall(r"(?m)^\s+status:\s*ready\s*$", text))
    if in_progress:
        return {
            "name": "backlog",
            "ok": False,
            "level": "critical",
            "detail": f"{in_progress} in-progress item(s)",
        }
    if ready:
        return {
            "name": "backlog",
            "ok": True,
            "level": "warning",
            "detail": f"{ready} ready item(s) explicitly deferred",
        }
    return {"name": "backlog", "ok": True, "level": "ok", "detail": "all items done"}


def check_delivery_artifacts(repo_root: Path) -> dict[str, Any]:
    """REVIEW2-11 delivery gate: no runtime caches/keys/prototype in a release.

    Hard fails (critical):
    * any tracked path matching __pycache__ / *.pyc / *.db(-wal|-shm) /
      *.pdb / helper.exe / private-key-handles-*.json;
    * a production composition root (scripts/run_cockpit.py) referencing the
      GmSSL prototype provider;
    * secret-scan fixture exemptions expanding beyond tests/ + loop/.

    Warning: the Win7 separation doc missing its release markers.
    """

    result = _run(repo_root, ["git", "ls-files"])
    forbidden = [
        line
        for line in result.stdout.splitlines()
        if FORBIDDEN_TRACKED_ARTIFACTS.search(line)
    ]
    if forbidden:
        return {
            "name": "delivery_artifacts",
            "ok": False,
            "level": "critical",
            "detail": f"forbidden tracked artifacts: {forbidden[:5]}",
        }
    production_runner = repo_root / "scripts" / "run_cockpit.py"
    if (
        production_runner.is_file()
        and "GmsslPrototypeProvider"
        in production_runner.read_text(encoding="utf-8")
    ):
        return {
            "name": "delivery_artifacts",
            "ok": False,
            "level": "critical",
            "detail": "run_cockpit.py references the GmSSL prototype provider",
        }
    secret_scan = (repo_root / "scripts" / "secret_scan.py")
    if (
        not secret_scan.is_file()
        or "_FIXTURE_ALLOWED_PREFIXES" not in secret_scan.read_text(encoding="utf-8")
        or '"tests/"' not in secret_scan.read_text(encoding="utf-8")
    ):
        return {
            "name": "delivery_artifacts",
            "ok": False,
            "level": "critical",
            "detail": "secret-scan fixture exemption is not narrowly scoped",
        }
    win7_doc = repo_root / "docs" / "architecture" / "win7-compat-branch.md"
    if not win7_doc.is_file():
        return {
            "name": "delivery_artifacts",
            "ok": False,
            "level": "critical",
            "detail": "win7-compat-branch.md missing",
        }
    win7 = win7_doc.read_text(encoding="utf-8")
    missing_markers = [marker for marker in ("独立", "发布") if marker not in win7]
    if missing_markers:
        return {
            "name": "delivery_artifacts",
            "ok": False,
            "level": "warning",
            "detail": f"win7 doc missing release markers: {missing_markers}",
        }
    return {
        "name": "delivery_artifacts",
        "ok": True,
        "level": "ok",
        "detail": "clean",
    }


def build_report(
    repo_root: Path,
    *,
    expect_version: str | None,
    python: str | None,
) -> dict[str, Any]:
    checks = [
        check_git_clean(repo_root),
        check_version(repo_root, expect_version),
        check_state(repo_root),
        check_backlog(repo_root),
        check_audit(repo_root, python),
        check_secret_scan(repo_root, python),
        check_traceability(repo_root, python),
        check_delivery_artifacts(repo_root),
    ]
    critical = [c for c in checks if not c["ok"] and c["level"] == "critical"]
    warnings = [c for c in checks if not c["ok"] or c["level"] == "warning"]
    status = "ok" if not critical and not warnings else (
        "warning" if not critical else "critical"
    )
    return {
        "ok": not critical and not warnings,
        "status": status,
        "version": next((c["detail"] for c in checks if c["name"] == "version"), ""),
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo pre-release readiness check")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expect-version", default=None)
    parser.add_argument("--python", default=None)
    args = parser.parse_args(argv)
    report = build_report(
        args.repo_root.resolve(),
        expect_version=args.expect_version,
        python=args.python,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if report["status"] == "ok" else (1 if report["status"] == "warning" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
