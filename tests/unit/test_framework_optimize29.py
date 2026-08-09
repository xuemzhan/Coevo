"""FRAMEWORK-OPTIMIZE-28: docstring-completion guards for refactored domains."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# (relative path, function name) pairs that must carry a docstring. Extended in
# future comment-strengthening rounds instead of being weakened.
REQUIRED = {
    "src/coevo/decision_brief/_build.py": (
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
        "clone_section",
    ),
    "src/coevo/decision_brief/_util.py": (
        "_is_link_or_reparse",
        "_safe_string",
        "_digest",
        "_parse_utc",
        "_encode_json",
    ),
    "src/coevo/decision_brief/models.py": (
        "_validate_risk_report",
        "_risk_digest",
        "_version_digest",
        "_version_digest_values",
        "_content_digest",
        "_content_plain",
        "_content_sources",
        "_validate_template_ref",
        "_safe_string",
        "_parse_utc",
        "_encode_json",
    ),
    "src/coevo/merge/engine.py": (
        "_rollback_receipt_commit",
        "_reject",
        "_merge_text_field",
        "_merge_status_field",
        "_merge_str_list_field",
        "receipt_builder",
    ),
    "src/coevo/merge/receipt.py": (
        "_validate_receipt",
        "_signed_fields",
        "_freeze_value",
        "_copy_domain_value",
        "_canonical_plain",
        "_encode",
        "_guard_integer_materialization",
        "_parse_utc",
        "_revision_number",
        "_append",
        "_validate_history",
        "charge_utf8",
        "normalize",
        "visit",
    ),
    "src/coevo/merge/repository.py": (
        "create",
        "open",
        "_cleanup_failed_create",
        "_validate_schema",
        "_checkpoint",
        "_recover",
        "verified_history",
        "_decode_receipt",
        "_decode_baseline",
        "_decode_override",
        "_require_exact_mapping",
    ),
    "src/coevo/merge/models.py": ("_to_jsonable",),
    "src/coevo/orchestrator/_real_chain.py": (
        "_event_and_project_digests",
        "_validate_fixed_chain",
        "_trace",
        "_report",
        "_outcome",
        "project_baseline_to_requirements",
        "invoke",
        "build",
    ),
}


def _has_docstring(node: ast.AST) -> bool:
    return (
        bool(node.body)
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
        and bool(node.body[0].value.value.strip())
    )


class DocstringCompletionGuardTests(unittest.TestCase):
    def test_required_functions_have_docstrings(self):
        missing: list[str] = []
        for rel, names in REQUIRED.items():
            tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
            by_name: dict[str, list[ast.FunctionDef]] = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    by_name.setdefault(node.name, []).append(node)
            for name in names:
                candidates = by_name.get(name, [])
                self.assertTrue(candidates, f"{rel}: {name} not found")
                if not any(_has_docstring(c) for c in candidates):
                    missing.append(f"{rel}:{name}")
        self.assertEqual([], missing, "functions missing docstrings")


if __name__ == "__main__":
    unittest.main()
