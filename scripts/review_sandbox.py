"""Read-only review sandbox governance guard (std-lib only, zero download).

Lifecycle for one independent reviewer role (verifier or security reviewer):

  prepare  -> isolated clone of the pinned repo commit plus a pin manifest.
              The pin and the clone live under ROOT/loop/runtime/review-sandboxes
              (gitignored), so the main worktree is never touched.
  check    -> verify the sandbox is still exactly the pinned commit:
              * git HEAD must equal the pinned commit (no commits allowed);
              * every tracked path outside loop/ must be byte-identical to the
                pinned manifest (no edits, additions, deletions, renames);
              * loop/ record by-products (VERIFICATION.md, tool-audit.jsonl,
                audit-head*) are the only allowed changes and are reported as
                informational evidence, never accepted as source changes.
  discard  -> delete the sandbox clone and its pin (safe-path validated).

The guard is executed by the orchestrator before a reviewer report is
accepted: a violated sandbox voids the review and the report is discarded.
See docs/process/independent-review-governance.md for the full policy.

Verification venue (REVIEW-SANDBOX-2): the sandbox provides the read-only
guard, static review and fmt/lint/unit/targeted checks. The authoritative
full quality gate (crypto/GmSSL/opencode-dependent tests) runs on the MAIN
worktree pinned to the reviewed commit, because a junction-mounted .tools is
rejected by the reparse-point hardening and a copied .tools cannot reproduce
the GmSSL helper/DLL interaction (GMH-E-MAGIC) and opencode config resolution
(see the governance doc).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SANDBOX_ROOT = ROOT / "loop" / "runtime" / "review-sandboxes"
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}")
ALLOWED_ROLES = {"verifier", "security-reviewer"}
SCHEMA = "review-sandbox/v1"


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def _git(repo: Path, *args: str, timeout: int = 300) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "git %s failed (%d): %s" % (" ".join(args), proc.returncode, proc.stderr.strip()[:500])
        )
    return proc.stdout


def tracked_manifest(repo: Path) -> str:
    """SHA-256 over sorted ls-tree entries of every tracked path outside loop/."""
    out = _git(repo, "ls-tree", "-r", "HEAD")
    entries = []
    for line in out.splitlines():
        if not line:
            continue
        tab = line.find("\t")
        if tab < 0:
            continue
        path = line[tab + 1 :]
        if path.startswith("loop/"):
            continue
        entries.append(line)
    blob = ("\n".join(sorted(entries)) + "\n").encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def status_changes(repo: Path) -> list[tuple[str, list[str]]]:
    """Parse porcelain status into (code, [paths]) tuples; rename-aware."""
    out = _git(repo, "status", "--porcelain", "--untracked-files=all")
    changes: list[tuple[str, list[str]]] = []
    for line in out.splitlines():
        if not line:
            continue
        code = line[:2]
        body = line[3:]
        if code[0] == "R" and " -> " in body:
            left, right = body.split(" -> ", 1)
            changes.append((code, [left.strip(), right.strip()]))
        else:
            changes.append((code, [body]))
    return changes


class ReviewSandbox:
    def __init__(self, repo_root: Path, sandbox_root: Path):
        self.repo_root = Path(repo_root).resolve()
        self.sandbox_root = Path(sandbox_root).resolve()

    # ---------- path safety ----------
    def _target(self, name: str) -> Path:
        if not NAME_RE.fullmatch(name):
            raise ValueError("unsafe sandbox name: %r" % name)
        base = self.sandbox_root
        target = (base / name).resolve()
        if target == base or base not in target.parents:
            raise ValueError("sandbox target escapes sandbox root: %r" % name)
        return target

    def _pin_path(self, name: str) -> Path:
        self._target(name)  # validate name
        return self.sandbox_root / (name + ".pin.json")

    # ---------- lifecycle ----------
    def prepare(self, name: str, commit: str, role: str) -> dict:
        if role not in ALLOWED_ROLES:
            raise ValueError("unsupported reviewer role: %r" % role)
        target = self._target(name)
        pin_path = self._pin_path(name)
        if target.exists() or pin_path.exists():
            raise RuntimeError("sandbox already exists: %r" % name)
        self.sandbox_root.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--no-hardlinks", "--no-local", str(self.repo_root), str(target)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        # Isolation guard: the prepared sandbox must be a standalone git
        # worktree whose toplevel is the sandbox directory itself, and it must
        # not carry runtime material (loop/runtime, .tools, nested sandboxes)
        # from the source repository. Without this guard a broken preparation
        # can produce a plain directory inside the source worktree, and each
        # later run copies that directory into itself, nesting
        # review-sandboxes inside review-sandboxes without bound.
        try:
            self._assert_isolated(target)
        except RuntimeError:
            _rmtree_retry(target)
            raise
        head = _git(target, "rev-parse", "HEAD").strip()
        if commit != "HEAD":
            _git(target, "checkout", "--detach", commit)
            head = _git(target, "rev-parse", "HEAD").strip()
        pin = {
            "schema": SCHEMA,
            "name": name,
            "role": role,
            "commit": head,
            "prepared_at": _now(),
            "manifest": tracked_manifest(target),
            "protected": "all tracked paths outside loop/",
        }
        pin_path.write_text(
            json.dumps(pin, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return {"ok": True, "sandbox": str(target), "pin": str(pin_path), **pin}

    def _assert_isolated(self, target: Path) -> None:
        """Raise unless target is a standalone clone with no leaked runtime dirs.

        Leaked paths are exactly the ones that caused the recursive
        review-sandboxes nesting: ``loop/runtime`` (which holds the sandbox
        root itself), ``.tools``, and any nested ``review-sandboxes`` tree.
        """
        toplevel = _git(target, "rev-parse", "--show-toplevel").strip()
        if Path(toplevel).resolve() != target.resolve():
            raise RuntimeError(
                "sandbox isolation violation: clone resolves to %r, not the sandbox"
                % toplevel
            )
        for leaked in ("loop/runtime", ".tools", "loop/runtime/review-sandboxes"):
            if (target / leaked).exists():
                raise RuntimeError(
                    "sandbox isolation violation: %s leaked into the clone" % leaked
                )

    def check(self, name: str) -> dict:
        target = self._target(name)
        pin_path = self._pin_path(name)
        if not target.exists() or not pin_path.exists():
            return {"ok": False, "missing": True, "sandbox": str(target), "pin": str(pin_path)}
        pin = json.loads(pin_path.read_text(encoding="utf-8"))
        violations: list[dict] = []
        loop_delta: list[dict] = []
        head = _git(target, "rev-parse", "HEAD").strip()
        if head != pin.get("commit"):
            violations.append({"kind": "head-mismatch", "expected": pin.get("commit"), "actual": head})
        try:
            manifest = tracked_manifest(target)
        except RuntimeError as exc:
            violations.append({"kind": "manifest-error", "detail": str(exc)})
            manifest = None
        if manifest is not None and manifest != pin.get("manifest"):
            violations.append({"kind": "manifest-mismatch", "expected": pin.get("manifest"), "actual": manifest})
        for code, paths in status_changes(target):
            for path in paths:
                item = {"code": code, "path": path}
                if path.startswith("loop/"):
                    loop_delta.append(item)
                else:
                    violations.append({"kind": "protected-change", **item})
        return {
            "ok": not violations,
            "missing": False,
            "name": name,
            "role": pin.get("role"),
            "head": head,
            "pinned_commit": pin.get("commit"),
            "violations": violations,
            "loop_delta": loop_delta,
        }

    def discard(self, name: str) -> dict:
        target = self._target(name)
        pin_path = self._pin_path(name)
        removed_target = target.exists()
        removed_pin = pin_path.exists()
        if removed_target:
            _rmtree_retry(target)
        if removed_pin:
            pin_path.unlink()
        return {"ok": True, "sandbox": str(target), "removed_sandbox": removed_target, "removed_pin": removed_pin}


def _clear_readonly(func, path, exc_info):
    """onexc helper: clear the read-only attribute and retry once."""
    try:
        os.chmod(path, 0o777)
    except OSError:
        pass
    try:
        func(path)
    except OSError:
        pass


def _rmtree_retry(path: Path, attempts: int = 4) -> None:
    """Robust recursive delete: transient Windows lock/AV holds retried.

    Falls back to a long-path-aware walker (NT ``\\\\?\\`` namespace) when the
    tree exceeds the legacy MAX_PATH limit that shutil.rmtree cannot traverse.
    """
    last_error = None
    for _ in range(attempts):
        try:
            shutil.rmtree(path, onexc=_clear_readonly)
            return
        except OSError as exc:
            last_error = exc
            time.sleep(0.25)
    _rmtree_long(path)


def _rmtree_long(path: Path) -> None:
    """Iterative depth-first deletion using the ``\\\\?\\`` NT namespace.

    Handles arbitrarily deep trees and paths beyond 260 characters. Reparse
    points (junctions/symlinks) are removed as leaves and never traversed, so
    a malformed sandbox cannot make the walker loop.
    """
    root = "\\\\?\\" + str(path.resolve())
    stack: list[tuple[str, bool]] = [(root, False)]
    while stack:
        current, finalize = stack.pop()
        if finalize:
            try:
                os.rmdir(current)
            except OSError:
                pass
            continue
        stack.append((current, True))
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        for entry in entries:
            full = os.path.join(current, entry.name)
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError:
                continue
            if is_dir:
                stack.append((full, False))
                continue
            try:
                if entry.is_symlink():
                    os.rmdir(full)
                else:
                    os.chmod(full, 0o777)
                    os.remove(full)
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only review sandbox guard")
    parser.add_argument("--root", default=str(ROOT), help="repo root (default: parent of scripts/)")
    sub = parser.add_subparsers(dest="command", required=True)
    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--name", required=True)
    p_prepare.add_argument("--role", required=True, choices=sorted(ALLOWED_ROLES))
    p_prepare.add_argument("--ref", default="HEAD")
    p_check = sub.add_parser("check")
    p_check.add_argument("--name", required=True)
    p_discard = sub.add_parser("discard")
    p_discard.add_argument("--name", required=True)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    sandbox_root = root / "loop" / "runtime" / "review-sandboxes"
    if not root.joinpath(".git").is_dir():
        print(json.dumps({"ok": False, "error": "not a git repo root: %s" % root}))
        return 30
    guard = ReviewSandbox(root, sandbox_root)
    try:
        if args.command == "prepare":
            result = guard.prepare(args.name, args.ref, args.role)
            code = 0
        elif args.command == "check":
            result = guard.check(args.name)
            code = 0 if result.get("ok") else (3 if result.get("missing") else 2)
        else:
            result = guard.discard(args.name)
            code = 0
    except (ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 30
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
