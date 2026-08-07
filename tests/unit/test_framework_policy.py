"""US-16-AC-2: Policy abstraction tests (AC-2.1/2.2/2.3/2.8)."""

from __future__ import annotations

import ast
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from src.coevo.framework.policy import (
    EMERGENCY_POST_HOC_CONFIRM_WINDOW_SEC,
    MAX_RECOVER_ATTEMPTS_LIMIT,
    ConsentProfile,
    Policy,
    PolicyValidationError,
    RetryProfile,
    TimeoutProfile,
    default_profiles,
    get_default_profile,
    validate_policy,
)

ROOT = Path(__file__).resolve().parents[2]


def base_policy(**overrides) -> Policy:
    policy = get_default_profile("INTERACTIVE")
    return replace(policy, **overrides)


class PolicyTests(unittest.TestCase):
    def test_four_default_profiles_all_valid(self) -> None:
        profiles = default_profiles()
        self.assertEqual(len(profiles), 4)
        for policy in profiles:
            validate_policy(policy)  # must not raise

    def test_policy_version_required(self) -> None:
        with self.assertRaises(PolicyValidationError):
            validate_policy(base_policy(policy_version=""))

    def test_profile_closed_set(self) -> None:
        with self.assertRaises(PolicyValidationError):
            validate_policy(base_policy(profile="SOLO"))

    def test_l16_every_default_profile_within_retry_limit(self) -> None:
        for policy in default_profiles():
            self.assertLessEqual(
                policy.retry_profile.max_recover_attempts,
                MAX_RECOVER_ATTEMPTS_LIMIT,
                policy.profile,
            )

    def test_retries_over_limit_rejected(self) -> None:
        policy = replace(
            base_policy(),
            retry_profile=RetryProfile(5, 3, (1, 5, 15)),
        )
        with self.assertRaises(PolicyValidationError):
            validate_policy(policy)

    def test_emergency_default_is_fail_fast(self) -> None:
        emergency = get_default_profile("EMERGENCY")
        self.assertEqual(emergency.retry_profile.max_recover_attempts, 1)
        self.assertEqual(emergency.timeout_profile.plan_total_timeout_sec, 60)
        self.assertFalse(emergency.consent.requires_human_confirmation)
        self.assertEqual(
            emergency.consent.post_hoc_confirm_window_sec,
            EMERGENCY_POST_HOC_CONFIRM_WINDOW_SEC,
        )
        validate_policy(emergency)

    def test_emergency_non_compliant_rejected(self) -> None:
        emergency = get_default_profile("EMERGENCY")
        with self.assertRaises(PolicyValidationError):
            validate_policy(
                replace(
                    emergency,
                    retry_profile=RetryProfile(2, 1, (1,)),
                )
            )
        with self.assertRaises(PolicyValidationError):
            validate_policy(
                replace(
                    emergency,
                    timeout_profile=TimeoutProfile(15, 300, 0),
                )
            )
        with self.assertRaises(PolicyValidationError):
            validate_policy(
                replace(
                    emergency,
                    consent=ConsentProfile(True, "project_owner", 1800),
                )
            )
        with self.assertRaises(PolicyValidationError):
            validate_policy(
                replace(
                    emergency,
                    consent=ConsentProfile(False, "project_owner", 60),
                )
            )

    def test_backoff_must_be_positive(self) -> None:
        with self.assertRaises(PolicyValidationError):
            validate_policy(
                replace(
                    base_policy(),
                    retry_profile=RetryProfile(2, 3, (0,)),
                )
            )
        with self.assertRaises(PolicyValidationError):
            validate_policy(
                replace(
                    base_policy(),
                    retry_profile=RetryProfile(2, 3, ()),
                )
            )

    def test_module_imports_stdlib_only(self) -> None:
        """L15: framework modules import only stdlib or local src modules."""

        allowed = set(sys.stdlib_module_names) | {"src"}
        bad: list[str] = []
        for path in sorted((ROOT / "src" / "coevo" / "framework").glob("*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".")[0] not in allowed:
                            bad.append(f"{path.name}: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.level > 0:
                        continue
                    if node.module and node.module.split(".")[0] not in allowed:
                        bad.append(f"{path.name}: {node.module}")
        self.assertEqual([], bad, "third-party imports found in framework modules")


if __name__ == "__main__":
    unittest.main()
