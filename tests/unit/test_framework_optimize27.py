"""FRAMEWORK-OPTIMIZE-26: TaskDecompositionAgent._validate phase guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.task_decomposition import agent


ROOT = Path(__file__).resolve().parents[2]
AGENT = ROOT / "src/coevo/task_decomposition/agent.py"

# Fail-closed error markers that must survive the pure migration (contiguous in
# single source literals).
MARKERS = (
    "tasks must be a bounded list",
    "candidate_edges must be a bounded list",
    "task entry must be an object",
    "unknown or unsafe work_package_id",
    "unsafe task_id",
    "task window must be ISO-8601 Z",
    "task window is inverted",
    "invalid acceptance_criteria",
    "edge entry must be an object",
    "edge ids must be safe-ids",
    "edge cannot be a self-loop",
    "edge references an unknown task id",
)


class TaskValidationDecompositionGuardTests(unittest.TestCase):
    def test_validate_is_decomposed(self):
        tree = ast.parse(AGENT.read_text(encoding="utf-8"))
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "TaskDecompositionAgent"
        )
        validate = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "_validate"
        )
        self.assertLessEqual(
            validate.end_lineno - validate.lineno,
            60,
            "_validate() must stay a linear orchestration (was 108 lines)",
        )

    def test_parse_helpers_exist(self):
        self.assertTrue(hasattr(agent, "_parse_task"))
        self.assertTrue(hasattr(agent, "_parse_edge"))

    def test_validate_calls_parse_helpers(self):
        text = AGENT.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "TaskDecompositionAgent"
        )
        validate = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "_validate"
        )
        src = ast.get_source_segment(text, validate)
        self.assertIn("_parse_task(", src)
        self.assertIn("_parse_edge(", src)

    def test_error_message_markers_survive(self):
        text = AGENT.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing error marker: {marker}")


if __name__ == "__main__":
    unittest.main()
