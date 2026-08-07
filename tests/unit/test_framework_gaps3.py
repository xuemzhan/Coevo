"""FRAMEWORK-GAPS-3: semver trailing-newline strictness."""

from __future__ import annotations

import hashlib
import json
import unittest

from src.coevo.framework.manifest_checker import ManifestCheckInput, check


def canonical(obj: object) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def make_manifest(semantic_version: str):
    cert_fp = hashlib.sha256(b"FAKE-CERT-DER").hexdigest()
    manifest = {
        "apiVersion": "coevo.framework/v1",
        "kind": "Agent",
        "metadata": {
            "agent_id": "task_decomposition.basic",
            "display_name": "task-decomposition agent",
            "semantic_version": semantic_version,
        },
        "spec": {
            "capability": "task_decomposition",
            "requires_human_confirmation": True,
        },
        "policy_profile": "INTERACTIVE",
        "policy_version": "1.0",
        "policy_ref": {
            "signer_cert_fingerprint": cert_fp,
            "signature": "00" * 64,
        },
        "security": {"crypto_scope": "mvp-prototype"},
        "audit": {"redact_in_audit": ["policy_profile"]},
    }
    stripped = json.loads(json.dumps(manifest, ensure_ascii=True))
    stripped.get("metadata", {}).pop("spec_hash", None)
    stripped.get("policy_ref", {}).pop("spec_hash", None)
    stripped.get("policy_ref", {}).pop("signature", None)
    spec_hash = hashlib.sha256(canonical(stripped)).hexdigest()
    manifest["metadata"]["spec_hash"] = spec_hash
    manifest["policy_ref"]["spec_hash"] = spec_hash
    return manifest


class _FakePolicyRegistry:
    def has_policy_version(self, profile: str, version: str) -> bool:
        return (profile, version) == ("INTERACTIVE", "1.0")


class _FakeResolver:
    def __init__(self) -> None:
        self.der = b"FAKE-CERT-DER"

    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None:
        return (
            self.der
            if hashlib.sha256(self.der).hexdigest() == fingerprint_hex
            else None
        )


class _FakeVerifier:
    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool:
        return True


def run_check(manifest: dict):
    return check(
        ManifestCheckInput(
            manifest_bytes=canonical(manifest),
            trusted_anchor_pubkey=b"ANCHOR-PUBKEY",
        ),
        policy_registry=_FakePolicyRegistry(),
        cert_resolver=_FakeResolver(),
        signature_verifier=_FakeVerifier(),
    )


class SemverTrailingNewlineTests(unittest.TestCase):
    def test_trailing_newline_rejected(self) -> None:
        """GAPS-3: Python `$` matches before a final newline; `\\Z` must not."""

        result = run_check(make_manifest("1.0.0\n"))
        self.assertFalse(result.accepted)
        self.assertIn("semver", result.failure_reason or "")

    def test_clean_semver_accepted(self) -> None:
        result = run_check(make_manifest("1.0.0"))
        self.assertTrue(result.accepted, result.failure_reason)


if __name__ == "__main__":
    unittest.main()
