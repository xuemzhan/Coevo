"""FRAMEWORK-OPTIMIZE-4: default Policy profiles lazy-cache tests."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.coevo.framework.policy import (
    Policy,
    PolicyValidationError,
    default_profiles,
    get_default_profile,
)


class DefaultProfileCacheTests(unittest.TestCase):
    def test_default_profiles_are_cached_and_immutable(self) -> None:
        first = default_profiles()
        second = default_profiles()
        self.assertIs(first, second, "default profiles must be cached")
        self.assertEqual(
            ("INTERACTIVE", "BATCH", "AUDIT_ONLY", "EMERGENCY"),
            tuple(p.profile for p in first),
        )
        for policy in first:
            with self.assertRaises(FrozenInstanceError):
                policy.profile = "TAMPERED"

    def test_get_default_profile_matches_and_is_cached(self) -> None:
        profiles = default_profiles()
        for profile in ("INTERACTIVE", "BATCH", "AUDIT_ONLY", "EMERGENCY"):
            resolved = get_default_profile(profile)
            self.assertIs(
                next(p for p in profiles if p.profile == profile),
                resolved,
                "get_default_profile must use the cache",
            )
        self.assertIs(
            get_default_profile("INTERACTIVE"),
            get_default_profile("INTERACTIVE"),
        )

    def test_get_default_profile_fails_closed_on_unknown_name(self) -> None:
        with self.assertRaises(PolicyValidationError):
            get_default_profile("NOT_A_PROFILE")

    def test_default_profile_numeric_bounds_unchanged(self) -> None:
        interactive = get_default_profile("INTERACTIVE")
        emergency = get_default_profile("EMERGENCY")
        self.assertIsInstance(interactive, Policy)
        self.assertLessEqual(interactive.retry_profile.max_recover_attempts, 3)
        self.assertLessEqual(emergency.timeout_profile.plan_total_timeout_sec, 60)
        self.assertEqual(30 * 60, emergency.consent.post_hoc_confirm_window_sec)


if __name__ == "__main__":
    unittest.main()
