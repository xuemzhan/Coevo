"""FRAMEWORK-OPTIMIZE-33: 64-hex regex convergence guards."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from src.coevo.ids import HEX_64, is_hex_64


ROOT = Path(__file__).resolve().parents[2]

# Modules that must use the shared leaf instead of a local 64-hex pattern.
CONVERGED = {
    "src/coevo/identity/private_keys.py": ("from src.coevo.ids import HEX_64 as _HEX_64",),
    "src/coevo/protocol/sm2_sign.py": ("from src.coevo.ids import HEX_64 as _HEX_64",),
    "src/coevo/audit_governance/models.py": ("from src.coevo.ids import is_hex_64",),
    "src/coevo/crypto/cng_handle.py": ("from src.coevo.ids import is_hex_64",),
}


class Hex64ConvergenceGuardTests(unittest.TestCase):
    def test_shared_pattern_is_fully_anchored(self):
        self.assertEqual(r"^[0-9a-f]{64}\Z", HEX_64.pattern)
        self.assertTrue(is_hex_64("a" * 64))
        self.assertFalse(is_hex_64("a" * 64 + "\n"))

    def test_converged_modules_use_shared_leaf(self):
        for relative, markers in CONVERGED.items():
            source = (ROOT / relative).read_text(encoding="utf-8")
            for marker in markers:
                self.assertIn(marker, source, f"{relative} must import {marker}")
            self.assertNotIn(
                're.compile(r"^[0-9a-f]{64}$"',
                source,
                f"{relative} must not keep a local 64-hex pattern",
            )
            self.assertNotIn(
                're.fullmatch(r"[0-9a-f]{64}"',
                source,
                f"{relative} must not keep a local fullmatch 64-hex pattern",
            )

    def test_shared_pattern_still_compiles(self):
        self.assertIsNotNone(re.fullmatch(HEX_64.pattern, "a" * 64))


if __name__ == "__main__":
    unittest.main()
