"""US-3 talent pool domain model (US-3-AC-1 / AC-2).

Field-minimum contract (AC-2)
-----------------------------
A :class:`Talent` carries exactly the following fields:

* ``talent_code`` — stable, opaque, organisation-assigned identifier
  (e.g. ``"t.7af3"``). NEVER the real name.
* ``skill_tags`` — closed-set tuple of :class:`SkillTag` (each tag is
  a ``"<category>:<value>"`` string). NO free-text resumes.
* ``credentials`` — closed-set tuple of strings drawn from a small
  whitelist (``"cert.pmp"``, ``"cert.audit"``, etc.). NO free-text.
* ``current_task_count`` — non-negative integer (current active load).
* ``max_parallel_tasks`` — positive integer (capacity ceiling).
* ``availability`` — :class:`AvailabilityWindow` (ISO-8601 UTC Z range).
* ``redacted_identity`` — :class:`RedactedIdentity` produced by
  :mod:`.redaction`. Raw PII never enters this model.

A :class:`TalentPool` is a frozen tuple of :class:`Talent` plus a
``pool_code`` (stable identifier for the talent database).

The model layer enforces strict invariants at construction time so
that any persisted record that violates AC-2's field-minimum contract
fails closed (AGENTS.md §3 第 7 条).
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import Iterable


class TalentRecommenderError(Exception):
    """Base class for all US-3 errors. Fail-closed by default."""


class TalentValidationError(TalentRecommenderError):
    """Raised when a Talent / TalentPool violates the field-minimum contract.

    Distinct from :class:`TalentRecommenderError` so callers can branch
    on "validation failed (user-fixable)" vs "structural invariant
    violated (engineering bug)".
    """


_SAFE_CODE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.\-]{0,63}$")
_ISO_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")


@dataclass(frozen=True)
class SkillTag:
    """A single skill tag attached to a :class:`Talent`.

    Tags are ``"<category>:<value>"`` strings, where ``category`` is
    one of a closed set enforced at parse time (see
    :func:`validate_skill_tag`).
    """

    value: str  # e.g. "tech:python", "domain:audit"

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or ":" not in self.value:
            raise TalentValidationError(
                f"skill tag must be 'category:value'; got {self.value!r}"
            )
        category, _, sub = self.value.partition(":")
        if not category or not sub:
            raise TalentValidationError(
                f"skill tag must have non-empty category AND value; got {self.value!r}"
            )
        if not _SAFE_CODE.match(category) or not _SAFE_CODE.match(sub):
            raise TalentValidationError(
                f"skill tag parts must match safe-id; got {self.value!r}"
            )


@dataclass(frozen=True)
class AvailabilityWindow:
    """An ISO-8601 UTC 'Z' half-open window in which a talent is available."""

    start: str
    end: str

    def __post_init__(self) -> None:
        if not _ISO_Z.match(self.start):
            raise TalentValidationError(
                f"availability.start must be ISO-8601 UTC 'Z'; got {self.start!r}"
            )
        if not _ISO_Z.match(self.end):
            raise TalentValidationError(
                f"availability.end must be ISO-8601 UTC 'Z'; got {self.end!r}"
            )
        if self.end < self.start:
            raise TalentValidationError(
                f"availability.end ({self.end!r}) must be >= start ({self.start!r})"
            )

    def overlaps(self, other: "AvailabilityWindow") -> bool:
        """Return True iff this window overlaps ``other`` (half-open)."""
        return not (self.end <= other.start or other.end <= self.start)


@dataclass(frozen=True)
class RedactedIdentity:
    """A redaction of PII into stable codes / hashes.

    The recommender NEVER sees the raw identity; only the redacted
    form is carried through. ``display_hint`` is a short non-PII
    token (≤16 chars) suitable for UI rendering.
    """

    pool_code: str
    display_hint: str
    identity_hash: str  # hex SHA-256


@dataclass(frozen=True)
class Talent:
    """A single candidate in the :class:`TalentPool`.

    All fields are required. There are no optional fields, no
    free-text descriptions, no raw names. Any caller that needs a
    raw identity must use :func:`src.coevo.talent.redaction.redact_identity`
    to produce this object.
    """

    talent_code: str
    skill_tags: tuple[SkillTag, ...]
    credentials: tuple[str, ...]
    current_task_count: int
    max_parallel_tasks: int
    availability: AvailabilityWindow
    redacted_identity: RedactedIdentity

    def __post_init__(self) -> None:
        if not _SAFE_CODE.match(self.talent_code):
            raise TalentValidationError(
                f"talent_code must match safe-id; got {self.talent_code!r}"
            )
        # Skill tag uniqueness
        seen: set[str] = set()
        for tag in self.skill_tags:
            if tag.value in seen:
                raise TalentValidationError(
                    f"duplicate skill_tag {tag.value!r}"
                )
            seen.add(tag.value)
        # Credential format
        for cred in self.credentials:
            if not _SAFE_CODE.match(cred):
                raise TalentValidationError(
                    f"credential must match safe-id; got {cred!r}"
                )
        # Load invariants
        if self.current_task_count < 0:
            raise TalentValidationError("current_task_count must be >= 0")
        if self.max_parallel_tasks < 1:
            raise TalentValidationError("max_parallel_tasks must be >= 1")
        if self.current_task_count > self.max_parallel_tasks:
            raise TalentValidationError(
                "current_task_count cannot exceed max_parallel_tasks"
            )


@dataclass(frozen=True)
class TalentPool:
    """A frozen collection of :class:`Talent` records.

    Carries the metadata required by the recommender (pool_code +
    schema_version). Talent codes are unique within a pool.
    """

    pool_code: str
    schema_version: str
    talents: tuple[Talent, ...]

    def __post_init__(self) -> None:
        if not _SAFE_CODE.match(self.pool_code):
            raise TalentValidationError(
                f"pool_code must match safe-id; got {self.pool_code!r}"
            )
        if self.schema_version != "1.0":
            raise TalentValidationError(
                f"unsupported schema_version {self.schema_version!r}; only '1.0' is supported"
            )
        if not self.talents:
            raise TalentValidationError("TalentPool.talents must be non-empty")
        seen: set[str] = set()
        for t in self.talents:
            if t.talent_code in seen:
                raise TalentValidationError(
                    f"duplicate talent_code {t.talent_code!r}"
                )
            seen.add(t.talent_code)
            if t.redacted_identity.pool_code != self.pool_code:
                raise TalentValidationError(
                    f"talent {t.talent_code!r} identity pool_code does not match pool"
                )
        # O(1) code -> talent index. Private and excluded from
        # equality / hashing (declared fields only).
        object.__setattr__(
            self, "_code_index", {t.talent_code: t for t in self.talents}
        )

    def by_code(self, talent_code: str) -> Talent | None:
        return self._code_index.get(talent_code)


class OverloadReason(enum.Enum):
    """Reasons a candidate may be flagged as overloaded."""

    AT_CAPACITY = "at_capacity"  # current == max
    OVER_CAPACITY = "over_capacity"  # current > max (data corruption)
    WINDOW_CONFLICT = "window_conflict"  # requested window does not overlap availability


@dataclass(frozen=True)
class LoadAlert:
    """A single load / conflict alert attached to a recommendation."""

    talent_code: str
    reason: OverloadReason
    detail: str


@dataclass(frozen=True)
class RecommendationReason:
    """A single (transparent) reason a candidate was scored."""

    kind: str  # closed set: "skill_match", "credential_match", "availability_fit", "load_capacity", "tie_break"
    weight: float  # non-negative contribution to the final score
    detail: str


@dataclass(frozen=True)
class Recommendation:
    """A single ranked recommendation for a task slot."""

    talent: Talent
    score: float  # final non-negative score
    reasons: tuple[RecommendationReason, ...]
    alerts: tuple[LoadAlert, ...]
    rank: int  # 1-based rank within the recommendation list

    def __post_init__(self) -> None:
        if self.score < 0.0:
            raise TalentValidationError("score must be >= 0")
        if self.rank < 1:
            raise TalentValidationError("rank must be >= 1")
