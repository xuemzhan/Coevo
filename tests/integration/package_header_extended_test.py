"""Deferred algorithm-registry tests outside the US-5-AC-1 wire surface."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from coevo.protocol.sm2_extension import (
    AgentPackageAlgorithmUnsupportedError,
    IMPLEMENTED_KEY_ALGORITHMS,
    SM2_SM3,
    SUPPORTED_KEY_ALGORITHMS,
    require_supported_key_algorithm,
)


class DeferredAlgorithmRegistryTests(unittest.TestCase):
    def test_sm2_is_recognised_but_not_implemented(self) -> None:
        self.assertEqual(SUPPORTED_KEY_ALGORITHMS, frozenset({SM2_SM3}))
        self.assertEqual(IMPLEMENTED_KEY_ALGORITHMS, frozenset())
        with self.assertRaises(AgentPackageAlgorithmUnsupportedError):
            require_supported_key_algorithm(SM2_SM3)

    def test_rsa_is_not_advertised_as_a_wire_algorithm(self) -> None:
        with self.assertRaises(AgentPackageAlgorithmUnsupportedError):
            require_supported_key_algorithm("rsa-pkcs1-v1_5-sha256")

    def test_error_does_not_contain_key_material(self) -> None:
        marker = "private-key-material"
        try:
            require_supported_key_algorithm(SM2_SM3)
        except AgentPackageAlgorithmUnsupportedError as exc:
            rendered = str(exc)
            self.assertIn(SM2_SM3, rendered)
            self.assertNotIn(marker, rendered)


if __name__ == "__main__":
    unittest.main()
