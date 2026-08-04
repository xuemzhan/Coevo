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
from unittest import mock


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
        (root / "python-path.txt").write_text(
            sys.executable + "\n", encoding="utf-8"
        )
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

    class _FakeHealthzResponse:
        def __init__(self, status: int, body: str):
            self.status = status
            self._body = body

        def read(self, n: int = -1) -> bytes:
            return self._body.encode("utf-8")

        def __enter__(self) -> "_FakeHealthzResponse":
            return self

        def __exit__(self, *exc: object) -> bool:
            return False

    def _cockpit_check(self, status: int, body: str):
        with mock.patch.object(
            health.urllib.request,
            "urlopen",
            return_value=self._FakeHealthzResponse(status, body),
        ):
            return health.check_cockpit("http://127.0.0.1:9")

    def test_cockpit_ok_with_identity(self):
        result = self._cockpit_check(
            200, '{"status":"ok","service":"coevo-cockpit","uptime_sec":1.0}'
        )
        self.assertTrue(result["ok"])

    def test_cockpit_wrong_service_is_degraded(self):
        result = self._cockpit_check(200, '{"status":"ok","service":"other"}')
        self.assertFalse(result["ok"])
        self.assertEqual("degraded", result["level"])
        self.assertIn("other", result["detail"])

    def test_cockpit_non_200_is_degraded(self):
        result = self._cockpit_check(500, '{"status":"error"}')
        self.assertFalse(result["ok"])
        self.assertEqual("degraded", result["level"])

    def test_cockpit_malformed_body_is_degraded(self):
        result = self._cockpit_check(200, "not-json")
        self.assertFalse(result["ok"])
        self.assertEqual("degraded", result["level"])

    def _seed_backup(self, backup_root: Path, label: str, days_ago: float) -> None:
        from datetime import UTC, datetime, timedelta

        target = backup_root / label
        target.mkdir(parents=True, exist_ok=True)
        created = (datetime.now(UTC) - timedelta(days=days_ago)).isoformat().replace(
            "+00:00", "Z"
        )
        (target / "manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "label": label,
                    "created_at": created,
                    "files": [],
                }
            ),
            encoding="utf-8",
        )

    def test_backup_missing_root_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = health.check_backup(Path(tmp) / "nope", 7)
            self.assertFalse(result["ok"])
            self.assertEqual("degraded", result["level"])

    def test_backup_fresh_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_backup(root, "b1", 0)
            result = health.check_backup(root, 7)
            self.assertTrue(result["ok"])
            self.assertIn("b1", result["detail"])

    def test_backup_stale_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_backup(root, "old", 10)
            result = health.check_backup(root, 7)
            self.assertFalse(result["ok"])
            self.assertEqual("degraded", result["level"])
            self.assertIn("old", result["detail"])

    def test_backup_picks_newest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_backup(root, "old", 10)
            self._seed_backup(root, "fresh", 0.5)
            result = health.check_backup(root, 7)
            self.assertTrue(result["ok"])
            self.assertIn("fresh", result["detail"])

    def test_backup_future_timestamp_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_backup(root, "b-future", -3)  # 3 days in the future
            result = health.check_backup(root, 7)
            self.assertFalse(result["ok"])
            self.assertEqual("degraded", result["level"])
            self.assertIn("future", result["detail"])

    def test_backup_verify_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_backup(root, "b1", 0)
            with mock.patch.object(
                health.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 0, stdout='{"ok": true}', stderr=""
                ),
            ):
                result = health.check_backup(
                    root, 7, verify=True, repo_root=ROOT
                )
            self.assertTrue(result["ok"])
            self.assertIn("integrity=ok", result["detail"])

    def test_backup_verify_failure_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_backup(root, "b1", 0)
            with mock.patch.object(
                health.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 1, stdout='{"ok": false, "problems": ["hash mismatch"]}', stderr=""
                ),
            ):
                result = health.check_backup(
                    root, 7, verify=True, repo_root=ROOT
                )
            self.assertFalse(result["ok"])
            self.assertEqual("degraded", result["level"])
            self.assertIn("integrity", result["detail"])

    def test_backup_verify_timeout_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed_backup(root, "b1", 0)
            with mock.patch.object(
                health.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(cmd="verify", timeout=120),
            ):
                result = health.check_backup(
                    root, 7, verify=True, repo_root=ROOT
                )
            self.assertFalse(result["ok"])
            self.assertEqual("degraded", result["level"])
            self.assertIn("timed out", result["detail"])

    def test_pin_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = health.check_pin(self._install_root(tmp))
            self.assertTrue(result["ok"])
            self.assertIn(sys.executable, result["detail"])

    def test_pin_missing_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = health.check_pin(root)
            self.assertFalse(result["ok"])
            self.assertEqual("degraded", result["level"])
            self.assertIn("missing", result["detail"])

    def test_pin_relative_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._install_root(tmp)
            (root / "python-path.txt").write_text("python.exe\n", encoding="utf-8")
            result = health.check_pin(root)
            self.assertFalse(result["ok"])
            self.assertEqual("degraded", result["level"])
            self.assertIn("absolute", result["detail"])

    def test_pin_target_missing_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._install_root(tmp)
            (root / "python-path.txt").write_text(
                str(root / "nope.exe") + "\n", encoding="utf-8"
            )
            result = health.check_pin(root)
            self.assertFalse(result["ok"])
            self.assertEqual("degraded", result["level"])
            self.assertIn("missing", result["detail"])

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
            names = [check["name"] for check in report["checks"]]
            for expected in ("backup", "pin"):
                self.assertIn(expected, names)


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

    def test_pin_python_writes_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fake_install(tmp)
            result = self._run(
                "-Action", "PinPython",
                "-InstallRoot", root,
                "-PythonPath", sys.executable,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            sidecar = Path(root) / "python-path.txt"
            self.assertTrue(sidecar.is_file())
            self.assertEqual(
                sys.executable,
                sidecar.read_text(encoding="utf-8").strip(),
            )

    def test_pin_python_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fake_install(tmp)
            result = self._run(
                "-Action", "PinPython",
                "-InstallRoot", root,
                "-PythonPath", sys.executable,
                "-DryRun",
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("DRY-RUN pin python", result.stdout)
            self.assertFalse((Path(root) / "python-path.txt").exists())

    def test_pin_python_missing_install_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run(
                "-Action", "PinPython",
                "-InstallRoot", str(Path(tmp) / "missing"),
                "-PythonPath", sys.executable,
            )
            self.assertNotEqual(0, result.returncode)

    def test_register_dry_run_prints_pin_and_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run(
                "-Action", "Register",
                "-InstallRoot", self._fake_install(tmp),
                "-PythonPath", sys.executable,
                "-TaskName", "CoevoTest-" + "z" * 8,
                "-DryRun",
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("DRY-RUN pin python", result.stdout)
            self.assertIn("DRY-RUN register", result.stdout)

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
