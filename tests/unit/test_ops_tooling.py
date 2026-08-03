"""OPS-1: health check, autostart helper, and access-log rotation tests."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location(
    "health_check", ROOT / "scripts" / "health_check.py"
)
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)

AUTOSTART = ROOT / "scripts" / "register-autostart.ps1"


class HealthCheckTests(unittest.TestCase):
    def _install_root(self, tmp: str, version: str = "1.2.3") -> Path:
        root = Path(tmp)
        (root / "logs").mkdir(parents=True, exist_ok=True)
        (root / "current").write_text(version + "\n", encoding="utf-8")
        version_py = root / "app" / version / "src" / "coevo" / "version.py"
        version_py.parent.mkdir(parents=True, exist_ok=True)
        version_py.write_text(
            f'APP_NAME = "coevo"\nVERSION: str = "{version}"\n', encoding="utf-8"
        )
        return root

    def test_dirs_ok_and_missing_logs_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "logs").mkdir(exist_ok=True)
            self.assertTrue(health.check_dirs(Path(tmp))["ok"])
            missing_logs = Path(tmp) / "nologs"
            missing_logs.mkdir(exist_ok=True)
            result = health.check_dirs(missing_logs)
            self.assertFalse(result["ok"])
            self.assertIn("logs", result["detail"])

    def test_disk_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(
                health.check_disk(Path(tmp), min_free_bytes=1)["ok"]
            )
            result = health.check_disk(Path(tmp), min_free_bytes=10**30)
            self.assertFalse(result["ok"])

    def test_version_consistency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._install_root(tmp)
            self.assertTrue(health.check_version(root)["ok"])
            (root / "current").write_text("9.9.9\n", encoding="utf-8")
            self.assertFalse(health.check_version(root)["ok"])

    def test_lock_fresh_and_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = root / "cockpit.lock"
            lock.write_text("1\n", encoding="utf-8")
            self.assertTrue(health.check_lock(root)["ok"])
            old = time.time() - health._STALE_LOCK_SECONDS - 10
            import os
            os.utime(lock, (old, old))
            self.assertFalse(health.check_lock(root)["ok"])

    def test_build_report_aggregation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._install_root(tmp)
            report = health.build_report(
                install_root=root,
                repo_root=ROOT,
                cockpit_url="http://127.0.0.1:9",
                min_free_bytes=1,
                audit_python=None,
            )
            # Cockpit on an unused port is unreachable (degraded), not critical.
            self.assertIn(report["status"], ("ok", "degraded"))
            self.assertIsInstance(report["checks"], list)
            self.assertTrue(report["checks"][0]["ok"])  # dirs


class AutostartHelperTests(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(AUTOSTART),
                *args,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

    def _fake_install(self, tmp: str) -> str:
        root = Path(tmp)
        (root / "app" / "1.2.3" / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "current").write_text("1.2.3\n", encoding="utf-8")
        (root / "app" / "1.2.3" / "scripts" / "run_cockpit.py").write_text(
            "print('runner')", encoding="utf-8"
        )
        return str(root)

    def test_status_not_registered(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run(
                "-Action", "Status",
                "-InstallRoot", self._fake_install(tmp),
                "-TaskName", "CoevoTest-" + "x" * 8,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("NOT registered", result.stdout)

    def test_dry_run_register_prints_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run(
                "-Action", "Register",
                "-InstallRoot", self._fake_install(tmp),
                "-PythonPath", sys.executable,
                "-TaskName", "CoevoTest-" + "y" * 8,
                "-DryRun",
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("DRY-RUN register", result.stdout)
            self.assertIn("run_cockpit.py", result.stdout)

    def test_missing_install_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run(
                "-Action", "Register",
                "-InstallRoot", str(Path(tmp) / "missing"),
                "-DryRun",
            )
            self.assertNotEqual(0, result.returncode)


class AccessLogRotationTests(unittest.TestCase):
    def test_rotation_by_size_and_backup_shift(self):
        from src.coevo.cockpit.server import _CockpitLogWriter

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "access.jsonl"
            writer = _CockpitLogWriter(path, max_bytes=256, backup_count=3)
            try:
                for index in range(12):
                    writer.write({"i": index, "pad": "x" * 100})
            finally:
                writer.close()
            self.assertTrue(path.exists() or (path.with_suffix(".1")).exists())
            backups = sorted(
                p.name
                for p in Path(tmp).glob("access.*")
                if p.name != "access.jsonl"
            )
            self.assertTrue(backups, "expected at least one rotated backup")
            self.assertLessEqual(len(backups), 3)

    def test_rotation_failure_never_breaks_writes(self):
        from unittest import mock
        from src.coevo.cockpit import server as server_module

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "access.jsonl"
            writer = server_module._CockpitLogWriter(
                path, max_bytes=64, backup_count=2
            )
            try:
                writer.write({"a": "b"})
                with mock.patch.object(
                    server_module.os, "replace", side_effect=OSError("boom")
                ):
                    writer.write({"c": "d" * 200})  # rotation fails, write must survive
                self.assertGreaterEqual(writer.errors, 1)
                writer.write({"e": "f"})
                self.assertFalse(writer._stream.closed)
            finally:
                writer.close()


if __name__ == "__main__":
    unittest.main()
