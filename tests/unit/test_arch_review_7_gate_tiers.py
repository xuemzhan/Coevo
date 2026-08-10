"""ARCH-REVIEW-7: gate tier (fast vs quality) guard tests.

Contract (docs/architecture/gate-tiers.md):

* ``fast`` = compileall + lint + unit tests (iteration inner loop);
* ``quality`` stays the release/closure gate and its command set is a
  regression pin (fingerprint unchanged);
* ``make.cs`` exposes the ``fast`` target;
* any change to the gate scripts must re-sync the script inventory locks.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location(
    "quality_gate", ROOT / "scripts" / "quality_gate.py"
)
quality_gate = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / "scripts"))
assert spec.loader is not None
spec.loader.exec_module(quality_gate)


class FastTierTests(unittest.TestCase):
    def test_fast_target_equals_fmt_lint_unit(self) -> None:
        self.assertIn("fast", quality_gate.TARGETS)
        expected = (
            quality_gate.TARGETS["fmt"]
            + quality_gate.TARGETS["lint"]
            + [
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "tests/unit",
                    "-v",
                ]
            ]
        )
        self.assertEqual(quality_gate.TARGETS["fast"], expected)
        self.assertEqual(quality_gate.commands("fast"), expected)

    def test_quality_target_command_set_unchanged(self) -> None:
        """Regression pin: quality = fmt+lint+test+security+e2e."""
        self.assertEqual(
            quality_gate.commands("quality"),
            [
                command
                for name in (
                    "fmt",
                    "lint",
                    "test",
                    "test-security",
                    "test-e2e",
                )
                for command in quality_gate.TARGETS[name]
            ],
        )
        self.assertEqual(
            quality_gate.fingerprint(quality_gate.commands("quality")),
            "f742f64aa8dce72c",
        )

    def test_make_shim_exposes_fast_target(self) -> None:
        source = (ROOT / "scripts" / "tool-shims" / "make.cs").read_text(
            encoding="utf-8"
        )
        self.assertIn('"fast"', source)
        self.assertIn("fast|test", source)

    def test_gate_tiers_doc_exists(self) -> None:
        doc = (ROOT / "docs" / "architecture" / "gate-tiers.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("fast", doc)
        self.assertIn("quality", doc)
        self.assertIn("python-script-lock.tsv", doc)


if __name__ == "__main__":
    unittest.main()
