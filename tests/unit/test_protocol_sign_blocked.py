"""REVIEW-FIX-1: assert_sign_blocked is fail-closed by name and behaviour.

The previous ``build_signed_payload`` name implied a working signing
path while the function always raised. The renamed surface makes the
blocked state explicit and must keep raising
:class:`AgentPackageCryptoUnavailableError` until an approved SM2
product is wired in (crypto scheme is out of scope for this slice).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import src.coevo.protocol as protocol
from src.coevo.protocol import assert_sign_blocked
from src.coevo.protocol.sm2_sign import AgentPackageCryptoUnavailableError


class AssertSignBlockedTests(unittest.TestCase):
    def test_always_raises_crypto_unavailable(self):
        with self.assertRaises(AgentPackageCryptoUnavailableError):
            assert_sign_blocked({}, signer_cert_id="CERT-SENDER")

    def test_legacy_name_is_removed(self):
        self.assertFalse(hasattr(protocol, "build_signed_payload"))
