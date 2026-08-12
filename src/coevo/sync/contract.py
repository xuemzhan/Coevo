"""sync.contract - cross-node sync envelope contract (PRODUCT-REVIEW T-11).

Design-only executable contract: the center-end/offline sync protocol will
carry signed event envelopes between nodes. This module pins the envelope
shape, versioning, ordering and replay-protection rules so the design cannot
drift from a checkable contract before implementation.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 跨节点同步信封契约：版本化、失败关闭、防重放。
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any, Mapping


SYNC_SCHEMA_VERSION: str = "0.1"

_SAFE_ID: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_.\-]{1,128}$")
_HEX_64: re.Pattern[str] = re.compile(r"^[0-9a-f]{64}$")


class SyncContractError(RuntimeError):
    """A sync envelope violated the contract."""


@dataclass(frozen=True)
class SyncEnvelope:
    """One ordered, replay-protected event envelope between nodes."""

    schema_version: str
    source_node: str
    event_id: str
    sequence: int
    created_at: str
    payload_digest: str
    previous_hash: str


def validate_envelope(data: Mapping[str, Any]) -> SyncEnvelope:
    """Fail-closed validation of a sync envelope mapping."""
    if not isinstance(data, Mapping):
        raise SyncContractError("envelope must be a mapping")
    for field in (
        "schema_version",
        "source_node",
        "event_id",
        "created_at",
        "payload_digest",
        "previous_hash",
    ):
        if not isinstance(data.get(field), str) or not data[field]:
            raise SyncContractError(f"{field} must be a non-empty string")
    if not isinstance(data.get("sequence"), int) or data["sequence"] <= 0:
        raise SyncContractError("sequence must be a positive integer")
    schema = data["schema_version"]
    if schema != SYNC_SCHEMA_VERSION:
        raise SyncContractError(
            f"unsupported sync schema_version {schema!r}"
        )
    for label in ("source_node", "event_id"):
        if not _SAFE_ID.fullmatch(data[label]):
            raise SyncContractError(f"{label} must be a safe id")
    for label in ("payload_digest", "previous_hash"):
        if not _HEX_64.fullmatch(data[label]):
            raise SyncContractError(f"{label} must be a 64-char lowercase hex")
    from src.coevo.timefmt import is_iso_utc_z

    if not is_iso_utc_z(data["created_at"]):
        raise SyncContractError("created_at must be ISO-8601 UTC Z")
    return SyncEnvelope(
        schema_version=schema,
        source_node=data["source_node"],
        event_id=data["event_id"],
        sequence=data["sequence"],
        created_at=data["created_at"],
        payload_digest=data["payload_digest"],
        previous_hash=data["previous_hash"],
    )


def envelope_digest(envelope: SyncEnvelope) -> str:
    """Canonical digest of an envelope (excluding previous_hash linkage)."""
    body = (
        f"{envelope.schema_version}|{envelope.source_node}|"
        f"{envelope.event_id}|{envelope.sequence}|"
        f"{envelope.created_at}|{envelope.payload_digest}"
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def validate_chain(envelopes: list[SyncEnvelope]) -> tuple[str, ...]:
    """Validate ordering + replay protection for a source-node chain.

    Rules:
    * sequence strictly increments by 1 per source node;
    * the first envelope links to the 64-char genesis hash ``0``;
    * each next envelope's ``previous_hash`` equals the previous envelope's
      digest (hash linkage);
    * event ids are unique per source node (replay protection).
    """
    digests: list[str] = []
    seen_events: set[str] = set()
    previous = "0" * 64
    for index, envelope in enumerate(envelopes, start=1):
        if envelope.previous_hash != previous:
            raise SyncContractError(
                f"envelope {index} breaks hash linkage"
            )
        if envelope.sequence != index:
            raise SyncContractError(
                f"envelope {index} sequence {envelope.sequence} != {index}"
            )
        if envelope.event_id in seen_events:
            raise SyncContractError(
                f"replay detected for event {envelope.event_id!r}"
            )
        seen_events.add(envelope.event_id)
        digest = envelope_digest(envelope)
        digests.append(digest)
        previous = digest
    return tuple(digests)
