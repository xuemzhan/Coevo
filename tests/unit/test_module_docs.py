"""OPTIMIZE-16: module-documentation governance guards.

Keeps `docs/modules/` honest: every `src/coevo` package must have a module
doc, every production file must be listed in that doc's file inventory, the
root-level modules must be covered by `root_modules.md`, and the index must
list every package.
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = ROOT / "src" / "coevo"
DOC_DIR = ROOT / "docs" / "modules"


def _packages() -> list[str]:
    return sorted(
        path.name
        for path in PKG_ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    )


class ModuleDocsTests(unittest.TestCase):
    def test_every_package_has_a_module_doc(self):
        missing = [p for p in _packages() if not (DOC_DIR / f"{p}.md").is_file()]
        self.assertEqual([], missing, "packages missing module docs")

    def test_every_package_file_is_listed_in_its_doc(self):
        for pkg_dir in sorted(PKG_ROOT.iterdir()):
            if not pkg_dir.is_dir() or not (pkg_dir / "__init__.py").is_file():
                continue
            doc = DOC_DIR / f"{pkg_dir.name}.md"
            if not doc.is_file():
                continue
            text = doc.read_text(encoding="utf-8")
            missing = sorted(
                path.name
                for path in pkg_dir.glob("*.py")
                if path.name != "__init__.py" and path.name not in text
            )
            self.assertEqual(
                [], missing, f"{pkg_dir.name} files missing from its module doc"
            )

    def test_root_modules_are_documented(self):
        text = (DOC_DIR / "root_modules.md").read_text(encoding="utf-8")
        missing = sorted(
            path.name
            for path in PKG_ROOT.glob("*.py")
            if path.name != "__init__.py" and path.name not in text
        )
        self.assertEqual(
            [], missing, "root module files missing from root_modules.md"
        )

    def test_index_lists_every_package(self):
        index = (DOC_DIR / "README.md").read_text(encoding="utf-8")
        missing = [p for p in _packages() if p not in index]
        self.assertEqual([], missing, "packages missing from module-docs index")


if __name__ == "__main__":
    unittest.main()
