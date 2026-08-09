"""FRAMEWORK-OPTIMIZE-38: _build_content phase-decomposition guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.decision_brief import _build


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "src/coevo/decision_brief/_build.py"

HELPERS = ("_type_parameters", "_content_title", "_progress_text")

# Fail-closed error markers that must survive the pure migration (contiguous in
# single source literals).
MARKERS = (
    "period_end must be >= period_start",
    "topic_risk_ids must be a non-empty tuple of unique strings",
    "PERIODIC briefs cannot use topic_risk_ids",
    "RISK_TOPIC briefs require topic_risk_ids",
    "STAGE briefs do not accept period or topic parameters",
)


class BuildContentDecompositionGuardTests(unittest.TestCase):
    def test_build_content_is_decomposed(self):
        tree = ast.parse(BUILD.read_text(encoding="utf-8"))
        fn = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_build_content"
        )
        self.assertLessEqual(
            fn.end_lineno - fn.lineno,
            100,
            "_build_content() must stay an assembly orchestration (was 145 lines)",
        )

    def test_phase_helpers_exist(self):
        for name in HELPERS:
            self.assertTrue(hasattr(_build, name), f"_build.{name} missing")

    def test_build_content_calls_all_helpers(self):
        text = BUILD.read_text(encoding="utf-8")
        tree = ast.parse(text)
        fn = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_build_content"
        )
        src = ast.get_source_segment(text, fn)
        for name in HELPERS:
            self.assertIn(f"{name}(", src, f"_build_content() must call {name}")

    def test_error_message_markers_survive(self):
        text = BUILD.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing error marker: {marker}")


if __name__ == "__main__":
    unittest.main()
