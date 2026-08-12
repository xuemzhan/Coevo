"""CI-1: artifact restore script + workflow plan consistency tests."""
from __future__ import annotations

import hashlib
import importlib.util
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
BUILD_SPEC = importlib.util.spec_from_file_location(
    "ci_build_toolchain", ROOT / "scripts" / "ci-build-toolchain.py"
)
build = importlib.util.module_from_spec(BUILD_SPEC)
BUILD_SPEC.loader.exec_module(build)


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
            tmp_dir = Path(tmp)
            descriptor = tmp_dir / "ci-artifact.json"
            descriptor.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "name": "coevo-toolchain-win64",
                        "format": "zip",
                        "url_pattern": "https://example.com/<version>.zip",
                        "version": "pending",
                        "url": "",
                        "sha256": "pending",
                        "contents": [],
                        "publish_instructions": "",
                    }
                ),
                encoding="utf-8",
            )
            install_root = tmp_dir / "restored"
            # No -ArtifactSha256: the script reads the descriptor whose
            # sha256 is 'pending' until the artifact is published.
            result = _run_restore(
                "-InstallRoot", str(install_root),
                "-DescriptorPath", str(descriptor),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("pinned", result.stderr.lower())


class CiBuildToolchainTests(unittest.TestCase):
    def _fake_tools(self, tmp: str) -> Path:
        root = Path(tmp) / "tools"
        (root / "python" / "3.14.3").mkdir(parents=True)
        (root / "python" / "3.14.3" / "python.exe").write_text(
            "x", encoding="utf-8"
        )
        (root / "node" / "24.14.0").mkdir(parents=True)
        (root / "node" / "24.14.0" / "node.exe").write_text("x", encoding="utf-8")
        (root / "control").mkdir()
        (root / "control" / "control.pyz").write_text("x", encoding="utf-8")
        (root / "gmssl" / "bin").mkdir(parents=True)
        (root / "gmssl" / "bin" / "gmssl.dll").write_text("x", encoding="utf-8")
        return root

    def test_build_archive_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            out = tmp_dir / "out.zip"
            code = build.main(
                [
                    "--version", "1.0.0",
                    "--out", str(out),
                    "--tools-root", str(self._fake_tools(tmp)),
                ]
            )
            self.assertEqual(0, code)
            with zipfile.ZipFile(out) as zf:
                names = zf.namelist()
            self.assertIn(".tools/python/3.14.3/python.exe", names)
            self.assertIn(".tools/control/control.pyz", names)
            self.assertIn(".tools/gmssl/bin/gmssl.dll", names)

    def test_build_refuses_missing_runtime_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            tools = self._fake_tools(tmp)
            (tools / "node" / "24.14.0" / "node.exe").unlink()
            with self.assertRaises(SystemExit):
                build.build_archive(tools, tmp_dir / "out.zip")

    def test_build_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            out = tmp_dir / "out.zip"
            out.write_text("x", encoding="utf-8")
            with self.assertRaises(SystemExit):
                build.build_archive(self._fake_tools(tmp), out)

    def test_build_archive_is_byte_reproducible(self):
        """MATURITY-O-02: the artifact hash must not drift between builds."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            tools = self._fake_tools(tmp)
            first = tmp_dir / "first.zip"
            second = tmp_dir / "second.zip"
            build.build_archive(tools, first)
            build.build_archive(tools, second)
            self.assertEqual(
                hashlib.sha256(first.read_bytes()).hexdigest(),
                hashlib.sha256(second.read_bytes()).hexdigest(),
                "toolchain artifact must be byte-reproducible",
            )


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

    def test_artifact_descriptor_is_parseable_and_pinned(self):
        data = json.loads(DESCRIPTOR.read_text(encoding="utf-8"))
        self.assertEqual("1.0", data["schema_version"])
        self.assertEqual("coevo-toolchain-win64", data["name"])
        self.assertIn("url", data)
        self.assertRegex(data["sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(data["version"], r"^\d+\.\d+\.\d+$")
        self.assertTrue(data["url"].startswith("https://"))
        self.assertTrue(data["publish_instructions"])


if __name__ == "__main__":
    unittest.main()
