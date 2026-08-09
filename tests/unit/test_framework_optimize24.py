"""FRAMEWORK-OPTIMIZE-23: manifest_checker._validate phase-decomposition guards."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from src.coevo.framework import manifest_checker


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "src/coevo/framework/manifest_checker.py"

PHASES = (
    "_validate_metadata",
    "_validate_spec",
    "_validate_security",
    "_validate_audit",
    "_require_policy",
    "_compute_spec_hash",
    "_verify_policy_binding",
)

# Fail-closed error markers that must survive the pure migration. Markers are
# matched against raw source text, so each appears contiguously in one literal.
MARKERS = (
    "metadata must be an object",
    "agent_id must be a safe-id",
    "spec.requires_human_confirmation must be a bool",
    "CRYPTO_PROXY requires crypto_scope approved-product",
    "redact_in_audit must be a list of strings",
    "not present in the deployment policy registry",
    "spec_hash does not match the canonical manifest bytes",
    "policy_ref.signature must be hex-encoded",
    "signer_cert_fingerprint does not match the resolved certificate",
    "policy_ref signature verification failed",
    "trusted_anchor_pubkey must be non-empty bytes",
)


class ManifestCheckerDecompositionGuardTests(unittest.TestCase):
    def test_validate_is_decomposed(self):
        tree = ast.parse(CHECKER.read_text(encoding="utf-8"))
        validate = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_validate"
        )
        self.assertLessEqual(
            validate.end_lineno - validate.lineno,
            80,
            "_validate() must stay a linear orchestration (was 150 lines)",
        )

    def test_phase_helpers_exist(self):
        for name in PHASES:
            self.assertTrue(
                hasattr(manifest_checker, name), f"manifest_checker.{name} missing"
            )

    def test_validate_orchestrates_all_phases(self):
        text = CHECKER.read_text(encoding="utf-8")
        tree = ast.parse(text)
        validate = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_validate"
        )
        src = ast.get_source_segment(text, validate)
        for name in PHASES:
            self.assertIn(f"{name}(", src, f"_validate() must call {name}")

    def test_error_message_markers_survive(self):
        text = CHECKER.read_text(encoding="utf-8")
        for marker in MARKERS:
            self.assertIn(marker, text, f"missing error marker: {marker}")


if __name__ == "__main__":
    unittest.main()
