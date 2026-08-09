"""FRAMEWORK-OPTIMIZE-30: docstring-completion guards (audit + real_chain_store)."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED = {
    "src/coevo/audit_governance/stream_store.py": {
        "_append_record",
        "_read_rows",
        "_chain_hash",
    },
    "src/coevo/audit_governance/facade.py": {"_event_matches", "_event_to_export_row"},
    "src/coevo/orchestrator/real_chain_store.py": {
        "validate",
        "_snapshot",
        "_restore",
        "_cleanup_failed_create",
        "_guard",
        "_schema_projection_for",
        "_trusted_schema_projection",
        "_validate_schema",
        "_store_id_unlocked",
        "_checkpoint",
        "_recover_unlocked",
        "recover",
        "_transaction",
        "_audit",
        "_verify_audit_chain_unlocked",
        "_mark_interrupted_for_recovery",
        "record_attempt",
        "_require",
        "operation",
    },
}


def _has_docstring(node: ast.AST) -> bool:
    return (
        bool(node.body)
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
        and bool(node.body[0].value.value.strip())
    )


def _is_stub(node: ast.FunctionDef) -> bool:
    if len(node.body) != 1:
        return False
    stmt = node.body[0]
    if isinstance(stmt, ast.Pass):
        return True
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and stmt.value.value is Ellipsis
    )


class FinalDocstringGuardTests(unittest.TestCase):
    def test_required_functions_have_docstrings(self):
        missing: list[str] = []
        for rel, names in REQUIRED.items():
            tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
            occurrences: dict[str, list[ast.FunctionDef]] = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    occurrences.setdefault(node.name, []).append(node)
            for name in names:
                self.assertTrue(
                    occurrences.get(name), f"{rel}: {name} not found"
                )
                for node in occurrences[name]:
                    if _is_stub(node):
                        continue
                    if not _has_docstring(node):
                        missing.append(f"{rel}:{node.lineno}:{name}")
        self.assertEqual([], missing, "functions missing docstrings")


if __name__ == "__main__":
    unittest.main()
