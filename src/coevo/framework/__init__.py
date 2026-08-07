"""Framework layer (CTAF US-16): manifest checking, policy and plan control.

US-16-AC-1 ships the manifest-checker; US-16-AC-2 ships Policy abstractions,
Plan/L18 white-list rules, the eight-state lifecycle (L19) and
``validate_plan``.  The layer follows CTAF v0.4.1
(``docs/plans/distributed-agent-framework/design-proposal.md``).
"""

from .manifest_checker import (
    AUDIT_PROJECTION_KEYS,
    AgentManifest,
    ManifestCheckInput,
    ManifestCheckResult,
    ManifestRegistry,
    ManifestValidationError,
    check,
)
from .lifecycle import LifecycleState, can_transition, validate_transition_path
from .plan import (
    POLICY_OWNED_NUMERIC_KEYS,
    Plan,
    PlanEdge,
    PlanNode,
    PlanNodeKind,
    plan_fingerprint,
)
from .policy import (
    PROFILES,
    Policy,
    PolicyValidationError,
    default_profiles,
    get_default_profile,
    validate_policy,
)
from .validation import (
    VALIDATION_PROJECTION_KEYS,
    ValidationResult,
    validate_plan,
)

__all__ = [
    "AUDIT_PROJECTION_KEYS",
    "AgentManifest",
    "LifecycleState",
    "ManifestCheckInput",
    "ManifestCheckResult",
    "ManifestRegistry",
    "ManifestValidationError",
    "POLICY_OWNED_NUMERIC_KEYS",
    "PROFILES",
    "Plan",
    "PlanEdge",
    "PlanNode",
    "PlanNodeKind",
    "Policy",
    "PolicyValidationError",
    "VALIDATION_PROJECTION_KEYS",
    "ValidationResult",
    "can_transition",
    "check",
    "default_profiles",
    "get_default_profile",
    "plan_fingerprint",
    "validate_plan",
    "validate_policy",
    "validate_transition_path",
]
