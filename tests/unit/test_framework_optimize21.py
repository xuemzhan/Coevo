"""FRAMEWORK-OPTIMIZE-20: _build extraction + models re-export guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.decision_brief import _build, models


ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "src/coevo/decision_brief/models.py"
BUILD = ROOT / "src/coevo/decision_brief/_build.py"

MOVED = (
    "_latest_receipt",
    "_validate_bound_risk",
    "_clone_risk_report",
    "_clone_confirmation",
    "_build_content",
    "_risk_conclusion",
    "_make_version",
    "_validate_stored_brief",
    "_validate_content_model",
    "_clone_content",
    "_clone_brief",
    "_brief_id",
    "_validate_docx",
)


class ExtractionGuardTests(unittest.TestCase):
    def test_models_no_longer_defines_moved_helpers(self):
        text = MODELS.read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(
                f"def {name}", text, f"models.py must not define {name}"
            )

    def test_models_reexports_from_build(self):
        text = MODELS.read_text(encoding="utf-8")
        self.assertIn("from ._build import", text)
        for name in MOVED:
            self.assertIs(
                getattr(models, name),
                getattr(_build, name),
                f"models.{name} must be the _build object",
            )

    def test_build_has_no_module_level_models_import(self):
        tree = ast.parse(BUILD.read_text(encoding="utf-8"))
        for stmt in tree.body:
            if isinstance(stmt, ast.ImportFrom) and stmt.module == "models":
                self.fail(f"module-level import from .models at line {stmt.lineno}")

    def test_each_build_function_lazily_imports_from_models_once(self):
        tree = ast.parse(BUILD.read_text(encoding="utf-8"))
        funcs = [
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual(MOVED, tuple(node.name for node in funcs))
        for fn in funcs:
            imports = [
                node
                for node in ast.walk(fn)
                if isinstance(node, ast.ImportFrom) and node.module == "models"
            ]
            self.assertEqual(
                1,
                len(imports),
                f"{fn.name} must import from .models exactly once (lazily)",
            )
            self.assertGreater(imports[0].lineno, fn.lineno)


if __name__ == "__main__":
    unittest.main()
