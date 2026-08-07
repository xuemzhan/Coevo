"""US-16-AC-2: eight-state lifecycle and L19 path rule (CTAF §8.3 / M2).

L19 (v0.4.1 semantics): any path returning from ESCALATED to ACTIVE must pass
through HELD; RETIRED is a direct terminal exit.  ``validate_transition_path``
is a pure, fail-closed validator used by :func:`validate_plan`.
"""

from __future__ import annotations

from enum import Enum


class LifecycleState(Enum):
    """CTAF §8.3 eight-state lifecycle."""

    REGISTERED = "REGISTERED"
    INSTANTIATED = "INSTANTIATED"
    ACTIVE = "ACTIVE"
    HELD = "HELD"
    RECOVERED = "RECOVERED"
    ESCALATED = "ESCALATED"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"


# Fail-closed transition table.  ESCALATED never leads to ACTIVE directly
# (L19); REVOKED is reachable from any live state; RETIRED is terminal.
_TRANSITIONS: dict[LifecycleState, frozenset[LifecycleState]] = {
    LifecycleState.REGISTERED: frozenset(
        {LifecycleState.INSTANTIATED, LifecycleState.REVOKED}
    ),
    LifecycleState.INSTANTIATED: frozenset(
        {LifecycleState.ACTIVE, LifecycleState.REVOKED}
    ),
    LifecycleState.ACTIVE: frozenset(
        {
            LifecycleState.HELD,
            LifecycleState.RECOVERED,
            LifecycleState.RETIRED,
            LifecycleState.REVOKED,
        }
    ),
    LifecycleState.HELD: frozenset(
        {
            LifecycleState.ACTIVE,
            LifecycleState.RECOVERED,
            LifecycleState.RETIRED,
            LifecycleState.REVOKED,
        }
    ),
    LifecycleState.RECOVERED: frozenset(
        {LifecycleState.ESCALATED, LifecycleState.RETIRED, LifecycleState.REVOKED}
    ),
    LifecycleState.ESCALATED: frozenset(
        {LifecycleState.HELD, LifecycleState.RETIRED, LifecycleState.REVOKED}
    ),
    LifecycleState.RETIRED: frozenset(),
    LifecycleState.REVOKED: frozenset(),
}


def can_transition(current: LifecycleState, target: LifecycleState) -> bool:
    """True when a single direct transition is allowed by the table."""

    return target in _TRANSITIONS.get(current, frozenset())


def validate_transition_path(
    path: tuple[LifecycleState, ...],
) -> tuple[bool, str | None]:
    """Validate a state path; rejects ESCALATED→ACTIVE jumps (L19).

    Returns ``(accepted, failure_reason)``; empty path is rejected (fail-closed).
    """

    if not path:
        return False, "transition path must not be empty"
    for index in range(len(path) - 1):
        current = path[index]
        target = path[index + 1]
        if not isinstance(current, LifecycleState) or not isinstance(
            target, LifecycleState
        ):
            return False, f"invalid state at step {index}"
        if not can_transition(current, target):
            reason = (
                "L19: ESCALATED must not jump directly to ACTIVE"
                if current is LifecycleState.ESCALATED
                and target is LifecycleState.ACTIVE
                else f"illegal transition {current.value} -> {target.value}"
            )
            return False, reason
    return True, None
