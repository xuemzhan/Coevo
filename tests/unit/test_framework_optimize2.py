"""FRAMEWORK-OPTIMIZE-2: shared UTC timestamp generator consolidation."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from src.coevo.timefmt import is_iso_utc_z, now_utc_iso_z


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "coevo"


class TimefmtNowTests(unittest.TestCase):
    def test_now_utc_iso_z_is_valid_iso_utc_with_fractional_seconds(self) -> None:
        value = now_utc_iso_z()
        self.assertTrue(is_iso_utc_z(value), value)
        self.assertIn(".", value, "expected fractional seconds to be preserved")
        self.assertTrue(value.endswith("Z"))

    def test_now_utc_iso_z_defined_only_in_timefmt(self) -> None:
        definitions = []
        inline = []
        for path in SRC.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(source.splitlines(), 1):
                stripped = line.strip()
                if re.match(r"^def (_now_utc_iso[a-z_]*|now_utc_iso_z)\(", stripped):
                    definitions.append((path.relative_to(ROOT).as_posix(), lineno))
                if re.search(
                    r"datetime\.now\((UTC|dt\.UTC)\)\.isoformat\(\)"
                    r'\.replace\("\+00:00", "Z"\)',
                    stripped,
                ):
                    inline.append((path.relative_to(ROOT).as_posix(), lineno))
        timefmt_defs = [
            item for item in definitions if item[0] == "src/coevo/timefmt.py"
        ]
        self.assertEqual(1, len(timefmt_defs), timefmt_defs)
        self.assertEqual(
            [],
            [item for item in definitions if item[0] != "src/coevo/timefmt.py"],
            "product modules must import now_utc_iso_z from src.coevo.timefmt",
        )
        self.assertEqual(
            [],
            inline,
            "no inline datetime.now(UTC).isoformat() copies outside timefmt",
        )


if __name__ == "__main__":
    unittest.main()
