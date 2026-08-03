"""CRYPTO-1: pure-Python SM3 cross-checked against the locked GmSSL 3.2.0 engine."""
from __future__ import annotations

import os
import subprocess
import unittest
import uuid
from pathlib import Path

from src.coevo.crypto import GmsslPrototypeProvider
from src.coevo.crypto.sm3 import sm3_hexdigest


ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == "nt", "locked Win64 GmSSL engine requires Windows")
class Sm3CrossCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = "sm3x-" + uuid.uuid4().hex[:16]
        cls.output = ROOT / "loop" / "runtime" / "sm2-test-pki" / cls.profile
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(ROOT / "scripts" / "generate-sm2-test-pki.ps1"),
             "-ProfileName", cls.profile],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        cls.provider = GmsslPrototypeProvider(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        import shutil
        shutil.rmtree(cls.output, ignore_errors=True)

    def _messages(self):
        yield b""
        yield b"abc"
        yield b"coevo offline task package"
        yield bytes(range(55))
        yield bytes(range(56))
        yield bytes(range(64))
        yield b"a" * 1000

    def test_pure_sm3_matches_gmssl_engine(self):
        for message in self._messages():
            with self.subTest(size=len(message)):
                self.assertEqual(
                    self.provider.sm3(message).hex(),
                    sm3_hexdigest(message),
                    f"SM3 mismatch for {len(message)}-byte message",
                )

    def test_pure_sm3_official_abc_vector(self):
        self.assertEqual(
            "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0",
            sm3_hexdigest(b"abc"),
        )


if __name__ == "__main__":
    unittest.main()
