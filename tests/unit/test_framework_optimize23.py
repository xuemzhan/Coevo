"""FRAMEWORK-OPTIMIZE-22: MergeEngine.merge phase-decomposition guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.merge.engine import MergeEngine


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "src/coevo/merge/engine.py"

PHASES = (
    "_validate_merge_inputs",
    "_import_binding_rejection",
    "_duplicate_rejection",
    "_revision_rejection",
    "_decision_maker_rejection",
    "_merge_fields",
    "_rejected_proposal",
    "_commit_proposal",
)

# Original fail-closed rejection markers that must survive the pure migration.
# Markers are matched against raw source text, so each must appear contiguously
# inside a single string literal (multi-literal concatenations are avoided).
REJECTION_MARKERS = (
    "transaction must be COMMITTED per AC-1 + P1",
    "no-op (AC-2 + P2)",
    "explicit user conflict resolution (section 16.4)",
    "(mandatory 8.4)",
    "(AC-6 + P3)",
    "refusing double-commit (AC-2 + P2)",
)


class MergeDecompositionGuardTests(unittest.TestCase):
    def test_merge_method_is_decomposed(self):
        tree = ast.parse(ENGINE.read_text(encoding="utf-8"))
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "MergeEngine"
        )
        merge = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "merge"
        )
        self.assertLessEqual(
            merge.end_lineno - merge.lineno,
            200,
            "merge() must stay a linear orchestration (was 394 lines)",
        )

    def test_phase_helpers_exist_as_private_methods(self):
        for name in PHASES:
            self.assertTrue(hasattr(MergeEngine, name), f"MergeEngine.{name} missing")

    def test_merge_orchestrates_all_phases(self):
        text = ENGINE.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "MergeEngine"
        )
        merge = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "merge"
        )
        src = ast.get_source_segment(text, merge)
        for name in PHASES:
            self.assertIn(f"self.{name}(", src, f"merge() must call {name}")

    def test_rejection_reason_markers_survive(self):
        text = ENGINE.read_text(encoding="utf-8")
        for marker in REJECTION_MARKERS:
            self.assertIn(marker, text, f"missing rejection marker: {marker}")


if __name__ == "__main__":
    unittest.main()
