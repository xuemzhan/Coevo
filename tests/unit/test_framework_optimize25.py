"""FRAMEWORK-OPTIMIZE-24: merge_and_commit phase-decomposition guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.merge.engine import MergeEngine


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "src/coevo/merge/engine.py"

PHASES = (
    "_receipt_context",
    "_receipt_binding_rejection",
    "_field_decision_rejection",
    "_status_task_rejection",
)

# Fail-closed rejection markers that must survive the pure migration. Markers
# appear contiguously inside single string literals in the source.
MARKERS = (
    "authoritative import facts do not bind to the report",
    "committed merge contains an untrusted field decision",
    "or references an unknown task",
    "receipt signer is not the verified merge recipient",
    "receipt commit failed",
)


class MergeCommitDecompositionGuardTests(unittest.TestCase):
    def test_merge_and_commit_is_decomposed(self):
        tree = ast.parse(ENGINE.read_text(encoding="utf-8"))
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "MergeEngine"
        )
        mac = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "merge_and_commit"
        )
        self.assertLessEqual(
            mac.end_lineno - mac.lineno,
            130,
            "merge_and_commit() must stay a linear orchestration (was 176 lines)",
        )

    def test_phase_helpers_exist_as_private_methods(self):
        for name in PHASES:
            self.assertTrue(hasattr(MergeEngine, name), f"MergeEngine.{name} missing")

    def test_merge_and_commit_orchestrates_all_phases(self):
        text = ENGINE.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "MergeEngine"
        )
        mac = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "merge_and_commit"
        )
        src = ast.get_source_segment(text, mac)
        for name in PHASES:
            self.assertIn(f"self.{name}(", src, f"merge_and_commit() must call {name}")

    def test_rejection_markers_survive(self):
        text = ENGINE.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing rejection marker: {marker}")


if __name__ == "__main__":
    unittest.main()
