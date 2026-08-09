"""FRAMEWORK-OPTIMIZE-25: dispatch_event AGENT_CALL branch extraction guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.orchestrator import service


ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "src/coevo/orchestrator/service.py"

# Trace-detail markers that must survive the pure migration (contiguous in a
# single source literal).
MARKERS = (
    "requires human confirmation",
    "not in registry",
    "executed",
    "retried successfully",
    "not available after retry",
    "skipped",
    "escalating to human",
)


class DispatchExtractionGuardTests(unittest.TestCase):
    def test_dispatch_event_is_decomposed(self):
        tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Orchestrator"
        )
        de = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "dispatch_event"
        )
        self.assertLessEqual(
            de.end_lineno - de.lineno,
            110,
            "dispatch_event() must stay a loop orchestration (was 170 lines)",
        )

    def test_agent_step_helper_and_result_exist(self):
        self.assertTrue(hasattr(service, "_dispatch_agent_step"))
        self.assertTrue(hasattr(service, "_AgentStepResult"))

    def test_dispatch_event_calls_helper(self):
        text = SERVICE.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Orchestrator"
        )
        de = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "dispatch_event"
        )
        src = ast.get_source_segment(text, de)
        self.assertIn("_dispatch_agent_step(", src)

    def test_trace_detail_markers_survive(self):
        text = SERVICE.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing trace-detail marker: {marker}")


if __name__ == "__main__":
    unittest.main()
