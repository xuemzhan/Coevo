"""Unit tests for the PROD-HARDEN-1 production support slice.

Covers the new operational layer (version metadata, validated runtime
configuration, logging bootstrap, cockpit launcher CLI) without making
the suite timing- or network-dependent.
"""
from __future__ import annotations

import logging
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.coevo.config import AppConfig, ConfigError, LOOPBACK_HOST
from src.coevo.logging_setup import setup_logging
from src.coevo.version import APP_NAME, VERSION, version_string


ROOT = Path(__file__).resolve().parents[2]


class VersionTests(unittest.TestCase):
    def test_version_is_semantic_not_timestamp(self):
        self.assertRegex(VERSION, r"^\d+\.\d+\.\d+$")
        self.assertEqual(APP_NAME, "coevo")
        self.assertEqual(f"coevo {VERSION}", version_string())


class AppConfigTests(unittest.TestCase):
    def test_defaults_are_loopback_and_valid(self):
        config = AppConfig()
        self.assertEqual(LOOPBACK_HOST, config.cockpit_host)
        self.assertIn(config.cockpit_port, range(1, 65536))
        self.assertIn(config.log_level, {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"})

    def test_non_loopback_host_is_rejected(self):
        with self.assertRaises(ConfigError):
            AppConfig(cockpit_host="0.0.0.0")
        with self.assertRaises(ConfigError):
            AppConfig(cockpit_host="10.0.0.1")

    def test_invalid_port_and_log_level_are_rejected(self):
        with self.assertRaises(ConfigError):
            AppConfig(cockpit_port=0)
        with self.assertRaises(ConfigError):
            AppConfig(cockpit_port=70000)
        with self.assertRaises(ConfigError):
            AppConfig(log_level="VERBOSE")

    def test_from_env_overrides_and_validates(self):
        config = AppConfig.from_env(
            {
                "COEVO_COCKPIT_PORT": "12742",
                "COEVO_LOG_LEVEL": "debug",
                "COEVO_SESSION_TIMEOUT_SEC": "60",
                "COEVO_DATA_DIR": str(ROOT / ".omo"),
            }
        )
        self.assertEqual(12742, config.cockpit_port)
        self.assertEqual("DEBUG", config.log_level)
        self.assertEqual(60, config.session_timeout_sec)
        self.assertEqual(ROOT / ".omo", config.data_dir)

    def test_from_env_fails_closed_on_bad_values(self):
        with self.assertRaises(ConfigError):
            AppConfig.from_env({"COEVO_COCKPIT_PORT": "not-a-number"})
        with self.assertRaises(ConfigError):
            AppConfig.from_env({"COEVO_COCKPIT_HOST": "0.0.0.0"})

    def test_default_paths_stay_under_app_data(self):
        config = AppConfig()
        self.assertEqual("cockpit-state.json", config.default_state_path().name)
        self.assertEqual("cockpit-access.jsonl", config.default_log_path().name)

    def test_lock_path_env_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "instance.lock"
            config = AppConfig.from_env({"COEVO_LOCK_PATH": str(lock)})
            self.assertEqual(lock, config.cockpit_lock_path)


class LoggingSetupTests(unittest.TestCase):
    def tearDown(self) -> None:
        root = logging.getLogger()
        for handler in list(root.handlers):
            root.removeHandler(handler)
            try:
                handler.close()
            except Exception:  # noqa: BLE001 - cleanup must not mask failures
                pass

    def test_setup_logging_writes_rotating_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_file = Path(tmp) / "app.log"
            try:
                logger = setup_logging(
                    log_file=log_file,
                    console=False,
                    level="DEBUG",
                    reset=True,
                )
                logger.info("probe message")
                for handler in logging.getLogger().handlers:
                    handler.flush()
                self.assertIn("probe message", log_file.read_text(encoding="utf-8"))
            finally:
                root = logging.getLogger()
                for handler in list(root.handlers):
                    root.removeHandler(handler)
                    try:
                        handler.close()
                    except Exception:  # noqa: BLE001 - cleanup must not mask
                        pass

    def test_setup_logging_rejects_unknown_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ConfigError):
                setup_logging(log_file=Path(tmp) / "x.log", level="NOPE")


class CockpitLauncherCliTests(unittest.TestCase):
    def test_version_flag(self):
        result = subprocess.run(
            ["python", "scripts/run_cockpit.py", "--version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("coevo", result.stdout)

    def test_check_flag_validates_config(self):
        result = subprocess.run(
            ["python", "scripts/run_cockpit.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("config ok", result.stdout)

    def test_bad_port_fails_closed(self):
        result = subprocess.run(
            ["python", "scripts/run_cockpit.py", "--port", "0"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("config error", result.stderr)

    def test_demo_runner_version_flag(self):
        result = subprocess.run(
            ["python", "scripts/run_demo.py", "--version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("coevo", result.stdout)


if __name__ == "__main__":
    unittest.main()
