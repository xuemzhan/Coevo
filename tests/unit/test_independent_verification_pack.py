"""Independent verification pack guard tests."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class VerificationPackTests(unittest.TestCase):
    def test_pack_covers_commands_evidence_and_gates(self) -> None:
        text = (
            ROOT / "docs" / "process" / "independent-verification-pack.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "mvp-verifier",
            "security-reviewer",
            "quality_gate.py --target fast",
            "requirements-test-matrix",
            "gate-results",
            "audit-head",
            "external-gates",
            "双签放行条件",
        ):
            self.assertIn(marker, text, marker)

    def test_external_gates_tracks_condition_11(self) -> None:
        gates = (
            ROOT / "docs" / "architecture" / "external-gates.md"
        ).read_text(encoding="utf-8")
        self.assertIn("mvp-complete 条件 11", gates)
        self.assertIn("`REVIEW-REQUIRED`", gates)

    def test_readiness_condition_11_is_updated(self) -> None:
        readiness = (
            ROOT / "docs" / "architecture" / "mvp-complete-readiness.md"
        ).read_text(encoding="utf-8")
        self.assertIn("待独立验收", readiness)


if __name__ == "__main__":
    unittest.main()
