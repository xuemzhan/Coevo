"""Unit tests for US-7-AC-4 controlled WPS launcher."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.coevo.cockpit import (
    CockpitValidationError,
    WpsLaunchDecision,
    WpsLauncher,
)


class WpsLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "report.docx").write_bytes(b"docx-content")
        (self.root / "docs" / "script.exe").write_bytes(b"exe-content")

    def launcher(self, **kwargs) -> WpsLauncher:
        kwargs.setdefault("dry_run", True)
        return WpsLauncher(self.root, **kwargs)

    def test_valid_document_dry_run_is_ok(self):
        result = self.launcher().launch("docs/report.docx")
        self.assertIs(WpsLaunchDecision.OK, result.decision)
        self.assertEqual(16, len(result.artifact_path_hash))

    def test_traversal_and_absolute_paths_are_denied(self):
        launcher = self.launcher()
        for bad in ("../outside.docx", "/etc/passwd", "docs\\..\\x.docx", "..", ""):
            result = launcher.launch(bad)
            self.assertIs(WpsLaunchDecision.DENIED, result.decision, bad)

    def test_disallowed_extension_is_denied(self):
        result = self.launcher().launch("docs/script.exe")
        self.assertIs(WpsLaunchDecision.DENIED, result.decision)

    def test_missing_file_is_denied(self):
        result = self.launcher().launch("docs/nope.docx")
        self.assertIs(WpsLaunchDecision.DENIED, result.decision)

    def test_symlink_escape_is_denied(self):
        outside = Path(self._temporary.name) / "outside.docx"
        outside.write_bytes(b"x")
        try:
            (self.root / "docs" / "link.docx").symlink_to(outside)
        except OSError:
            self.skipTest("symlink creation unavailable")
        result = self.launcher().launch("docs/link.docx")
        self.assertIs(WpsLaunchDecision.DENIED, result.decision)

    def test_runner_is_invoked_with_explicit_executable_and_path(self):
        captured: list[tuple[str, str]] = []

        def fake_runner(executable: str, path: Path) -> int:
            captured.append((executable, str(path)))
            return 0

        launcher = WpsLauncher(
            self.root,
            wps_executable="C:\\fake\\wps.exe",
            runner=fake_runner,
        )
        result = launcher.launch("docs/report.docx")
        self.assertIs(WpsLaunchDecision.OK, result.decision)
        self.assertEqual(0, result.returncode)
        self.assertEqual(1, len(captured))
        self.assertEqual("C:\\fake\\wps.exe", captured[0][0])
        self.assertTrue(captured[0][1].endswith("docs\\report.docx"))

    def test_runner_failure_is_error(self):
        def failing_runner(executable: str, path: Path) -> int:
            raise OSError("boom")

        launcher = WpsLauncher(
            self.root, wps_executable="C:\\fake\\wps.exe", runner=failing_runner
        )
        result = launcher.launch("docs/report.docx")
        self.assertIs(WpsLaunchDecision.ERROR, result.decision)

    def test_missing_absolute_executable_is_not_available(self):
        launcher = WpsLauncher(
            self.root, wps_executable="C:\\definitely\\missing\\wps.exe"
        )
        result = launcher.launch("docs/report.docx")
        self.assertIs(WpsLaunchDecision.NOT_AVAILABLE, result.decision)

    def test_invalid_root_is_rejected(self):
        with self.assertRaises(CockpitValidationError):
            WpsLauncher(Path(self._temporary.name) / "absent")


if __name__ == "__main__":
    unittest.main()
