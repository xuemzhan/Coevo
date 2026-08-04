"""AVAIL-1: run_cockpit --preflight logic + watchdog dry-run tests."""
from __future__ import annotations

import importlib.util
import http.server
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import types
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
BUDGET = ROOT / "scripts" / "restart-budget.ps1"


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


class PreflightEgressTests(unittest.TestCase):
    """OPS-4: model external-egress posture warnings in preflight."""

    def _config(self, tmp: str):
        return run_cockpit.AppConfig(
            data_dir=Path(tmp),
            log_dir=Path(tmp),
            cockpit_host="127.0.0.1",
            cockpit_port=12701,
            log_level="INFO",
        )

    def _fake_config(self, provider: str, base_url: str | None, external_data_ok: bool):
        return types.SimpleNamespace(
            provider=provider,
            base_url=base_url,
            external_data_ok=external_data_ok,
        )

    def test_preflight_degraded_when_non_loopback_egress_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = self._fake_config(
                "deepseek", "https://api.deepseek.com", True
            )
            with mock.patch.object(
                run_cockpit.subprocess, "run", return_value=_sealed_process()
            ), mock.patch(
                "src.coevo.model.config.load_model_config", return_value=fake
            ):
                code = run_cockpit.preflight(self._config(tmp))
            self.assertEqual(1, code)

    def test_preflight_ok_when_loopback_egress_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = self._fake_config(
                "local_openai", "http://127.0.0.1:8000/v1", True
            )
            with mock.patch.object(
                run_cockpit.subprocess, "run", return_value=_sealed_process()
            ), mock.patch(
                "src.coevo.model.config.load_model_config", return_value=fake
            ):
                code = run_cockpit.preflight(self._config(tmp))
            self.assertEqual(0, code)

    def test_preflight_degraded_when_legacy_env_switch_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = self._fake_config("offline", None, False)
            with mock.patch.object(
                run_cockpit.subprocess, "run", return_value=_sealed_process()
            ), mock.patch(
                "src.coevo.model.config.load_model_config", return_value=fake
            ), mock.patch.dict(
                os.environ, {"COEVO_LLM_EXTERNAL_DATA_OK": "1"}
            ):
                code = run_cockpit.preflight(self._config(tmp))
            self.assertEqual(1, code)

    def test_egress_warnings_message_content(self):
        fake = self._fake_config("deepseek", "https://api.deepseek.com", True)
        with mock.patch(
            "src.coevo.model.config.load_model_config", return_value=fake
        ):
            warnings = run_cockpit.model_egress_warnings()
        self.assertTrue(any("APPROVED" in item for item in warnings), warnings)

    def test_egress_warnings_silent_for_loopback_and_offline(self):
        fake = self._fake_config("offline", None, False)
        with mock.patch(
            "src.coevo.model.config.load_model_config", return_value=fake
        ), mock.patch.dict(
            os.environ, {"COEVO_LLM_EXTERNAL_DATA_OK": ""}
        ):
            warnings = run_cockpit.model_egress_warnings()
        self.assertEqual([], warnings)


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

    def test_dry_run_healthy_against_real_cockpit(self):
        from src.coevo.cockpit import CockpitHttpConfig, CockpitHttpServer

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=port,
                request_timeout_sec=3,
                lock_path=None,
            ),
            workspace_views=(),
            role_views=(),
        )
        server.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                result = self._run(
                    "-InstallRoot", self._fake_install(tmp),
                    "-Port", str(port),
                    "-DryRun",
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn("healthy", result.stdout)
        finally:
            server.stop()

    def test_dry_run_wrong_service_on_port_is_down(self):
        class _ImpostorHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                body = b'{"status":"ok","service":"other"}'
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args: object) -> None:
                pass

        imposter = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0), _ImpostorHandler
        )
        thread = threading.Thread(target=imposter.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                result = self._run(
                    "-InstallRoot", self._fake_install(tmp),
                    "-Port", str(imposter.server_address[1]),
                    "-DryRun",
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn("would restart", result.stdout)
                self.assertNotIn("healthy", result.stdout)
        finally:
            imposter.shutdown()
            thread.join(timeout=10)

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


class RestartBudgetTests(unittest.TestCase):
    """AVAIL-3: restart budget pure logic via the standalone helper."""

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(BUDGET),
                *args,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

    def _json(self, values: list[float]) -> str:
        import json

        return json.dumps(values)

    def test_empty_history_allowed(self):
        result = self._run(
            "-TimestampsJson", self._json([]),
            "-WindowSeconds", "3600",
            "-MaxRestarts", "5",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("allowed=True recent=0", result.stdout)

    def test_under_budget_allowed(self):
        now = time.time()
        result = self._run(
            "-TimestampsJson", self._json([now - 10, now - 20, now - 30, now - 40]),
            "-WindowSeconds", "3600",
            "-MaxRestarts", "5",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("allowed=True recent=4", result.stdout)

    def test_budget_exhausted_denied(self):
        now = time.time()
        result = self._run(
            "-TimestampsJson", self._json([now - i for i in range(5)]),
            "-WindowSeconds", "3600",
            "-MaxRestarts", "5",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("allowed=False recent=5", result.stdout)

    def test_old_restarts_outside_window_ignored(self):
        now = time.time()
        result = self._run(
            "-TimestampsJson", self._json([now - 10, now - 7200, now - 9000]),
            "-WindowSeconds", "3600",
            "-MaxRestarts", "5",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("allowed=True recent=1", result.stdout)

    def test_invalid_parameters_fail_closed(self):
        result = self._run(
            "-TimestampsJson", self._json([]),
            "-WindowSeconds", "0",
            "-MaxRestarts", "5",
        )
        self.assertNotEqual(0, result.returncode)


if __name__ == "__main__":
    unittest.main()
