"""US-16-AC-2: eight-state lifecycle and L19 path tests (AC-2.7)."""

from __future__ import annotations

import unittest

from src.coevo.framework.lifecycle import (
    LifecycleState,
    can_transition,
    validate_transition_path,
)

REGISTERED = LifecycleState.REGISTERED
INSTANTIATED = LifecycleState.INSTANTIATED
ACTIVE = LifecycleState.ACTIVE
HELD = LifecycleState.HELD
RECOVERED = LifecycleState.RECOVERED
ESCALATED = LifecycleState.ESCALATED
RETIRED = LifecycleState.RETIRED
REVOKED = LifecycleState.REVOKED


class LifecycleL19Tests(unittest.TestCase):
    def test_escalated_direct_to_active_rejected(self) -> None:
        accepted, reason = validate_transition_path((ESCALATED, ACTIVE))
        self.assertFalse(accepted)
        self.assertIn("L19", reason or "")

    def test_escalated_held_active_accepted(self) -> None:
        accepted, reason = validate_transition_path((ESCALATED, HELD, ACTIVE))
        self.assertTrue(accepted, reason)

    def test_escalated_retired_direct_exit_accepted(self) -> None:
        accepted, reason = validate_transition_path((ESCALATED, RETIRED))
        self.assertTrue(accepted, reason)

    def test_escalated_held_redispatch_accepted(self) -> None:
        accepted, reason = validate_transition_path(
            (ESCALATED, HELD, ACTIVE, HELD, ACTIVE)
        )
        self.assertTrue(accepted, reason)

    def test_normal_dispatch_path_accepted(self) -> None:
        accepted, reason = validate_transition_path(
            (REGISTERED, INSTANTIATED, ACTIVE, HELD, ACTIVE)
        )
        self.assertTrue(accepted, reason)

    def test_recover_then_escalate_path_accepted(self) -> None:
        accepted, reason = validate_transition_path(
            (ACTIVE, RECOVERED, ESCALATED, HELD, ACTIVE)
        )
        self.assertTrue(accepted, reason)

    def test_illegal_transition_rejected(self) -> None:
        accepted, reason = validate_transition_path((ACTIVE, ESCALATED))
        self.assertFalse(accepted)
        self.assertIn("illegal transition", reason or "")

    def test_empty_path_rejected(self) -> None:
        accepted, _reason = validate_transition_path(())
        self.assertFalse(accepted)

    def test_terminal_states_have_no_exits(self) -> None:
        self.assertFalse(can_transition(RETIRED, ACTIVE))
        self.assertFalse(can_transition(REVOKED, HELD))

    def test_revoked_reachable_from_live_states(self) -> None:
        self.assertTrue(can_transition(ACTIVE, REVOKED))
        self.assertTrue(can_transition(HELD, REVOKED))
        self.assertTrue(can_transition(ESCALATED, REVOKED))


if __name__ == "__main__":
    unittest.main()
