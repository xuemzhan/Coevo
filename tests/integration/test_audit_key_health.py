"""AUDIT-KEY-1: real audit-key health check against the repository config."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEALTH = ROOT / "scripts" / "audit_key_health.py"


def run_health(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HEALTH), "--repo-root", str(ROOT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )


class AuditKeyHealthIntegrationTests(unittest.TestCase):
    def test_repo_config_is_healthy(self):
        # The pinned F6DE certificate is present on the dev machine and the
        # audit head matches it; a healthy repo must report ok with exit 0.
        result = run_health()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual([], report["problems"])

    def test_config_only_check_is_healthy(self):
        result = run_health("--no-inspect")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])

    def test_corrupt_config_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "audit-signing.json"
            config.write_text("{broken", encoding="utf-8")
            result = run_health("--config", str(config), "--no-inspect")
            self.assertEqual(1, result.returncode)
            report = json.loads(result.stdout)
            self.assertFalse(report["ok"])
            self.assertTrue(report["remediations"])

    def test_missing_config_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_health(
                "--config", str(Path(tmp) / "missing.json"), "--no-inspect"
            )
            self.assertEqual(1, result.returncode)
            report = json.loads(result.stdout)
            self.assertFalse(report["ok"])


if __name__ == "__main__":
    unittest.main()
