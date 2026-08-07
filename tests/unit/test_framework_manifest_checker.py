"""US-16-AC-1: manifest-checker unit tests (T1..T6 contract + F5/F7/F8).

Covers every AC of US-16 AC-1 plus the abnormal inputs required by the
slice plan: unknown/missing/case-variant capabilities, non-bool confirmation
flags, out-of-closed-set crypto scopes, redaction outside the audit
projection, self-referential spec-hash negative cases, tampered/missing
policy_ref bindings, missing/unregistered policy versions, malformed JSON,
BOM, duplicate keys, non-bytes input, registration refusal, and the
stdlib-only invariant (L15).
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
import unittest
from pathlib import Path

from src.coevo.crypto.contract import ProviderScope
from src.coevo.framework import (
    AUDIT_PROJECTION_KEYS,
    AgentManifest,
    ManifestCheckInput,
    ManifestRegistry,
    ManifestValidationError,
    check,
)
from src.coevo.orchestrator.models import AgentCapability

ROOT = Path(__file__).resolve().parents[2]

FAKE_CERT_DER = b"FAKE-CERT-DER"
FAKE_CERT_FP = hashlib.sha256(FAKE_CERT_DER).hexdigest()
FAKE_SIGNATURE = "00" * 64


def canonical_bytes(obj: object) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def compute_spec_hash(manifest: dict[str, object]) -> str:
    """SHA-256 over canonical bytes excluding the three self-referential fields."""

    stripped = json.loads(json.dumps(manifest, ensure_ascii=True))
    stripped.get("metadata", {}).pop("spec_hash", None)
    stripped.get("policy_ref", {}).pop("spec_hash", None)
    stripped.get("policy_ref", {}).pop("signature", None)
    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()


def finalize(manifest: dict[str, object]) -> dict[str, object]:
    """Recompute and re-bind spec_hash after mutating a manifest."""

    spec_hash = compute_spec_hash(manifest)
    metadata = manifest.setdefault("metadata", {})
    assert isinstance(metadata, dict)
    metadata["spec_hash"] = spec_hash
    policy_ref = manifest.setdefault("policy_ref", {})
    assert isinstance(policy_ref, dict)
    policy_ref["spec_hash"] = spec_hash
    return manifest


def make_manifest(**overrides) -> dict[str, object]:
    """Build a valid manifest dict; ``spec_hash`` is computed automatically."""

    base: dict[str, object] = {
        "apiVersion": "coevo.framework/v1",
        "kind": "Agent",
        "metadata": {
            "agent_id": "task_decomposition.basic",
            "display_name": "task-decomposition agent",
            "semantic_version": "0.2.0",
        },
        "spec": {
            "capability": "task_decomposition",
            "requires_human_confirmation": True,
            "confirmation_role": "project_owner",
        },
        "policy_profile": "INTERACTIVE",
        "policy_version": "1.0",
        "policy_ref": {
            "signer_cert_fingerprint": FAKE_CERT_FP,
            "signature": FAKE_SIGNATURE,
        },
        "security": {"crypto_scope": "mvp-prototype"},
        "audit": {"redact_in_audit": ["policy_profile"]},
    }
    for key, value in overrides.items():
        if value is _DELETE:
            base.pop(key, None)
        else:
            base[key] = value

    return finalize(base)


class _Delete:
    pass


_DELETE = _Delete()


class _FakePolicyRegistry:
    def __init__(self, pairs: set[tuple[str, str]] | None = None) -> None:
        self.pairs = pairs or {("INTERACTIVE", "1.0")}

    def has_policy_version(self, profile: str, version: str) -> bool:
        return (profile, version) in self.pairs


class _FakeCertResolver:
    def __init__(self, der: bytes | None = FAKE_CERT_DER) -> None:
        self.der = der

    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None:
        if self.der is None:
            return None
        return self.der if hashlib.sha256(self.der).hexdigest() == fingerprint_hex else None


class _FakeSignatureVerifier:
    def __init__(self, ok: bool = True) -> None:
        self.ok = ok

    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool:
        return self.ok


def run_check(
    manifest: dict[str, object],
    *,
    policy_registry: _FakePolicyRegistry | None = None,
    cert_resolver: _FakeCertResolver | None = None,
    signature_verifier: _FakeSignatureVerifier | None = None,
    anchor: bytes = b"ANCHOR-PUBKEY",
):
    return check(
        ManifestCheckInput(
            manifest_bytes=canonical_bytes(manifest),
            trusted_anchor_pubkey=anchor,
            now="2026-08-07T09:00:00Z",
        ),
        policy_registry=policy_registry or _FakePolicyRegistry(),
        cert_resolver=cert_resolver or _FakeCertResolver(),
        signature_verifier=signature_verifier or _FakeSignatureVerifier(),
    )


class ManifestCheckerTests(unittest.TestCase):
    def test_minimal_valid_manifest_accepted_and_registers(self) -> None:
        """AC-1.1 (T1): minimal valid manifest passes and can be registered."""

        result = run_check(make_manifest())
        self.assertTrue(result.accepted, result.failure_reason)
        self.assertIsNone(result.failure_reason)
        manifest = result.validated_manifest
        self.assertIsNotNone(manifest)
        assert manifest is not None
        self.assertEqual(manifest.agent_id, "task_decomposition.basic")
        self.assertEqual(manifest.capability, AgentCapability.TASK_DECOMPOSITION)
        registry = ManifestRegistry()
        registry.register(result)
        self.assertEqual(registry.get("task_decomposition.basic"), manifest)

    def test_unknown_capability_rejected(self) -> None:
        """AC-1.2 (T2): capability outside the closed set is rejected."""

        manifest = make_manifest()
        spec = manifest["spec"]
        assert isinstance(spec, dict)
        spec["capability"] = "not_a_capability"
        result = run_check(finalize(manifest))
        self.assertFalse(result.accepted)
        self.assertIn("capability", result.failure_reason or "")

    def test_missing_capability_rejected(self) -> None:
        manifest = make_manifest()
        spec = manifest["spec"]
        assert isinstance(spec, dict)
        spec.pop("capability")
        result = run_check(finalize(manifest))
        self.assertFalse(result.accepted)

    def test_capability_case_variant_rejected(self) -> None:
        manifest = make_manifest()
        spec = manifest["spec"]
        assert isinstance(spec, dict)
        spec["capability"] = "Task_Decomposition"
        self.assertFalse(run_check(finalize(manifest)).accepted)

    def test_human_confirmation_defaults_true(self) -> None:
        """AC-1.3 (T3): absent flag defaults to True."""

        manifest = make_manifest()
        spec = manifest["spec"]
        assert isinstance(spec, dict)
        spec.pop("requires_human_confirmation")
        result = run_check(finalize(manifest))
        self.assertTrue(result.accepted, result.failure_reason)
        assert result.validated_manifest is not None
        self.assertTrue(result.validated_manifest.requires_human_confirmation)

    def test_human_confirmation_explicit_false_accepted(self) -> None:
        manifest = make_manifest()
        spec = manifest["spec"]
        assert isinstance(spec, dict)
        spec["requires_human_confirmation"] = False
        result = run_check(finalize(manifest))
        self.assertTrue(result.accepted, result.failure_reason)
        assert result.validated_manifest is not None
        self.assertFalse(result.validated_manifest.requires_human_confirmation)

    def test_human_confirmation_non_bool_rejected(self) -> None:
        manifest = make_manifest()
        spec = manifest["spec"]
        assert isinstance(spec, dict)
        spec["requires_human_confirmation"] = "yes"
        self.assertFalse(run_check(finalize(manifest)).accepted)

    def test_crypto_scope_enum(self) -> None:
        """AC-1.4 (T4): crypto_scope must be a ProviderScope member."""

        manifest = make_manifest()
        security = manifest["security"]
        assert isinstance(security, dict)
        security["crypto_scope"] = "unknown-scope"
        self.assertFalse(run_check(finalize(manifest)).accepted)

        security["crypto_scope"] = ProviderScope.APPROVED_PRODUCT.value
        self.assertTrue(run_check(finalize(manifest)).accepted)

    def test_redact_subset_of_audit_projection(self) -> None:
        """AC-1.5 (T5): redact_in_audit must be a projection subset."""

        manifest = make_manifest()
        audit = manifest["audit"]
        assert isinstance(audit, dict)
        audit["redact_in_audit"] = ["policy_profile", "signed_at"]
        self.assertTrue(run_check(finalize(manifest)).accepted)

        audit["redact_in_audit"] = ["model_reasoning", "user_input"]
        result = run_check(finalize(manifest))
        self.assertFalse(result.accepted)
        self.assertIn("audit projection", result.failure_reason or "")

        audit["redact_in_audit"] = "policy_profile"
        self.assertFalse(run_check(finalize(manifest)).accepted)

    def test_spec_hash_mismatch_rejected(self) -> None:
        """AC-1.6 (F5): a tampered spec_hash is rejected."""

        manifest = make_manifest()
        metadata = manifest["metadata"]
        assert isinstance(metadata, dict)
        metadata["spec_hash"] = "0" * 64
        self.assertFalse(run_check(manifest).accepted)

    def test_spec_hash_excludes_self_referential_fields(self) -> None:
        """F5 negative: naive full-bytes hash (including the field) is rejected."""

        manifest = make_manifest()
        stripped = json.loads(json.dumps(manifest, ensure_ascii=True))
        metadata = stripped.get("metadata", {})
        policy_ref = stripped.get("policy_ref", {})
        if isinstance(metadata, dict):
            metadata.pop("spec_hash", None)
        if isinstance(policy_ref, dict):
            policy_ref.pop("spec_hash", None)
            policy_ref.pop("signature", None)
        # Naive hash that DOES include the self-referential fields.
        naive = hashlib.sha256(canonical_bytes(manifest)).hexdigest()
        correct = hashlib.sha256(canonical_bytes(stripped)).hexdigest()
        self.assertNotEqual(naive, correct)
        metadata = manifest["metadata"]
        assert isinstance(metadata, dict)
        metadata["spec_hash"] = naive
        policy_ref = manifest["policy_ref"]
        assert isinstance(policy_ref, dict)
        policy_ref["spec_hash"] = naive
        result = run_check(manifest)
        self.assertFalse(result.accepted)
        self.assertIn("spec_hash", result.failure_reason or "")

    def test_policy_ref_signature_tampered_rejected(self) -> None:
        """AC-1.7 (F8): a bad signature is rejected."""

        result = run_check(make_manifest(), signature_verifier=_FakeSignatureVerifier(False))
        self.assertFalse(result.accepted)
        self.assertIn("signature", result.failure_reason or "")

    def test_policy_ref_cert_fingerprint_mismatch_rejected(self) -> None:
        manifest = make_manifest()
        policy_ref = manifest["policy_ref"]
        assert isinstance(policy_ref, dict)
        policy_ref["signer_cert_fingerprint"] = "0" * 64
        result = run_check(finalize(manifest))
        self.assertFalse(result.accepted)
        self.assertIn("certificate", result.failure_reason or "")

    def test_policy_ref_cert_not_found_rejected(self) -> None:
        result = run_check(make_manifest(), cert_resolver=_FakeCertResolver(None))
        self.assertFalse(result.accepted)
        self.assertIn("not found", result.failure_reason or "")

    def test_policy_ref_missing_fields_rejected(self) -> None:
        manifest = make_manifest()
        policy_ref = manifest["policy_ref"]
        assert isinstance(policy_ref, dict)
        policy_ref.pop("signature")
        self.assertFalse(run_check(manifest).accepted)

        manifest = make_manifest()
        policy_ref = manifest["policy_ref"]
        assert isinstance(policy_ref, dict)
        policy_ref.pop("spec_hash")
        self.assertFalse(run_check(manifest).accepted)

    def test_policy_version_required(self) -> None:
        """AC-1.8 (F7): policy_version is mandatory."""

        manifest = make_manifest()
        manifest["policy_version"] = ""
        self.assertFalse(run_check(finalize(manifest)).accepted)

        manifest = make_manifest()
        manifest.pop("policy_version")
        self.assertFalse(run_check(finalize(manifest)).accepted)

    def test_policy_version_not_in_registry_rejected(self) -> None:
        result = run_check(
            make_manifest(),
            policy_registry=_FakePolicyRegistry({("INTERACTIVE", "2.0")}),
        )
        self.assertFalse(result.accepted)
        self.assertIn("policy registry", result.failure_reason or "")

    def test_malformed_json_rejected(self) -> None:
        result = check(
            ManifestCheckInput(manifest_bytes=b"{not json"),
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeCertResolver(),
            signature_verifier=_FakeSignatureVerifier(),
        )
        self.assertFalse(result.accepted)
        self.assertIn("JSON", result.failure_reason or "")

    def test_bom_rejected(self) -> None:
        body = canonical_bytes(make_manifest())
        result = check(
            ManifestCheckInput(manifest_bytes=b"\xef\xbb\xbf" + body),
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeCertResolver(),
            signature_verifier=_FakeSignatureVerifier(),
        )
        self.assertFalse(result.accepted)
        self.assertIn("BOM", result.failure_reason or "")

    def test_duplicate_keys_rejected(self) -> None:
        payload = (
            b'{"metadata":{"agent_id":"a","agent_id":"b"},'
            b'"spec":{},"policy_profile":"p","policy_version":"1",'
            b'"policy_ref":{},"security":{},"audit":{}}'
        )
        result = check(
            ManifestCheckInput(manifest_bytes=payload),
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeCertResolver(),
            signature_verifier=_FakeSignatureVerifier(),
        )
        self.assertFalse(result.accepted)
        self.assertIn("duplicate key", result.failure_reason or "")

    def test_non_bytes_input_rejected(self) -> None:
        result = check(
            ManifestCheckInput(manifest_bytes="not bytes"),  # type: ignore[arg-type]
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeCertResolver(),
            signature_verifier=_FakeSignatureVerifier(),
        )
        self.assertFalse(result.accepted)

    def test_failure_does_not_register(self) -> None:
        """AC-1.9: failed validation never reaches the registry."""

        manifest = make_manifest()
        metadata = manifest["metadata"]
        assert isinstance(metadata, dict)
        metadata["spec_hash"] = "0" * 64
        result = run_check(manifest)
        self.assertFalse(result.accepted)
        registry = ManifestRegistry()
        with self.assertRaises(ManifestValidationError):
            registry.register(result)
        self.assertIsNone(registry.get("task_decomposition.basic"))

    def test_register_duplicate_rejected(self) -> None:
        registry = ManifestRegistry()
        registry.register(run_check(make_manifest()))
        with self.assertRaises(ManifestValidationError):
            registry.register(run_check(make_manifest()))

    def test_audit_projection_keys_used(self) -> None:
        result = run_check(make_manifest())
        record = result.to_audit_record()
        self.assertEqual(set(record), set(AUDIT_PROJECTION_KEYS))
        self.assertTrue(record["accepted"])

    def test_module_imports_stdlib_only(self) -> None:
        """L15: manifest_checker imports only stdlib or local coevo modules."""

        source = (ROOT / "src" / "coevo" / "framework" / "manifest_checker.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        allowed = set(sys.stdlib_module_names)
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top not in allowed and top not in {"src"}:
                        bad.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    if top not in allowed and top not in {"src"}:
                        bad.append(node.module)
        self.assertEqual([], bad, "third-party imports found in manifest_checker.py")


if __name__ == "__main__":
    unittest.main()
