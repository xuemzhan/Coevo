"""US-16-AC-2: Policy abstraction (CTAF §6.5 / M2).

A Policy owns every numeric execution boundary (timeouts, retry counts,
consent windows); a Plan only references a ``(policy_profile,
policy_version)`` pair (L18 white-list rule).  Four default profiles are
provided (INTERACTIVE / BATCH / AUDIT_ONLY / EMERGENCY); every profile
satisfies L16 (``max_recover_attempts <= 3``) and EMERGENCY is fail-fast
with a post-hoc confirmation window (F1/F9, v0.4.1).

L15: standard library only, no third-party runtime dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

PROFILES = frozenset({"INTERACTIVE", "BATCH", "AUDIT_ONLY", "EMERGENCY"})
MAX_RECOVER_ATTEMPTS_LIMIT = 3  # L16 / §8.3 "recover 计数 ≥ 3 → ESCALATED"
EMERGENCY_PLAN_TOTAL_TIMEOUT_MAX_SEC = 60
EMERGENCY_POST_HOC_CONFIRM_WINDOW_SEC = 30 * 60
TIMEOUT_UPPER_BOUNDS = {
    "dispatch_timeout_sec": 600,
    "plan_total_timeout_sec": 7200,
    "consent_timeout_sec": 7200,
}


class PolicyValidationError(Exception):
    """Raised when a Policy violates the framework invariants."""


@dataclass(frozen=True)
class TimeoutProfile:
    dispatch_timeout_sec: int
    plan_total_timeout_sec: int
    consent_timeout_sec: int


@dataclass(frozen=True)
class RetryProfile:
    max_recover_attempts: int
    max_router_retries: int
    recover_backoff_sec: tuple[int, ...]


@dataclass(frozen=True)
class ConsentProfile:
    requires_human_confirmation: bool
    default_role: str
    post_hoc_confirm_window_sec: int = 0


@dataclass(frozen=True)
class Policy:
    """CTAF §6.5 Policy instance. ``policy_version`` is mandatory (F7)."""

    policy_id: str
    policy_version: str
    profile: str
    timeout_profile: TimeoutProfile
    retry_profile: RetryProfile
    consent: ConsentProfile
    audit_redaction: tuple[str, ...]
    ground_truth_required: tuple[str, ...]


def default_profiles() -> tuple[Policy, ...]:
    """The four v0.4.1 default profiles (CTAF §6.5, B6/F1/F9)."""

    return (
        Policy(
            policy_id="policy.interactive.v1",
            policy_version="1.0",
            profile="INTERACTIVE",
            timeout_profile=TimeoutProfile(30, 600, 600),
            retry_profile=RetryProfile(3, 3, (1, 5, 15)),
            consent=ConsentProfile(True, "project_owner"),
            audit_redaction=("model_reasoning", "user_input"),
            ground_truth_required=(
                "plan_hashability",
                "dag_acyclic",
                "tool_scope_within_l4",
            ),
        ),
        Policy(
            policy_id="policy.batch.v1",
            policy_version="1.0",
            profile="BATCH",
            timeout_profile=TimeoutProfile(120, 3600, 600),
            retry_profile=RetryProfile(2, 3, (1, 5)),
            consent=ConsentProfile(False, "project_owner"),
            audit_redaction=("model_reasoning",),
            ground_truth_required=("plan_hashability", "dag_acyclic"),
        ),
        Policy(
            policy_id="policy.audit_only.v1",
            policy_version="1.0",
            profile="AUDIT_ONLY",
            timeout_profile=TimeoutProfile(60, 900, 600),
            retry_profile=RetryProfile(3, 3, (1, 5, 15)),
            consent=ConsentProfile(True, "project_owner"),
            audit_redaction=("model_reasoning", "user_input"),
            ground_truth_required=(
                "plan_hashability",
                "dag_acyclic",
                "tool_scope_within_l4",
            ),
        ),
        Policy(
            policy_id="policy.emergency.v1",
            policy_version="1.0",
            profile="EMERGENCY",
            timeout_profile=TimeoutProfile(15, 60, 0),
            retry_profile=RetryProfile(1, 1, (1,)),
            consent=ConsentProfile(
                False,
                "project_owner",
                post_hoc_confirm_window_sec=EMERGENCY_POST_HOC_CONFIRM_WINDOW_SEC,
            ),
            audit_redaction=("model_reasoning",),
            ground_truth_required=(
                "plan_hashability",
                "dag_acyclic",
                "tool_scope_within_l4",
            ),
        ),
    )


def validate_policy(policy: Policy) -> None:
    """Validate a Policy instance (pure, fail-closed)."""

    if not isinstance(policy, Policy):
        raise PolicyValidationError("policy must be a Policy instance")
    if not policy.policy_id or not policy.policy_version:
        raise PolicyValidationError("policy_id and policy_version are required (F7)")
    if policy.profile not in PROFILES:
        raise PolicyValidationError(
            f"profile outside the closed set {sorted(PROFILES)}: {policy.profile!r}"
        )
    timeout = policy.timeout_profile
    _require_strict_int(timeout.dispatch_timeout_sec, "dispatch_timeout_sec")
    _require_strict_int(timeout.plan_total_timeout_sec, "plan_total_timeout_sec")
    _require_strict_int(timeout.consent_timeout_sec, "consent_timeout_sec")
    if timeout.dispatch_timeout_sec <= 0:
        raise PolicyValidationError("dispatch_timeout_sec must be positive")
    if timeout.dispatch_timeout_sec > TIMEOUT_UPPER_BOUNDS["dispatch_timeout_sec"]:
        raise PolicyValidationError(
            f"dispatch_timeout_sec exceeds "
            f"{TIMEOUT_UPPER_BOUNDS['dispatch_timeout_sec']}s upper bound (Info4)"
        )
    if timeout.plan_total_timeout_sec <= 0:
        raise PolicyValidationError("plan_total_timeout_sec must be positive")
    if timeout.plan_total_timeout_sec > TIMEOUT_UPPER_BOUNDS["plan_total_timeout_sec"]:
        raise PolicyValidationError(
            f"plan_total_timeout_sec exceeds "
            f"{TIMEOUT_UPPER_BOUNDS['plan_total_timeout_sec']}s upper bound (Info4)"
        )
    if timeout.consent_timeout_sec < 0:
        raise PolicyValidationError("consent_timeout_sec must be non-negative")
    if timeout.consent_timeout_sec > TIMEOUT_UPPER_BOUNDS["consent_timeout_sec"]:
        raise PolicyValidationError(
            f"consent_timeout_sec exceeds "
            f"{TIMEOUT_UPPER_BOUNDS['consent_timeout_sec']}s upper bound (Info4)"
        )
    retry = policy.retry_profile
    _require_strict_int(retry.max_recover_attempts, "max_recover_attempts")
    _require_strict_int(retry.max_router_retries, "max_router_retries")
    if not 1 <= retry.max_recover_attempts <= MAX_RECOVER_ATTEMPTS_LIMIT:
        raise PolicyValidationError(
            f"max_recover_attempts must be within "
            f"[1, {MAX_RECOVER_ATTEMPTS_LIMIT}] (L16); got {retry.max_recover_attempts}"
        )
    if retry.max_router_retries < 0:
        raise PolicyValidationError("max_router_retries must be non-negative")
    if not retry.recover_backoff_sec or any(
        value <= 0 for value in retry.recover_backoff_sec
    ):
        raise PolicyValidationError("recover_backoff_sec must be non-empty positive ints")
    for value in retry.recover_backoff_sec:
        _require_strict_int(value, "recover_backoff_sec entry")
    if not isinstance(policy.consent.requires_human_confirmation, bool):
        raise PolicyValidationError("requires_human_confirmation must be bool")
    if not policy.consent.default_role:
        raise PolicyValidationError("consent.default_role must be non-empty")
    _require_strict_int(
        policy.consent.post_hoc_confirm_window_sec,
        "post_hoc_confirm_window_sec",
    )
    if policy.consent.post_hoc_confirm_window_sec < 0:
        raise PolicyValidationError("post_hoc_confirm_window_sec must be non-negative")
    if not isinstance(policy.audit_redaction, tuple) or not all(
        isinstance(item, str) for item in policy.audit_redaction
    ):
        raise PolicyValidationError("audit_redaction must be a tuple of strings")
    if policy.profile == "EMERGENCY":
        # v0.4.1 F1/F9: fail-fast, post-hoc human confirmation, no inline wait.
        if retry.max_recover_attempts != 1:
            raise PolicyValidationError(
                "EMERGENCY profile must use exactly 1 recover attempt (F1)"
            )
        if timeout.plan_total_timeout_sec > EMERGENCY_PLAN_TOTAL_TIMEOUT_MAX_SEC:
            raise PolicyValidationError(
                "EMERGENCY plan_total_timeout_sec must be <= "
                f"{EMERGENCY_PLAN_TOTAL_TIMEOUT_MAX_SEC}s (F1)"
            )
        if policy.consent.requires_human_confirmation:
            raise PolicyValidationError(
                "EMERGENCY must not wait inline for human confirmation (F1)"
            )
        if (
            policy.consent.post_hoc_confirm_window_sec
            != EMERGENCY_POST_HOC_CONFIRM_WINDOW_SEC
        ):
            raise PolicyValidationError(
                "EMERGENCY requires a 30-minute post-hoc confirmation window (F9)"
            )


def _require_strict_int(value: object, label: str) -> None:
    """Reject bool and non-int values with a controlled error (GAPS-2)."""

    if type(value) is not int:
        raise PolicyValidationError(f"{label} must be an integer (bool rejected)")


def get_default_profile(profile: str) -> Policy:
    """Return the default profile for a closed-set name (fail-closed)."""

    for candidate in default_profiles():
        if candidate.profile == profile:
            return candidate
    raise PolicyValidationError(
        f"profile outside the closed set {sorted(PROFILES)}: {profile!r}"
    )
