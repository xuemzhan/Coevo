"""FRAMEWORK-OPTIMIZE-31: _score_candidate phase-decomposition guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.talent import recommender


ROOT = Path(__file__).resolve().parents[2]
RECOMMENDER = ROOT / "src/coevo/talent/recommender.py"

PHASES = (
    "_match_skills",
    "_match_credentials",
    "_window_fit",
    "_load_headroom",
    "_tie_break",
)

# Reason-kind markers that must survive the pure migration (contiguous in a
# single source literal).
MARKERS = (
    "skill_match",
    "credential_match",
    "availability_fit",
    "load_capacity",
    "tie_break",
)


class ScoreCandidateDecompositionGuardTests(unittest.TestCase):
    def test_score_candidate_is_decomposed(self):
        tree = ast.parse(RECOMMENDER.read_text(encoding="utf-8"))
        fn = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_score_candidate"
        )
        self.assertLessEqual(
            fn.end_lineno - fn.lineno,
            70,
            "_score_candidate() must stay an orchestration (was 123 lines)",
        )

    def test_phase_helpers_exist(self):
        for name in PHASES:
            self.assertTrue(hasattr(recommender, name), f"recommender.{name} missing")

    def test_score_candidate_calls_all_phases(self):
        text = RECOMMENDER.read_text(encoding="utf-8")
        tree = ast.parse(text)
        fn = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_score_candidate"
        )
        src = ast.get_source_segment(text, fn)
        for name in PHASES:
            self.assertIn(f"{name}(", src, f"_score_candidate() must call {name}")

    def test_reason_kind_markers_survive(self):
        text = RECOMMENDER.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing reason-kind marker: {marker}")


if __name__ == "__main__":
    unittest.main()
