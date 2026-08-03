"""CI-1: artifact restore script + workflow plan consistency tests."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESTORE = ROOT / "scripts" / "ci-restore-toolchain.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"
DESCRIPTOR = ROOT / "docs" / "dependencies" / "ci-artifact.json"


def _build_archive(path: Path, *, include_control: bool = True) -> str:
    """Create a synthetic toolchain archive with the expected layout."""
    entries = {
        ".tools/python/3.14.3/python.exe": b"fake python",
        ".tools/node/24.14.0/node.exe": b"fake node",
    }
    if include_control:
        entries[".tools/control/control.pyz"] = b"fake control"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_restore(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RESTORE),
            *args,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )


class CiRestoreScriptTests(unittest.TestCase):
    def test_restore_succeeds_with_matching_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            archive = tmp_dir / "toolchain.zip"
            digest = _build_archive(archive)
            install_root = tmp_dir / "restored"
            result = _run_restore(
                "-LocalPath", str(archive),
                "-ArtifactSha256", digest,
                "-InstallRoot", str(install_root),
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue((install_root / "python" / "3.14.3" / "python.exe").is_file())
            self.assertTrue((install_root / "node" / "24.14.0" / "node.exe").is_file())
            self.assertTrue((install_root / "control" / "control.pyz").is_file())

    def test_hash_mismatch_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            archive = tmp_dir / "toolchain.zip"
            _build_archive(archive)
            install_root = tmp_dir / "restored"
            result = _run_restore(
                "-LocalPath", str(archive),
                "-ArtifactSha256", "0" * 64,
                "-InstallRoot", str(install_root),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("hash mismatch", result.stderr.lower())
            self.assertFalse(install_root.exists())

    def test_missing_expected_entry_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            archive = tmp_dir / "toolchain.zip"
            digest = _build_archive(archive, include_control=False)
            install_root = tmp_dir / "restored"
            result = _run_restore(
                "-LocalPath", str(archive),
                "-ArtifactSha256", digest,
                "-InstallRoot", str(install_root),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("missing", result.stderr.lower())
            self.assertFalse(install_root.exists())

    def test_pending_descriptor_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            install_root = Path(tmp) / "restored"
            # No -ArtifactSha256: the script reads the descriptor whose
            # sha256 is 'pending' until the artifact is published.
            result = _run_restore("-InstallRoot", str(install_root))
            self.assertNotEqual(0, result.returncode)
            self.assertIn("pinned", result.stderr.lower())


class CiPlanConsistencyTests(unittest.TestCase):
    def test_workflow_runs_verification_side_gates(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("windows-latest", text)
        self.assertIn("ci-restore-toolchain.ps1", text)
        for target in ("fmt", "lint", "test", "test-security", "test-e2e"):
            self.assertIn(f"--target {target}", text)
        # The sealed quality target (audit signing) stays on the
        # maintainer machine; CI must not attempt it.
        self.assertNotIn("--target quality", text)
        self.assertIn("upload-artifact@v4", text)

    def test_artifact_descriptor_is_parseable_and_pending(self):
        data = json.loads(DESCRIPTOR.read_text(encoding="utf-8"))
        self.assertEqual("1.0", data["schema_version"])
        self.assertEqual("coevo-toolchain-win64", data["name"])
        self.assertIn("url", data)
        self.assertEqual("pending", data["sha256"])
        self.assertTrue(data["publish_instructions"])


if __name__ == "__main__":
    unittest.main()
