"""Framework layer (CTAF US-16): deployment-point manifest checking.

US-16-AC-1 ships the manifest-checker; US-16-AC-2 (Policy abstractions and
``validate_plan``) lands in the next loop round.  The layer follows CTAF
v0.4.1 (``docs/plans/distributed-agent-framework/design-proposal.md``).
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

__all__ = [
    "AUDIT_PROJECTION_KEYS",
    "AgentManifest",
    "ManifestCheckInput",
    "ManifestCheckResult",
    "ManifestRegistry",
    "ManifestValidationError",
    "check",
]
