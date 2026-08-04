"""AVAIL-1: run_cockpit --preflight logic + watchdog dry-run tests."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location(
    "run_cockpit_cli", ROOT / "scripts" / "run_cockpit.py"
)
run_cockpit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_cockpit)

WATCHDOG = ROOT / "scripts" / "cockpit-watchdog.ps1"


def _sealed_process() -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        [], 0, stdout=json.dumps({"ok": True, "status": "fully-sealed"}), stderr=""
    )


class PreflightTests(unittest.TestCase):
    def _config(self, tmp: str):
        return run_cockpit.AppConfig(
            data_dir=Path(tmp),
            log_dir=Path(tmp),
            cockpit_host="127.0.0.1",
            cockpit_port=12701,
            log_level="INFO",
        )

    def test_preflight_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                run_cockpit.subprocess, "run", return_value=_sealed_process()
            ):
                code = run_cockpit.preflight(self._config(tmp))
            self.assertEqual(0, code)

    def test_preflight_critical_unwritable_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "data-file"
            bad.write_text("not a dir", encoding="utf-8")
            config = run_cockpit.AppConfig(
                data_dir=bad, log_dir=Path(tmp), log_level="INFO"
            )
            with mock.patch.object(
                run_cockpit.subprocess, "run", return_value=_sealed_process()
            ):
                code = run_cockpit.preflight(config)
            self.assertEqual(2, code)

    def test_preflight_critical_audit_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            failed = subprocess.CompletedProcess(
                [], 1, stdout="", stderr="signature invalid"
            )
            with mock.patch.object(
                run_cockpit.subprocess, "run", return_value=failed
            ):
                code = run_cockpit.preflight(self._config(tmp))
            self.assertEqual(2, code)

    def test_preflight_degraded_on_unsealed_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            unsealed = subprocess.CompletedProcess(
                [],
                0,
                stdout=json.dumps(
                    {"ok": True, "status": "valid-prefix-with-unsealed-tail"}
                ),
                stderr="",
            )
            with mock.patch.object(
                run_cockpit.subprocess, "run", return_value=unsealed
            ):
                code = run_cockpit.preflight(self._config(tmp))
            self.assertEqual(1, code)


class WatchdogTests(unittest.TestCase):
    def _fake_install(self, tmp: str) -> str:
        root = Path(tmp)
        (root / "app" / "1.2.3" / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "current").write_text("1.2.3\n", encoding="utf-8")
        (root / "app" / "1.2.3" / "scripts" / "run_cockpit.py").write_text(
            "print('runner')", encoding="utf-8"
        )
        return str(root)

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(WATCHDOG),
                *args,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

    def test_dry_run_down_reports_restart_without_touching_system(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run(
                "-InstallRoot", self._fake_install(tmp),
                "-Port", "9",
                "-DryRun",
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("DRY-RUN", result.stdout)
            self.assertIn("would restart", result.stdout)
            self.assertNotIn("Started", result.stdout)

    def test_sidecar_pin_is_used_for_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "python-path.txt").write_text(
                sys.executable + "\n", encoding="utf-8"
            )
            result = self._run(
                "-InstallRoot", self._fake_install(tmp),
                "-Port", "9",
                "-DryRun",
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("DRY-RUN", result.stdout)
            self.assertIn("would restart", result.stdout)
            self.assertIn(sys.executable, result.stdout)

    def test_sidecar_pin_missing_interpreter_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "python-path.txt").write_text(
                str(Path(tmp) / "missing-python.exe") + "\n", encoding="utf-8"
            )
            result = self._run(
                "-InstallRoot", self._fake_install(tmp),
                "-Port", "9",
                "-DryRun",
            )
            self.assertNotEqual(0, result.returncode)

    def test_sidecar_pin_relative_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "python-path.txt").write_text(
                "python.exe\n", encoding="utf-8"
            )
            result = self._run(
                "-InstallRoot", self._fake_install(tmp),
                "-Port", "9",
                "-DryRun",
            )
            self.assertNotEqual(0, result.returncode)

    def test_explicit_python_path_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run(
                "-InstallRoot", self._fake_install(tmp),
                "-PythonPath", str(Path(tmp) / "nope.exe"),
                "-Port", "9",
                "-DryRun",
            )
            self.assertNotEqual(0, result.returncode)

    def test_missing_install_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run(
                "-InstallRoot", str(Path(tmp) / "missing"), "-DryRun"
            )
            self.assertNotEqual(0, result.returncode)


if __name__ == "__main__":
    unittest.main()
