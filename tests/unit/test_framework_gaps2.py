"""FRAMEWORK-GAPS-2: closure tests for GAPS-1 review observations."""

from __future__ import annotations

import hashlib
import json
import unittest
from dataclasses import replace

from src.coevo.framework.a2a import A2aMessage, A2aValidationError, PolicyRef, validate_a2a
from src.coevo.framework.lifecycle import LifecycleState
from src.coevo.framework.manifest_checker import ManifestCheckInput, check
from src.coevo.framework.memory import (
    MemoryKind,
    MemoryRecord,
    MemoryValidationError,
    record_fingerprint,
    validate_record,
)
from src.coevo.framework.orchestrator import (
    ChainStep,
    OrchestrationMode,
    OrchestrationStatus,
    chain_plan,
    transition,
)
from src.coevo.framework.policy import (
    PolicyValidationError,
    TimeoutProfile,
    default_profiles,
    get_default_profile,
    validate_policy,
)
from src.coevo.framework.plan import Plan
from src.coevo.framework.validation import validate_plan


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


def run_manifest_check(manifest: dict):
    return check(
        ManifestCheckInput(
            manifest_bytes=canonical(manifest),
            trusted_anchor_pubkey=b"ANCHOR-PUBKEY",
        ),
        policy_registry=_FakePolicyRegistry(),
        cert_resolver=_FakeResolver(),
        signature_verifier=_FakeVerifier(),
    )


def valid_plan() -> Plan:
    return chain_plan(
        "task-0001",
        (ChainStep("s1", "task_flow_understanding"),),
        get_default_profile("INTERACTIVE"),
    )


class FrameworkGaps2Tests(unittest.TestCase):
    def test_policy_strict_int_fields(self) -> None:
        """GAPS-2-1: bool/str/float timeouts are rejected as PolicyValidationError."""

        for policy in default_profiles():
            validate_policy(policy)
        base = get_default_profile("INTERACTIVE")
        for bad_value in (True, "30", 30.0):  # type: ignore[assignment]
            with self.assertRaises(PolicyValidationError):
                validate_policy(
                    replace(
                        base,
                        timeout_profile=replace(
                            base.timeout_profile,
                            dispatch_timeout_sec=bad_value,  # type: ignore[arg-type]
                        ),
                    )
                )
        with self.assertRaises(PolicyValidationError):
            validate_policy(
                replace(
                    base,
                    retry_profile=replace(
                        base.retry_profile,
                        max_recover_attempts=True,  # type: ignore[arg-type]
                    ),
                )
            )

    def test_manifest_semver_strict(self) -> None:
        """GAPS-2-2: leading zeros are not valid semver."""

        for bad in ("1.01.0", "01.0.0", "1.0.01"):
            result = run_manifest_check(make_manifest(bad))
            self.assertFalse(result.accepted, bad)
            self.assertIn("semver", result.failure_reason or "")
        self.assertTrue(
            run_manifest_check(make_manifest("0.2.0")).accepted
        )
        self.assertTrue(
            run_manifest_check(make_manifest("1.0.0")).accepted
        )

    def test_a2a_created_at_calendar(self) -> None:
        """GAPS-2-2: impossible dates are rejected."""

        for bad in ("2026-99-99T99:99:99Z", "2026-02-30T00:00:00Z"):
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
                created_at=bad,
            )
            with self.assertRaises(A2aValidationError):
                validate_a2a(message)

    def test_memory_occurred_at_calendar(self) -> None:
        """GAPS-2-2: impossible dates are rejected."""

        record = MemoryRecord(
            record_id="0" * 64,
            kind=MemoryKind.EPISODIC,
            project_id="PRJ001",
            occurred_at="2026-02-30T00:00:00Z",
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

    def test_validated_at_strict_before_projection(self) -> None:
        """GAPS-2-3: validated_at is validated before entering projections."""

        plan = valid_plan()
        policy = get_default_profile("INTERACTIVE")
        for bad in ("", "2026-08-08 08:00:00Z", "2026-99-99T99:99:99Z"):
            result = validate_plan(
                plan,
                policy,
                scope_checker=_AllowAll(),
                rbac_checker=_AllowAll(),
                actor="owner",
                validated_at=bad,
            )
            self.assertFalse(result.accepted, bad)
            self.assertIn("validated_at", result.failure_reason or "")
        outcome = transition(
            OrchestrationMode.STATE_MACHINE,
            plan_hash=plan.plan_id,
            path=(LifecycleState.ESCALATED, LifecycleState.RETIRED),
            validated_at="",
        )
        self.assertEqual(outcome.status, OrchestrationStatus.REJECTED)
        self.assertIn("validated_at", outcome.failure_reason or "")
        outcome = transition(
            OrchestrationMode.STATE_MACHINE,
            plan_hash=plan.plan_id,
            path=(LifecycleState.ESCALATED, LifecycleState.RETIRED),
            validated_at="2026-08-08T08:00:00Z",
        )
        self.assertTrue(outcome.accepted)
        self.assertEqual(outcome.status, OrchestrationStatus.COMPLETED)

    def test_fractional_iso_seconds_accepted(self) -> None:
        """ISO-8601 fractional seconds (product now_utc_iso_z format) pass."""

        plan = valid_plan()
        result = validate_plan(
            plan,
            get_default_profile("INTERACTIVE"),
            scope_checker=_AllowAll(),
            rbac_checker=_AllowAll(),
            actor="owner",
            validated_at="2026-08-08T08:00:00.123456Z",
        )
        self.assertTrue(result.accepted, result.failure_reason)


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


class _AllowAll:
    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: Plan, actor: str) -> bool:
        return True


if __name__ == "__main__":
    unittest.main()
