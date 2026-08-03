"""BACKUP-1: crash / interrupted-operation recovery fault-injection tests."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts" / "install_cockpit.py"


class StateStoreInterruptedSaveTests(unittest.TestCase):
    """A crashed save (tmp file left, os.replace never ran) must not corrupt state."""

    def test_stale_tmp_does_not_corrupt_committed_state(self):
        from src.coevo.cockpit.state_store import CockpitStateStore
        from src.coevo.cockpit.models import WorkspaceView

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit-state.json"
            store = CockpitStateStore(path)
            store.save(
                (WorkspaceView("PRJ001", "A", ("r.1",), 1, 1, 1),),
                (),
            )
            committed = path.read_bytes()
            # Simulate an interrupted save of a different payload: a stale
            # temp file is left next to the committed state.
            stale = path.with_name("cockpit-state.json.stale.tmp")
            stale.write_text('{"schema_version":"1.0","corrupt":true}', encoding="utf-8")
            loaded = store.load()
            self.assertIsNotNone(loaded)
            views, roles = loaded
            self.assertEqual(1, len(views))
            self.assertEqual("PRJ001", views[0].project_id)
            self.assertEqual(committed, path.read_bytes(), "load must not rewrite state")

    def test_restart_loads_last_committed_state(self):
        from src.coevo.cockpit.state_store import CockpitStateStore
        from src.coevo.cockpit.models import WorkspaceView

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit-state.json"
            store = CockpitStateStore(path)
            store.save((WorkspaceView("PRJ001", "A", ("r.1",), 1, 1, 1),), ())
            reopened = CockpitStateStore(path)
            views, _ = reopened.load()
            self.assertEqual("PRJ001", views[0].project_id)


class InstallerInterruptedUpgradeTests(unittest.TestCase):
    """A crash between copying app/<new> and switching the pointer must not break recovery."""

    def _run(self, install_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(INSTALLER), "--install-root", str(install_root), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

    def test_partial_upgrade_leaves_pointer_intact_and_force_completes(self):
        with tempfile.TemporaryDirectory() as tmp:
            install = Path(tmp)
            self.assertEqual(
                0, self._run(install, "--action", "install", "--version", "9.9.9").returncode
            )
            # Simulate a crash mid-upgrade: app/9.9.10 exists, pointer still 9.9.9.
            partial = install / "app" / "9.9.10"
            partial.mkdir(parents=True)
            (partial / "partial.txt").write_text("half-copied", encoding="utf-8")
            self.assertEqual(
                "9.9.9", (install / "current").read_text(encoding="utf-8").strip()
            )
            # check still reports the committed version and passes integrity.
            check = self._run(install, "--action", "check")
            self.assertEqual(0, check.returncode, check.stdout + check.stderr)
            # Retry upgrade without force is refused (fail-closed), with force completes.
            refused = self._run(install, "--action", "upgrade", "--version", "9.9.10")
            self.assertNotEqual(0, refused.returncode)
            forced = self._run(install, "--action", "upgrade", "--version", "9.9.10", "--force")
            self.assertEqual(0, forced.returncode, forced.stdout + forced.stderr)
            self.assertEqual(
                "9.9.10", (install / "current").read_text(encoding="utf-8").strip()
            )
            self.assertEqual(0, self._run(install, "--action", "check").returncode)


if __name__ == "__main__":
    unittest.main()
