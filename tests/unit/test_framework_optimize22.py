"""FRAMEWORK-OPTIMIZE-21: repo-wide unused top-level import guard."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "coevo"

# Intentional import-surface re-exports that are never referenced inside the
# defining module (kept for the historical private import surface). New
# re-export modules must extend this allowlist instead of regressing the guard.
ALLOWED_UNUSED = {
    "src/coevo/decision_brief/models.py": {
        "_stat_is_reparse",
        "_brief_id",
        "_build_content",
        "_clone_brief",
        "_clone_confirmation",
        "_clone_content",
        "_clone_risk_report",
        "_latest_receipt",
        "_make_version",
        "_risk_conclusion",
        "_validate_bound_risk",
        "_validate_content_model",
        "_validate_docx",
        "_validate_stored_brief",
    },
    # Package-level re-export: src/coevo/app/__init__.py imports
    # now_utc_iso_z from demo_support and re-exports it for consumers.
    "src/coevo/app/demo_support.py": {"now_utc_iso_z"},
}


def unused_import_names(text: str) -> list[tuple[int, str]]:
    tree = ast.parse(text)
    used = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    found: list[tuple[int, str]] = []
    for stmt in tree.body:
        if isinstance(stmt, ast.Import):
            for alias in stmt.names:
                name = alias.asname or alias.name.split(".")[0]
                if name not in used:
                    found.append((stmt.lineno, alias.name))
        elif isinstance(stmt, ast.ImportFrom) and stmt.module != "__future__":
            for alias in stmt.names:
                name = alias.asname or alias.name
                if name not in used:
                    found.append((stmt.lineno, alias.name))
    return found


class UnusedImportGuardTests(unittest.TestCase):
    def test_no_unused_top_level_imports_outside_allowlist(self):
        violations: list[str] = []
        for path in sorted(SRC.rglob("*.py")):
            if path.name == "__init__.py":
                continue
            rel = path.relative_to(ROOT).as_posix()
            allowed = ALLOWED_UNUSED.get(rel, set())
            try:
                found = unused_import_names(path.read_text(encoding="utf-8"))
            except SyntaxError as exc:
                self.fail(f"{rel}: syntax error: {exc}")
            for lineno, name in found:
                if name not in allowed:
                    violations.append(f"{rel}:{lineno}: {name}")
        self.assertEqual([], violations)

    def test_allowlist_entries_are_actual_imports(self):
        for rel, names in ALLOWED_UNUSED.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            for name in names:
                self.assertIn(name, text, f"{rel} does not import {name}")


if __name__ == "__main__":
    unittest.main()
