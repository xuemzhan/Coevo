"""Unit tests for GmSSL prototype provider launch retry (stability)."""
from __future__ import annotations

import struct
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from src.coevo.crypto.gmssl_provider import GmsslPrototypeError, GmsslPrototypeProvider


_REPLY = b"COEVOCRYPTO-R/1"


def _reply(frame: bytes) -> bytes:
    return _REPLY + bytes([1]) + struct.pack(">I", len(frame)) + frame


def _provider() -> GmsslPrototypeProvider:
    provider = object.__new__(GmsslPrototypeProvider)
    provider._root = Path(".")
    provider._launcher = Path("crypto-helper.ps1")
    provider._timeout = 1.0
    return provider


class GmsslLaunchRetryTests(unittest.TestCase):
    def test_transient_launch_failure_is_retried_and_succeeds(self):
        provider = _provider()
        results = [
            subprocess.CompletedProcess([], 1, stdout=b"", stderr=b""),
            subprocess.CompletedProcess([], 0, stdout=_reply(b"ok"), stderr=b""),
        ]
        with mock.patch.object(
            subprocess, "run", side_effect=results
        ) as run:
            frames = provider._invoke(1, "demo", b"request")
        self.assertEqual((b"ok",), frames)
        self.assertEqual(2, run.call_count, "transient launch failure must retry")

    def test_repeated_launch_failure_raises_after_bounded_retries(self):
        provider = _provider()
        results = [
            subprocess.CompletedProcess([], 1, stdout=b"", stderr=b""),
            subprocess.CompletedProcess([], 1, stdout=b"", stderr=b""),
        ]
        with mock.patch.object(subprocess, "run", side_effect=results) as run:
            with self.assertRaises(GmsslPrototypeError) as ctx:
                provider._invoke(1, "demo", b"request", retries=1)
        self.assertEqual("GCP-E-LAUNCH", str(ctx.exception))
        self.assertEqual(2, run.call_count, "retries must be bounded")

    def test_default_retries_absorb_two_transient_launch_failures(self):
        provider = _provider()
        results = [
            subprocess.CompletedProcess([], 1, stdout=b"", stderr=b""),
            subprocess.CompletedProcess([], 1, stdout=b"", stderr=b""),
            subprocess.CompletedProcess([], 0, stdout=_reply(b"ok"), stderr=b""),
        ]
        with mock.patch.object(subprocess, "run", side_effect=results) as run:
            frames = provider._invoke(1, "demo", b"request")
        self.assertEqual((b"ok",), frames)
        self.assertEqual(3, run.call_count, "default retries must cover two retries")

    def test_helper_reported_crypto_error_is_never_retried(self):
        provider = _provider()
        error = subprocess.CompletedProcess(
            [], 2, stdout=b"", stderr=b"GCP-E-SIGN key rejected"
        )
        with mock.patch.object(subprocess, "run", return_value=error) as run:
            with self.assertRaises(GmsslPrototypeError) as ctx:
                provider._invoke(1, "demo", b"request")
        self.assertIn("GCP-E-SIGN", str(ctx.exception))
        self.assertEqual(1, run.call_count, "authoritative helper errors must not retry")

    def test_oserror_launch_failure_retries_then_raises(self):
        provider = _provider()
        with mock.patch.object(
            subprocess,
            "run",
            side_effect=[OSError("spawn race"), OSError("spawn race")],
        ) as run:
            with self.assertRaises(GmsslPrototypeError) as ctx:
                provider._invoke(1, "demo", b"request", retries=1)
        self.assertEqual("GCP-E-LAUNCH", str(ctx.exception))
        self.assertEqual(2, run.call_count)

    def test_invalid_retries_are_rejected(self):
        provider = _provider()
        with self.assertRaises(ValueError):
            provider._invoke(1, "demo", b"request", retries=5)


if __name__ == "__main__":
    unittest.main()
