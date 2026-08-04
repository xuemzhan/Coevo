"""INSTALL-1: offline install / upgrade / rollback / uninstall integration tests.

The installer is executed as a subprocess against a temporary install
root so the real CLI surface (exit codes, fail-closed behaviour) is
verified end to end without touching the repository or user app data.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts" / "install_cockpit.py"


def run_installer(
    install_root: Path,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(INSTALLER),
            "--install-root",
            str(install_root),
            *args,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


class InstallerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.install_root = Path(self._tmp.name)

    def test_install_creates_bundle_pointer_and_manifest(self):
        result = run_installer(
            self.install_root, "--action", "install", "--version", "9.9.9"
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        app = self.install_root / "app" / "9.9.9"
        self.assertTrue((app / "src" / "coevo" / "version.py").is_file())
        self.assertTrue((app / "scripts" / "run_cockpit.py").is_file())
        self.assertTrue((app / "config" / "model-config.json").is_file())
        self.assertEqual("9.9.9", (self.install_root / "current").read_text(encoding="utf-8").strip())
        manifest = self.install_root / "manifests" / "9.9.9.sha256"
        self.assertTrue(manifest.is_file())
        self.assertIn("src/coevo/version.py", manifest.read_text(encoding="utf-8"))
        releases = json.loads((self.install_root / "releases.json").read_text(encoding="utf-8"))
        self.assertEqual(1, len(releases["entries"]))
        self.assertEqual("9.9.9", releases["entries"][0]["version"])

    def test_install_pins_python_interpreter(self):
        self.assertEqual(
            0,
            run_installer(
                self.install_root, "--action", "install", "--version", "9.9.9"
            ).returncode,
        )
        pin = self.install_root / "python-path.txt"
        self.assertTrue(pin.is_file())
        self.assertEqual(sys.executable, pin.read_text(encoding="utf-8").strip())

    def test_check_passes_after_install(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        result = run_installer(self.install_root, "--action", "check")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("current=9.9.9", result.stdout)

    def test_check_fails_without_python_pin(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        (self.install_root / "python-path.txt").unlink()
        result = run_installer(self.install_root, "--action", "check")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("python pin missing", result.stderr)

    def test_check_fails_on_relative_python_pin(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        (self.install_root / "python-path.txt").write_text("python.exe\n", encoding="utf-8")
        result = run_installer(self.install_root, "--action", "check")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("absolute", result.stderr)

    def test_check_fails_on_missing_pin_target(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        missing = self.install_root / "missing-python.exe"
        (self.install_root / "python-path.txt").write_text(str(missing) + "\n", encoding="utf-8")
        result = run_installer(self.install_root, "--action", "check")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing", result.stderr)

    def test_upgrade_keeps_previous_and_switches_pointer(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        self.assertEqual(0, run_installer(self.install_root, "--action", "upgrade", "--version", "9.9.10").returncode)
        self.assertEqual(
            "9.9.10",
            (self.install_root / "current").read_text(encoding="utf-8").strip(),
        )
        self.assertTrue((self.install_root / "app" / "9.9.9").is_dir())
        releases = json.loads((self.install_root / "releases.json").read_text(encoding="utf-8"))
        self.assertEqual(2, len(releases["entries"]))
        self.assertEqual("9.9.9", releases["entries"][1]["previous"])
        self.assertEqual("9.9.10", releases["entries"][1]["version"])

    def test_rollback_restores_previous_after_verification(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        self.assertEqual(0, run_installer(self.install_root, "--action", "upgrade", "--version", "9.9.10").returncode)
        result = run_installer(self.install_root, "--action", "rollback")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            "9.9.9",
            (self.install_root / "current").read_text(encoding="utf-8").strip(),
        )
        self.assertEqual(0, run_installer(self.install_root, "--action", "check").returncode)

    def test_rollback_without_previous_is_fail_closed(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        result = run_installer(self.install_root, "--action", "rollback")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(
            "9.9.9",
            (self.install_root / "current").read_text(encoding="utf-8").strip(),
        )

    def test_uninstall_removes_current_only(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        self.assertEqual(0, run_installer(self.install_root, "--action", "upgrade", "--version", "9.9.10").returncode)
        result = run_installer(self.install_root, "--action", "uninstall")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse((self.install_root / "app" / "9.9.10").exists())
        self.assertTrue((self.install_root / "app" / "9.9.9").is_dir())
        self.assertFalse((self.install_root / "current").exists())

    def test_uninstall_all_removes_versions_and_history(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        self.assertEqual(0, run_installer(self.install_root, "--action", "upgrade", "--version", "9.9.10").returncode)
        result = run_installer(self.install_root, "--action", "uninstall", "--all")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse((self.install_root / "app").exists())
        self.assertFalse((self.install_root / "releases.json").exists())
        self.assertFalse((self.install_root / "current").exists())

    def test_invalid_version_is_fail_closed(self):
        for bad in ("1.0", "v1.2.3", "..", "9.9.9-rc1", "2026-08-03T12:00:00Z"):
            result = run_installer(self.install_root, "--action", "install", "--version", bad)
            self.assertNotEqual(0, result.returncode, bad)
            self.assertFalse((self.install_root / "current").exists(), bad)

    def test_install_from_invalid_source_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as empty:
            result = run_installer(
                self.install_root,
                "--action",
                "install",
                "--version",
                "9.9.9",
                "--source-root",
                empty,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertFalse((self.install_root / "current").exists())

    def test_double_install_same_version_requires_force(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        result = run_installer(self.install_root, "--action", "install", "--version", "9.9.9")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("already installed", result.stderr)

    def test_corrupted_file_is_detected_by_check(self):
        self.assertEqual(0, run_installer(self.install_root, "--action", "install", "--version", "9.9.9").returncode)
        victim = self.install_root / "app" / "9.9.9" / "src" / "coevo" / "version.py"
        with victim.open("a", encoding="utf-8") as stream:
            stream.write("# tampered\n")
        result = run_installer(self.install_root, "--action", "check")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("integrity", result.stderr)


if __name__ == "__main__":
    unittest.main()
