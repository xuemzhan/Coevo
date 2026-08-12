"""ARCH-REVIEW-9: Win7 compatibility subset wired into the quality gate.

Contract: the `test-win7` target runs `tests/win7` and is part of the full
`quality` command set, so the Win7 compat profile cannot silently rot.
The explicit feature-degradation list lives in
`docs/architecture/win7-compat-branch.md` (guarded by
`tests/win7/test_win7_compat_profile.py`).
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
sys.modules[spec.name] = quality_gate
spec.loader.exec_module(quality_gate)


class Win7GateTests(unittest.TestCase):
    def test_test_win7_target_runs_win7_suite(self) -> None:
        self.assertIn("test-win7", quality_gate.TARGETS)
        self.assertEqual(
            quality_gate.TARGETS["test-win7"],
            [
                [
                    sys.executable,
                    str(ROOT / "scripts" / "test.py"),
                    "--suite",
                    "win7",
                ]
            ],
        )

    def test_win7_is_part_of_quality_gate(self) -> None:
        quality = quality_gate.commands("quality")
        win7_argv = quality_gate.TARGETS["test-win7"][0]
        self.assertIn(win7_argv, quality)
        self.assertEqual(
            quality_gate.fingerprint(quality),
            "b5c12e15ae7c559f",
        )

    def test_make_shim_exposes_test_win7(self) -> None:
        source = (ROOT / "scripts" / "tool-shims" / "make.cs").read_text(
            encoding="utf-8"
        )
        self.assertIn('"test-win7"', source)
        self.assertIn("test-win7|quality", source)

    def test_win7_suite_and_degradation_doc_exist(self) -> None:
        self.assertTrue(
            (ROOT / "tests" / "win7" / "test_win7_compat_profile.py").is_file()
        )
        doc = (ROOT / "docs" / "architecture" / "win7-compat-branch.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("win7-compat", doc)


if __name__ == "__main__":
    unittest.main()
