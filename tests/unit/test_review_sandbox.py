"""Unit tests for the read-only review sandbox guard (GOV-REVIEW-1)."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("review_sandbox", ROOT / "scripts/review_sandbox.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise AssertionError("git %s failed: %s" % (" ".join(args), proc.stderr))
    return proc.stdout


class ReviewSandboxGuardTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        self.sandboxes = Path(self._tmp.name) / "sandboxes"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "test")
        (self.repo / "src").mkdir()
        (self.repo / "docs").mkdir()
        (self.repo / "loop").mkdir()
        (self.repo / "src" / "a.py").write_text("VALUE=1\n", encoding="utf-8")
        (self.repo / "docs" / "d.md").write_text("doc\n", encoding="utf-8")
        (self.repo / "Makefile").write_text("all:\n", encoding="utf-8")
        (self.repo / "loop" / "VERIFICATION.md").write_text("record\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "initial")
        self.commit = git(self.repo, "rev-parse", "HEAD").strip()
        self.guard = guard.ReviewSandbox(self.repo, self.sandboxes)

    def tearDown(self):
        self._tmp.cleanup()

    def test_prepare_creates_isolated_copy_and_pin(self):
        result = self.guard.prepare("v1", "HEAD", "verifier")
        self.assertTrue(result["ok"])
        target = self.sandboxes / "v1"
        self.assertTrue(target.is_dir())
        self.assertEqual(self.commit, git(target, "rev-parse", "HEAD").strip())
        pin = json.loads((self.sandboxes / "v1.pin.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["commit"], self.commit)
        self.assertEqual(pin["role"], "verifier")
        self.assertEqual(result["manifest"], pin["manifest"])
        self.assertTrue(self.guard.check("v1")["ok"])

    def test_prepare_clone_is_standalone_and_leaks_nothing(self):
        self.guard.prepare("v1", "HEAD", "verifier")
        target = self.sandboxes / "v1"
        # The clone must be a standalone git worktree, not a plain directory
        # inside the source repository (walk-up .git discovery must not leak).
        toplevel = git(target, "rev-parse", "--show-toplevel").strip()
        self.assertEqual(Path(toplevel).resolve(), target.resolve())
        # Untracked runtime material must never leak into the clone.
        self.assertFalse((target / "loop" / "runtime").exists())
        self.assertFalse((target / ".tools").exists())
        self.assertFalse((target / "loop" / "runtime" / "review-sandboxes").exists())

    def test_assert_isolated_rejects_plain_dir_inside_another_repo(self):
        # Simulate the failure mode that produced the recursive nesting: a
        # "sandbox" that is only a plain directory inside the source repo.
        bad = self.repo / "loop" / "runtime" / "review-sandboxes" / "bad"
        bad.mkdir(parents=True)
        with self.assertRaises(RuntimeError):
            self.guard._assert_isolated(bad)

    def test_assert_isolated_rejects_leaked_runtime_dir(self):
        iso = self.sandboxes / "iso"
        iso.mkdir(parents=True)
        git(iso, "init", "-q")
        git(iso, "config", "user.email", "test@example.com")
        git(iso, "config", "user.name", "test")
        (iso / "f.txt").write_text("x\n", encoding="utf-8")
        git(iso, "add", "-A")
        git(iso, "commit", "-q", "-m", "init")
        # A leaked loop/runtime (or .tools) inside an otherwise valid clone is
        # a containment violation and must be rejected.
        (iso / "loop" / "runtime").mkdir(parents=True)
        with self.assertRaises(RuntimeError):
            self.guard._assert_isolated(iso)
        (iso / "loop" / "runtime").rmdir()
        (iso / "loop").rmdir()
        (iso / ".tools").mkdir()
        with self.assertRaises(RuntimeError):
            self.guard._assert_isolated(iso)

    def test_rmtree_retry_removes_readonly_files(self):
        tree = Path(self._tmp.name) / "ro-tree"
        (tree / "sub").mkdir(parents=True)
        target_file = tree / "sub" / "obj.idx"
        target_file.write_bytes(b"pack")
        os.chmod(target_file, 0o444)
        guard._rmtree_retry(tree)
        self.assertFalse(tree.exists())

    def test_prepare_rejects_unknown_role_and_existing_name(self):
        with self.assertRaises(ValueError):
            self.guard.prepare("x", "HEAD", "auditor")
        self.guard.prepare("v1", "HEAD", "verifier")
        with self.assertRaises(RuntimeError):
            self.guard.prepare("v1", "HEAD", "security-reviewer")

    def test_check_detects_protected_edit(self):
        self.guard.prepare("v1", "HEAD", "verifier")
        target = self.sandboxes / "v1"
        (target / "src" / "a.py").write_text("VALUE=2\n", encoding="utf-8")
        result = self.guard.check("v1")
        self.assertFalse(result["ok"])
        self.assertTrue(any(v["kind"] == "protected-change" and v["path"] == "src/a.py" for v in result["violations"]))

    def test_check_detects_untracked_protected_file(self):
        self.guard.prepare("v1", "HEAD", "verifier")
        (self.sandboxes / "v1" / "src" / "evil.py").write_text("x=1\n", encoding="utf-8")
        result = self.guard.check("v1")
        self.assertFalse(result["ok"])
        self.assertTrue(any(v["kind"] == "protected-change" and v["path"] == "src/evil.py" for v in result["violations"]))

    def test_check_detects_new_commit_in_sandbox(self):
        self.guard.prepare("v1", "HEAD", "verifier")
        target = self.sandboxes / "v1"
        git(target, "config", "user.email", "test@example.com")
        git(target, "config", "user.name", "test")
        (target / "loop" / "EXTRA.md").write_text("x\n", encoding="utf-8")
        git(target, "add", "-A")
        git(target, "commit", "-q", "-m", "sneaky")
        result = self.guard.check("v1")
        self.assertFalse(result["ok"])
        self.assertTrue(any(v["kind"] == "head-mismatch" for v in result["violations"]))

    def test_check_accepts_loop_record_byproducts(self):
        self.guard.prepare("v1", "HEAD", "verifier")
        target = self.sandboxes / "v1"
        with (target / "loop" / "VERIFICATION.md").open("a", encoding="utf-8") as stream:
            stream.write("## gate run\n")
        result = self.guard.check("v1")
        self.assertTrue(result["ok"], result)
        self.assertTrue(any(d["path"] == "loop/VERIFICATION.md" for d in result["loop_delta"]))

    def test_check_reports_missing_sandbox_or_pin(self):
        self.guard.prepare("v1", "HEAD", "verifier")
        (self.sandboxes / "v1.pin.json").unlink()
        result = self.guard.check("v1")
        self.assertTrue(result["missing"])
        self.assertFalse(result["ok"])

    def test_discard_removes_sandbox_and_pin(self):
        self.guard.prepare("v1", "HEAD", "verifier")
        result = self.guard.discard("v1")
        self.assertTrue(result["removed_sandbox"])
        self.assertTrue(result["removed_pin"])
        self.assertFalse((self.sandboxes / "v1").exists())
        self.assertFalse((self.sandboxes / "v1.pin.json").exists())

    def test_discard_rejects_unsafe_names(self):
        for bad in ("../escape", "a/b", ".", "", "a" * 80):
            with self.assertRaises(ValueError):
                self.guard.discard(bad)

    def test_manifest_excludes_loop_records_only(self):
        self.guard.prepare("v1", "HEAD", "verifier")
        target = self.sandboxes / "v1"
        # manifest must be stable even if loop/ records grow
        before = self.guard.check("v1")
        with (target / "loop" / "VERIFICATION.md").open("a", encoding="utf-8") as stream:
            stream.write("more\n")
        after = self.guard.check("v1")
        self.assertTrue(before["ok"] and after["ok"])
        self.assertEqual(before["head"], after["head"])


if __name__ == "__main__":
    unittest.main()
