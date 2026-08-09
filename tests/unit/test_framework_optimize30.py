"""FRAMEWORK-OPTIMIZE-29: docstring-completion guards for security-critical domains."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# (relative path, function name) pairs whose EVERY occurrence must carry a
# non-empty docstring. Duplicate names (e.g. audit_anchor `_run`) are checked
# for every occurrence.
REQUIRED = {
    "src/coevo/crypto/cng_handle.py": {
        "_validate_kek_name",
        "_locked_powershell",
        "to_mapping",
        "_run",
        "_append",
        "_read",
        "_write",
        "_verify_chain",
    },
    "src/coevo/crypto/gmssl_provider.py": {"verify", "_invoke", "_decode"},
    "src/coevo/crypto/sm3.py": {"_ff", "_gg", "_compress"},
    "src/coevo/identity/audit_anchor.py": {
        "_run",
        "_validate_marker",
        "_arguments",
        "_paths",
        "verify_marker",
        "_signature",
        "_decode_main",
        "_read_official",
        "_read_pending",
        "_tombstone",
        "_complete_retirement",
    },
    "src/coevo/identity/repository.py": {
        "_validate_schema",
        "_insert_audit",
        "_business_digest",
        "_checkpoint",
        "_internal_audit_valid",
        "_recover_and_require_consistent",
        "_commit_with_anchor",
    },
    "src/coevo/identity/private_keys.py": {
        "_powershell_executable",
        "_reference_from_helper",
        "verify",
        "_run",
        "store",
        "_record",
    },
    "src/coevo/identity/validation.py": {"_text", "_object", "_instant", "_digestable"},
    "src/coevo/identity/certificates.py": {"_instant"},
    "src/coevo/protocol/agent_package.py": {
        "_reserved_must_be_zero",
        "_require_text",
        "_require_nonce",
        "_require_int",
        "from_mapping",
        "_require_uuid_string",
        "_require_instant",
    },
    "src/coevo/protocol/package_store_db.py": {
        "_validate_iso_z",
        "_record_hash",
        "_row_to_record",
        "close",
        "_verify_integrity",
        "_verify_schema",
        "_verify_chain",
    },
    "src/coevo/protocol/package_builder.py": {"unique"},
    "src/coevo/protocol/import_service.py": {"_record"},
    "src/coevo/protocol/replay_detector.py": {"_registry_for"},
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
    """One-line protocol/abstract stub (``...`` or ``pass``) is exempt."""
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


class SecurityDomainDocstringGuardTests(unittest.TestCase):
    def test_required_functions_have_docstrings(self):
        missing: list[str] = []
        for rel, names in REQUIRED.items():
            tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
            occurrences: dict[str, list[ast.FunctionDef]] = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    occurrences.setdefault(node.name, []).append(node)
            for name in names:
                for node in occurrences.get(name, []):
                    if _is_stub(node):
                        continue
                    if not _has_docstring(node):
                        missing.append(f"{rel}:{node.lineno}:{name}")
        self.assertEqual([], missing, "functions missing docstrings")


if __name__ == "__main__":
    unittest.main()
