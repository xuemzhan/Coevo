"""US-16-AC-6: A2A wire 0.1 and policy_ref three-part binding tests (M5)."""

from __future__ import annotations

import ast
import hashlib
import sys
import unittest
from pathlib import Path

from src.coevo.framework.a2a import (
    A2A_PROJECTION_KEYS,
    A2aMessage,
    A2aValidationError,
    ENVELOPE_MAX_BYTES,
    PolicyRef,
    from_agent_fields,
    to_agent_fields,
    validate_a2a,
    validate_payload_size,
    verify_policy_ref,
)
from src.coevo.framework.manifest_checker import manifest_spec_hash

ROOT = Path(__file__).resolve().parents[2]

FAKE_CERT_DER = b"FAKE-A2A-CERT-DER"
FAKE_CERT_FP = hashlib.sha256(FAKE_CERT_DER).hexdigest()
FAKE_SIGNATURE = "00" * 64


def make_manifest_bytes() -> bytes:
    """A minimal canonical manifest whose spec_hash is computable."""

    import json

    manifest = {
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
    stripped = json.loads(json.dumps(manifest, ensure_ascii=True))
    stripped.get("metadata", {}).pop("spec_hash", None)
    stripped.get("policy_ref", {}).pop("spec_hash", None)
    stripped.get("policy_ref", {}).pop("signature", None)
    spec_hash = hashlib.sha256(
        json.dumps(stripped, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()
    metadata = manifest["metadata"]
    metadata["spec_hash"] = spec_hash
    policy_ref = manifest["policy_ref"]
    policy_ref["spec_hash"] = spec_hash
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def make_message(**overrides) -> A2aMessage:
    manifest_bytes = make_manifest_bytes()
    spec_hash = manifest_spec_hash(manifest_bytes)
    base = A2aMessage(
        task_id="task-0001",
        trace_id="a" * 64,
        sender_cert_id="CERT-SENDER-001",
        recipient_cert_id="CERT-RECIPIENT-021",
        sequence_no=12,
        business_correlation_key="BCK-001",
        purpose="TASK_DECOMPOSITION",
        policy_ref=PolicyRef(spec_hash, FAKE_CERT_FP, FAKE_SIGNATURE),
        payload_ref="pkg-0001",
        created_at="2026-08-08T08:00:00Z",
    )
    return type(base)(
        task_id=overrides.get("task_id", base.task_id),
        trace_id=overrides.get("trace_id", base.trace_id),
        sender_cert_id=overrides.get("sender_cert_id", base.sender_cert_id),
        recipient_cert_id=overrides.get("recipient_cert_id", base.recipient_cert_id),
        sequence_no=overrides.get("sequence_no", base.sequence_no),
        business_correlation_key=overrides.get(
            "business_correlation_key", base.business_correlation_key
        ),
        purpose=overrides.get("purpose", base.purpose),
        policy_ref=overrides.get("policy_ref", base.policy_ref),
        payload_ref=overrides.get("payload_ref", base.payload_ref),
        created_at=overrides.get("created_at", base.created_at),
    )


class _Resolver:
    def __init__(self, der: bytes | None = FAKE_CERT_DER) -> None:
        self.der = der

    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None:
        if self.der is None:
            return None
        return self.der if hashlib.sha256(self.der).hexdigest() == fingerprint_hex else None


class _BoomResolver(_Resolver):
    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None:
        raise RuntimeError("chain down")


class _AnyFingerprintResolver:
    def resolve_by_fingerprint(self, fingerprint_hex: str) -> bytes | None:
        return FAKE_CERT_DER


class _Verifier:
    def __init__(self, ok: bool = True) -> None:
        self.ok = ok

    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool:
        return self.ok


class _BoomVerifier(_Verifier):
    def verify(self, signer_cert_der: bytes, data: bytes, signature: bytes) -> bool:
        raise RuntimeError("verifier down")


def run_verify(message: A2aMessage, **kwargs):
    return verify_policy_ref(
        message,
        manifest_bytes=kwargs.pop("manifest_bytes", make_manifest_bytes()),
        cert_resolver=kwargs.pop("cert_resolver", _Resolver()),
        signature_verifier=kwargs.pop("signature_verifier", _Verifier()),
    )


class A2aTests(unittest.TestCase):
    def test_a2a_field_validation(self) -> None:
        """AC-6.1: every field is validated fail-closed."""

        validate_a2a(make_message())
        for field in (
            "task_id",
            "sender_cert_id",
            "recipient_cert_id",
            "payload_ref",
        ):
            with self.assertRaises(A2aValidationError):
                validate_a2a(make_message(**{field: "../escape"}))
        with self.assertRaises(A2aValidationError):
            validate_a2a(make_message(trace_id="short"))
        with self.assertRaises(A2aValidationError):
            validate_a2a(make_message(sequence_no=-1))
        with self.assertRaises(A2aValidationError):
            validate_a2a(make_message(sequence_no=True))
        with self.assertRaises(A2aValidationError):
            validate_a2a(make_message(business_correlation_key=""))
        with self.assertRaises(A2aValidationError):
            validate_a2a(make_message(purpose="not_a_capability"))
        with self.assertRaises(A2aValidationError):
            validate_a2a(make_message(created_at=""))

    def test_policy_ref_five_step_verification(self) -> None:
        """AC-6.2: the §7.3.3 five-step sequence is enforced."""

        result = run_verify(make_message())
        self.assertTrue(result.accepted, result.failure_reason)
        self.assertIsNone(result.failure_reason)

    def test_policy_ref_cert_missing_rejected(self) -> None:
        result = run_verify(make_message(), cert_resolver=_Resolver(None))
        self.assertFalse(result.accepted)
        self.assertIn("not found", result.failure_reason or "")

    def test_policy_ref_fingerprint_mismatch_rejected(self) -> None:
        message = make_message()
        ref = PolicyRef(
            spec_hash=message.policy_ref.spec_hash,
            signer_cert_fingerprint="0" * 64,
            signature=message.policy_ref.signature,
        )
        result = run_verify(
            make_message(policy_ref=ref),
            cert_resolver=_AnyFingerprintResolver(),
        )
        self.assertFalse(result.accepted)
        self.assertIn("fingerprint", result.failure_reason or "")

    def test_policy_ref_spec_hash_mismatch_rejected(self) -> None:
        message = make_message()
        ref = PolicyRef(
            spec_hash="1" * 64,
            signer_cert_fingerprint=message.policy_ref.signer_cert_fingerprint,
            signature=message.policy_ref.signature,
        )
        result = run_verify(make_message(policy_ref=ref))
        self.assertFalse(result.accepted)
        self.assertIn("spec_hash", result.failure_reason or "")

    def test_policy_ref_signature_failed_rejected(self) -> None:
        result = run_verify(make_message(), signature_verifier=_Verifier(False))
        self.assertFalse(result.accepted)
        self.assertIn("signature", result.failure_reason or "")

    def test_policy_ref_oversized_signature_rejected(self) -> None:
        """AC-6.1: policy_ref.signature is length-bounded fail-closed."""

        oversized = PolicyRef(
            spec_hash="0" * 64,
            signer_cert_fingerprint="0" * 64,
            signature="ab" * 513,  # 1026 hex chars > 1024 cap
        )
        with self.assertRaises(A2aValidationError):
            validate_a2a(make_message(policy_ref=oversized))

    def test_policy_ref_deep_manifest_fail_closed(self) -> None:
        """AC-6.2: pathological manifest depth must reject, not raise."""

        deep = b'{"k": 1}'
        for _ in range(4000):
            deep = b'{"k":' + deep + b'}'
        result = run_verify(make_message(), manifest_bytes=deep)
        self.assertFalse(result.accepted)
        self.assertIn("manifest", result.failure_reason or "")

    def test_policy_ref_injected_exceptions_fail_closed(self) -> None:
        result = run_verify(make_message(), cert_resolver=_BoomResolver())
        self.assertFalse(result.accepted)
        self.assertIn("certificate resolution failed", result.failure_reason or "")
        result = run_verify(make_message(), signature_verifier=_BoomVerifier())
        self.assertFalse(result.accepted)
        self.assertIn("signature verification failed", result.failure_reason or "")

    def test_agent_field_mapping_round_trip(self) -> None:
        """AC-6.3: A2A ↔ .agent field mapping round-trips."""

        message = make_message()
        fields = to_agent_fields(message)
        restored = from_agent_fields(fields)
        self.assertEqual(restored, message)
        self.assertEqual(to_agent_fields(restored), fields)
        fields.pop("created_at")
        with self.assertRaises(A2aValidationError):
            from_agent_fields(fields)
        fields = to_agent_fields(message)
        fields["bogus"] = 1
        with self.assertRaises(A2aValidationError):
            from_agent_fields(fields)

    def test_payload_split_boundary(self) -> None:
        """AC-6.4: >64 KiB business payloads must use payload_ref split."""

        validate_payload_size(ENVELOPE_MAX_BYTES, payload_ref="")
        with self.assertRaises(A2aValidationError):
            validate_payload_size(True, payload_ref="")
        with self.assertRaises(A2aValidationError):
            validate_payload_size(ENVELOPE_MAX_BYTES + 1, payload_ref="")
        validate_payload_size(ENVELOPE_MAX_BYTES + 1, payload_ref="pkg-0001")
        with self.assertRaises(A2aValidationError):
            validate_payload_size(ENVELOPE_MAX_BYTES + 1, payload_ref="../escape")

    def test_audit_projection_keys(self) -> None:
        record = run_verify(make_message()).to_audit_record()
        self.assertEqual(set(record), set(A2A_PROJECTION_KEYS))
        message_record = make_message().to_audit_record()
        self.assertIn("task_id", message_record)

    def test_module_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "a2a.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
        allowed = set(sys.stdlib_module_names) | {"src"}
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] not in allowed:
                        bad.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    continue
                if node.module and node.module.split(".")[0] not in allowed:
                    bad.append(node.module)
        self.assertEqual([], bad, "third-party imports found in a2a.py")


if __name__ == "__main__":
    unittest.main()
