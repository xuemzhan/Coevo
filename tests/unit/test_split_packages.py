"""OPTIMIZE-12: tests for the locked mechanical split tool (scripts/split_packages.py)."""
from __future__ import annotations

import ast
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "split_packages", ROOT / "scripts" / "split_packages.py"
)
split_packages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(split_packages)


_FIXTURE = '''"""pkg docstring."""

import os
from typing import Any


class Thing:
    """A thing."""

    def method(self) -> str:
        return "x"


@staticmethod
def helper(value: str) -> str:
    return value.upper()


__all__ = ["Thing", "helper"]
'''


class OffsetHelpersTests(unittest.TestCase):
    def test_line_offsets(self):
        offsets = split_packages.line_offsets("a\nbb\n")
        self.assertEqual([0, 2, 5], offsets)

    def test_node_slice_preserves_decorators(self):
        tree = ast.parse(_FIXTURE)
        offsets = split_packages.line_offsets(_FIXTURE)
        helper = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "helper"
        )
        start = split_packages.node_start(helper, offsets)
        end = split_packages.node_end(helper, offsets)
        segment = _FIXTURE[start:end]
        self.assertIn("@staticmethod", segment)
        self.assertIn("def helper", segment)

    def test_node_names(self):
        tree = ast.parse(_FIXTURE)
        assign = next(node for node in tree.body if isinstance(node, ast.Assign))
        self.assertEqual(["__all__"], split_packages.node_names(assign))

    def test_used_names_and_import_pruning(self):
        tree = ast.parse(
            "import os\nimport json\nfrom typing import Any\n\n"
            "value = os.path.join('a', 'b')\n"
        )
        body = tree.body
        used = split_packages.used_names(
            [node for node in body if not isinstance(node, (ast.Import, ast.ImportFrom))]
        )
        self.assertIn("os", used)
        kept = [
            split_packages.filter_import(node, used)
            for node in body
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        names = [
            name
            for item in kept
            if item is not None
            for name in split_packages.import_bound_names(item)
        ]
        self.assertIn("os", names)
        self.assertNotIn("json", names)
        self.assertNotIn("Any", names)


class SplitPackageTests(unittest.TestCase):
    def test_split_rewrites_init_and_creates_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "pkg"
            pkg_dir.mkdir()
            (pkg_dir / "__init__.py").write_text(_FIXTURE, encoding="utf-8")
            plan = {
                "modules": ["models"],
                "descriptions": {"models": "domain models (test fixture)"},
                "targets": {"Thing": "models", "helper": "models"},
                "keep_in_init": [],
            }
            with mock.patch.object(split_packages, "ROOT", Path(tmp)):
                split_packages.split_package("pkg", plan)
            models = pkg_dir / "models.py"
            self.assertTrue(models.is_file())
            models_text = models.read_text(encoding="utf-8")
            self.assertIn("class Thing", models_text)
            self.assertIn("def helper", models_text)
            init_text = (pkg_dir / "__init__.py").read_text(encoding="utf-8")
            self.assertIn("from .models import", init_text)
            self.assertIn("__all__", init_text)


if __name__ == "__main__":
    unittest.main()
