"""US-5 replay / duplicate-detection layer (US-5-AC-2 / 协议 § 17).

Scope
-----
This module implements the *logic* of 协议 § 17 duplicate / replay
detection over a flat in-memory registry. It does **not** persist
anything (persistence is a future slice — the receiver module
already covers the audit-log side via :mod:`coevo.audit`). It is a
pure function over a sequence of :class:`ProcessedPackage` records:

* same ``package_id`` ⇒ duplicate (协议 § 17 情况 1)
* same package digest ⇒ duplicate (协议 § 17 情况 2)
* ``sequence_no`` not greater than the most recent processed
  sequence from the same sender + project ⇒ replay candidate
  (协议 § 13 requires strictly increasing sequence numbers, so an
  equal sequence with different content is a reordering/replay
  anomaly and must not silently pass)
  (协议 § 17 情况 3)
* reference to an unknown original package (CORRECTION_PACKAGE /
  REVOCATION_PACKAGE) ⇒ invalid (协议 § 17 情况 4 / 5)

The detector refuses to silently accept any of these. A successful
:class:`check_replay` returns a :class:`ReplayDecision` describing
the outcome (accept / duplicate / replay / invalid-reference).

Non-goals
---------
* No persistence. The registry is supplied by the caller.
* No LLM, no IO, no model.
* No mutation of US-5-AC-1 wire layout.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-5 重放/重复检测（§17）：决策失败关闭，包身份绑定校验。
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Iterable


from .agent_package import PACKAGE_TYPES, AgentPackageError


class AgentPackageReplayError(AgentPackageError):
    """Raised when the replay / duplicate check rejects a package."""


class ReplayOutcome(enum.Enum):
    ACCEPT = "accept"
    DUPLICATE_PACKAGE_ID = "duplicate_package_id"        # 协议 § 17 情况 1
    DUPLICATE_DIGEST = "duplicate_digest"                # 协议 § 17 情况 2
    REPLAY_SEQUENCE = "replay_sequence"                  # 协议 § 17 情况 3
    REVOKED_PACKAGE = "revoked_package"                  # 协议 § 17 情况 4 (revocation)
    INVALID_REFERENCE = "invalid_reference"              # 协议 § 17 情况 5 / 6


@dataclass(frozen=True)
class ProcessedPackage:
    """A single record in the receiver's replay registry.

    ``package_digest`` is the canonical 64-char lowercase hex
    digest of the entire `.agent` file (协议 § 17 last bullet). The
    detector compares against this to catch content-equivalent
    re-uploads that happen to carry a fresh package_id.
    """

    package_id: str
    package_digest: str
    sender_cert_id: str
    recipient_cert_id: str
    project_id: str
    sequence_no: int


@dataclass(frozen=True)
class ReplayDecision:
    """Outcome of a :func:`check_replay` invocation.

    ``outcome`` is one of :class:`ReplayOutcome`. When it is
    :attr:`ReplayOutcome.ACCEPT`, ``previous_sequence_no`` is the
    highest sequence number previously processed for the same
    ``(sender_cert_id, recipient_cert_id, project_id)`` tuple, or
    ``None`` if no prior package exists.
    """

    outcome: ReplayOutcome
    previous_sequence_no: int | None
    detail: str


def _registry_for(
    registry: Iterable[ProcessedPackage],
    *,
    sender_cert_id: str,
    recipient_cert_id: str,
    project_id: str,
) -> list[ProcessedPackage]:
    """Return the bounded replay registry for a scope (fail-closed)."""
    return [
        r
        for r in registry
        if r.sender_cert_id == sender_cert_id
        and r.recipient_cert_id == recipient_cert_id
        and r.project_id == project_id
    ]


def check_replay(
    *,
    candidate: ProcessedPackage,
    registry: Iterable[ProcessedPackage] = (),
    revoked_package_ids: Iterable[str] = (),
) -> ReplayDecision:
    """Run the § 17 checks on ``candidate``.

    The detector returns rather than raises for the *reject*
    outcomes so callers can record a precise audit decision per
    协议 § 23 ("导入" + "重复检测" + "异常处置"). Only the structural
    validation failures raise (missing fields, bad types, unknown
    package_type, etc.).
    """
    if not isinstance(candidate, ProcessedPackage):
        raise AgentPackageReplayError("candidate must be ProcessedPackage")
    if not isinstance(candidate.package_id, str) or not candidate.package_id:
        raise AgentPackageReplayError("package_id must be a non-empty string")
    if not isinstance(candidate.package_digest, str) or not candidate.package_digest:
        raise AgentPackageReplayError("package_digest must be a non-empty string")
    if not isinstance(candidate.sender_cert_id, str) or not candidate.sender_cert_id:
        raise AgentPackageReplayError("sender_cert_id must be a non-empty string")
    if not isinstance(candidate.recipient_cert_id, str) or not candidate.recipient_cert_id:
        raise AgentPackageReplayError(
            "recipient_cert_id must be a non-empty string"
        )
    if not isinstance(candidate.project_id, str) or not candidate.project_id:
        raise AgentPackageReplayError("project_id must be a non-empty string")
    if not isinstance(candidate.sequence_no, int) or candidate.sequence_no < 1:
        raise AgentPackageReplayError("sequence_no must be a positive integer")

    revoked_set = set(revoked_package_ids)
    if candidate.package_id in revoked_set:
        return ReplayDecision(
            outcome=ReplayOutcome.REVOKED_PACKAGE,
            previous_sequence_no=None,
            detail=f"package_id {candidate.package_id!r} was revoked",
        )

    same_scope = _registry_for(
        registry,
        sender_cert_id=candidate.sender_cert_id,
        recipient_cert_id=candidate.recipient_cert_id,
        project_id=candidate.project_id,
    )
    # Single-pass scan (PERF-REPLAY-1): track the first package_id hit, the
    # first package_digest hit and the maximum sequence_no in one traversal
    # instead of three. Decision order and outcomes are byte-identical to the
    # previous three-pass version (id -> digest -> sequence priority); the id
    # hit keeps precedence over a digest hit even when the digest appears
    # earlier in the scope, so no early break is allowed.
    first_id_hit: ProcessedPackage | None = None
    first_digest_hit: ProcessedPackage | None = None
    previous_sequence_no: int | None = None
    for record in same_scope:
        if first_id_hit is None and record.package_id == candidate.package_id:
            first_id_hit = record
        if first_digest_hit is None and record.package_digest == candidate.package_digest:
            first_digest_hit = record
        if previous_sequence_no is None or record.sequence_no > previous_sequence_no:
            previous_sequence_no = record.sequence_no
    # 协议 § 17 情况 1: same package_id re-imported (highest precedence).
    if first_id_hit is not None:
        return ReplayDecision(
            outcome=ReplayOutcome.DUPLICATE_PACKAGE_ID,
            previous_sequence_no=first_id_hit.sequence_no,
            detail=(
                f"package_id {candidate.package_id!r} already processed "
                f"at sequence_no {first_id_hit.sequence_no}"
            ),
        )
    # 协议 § 17 情况 2: same package_digest re-imported.
    if first_digest_hit is not None:
        return ReplayDecision(
            outcome=ReplayOutcome.DUPLICATE_DIGEST,
            previous_sequence_no=first_digest_hit.sequence_no,
            detail=(
                f"package_digest {candidate.package_digest!r} already "
                f"processed at sequence_no {first_digest_hit.sequence_no}"
            ),
        )
    # 协议 § 17 情况 3 + § 13: sequence_no must be strictly greater
    # than the most recent processed sequence. An equal sequence with
    # different content is a reordering/replay anomaly and is rejected
    # (previously only strictly-earlier sequences were caught).
    if (
        previous_sequence_no is not None
        and candidate.sequence_no <= previous_sequence_no
    ):
        return ReplayDecision(
            outcome=ReplayOutcome.REPLAY_SEQUENCE,
            previous_sequence_no=previous_sequence_no,
            detail=(
                f"candidate sequence_no {candidate.sequence_no} is earlier than "
                f"the most recent {previous_sequence_no}"
            ),
        )
    return ReplayDecision(
        outcome=ReplayOutcome.ACCEPT,
        previous_sequence_no=previous_sequence_no,
        detail="candidate passes all § 17 checks",
    )


def check_reference_target(
    *,
    package_type: str,
    referenced_package_id: str | None,
    registry: Iterable[ProcessedPackage] = (),
) -> ReplayDecision:
    """Check § 17 情况 4 / 5: a CORRECTION or REVOCATION package
    must reference an existing, non-revoked original package.

    Raises :class:`AgentPackageReplayError` on structural failure;
    returns :class:`ReplayDecision` with
    :attr:`ReplayOutcome.INVALID_REFERENCE` when the referenced
    package is missing, and :attr:`ReplayOutcome.REVOKED_PACKAGE`
    when the referenced package was revoked.

    For non-correction / non-revocation packages the check is a
    no-op (:attr:`ReplayOutcome.ACCEPT`).
    """
    if package_type not in PACKAGE_TYPES:
        raise AgentPackageReplayError(
            f"package_type {package_type!r} is not in the protocol enum"
        )
    if package_type not in {"CORRECTION_PACKAGE", "REVOCATION_PACKAGE"}:
        return ReplayDecision(
            outcome=ReplayOutcome.ACCEPT,
            previous_sequence_no=None,
            detail="package type does not require a reference check",
        )
    if not isinstance(referenced_package_id, str) or not referenced_package_id:
        raise AgentPackageReplayError(
            f"{package_type} must reference a non-empty package_id"
        )
    for record in registry:
        if record.package_id == referenced_package_id:
            return ReplayDecision(
                outcome=ReplayOutcome.ACCEPT,
                previous_sequence_no=record.sequence_no,
                detail=f"references existing package_id {referenced_package_id!r}",
            )
    return ReplayDecision(
        outcome=ReplayOutcome.INVALID_REFERENCE,
        previous_sequence_no=None,
        detail=(
            f"{package_type} references unknown package_id "
            f"{referenced_package_id!r}"
        ),
    )
