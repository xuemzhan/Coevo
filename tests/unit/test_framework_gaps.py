"""FRAMEWORK-GAPS-1: closure tests for deferred review observations."""

from __future__ import annotations

import hashlib
import json
import unittest

from src.coevo.framework.a2a import A2aMessage, A2aValidationError, PolicyRef, validate_a2a
from src.coevo.framework.k8s_listing import (
    ListingInput,
    ListingValidationError,
    generate_listing,
    validate_listing_bytes,
)
from src.coevo.framework.manifest_checker import (
    ManifestCheckInput,
    check,
)
from src.coevo.framework.memory import (
    MemoryKind,
    MemoryRecord,
    MemoryValidationError,
    record_fingerprint,
    validate_record,
)
from src.coevo.framework.orchestrator import (
    ORCHESTRATION_PROJECTION_KEYS,
    ChainStep,
    OrchestrationError,
    OrchestrationMode,
    chain_plan,
    dispatch,
    plan_for,
)
from src.coevo.framework.policy import (
    PolicyValidationError,
    default_profiles,
    get_default_profile,
    validate_policy,
)
from src.coevo.framework.plan import Plan
from src.coevo.framework.tools import Tool, ToolSideEffect
from src.coevo.crypto.contract import ProviderScope


def canonical(obj: object) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def make_manifest(semantic_version: str = "0.2.0"):
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


class _AllowAll:
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: Plan, actor: str) -> bool:
        return True


class _RaisingChain:
    def chain_for(self, task_id: str):
        raise RuntimeError("chain down")


