"""FRAMEWORK-OPTIMIZE-34: from_mapping cross-field validation guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.protocol.agent_package import EnvelopeHeader


ROOT = Path(__file__).resolve().parents[2]
AGENT_PACKAGE = ROOT / "src/coevo/protocol/agent_package.py"

# Fail-closed error markers that must survive the pure migration (contiguous in
# single source literals).
MARKERS = (
    "is not in the protocol enum",
    "for protocol 1.0",
    "compression is not supported",
    "expires_at must be strictly after created_at",
    "nonce must not be empty when payload_length is nonzero",
    "1 TiB hard limit",
)


class FromMappingCrossFieldGuardTests(unittest.TestCase):
    def test_from_mapping_is_decomposed(self):
        tree = ast.parse(AGENT_PACKAGE.read_text(encoding="utf-8"))
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "EnvelopeHeader"
        )
        fn = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "from_mapping"
        )
        self.assertLessEqual(
            fn.end_lineno - fn.lineno,
            90,
            "from_mapping() must stay a construction + validation orchestration (was 103 lines)",
        )

    def test_cross_field_validator_exists_and_is_called(self):
        self.assertTrue(hasattr(EnvelopeHeader, "_validate_cross_fields"))
        text = AGENT_PACKAGE.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "EnvelopeHeader"
        )
        fn = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "from_mapping"
        )
        src = ast.get_source_segment(text, fn)
        self.assertIn("_validate_cross_fields(", src)

    def test_error_message_markers_survive(self):
        text = AGENT_PACKAGE.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing error marker: {marker}")


if __name__ == "__main__":
    unittest.main()
