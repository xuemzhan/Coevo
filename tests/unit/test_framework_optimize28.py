"""FRAMEWORK-OPTIMIZE-27: resume_real_chain phase-decomposition guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.orchestrator import _real_chain


ROOT = Path(__file__).resolve().parents[2]
REAL_CHAIN = ROOT / "src/coevo/orchestrator/_real_chain.py"

PHASES = (
    "_validate_resume_context",
    "_verify_resume_bindings",
    "_require_package_agent",
    "_begin_resume",
)

# Fail-closed error markers that must survive the pure migration (contiguous in
# single source literals).
MARKERS = (
    "resume requires CONFIRMED_PENDING_PACKAGE outcome",
    "confirmed outcome belongs to a different store",
    "resume context does not match confirmed outcome",
    "resume workspace revision does not match confirmed base_revision",
    "resume event digest does not match confirmed outcome",
    "confirmed outcome does not match stored state",
    "step 4 package agent must be registered and AVAILABLE",
    "confirmed outcome is missing package preview",
)


class ResumePhaseGuardTests(unittest.TestCase):
    def test_resume_real_chain_is_decomposed(self):
        tree = ast.parse(REAL_CHAIN.read_text(encoding="utf-8"))
        fn = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "resume_real_chain"
        )
        self.assertLessEqual(
            fn.end_lineno - fn.lineno,
            110,
            "resume_real_chain() must stay an orchestration (was 148 lines)",
        )

    def test_phase_helpers_exist(self):
        for name in PHASES:
            self.assertTrue(hasattr(_real_chain, name), f"_real_chain.{name} missing")

    def test_resume_real_chain_calls_all_phases(self):
        text = REAL_CHAIN.read_text(encoding="utf-8")
        tree = ast.parse(text)
        fn = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "resume_real_chain"
        )
        src = ast.get_source_segment(text, fn)
        for name in PHASES:
            self.assertIn(f"{name}(", src, f"resume_real_chain() must call {name}")

    def test_error_message_markers_survive(self):
        text = REAL_CHAIN.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing error marker: {marker}")


if __name__ == "__main__":
    unittest.main()
