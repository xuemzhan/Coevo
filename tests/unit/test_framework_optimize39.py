"""FRAMEWORK-OPTIMIZE-39: revise field-override dedup guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.progress_capture import service


ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "src/coevo/progress_capture/service.py"


class ReviseOverrideGuardTests(unittest.TestCase):
    def test_revise_is_deduplicated(self):
        tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "ProgressCaptureService"
        )
        fn = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "revise"
        )
        self.assertLessEqual(
            fn.end_lineno - fn.lineno,
            100,
            "revise() must stay a lean per-field flow (was 109 lines)",
        )

    def test_apply_override_helper_exists_and_is_called_thrice(self):
        self.assertTrue(hasattr(service, "_apply_override"))
        text = SERVICE.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "ProgressCaptureService"
        )
        fn = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "revise"
        )
        src = ast.get_source_segment(text, fn)
        self.assertEqual(3, src.count("_apply_override("))

    def test_override_construction_is_deduplicated(self):
        text = SERVICE.read_text(encoding="utf-8")
        tree = ast.parse(text)
        cls = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "ProgressCaptureService"
        )
        fn = next(
            node
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "revise"
        )
        src = ast.get_source_segment(text, fn)
        self.assertNotIn("ItemOverride(", src, "revise() must not construct overrides")
        self.assertIn("ItemOverride(", text, "the helper must construct overrides")

    def test_revise_validation_marker_survives(self):
        text = SERVICE.read_text(encoding="utf-8")
        self.assertIn(
            "revise requires at least one of new_text/new_kind/new_confidence",
            text,
        )


if __name__ == "__main__":
    unittest.main()
