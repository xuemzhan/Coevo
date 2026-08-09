"""FRAMEWORK-OPTIMIZE-13: shared 64-hex leaf (ids.py extension)."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.ids import HEX_64, is_hex_64


ROOT = Path(__file__).resolve().parents[2]


class Hex64Tests(unittest.TestCase):
    def test_shared_pattern_matches_64_lowercase_hex(self) -> None:
        self.assertEqual(r"^[0-9a-f]{64}\Z", HEX_64.pattern)
        self.assertTrue(is_hex_64("a" * 64))
        self.assertTrue(is_hex_64("0123456789abcdef" * 4))

    def test_is_hex_64_fails_closed(self) -> None:
        for value in (
            "",
            "A" * 64,
            "g" * 64,
            "a" * 63,
            "a" * 65,
            "a" * 64 + "\n",
            None,
            123,
        ):
            self.assertFalse(is_hex_64(value), repr(value))


class Hex64ConsolidationGuardTests(unittest.TestCase):
    def test_modules_use_shared_hex_64(self) -> None:
        modules = (
            "src/coevo/cockpit/models.py",
            "src/coevo/progress_capture/models.py",
            "src/coevo/progress_capture/watcher.py",
            "src/coevo/report/models.py",
            "src/coevo/framework/a2a.py",
            "src/coevo/framework/plan.py",
            "src/coevo/framework/memory.py",
            "src/coevo/identity/private_keys.py",
            "src/coevo/protocol/sm2_sign.py",
            "src/coevo/audit_governance/models.py",
            "src/coevo/crypto/cng_handle.py",
        )
        for relative in modules:
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(
                're.compile(r"^[0-9a-f]{64}$"',
                source,
                f"{relative} must import HEX_64 from src.coevo.ids",
            )

    def test_framework_modules_also_use_shared_safe_id(self) -> None:
        # OPTIMIZE-11 missed a2a/plan/memory; OPTIMIZE-13 closes the gap.
        for relative in (
            "src/coevo/framework/a2a.py",
            "src/coevo/framework/plan.py",
            "src/coevo/framework/memory.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(
                "from src.coevo.ids import SAFE_ID as _SAFE_ID",
                source,
                f"{relative} must alias the shared SAFE_ID",
            )


if __name__ == "__main__":
    unittest.main()