class FrameworkGapsTests(unittest.TestCase):
    def test_manifest_semver_enforced(self) -> None:
        """AC-1 L7 closure: semantic_version must be semver."""

        for bad in ("0.2", "v0.2.0"):
            result = check(
                ManifestCheckInput(
                    manifest_bytes=canonical(make_manifest(bad)),
                    trusted_anchor_pubkey=b"ANCHOR-PUBKEY",
                ),
                policy_registry=_FakePolicyRegistry(),
                cert_resolver=_FakeResolver(),
                signature_verifier=_FakeVerifier(),
            )
            self.assertFalse(result.accepted, bad)
            self.assertIn("semver", result.failure_reason or "")
        empty = check(
            ManifestCheckInput(
                manifest_bytes=canonical(make_manifest("")),
                trusted_anchor_pubkey=b"ANCHOR-PUBKEY",
            ),
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeResolver(),
            signature_verifier=_FakeVerifier(),
        )
        self.assertFalse(empty.accepted)
        result = check(
            ManifestCheckInput(
                manifest_bytes=canonical(make_manifest("0.2.0")),
                trusted_anchor_pubkey=b"ANCHOR-PUBKEY",
            ),
            policy_registry=_FakePolicyRegistry(),
            cert_resolver=_FakeResolver(),
            signature_verifier=_FakeVerifier(),
        )
        self.assertTrue(result.accepted, result.failure_reason)

    def test_a2a_created_at_iso(self) -> None:
        """AC-6 L7 closure: created_at must be ISO-8601 UTC with trailing Z."""

        message = A2aMessage(
            task_id="task-0001",
            trace_id="a" * 64,
            sender_cert_id="CERT-S",
            recipient_cert_id="CERT-R",
            sequence_no=1,
            business_correlation_key="BCK",
            purpose="TASK_DECOMPOSITION",
            policy_ref=PolicyRef("a" * 64, "b" * 64, "00" * 64),
            payload_ref="pkg-0001",
            created_at="2026-08-08 08:00:00",  # missing T and Z
        )
        with self.assertRaises(A2aValidationError):
            validate_a2a(message)

    def test_memory_occurred_at_iso(self) -> None:
        """AC-4 L7 closure: occurred_at must be ISO-8601 UTC with trailing Z."""

        record = MemoryRecord(
            record_id="0" * 64,
            kind=MemoryKind.EPISODIC,
            project_id="PRJ001",
            occurred_at="2026-08-08T08:00:00",  # no trailing Z
            fields=(),
            sensitive_fields=(),
        )
        record = MemoryRecord(
            record_id=record_fingerprint(record),
            kind=record.kind,
            project_id=record.project_id,
            occurred_at=record.occurred_at,
            fields=record.fields,
            sensitive_fields=record.sensitive_fields,
        )
        with self.assertRaises(MemoryValidationError):
            validate_record(record)

    def test_policy_timeout_upper_bounds(self) -> None:
        """AC-2 Info4 closure: default profiles pass; oversized rejected."""

        for policy in default_profiles():
            validate_policy(policy)
        base = get_default_profile("INTERACTIVE")
        from dataclasses import replace

        from src.coevo.framework.policy import TimeoutProfile

        for field, bad_value in (
            ("dispatch_timeout_sec", 601),
            ("plan_total_timeout_sec", 7201),
            ("consent_timeout_sec", 7201),
        ):
            timeout = replace(base.timeout_profile, **{field: bad_value})
            with self.assertRaises(PolicyValidationError):
                validate_policy(replace(base, timeout_profile=timeout))

    def test_orchestrator_chain_exception_closed(self) -> None:
        """AC-8 Low closure: chain provider exceptions become OrchestrationError."""

        with self.assertRaises(OrchestrationError):
            plan_for(
                OrchestrationMode.STATE_MACHINE,
                "task-0001",
                get_default_profile("INTERACTIVE"),
                static_chain_provider=_RaisingChain(),
                llm_provider=None,  # type: ignore[arg-type]
                scope_checker=_AllowAll(),
                rbac_checker=_AllowAll(),
                actor="owner",
            )

    def test_orchestration_audit_has_validated_at(self) -> None:
        """AC-8 Low closure: outcome audit projection includes validated_at."""

        self.assertIn("validated_at", ORCHESTRATION_PROJECTION_KEYS)
        plan = chain_plan(
            "task-0001",
            (ChainStep("s1", "task_flow_understanding"),),
            get_default_profile("INTERACTIVE"),
        )
        outcome = dispatch(
            OrchestrationMode.STATE_MACHINE,
            "task-0001",
            get_default_profile("INTERACTIVE"),
            plan=plan,
            actor="owner",
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            plan_executor=_OkExecutor(),
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertTrue(outcome.accepted)
        record = outcome.to_audit_record()
        self.assertEqual(set(record), set(ORCHESTRATION_PROJECTION_KEYS))
        self.assertEqual(record["validated_at"], "2026-08-08T08:00:00Z")

    def test_k8s_listing_item_unknown_keys_rejected(self) -> None:
        """AC-9 Low closure: spec item unknown fields are rejected."""

        listing = generate_listing(
            ListingInput(
                capabilities=(),
                tools=(_make_tool(),),
                policies=(),
                plans=(),
                generated_at="2026-08-08T08:00:00Z",
            )
        )
        parsed = json.loads(listing.decode("utf-8"))
        parsed["spec"]["tools"][0]["bogus"] = 1
        mutated = canonical(parsed)
        with self.assertRaises(ListingValidationError):
            validate_listing_bytes(mutated)
        validate_listing_bytes(listing)  # original still valid


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


class _OkExecutor:
    def execute(self, plan: Plan, actor: str):
        from src.coevo.framework.orchestrator import ExecutionResult

        return ExecutionResult(ok=True)


def _make_tool() -> Tool:
    return Tool(
        tool_id="coevo.tools.cycle_check",
        tool_version="1.0.0",
        display_name="cycle check",
        description="detect cycles",
        side_effects=ToolSideEffect.PURE,
        requires_consent=False,
        timeout_sec=5,
        size_in_bytes_max=4096,
        crypto_scope=ProviderScope.MVP_PROTOTYPE,
        audit_required=True,
        input_schema={"type": "object", "properties": {"nodes": {"type": "array", "items": {"type": "string"}}}},
        output_schema={"type": "object", "properties": {"cycle": {"type": "boolean"}}},
    )


if __name__ == "__main__":
    unittest.main()
