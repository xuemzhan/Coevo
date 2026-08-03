"""RELEASE-1: pre-release readiness check tests."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "release_check", ROOT / "scripts" / "release_check.py"
)
release_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_check)


class ReleaseCheckTests(unittest.TestCase):
    def _repo(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "src" / "coevo").mkdir(parents=True)
        (root / "loop").mkdir(parents=True)
        (root / "src" / "coevo" / "version.py").write_text(
            'VERSION: str = "1.2.3"\n', encoding="utf-8"
        )
        (root / "loop" / "STATE.json").write_text(
            json.dumps({"status": "done", "blocking_issue": "", "current_item": "X"})
            + "\n",
            encoding="utf-8",
        )
        (root / "loop" / "BACKLOG.yaml").write_text(
            "items:\n  - id: A\n    status: done\n", encoding="utf-8"
        )
        return root

    def test_version_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self.assertTrue(release_check.check_version(root, None)["ok"])
            self.assertTrue(release_check.check_version(root, "1.2.3")["ok"])
            self.assertFalse(release_check.check_version(root, "2.0.0")["ok"])

    def test_state_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self.assertTrue(release_check.check_state(root)["ok"])
            (root / "loop" / "STATE.json").write_text(
                json.dumps({"status": "blocked", "blocking_issue": "x"}) + "\n",
                encoding="utf-8",
            )
            self.assertFalse(release_check.check_state(root)["ok"])

    def test_backlog_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self.assertTrue(release_check.check_backlog(root)["ok"])
            (root / "loop" / "BACKLOG.yaml").write_text(
                "items:\n  - id: A\n    status: in-progress\n", encoding="utf-8"
            )
            self.assertFalse(release_check.check_backlog(root)["ok"])
            (root / "loop" / "BACKLOG.yaml").write_text(
                "items:\n  - id: A\n    status: ready\n", encoding="utf-8"
            )
            check = release_check.check_backlog(root)
            self.assertTrue(check["ok"])
            self.assertEqual("warning", check["level"])

    def test_subprocess_checks_and_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)

            def fake_run(repo, command):
                joined = " ".join(command)
                if "audit_seal.py" in joined:
                    return subprocess.CompletedProcess(
                        [], 0, stdout=json.dumps({"status": "fully-sealed"}), stderr=""
                    )
                if "secret_scan.py" in joined:
                    return subprocess.CompletedProcess([], 0, stdout="secret scan ok", stderr="")
                if "traceability_check.py" in joined:
                    return subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
                if command and command[0] == "git":
                    return subprocess.CompletedProcess([], 0, stdout="", stderr="")
                return subprocess.CompletedProcess([], 1, stdout="", stderr="boom")

            with mock.patch.object(release_check, "_run", side_effect=fake_run):
                report = release_check.build_report(root, expect_version="1.2.3", python="py")
            self.assertEqual("ok", report["status"], report)
            self.assertTrue(report["ok"])

            def fail_audit(repo, command):
                if "audit_seal.py" in " ".join(command):
                    return subprocess.CompletedProcess(
                        [], 1, stdout="", stderr="signature invalid"
                    )
                return fake_run(repo, command)

            with mock.patch.object(release_check, "_run", side_effect=fail_audit):
                report = release_check.build_report(root, expect_version="1.2.3", python="py")
            self.assertEqual("critical", report["status"])

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)

            def clean_git(repo, command):
                if command and command[0] == "git":
                    return subprocess.CompletedProcess([], 0, stdout="", stderr="")
                if "audit_seal.py" in " ".join(command):
                    return subprocess.CompletedProcess(
                        [], 0, stdout=json.dumps({"status": "fully-sealed"}), stderr=""
                    )
                return subprocess.CompletedProcess([], 0, stdout="ok", stderr="")

            with mock.patch.object(release_check, "_run", side_effect=clean_git):
                code = release_check.main(["--repo-root", str(root)])
            self.assertEqual(0, code)
            (root / "dirty.txt").write_text("x", encoding="utf-8")

            def dirty_git(repo, command):
                if command and command[0] == "git":
                    return subprocess.CompletedProcess([], 0, stdout="?? dirty.txt\n", stderr="")
                if "audit_seal.py" in " ".join(command):
                    return subprocess.CompletedProcess(
                        [], 0, stdout=json.dumps({"status": "fully-sealed"}), stderr=""
                    )
                if "secret_scan.py" in " ".join(command) or "traceability_check.py" in " ".join(command):
                    return subprocess.CompletedProcess([], 0, stdout="ok", stderr="")
                return subprocess.CompletedProcess([], 1, stdout="", stderr="boom")

            with mock.patch.object(release_check, "_run", side_effect=dirty_git):
                code = release_check.main(["--repo-root", str(root)])
            self.assertEqual(2, code)


if __name__ == "__main__":
    unittest.main()
