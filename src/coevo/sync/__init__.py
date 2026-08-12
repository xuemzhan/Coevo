"""sync - cross-node sync envelope contract, outbox and reconciliation.

Offline-first implementation of docs/architecture/sync-protocol.md
(PRODUCT-REVIEW T-11 contract, T-12 store/reconcile/file transport).
"""

from .contract import (
    SYNC_SCHEMA_VERSION,
    SyncContractError,
    SyncEnvelope,
    envelope_digest,
    validate_chain,
    validate_envelope,
)
from .store import (
    ReconcileResult,
    SyncOutbox,
    SyncReconciler,
    SyncRecord,
    export_bundle,
    load_bundle,
)

__all__ = [
    "SYNC_SCHEMA_VERSION",
    "SyncContractError",
    "SyncEnvelope",
    "envelope_digest",
    "validate_chain",
    "validate_envelope",
    "ReconcileResult",
    "SyncOutbox",
    "SyncReconciler",
    "SyncRecord",
    "export_bundle",
    "load_bundle",
]
