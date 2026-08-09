"""FRAMEWORK-OPTIMIZE-32: _analyze risk-rule decomposition guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.risk import analyzer


ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "src/coevo/risk/analyzer.py"

HELPERS = (
    "_validated_completed_task_ids",
    "_deadline_overrun_risk",
    "_evidence_shortfall_risk",
    "_long_silence_risk",
    "_predecessor_unfinished_risk",
    "_status_bloom_risk",
    "_coordination_risk",
)

# Risk-basis markers that must survive the pure migration (contiguous literals).
MARKERS = (
    "task/project deadline precedes now",
    "insufficient completed tasks",
    "no merged feedback for at least",
    "lack accepted completion markers",
    "may inherit risk",
    "may stall",
    "severity reached",
)


class RiskRuleDecompositionGuardTests(unittest.TestCase):
    def test_analyze_is_decomposed(self):
        tree = ast.parse(ANALYZER.read_text(encoding="utf-8"))
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "RiskAnalyzer"
        )
        fn = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "_analyze"
        )
        self.assertLessEqual(
            fn.end_lineno - fn.lineno,
            100,
            "_analyze() must stay a rule orchestration (was 120 lines)",
        )

    def test_rule_helpers_exist(self):
        for name in HELPERS:
            self.assertTrue(hasattr(analyzer, name), f"analyzer.{name} missing")

    def test_analyze_calls_all_helpers(self):
        text = ANALYZER.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "RiskAnalyzer"
        )
        fn = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "_analyze"
        )
        src = ast.get_source_segment(text, fn)
        for name in HELPERS:
            self.assertIn(f"{name}(", src, f"_analyze() must call {name}")

    def test_risk_basis_markers_survive(self):
        text = ANALYZER.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing risk-basis marker: {marker}")


if __name__ == "__main__":
    unittest.main()
