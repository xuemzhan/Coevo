"""FRAMEWORK-OPTIMIZE-16: shared PowerShell resolver + unification guards."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.coevo.powershell import (
    locked_powershell_executable,
    powershell_executable,
)


ROOT = Path(__file__).resolve().parents[2]
_PS_RELATIVE = "System32/WindowsPowerShell/v1.0/powershell.exe"


def _real_powershell() -> Path:
    return (
        Path(os.environ.get("SystemRoot", r"C:\Windows")) / _PS_RELATIVE
    ).resolve(strict=True)


class SimpleVariantTests(unittest.TestCase):
    def test_env_path_wins_when_absolute(self):
        with mock.patch.dict(
            os.environ, {"COEVO_POWERSHELL_PATH": str(_real_powershell())}
        ):
            self.assertEqual(
                str(_real_powershell()), powershell_executable(error_factory=ValueError)
            )

    def test_fallback_when_env_unset(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COEVO_POWERSHELL_PATH", None)
            result = powershell_executable(error_factory=ValueError)
        # Windows path case is case-insensitive; compare resolved paths.
        self.assertEqual(_real_powershell(), Path(result).resolve())

    def test_error_factory_when_unavailable(self):
        with mock.patch.dict(
            os.environ,
            {"SystemRoot": str(ROOT / "nonexistent-system-root")},
            clear=False,
        ):
            os.environ.pop("COEVO_POWERSHELL_PATH", None)
            with self.assertRaisesRegex(RuntimeError, "unavailable"):
                powershell_executable(error_factory=RuntimeError)


class LockedVariantTests(unittest.TestCase):
    def _lock(self, tmp: Path, *, sha256: str, size: int) -> Path:
        lock = tmp / "toolchain-lock.json"
        lock.write_text(
            json.dumps(
                {
                    "tools": {
                        "make_compatibility_shim": {
                            "windows_powershell": {
                                "windows_directory_relative_path": _PS_RELATIVE,
                                "size": size,
                                "sha256": sha256,
                            }
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        return lock

    def test_valid_locked_powershell_resolves(self):
        real = _real_powershell()
        with tempfile.TemporaryDirectory() as tmp:
            lock = self._lock(
                Path(tmp),
                sha256=hashlib.sha256(real.read_bytes()).hexdigest(),
                size=real.stat().st_size,
            )
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COEVO_POWERSHELL_PATH", None)
                self.assertEqual(
                    str(real), locked_powershell_executable(lock, error_factory=ValueError)
                )

    def test_tampered_sha_is_rejected(self):
        real = _real_powershell()
        with tempfile.TemporaryDirectory() as tmp:
            lock = self._lock(Path(tmp), sha256="0" * 64, size=real.stat().st_size)
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop("COEVO_POWERSHELL_PATH", None)
                with self.assertRaisesRegex(ValueError, "integrity check"):
                    locked_powershell_executable(lock, error_factory=ValueError)

    def test_bad_lock_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock = Path(tmp) / "toolchain-lock.json"
            lock.write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "metadata is unavailable"):
                locked_powershell_executable(lock, error_factory=RuntimeError)

    def test_non_absolute_env_path_is_rejected(self):
        real = _real_powershell()
        with tempfile.TemporaryDirectory() as tmp:
            lock = self._lock(
                Path(tmp),
                sha256=hashlib.sha256(real.read_bytes()).hexdigest(),
                size=real.stat().st_size,
            )
            with mock.patch.dict(
                os.environ, {"COEVO_POWERSHELL_PATH": "powershell.exe"}, clear=False
            ):
                with self.assertRaisesRegex(ValueError, "must be absolute"):
                    locked_powershell_executable(lock, error_factory=ValueError)


class UnificationGuardTests(unittest.TestCase):
    def test_modules_delegate_to_shared_leaf(self):
        for relative in (
            "src/coevo/identity/certificates.py",
            "src/coevo/identity/audit_anchor.py",
            "src/coevo/identity/private_keys.py",
            "src/coevo/crypto/cng_handle.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                "coevo.powershell", text, f"{relative} must import the shared leaf"
            )

    def test_no_local_powershell_resolution_copies(self):
        marker = "WindowsPowerShell/v1.0/powershell.exe"
        for relative in (
            "src/coevo/identity/certificates.py",
            "src/coevo/identity/audit_anchor.py",
            "src/coevo/identity/private_keys.py",
            "src/coevo/crypto/cng_handle.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(
                marker, text, f"{relative} must not keep a local resolver copy"
            )


if __name__ == "__main__":
    unittest.main()
