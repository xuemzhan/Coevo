"""RELEASE-1: pre-release readiness check tests."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
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
        (root / "scripts").mkdir(parents=True)
        (root / "docs" / "architecture").mkdir(parents=True)
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
        # REVIEW2-11: delivery-artifacts check needs a complete fixture.
        (root / "scripts" / "run_cockpit.py").write_text(
            "# production runner (no prototype crypto)\n", encoding="utf-8"
        )
        (root / "scripts" / "secret_scan.py").write_text(
            '_FIXTURE_ALLOWED_PREFIXES = ("tests/", "loop/")\n',
            encoding="utf-8",
        )
        (root / "docs" / "architecture" / "win7-compat-branch.md").write_text(
            "独立发布冻结依赖安全补偿测试计划\n", encoding="utf-8"
        )
        # ENG-OPTIMIZE-3: release report requires fresh gate evidence.
        gate_dir = root / "loop" / "runtime" / "gate-results"
        gate_dir.mkdir(parents=True)
        now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        (gate_dir / "fast-fixture.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "target": "fast",
                    "fingerprint": "a" * 16,
                    "exit_code": 0,
                    "ok": True,
                    "started_at": now,
                    "totals": {"discovered": 10, "passed": 10, "failed": 0, "skipped": 0},
                }
            ),
            encoding="utf-8",
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

    def test_real_backlog_matches_state(self):
        """RECORDS-2: every non-done BACKLOG item must be the current item."""
        backlog = (ROOT / "loop" / "BACKLOG.yaml").read_text(encoding="utf-8")
        state = json.loads((ROOT / "loop" / "STATE.json").read_text(encoding="utf-8"))
        current = state.get("current_item")
        non_done = []
        for match in re.finditer(
            r"  - id: (\S+)\n(.*?)(?=\n  - id: |\Z)", backlog, re.S
        ):
            ident = match.group(1)
            if "status: done" not in match.group(2):
                non_done.append(ident)
        self.assertEqual([], [i for i in non_done if i != current], non_done)
        self.assertTrue(current, "STATE must have a current_item")

    def test_delivery_artifacts_real_repo_clean(self):
        """REVIEW2-11: the tracked tree must carry no forbidden artifacts."""
        check = release_check.check_delivery_artifacts(ROOT)
        self.assertTrue(check["ok"], check)
        self.assertEqual("ok", check["level"])

    def test_delivery_artifacts_detects_forbidden_tracked(self):
        completed = subprocess.CompletedProcess(
            [],
            0,
            stdout="src/coevo/__pycache__/x.cpython-314.pyc\n"
                   "loop/private-key-handles-F6DE.json\n",
            stderr="",
        )
        with mock.patch.object(release_check, "_run", return_value=completed):
            check = release_check.check_delivery_artifacts(ROOT)
        self.assertFalse(check["ok"])
        self.assertEqual("critical", check["level"])
        self.assertIn("__pycache__", check["detail"])

    def test_delivery_artifacts_detects_prototype_in_production_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            scripts.mkdir(parents=True)
            (scripts / "run_cockpit.py").write_text(
                "from src.coevo.crypto import GmsslPrototypeProvider\n",
                encoding="utf-8",
            )
            (scripts / "secret_scan.py").write_text(
                '_FIXTURE_ALLOWED_PREFIXES = ("tests/", "loop/")\n',
                encoding="utf-8",
            )
            (root / "docs" / "architecture").mkdir(parents=True)
            (root / "docs" / "architecture" / "win7-compat-branch.md").write_text(
                "独立发布冻结依赖安全补偿测试计划\n", encoding="utf-8"
            )
            completed = subprocess.CompletedProcess([], 0, stdout="", stderr="")
            with mock.patch.object(release_check, "_run", return_value=completed):
                check = release_check.check_delivery_artifacts(root)
            self.assertFalse(check["ok"])
            self.assertIn("prototype", check["detail"])

    def test_recent_gate_real_repo_ok(self):
        """ENG-OPTIMIZE-3: the local gate-results artifact is fresh and passing."""
        check = release_check.check_recent_gate(ROOT)
        self.assertTrue(check["ok"], check)
        self.assertEqual("ok", check["level"])

    def test_recent_gate_missing_is_critical(self):
        with tempfile.TemporaryDirectory() as tmp:
            check = release_check.check_recent_gate(Path(tmp))
        self.assertFalse(check["ok"])
        self.assertEqual("critical", check["level"])

    def test_recent_gate_failed_is_critical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gate_dir = root / "loop" / "runtime" / "gate-results"
            gate_dir.mkdir(parents=True)
            (gate_dir / "fast.json").write_text(
                json.dumps(
                    {
                        "exit_code": 1,
                        "ok": False,
                        "started_at": "2026-08-10T00:00:00Z",
                        "totals": {
                            "discovered": 10,
                            "passed": 9,
                            "failed": 1,
                            "skipped": 0,
                        },
                    }
                ),
                encoding="utf-8",
            )
            check = release_check.check_recent_gate(root)
        self.assertFalse(check["ok"])
        self.assertEqual("critical", check["level"])

    def test_recent_gate_stale_is_critical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gate_dir = root / "loop" / "runtime" / "gate-results"
            gate_dir.mkdir(parents=True)
            stale = (datetime.now(UTC) - timedelta(days=30)).isoformat().replace(
                "+00:00", "Z"
            )
            (gate_dir / "fast.json").write_text(
                json.dumps(
                    {
                        "exit_code": 0,
                        "ok": True,
                        "started_at": stale,
                        "totals": {
                            "discovered": 10,
                            "passed": 10,
                            "failed": 0,
                            "skipped": 0,
                        },
                    }
                ),
                encoding="utf-8",
            )
            check = release_check.check_recent_gate(root)
        self.assertFalse(check["ok"])
        self.assertIn("stale", check["detail"])

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
