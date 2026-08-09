"""US-3 deterministic talent recommender (US-3-AC-1 / AC-3 + AC-4 + AC-5).

Scoring algorithm (deterministic, no IO, no model)
--------------------------------------------------
For each candidate in the pool we compute a non-negative score by
summing weighted contributions:

* +2.0 per matched ``required_skill_tags`` entry (case-sensitive
  exact match on ``SkillTag.value``)
* +1.0 per matched ``required_credentials`` entry
* +1.5 if the requested window fully contains the talent's
  availability window (perfect fit); +0.5 if they only overlap.
  0 if they don't overlap.
* +1.0 if the candidate's load is below capacity
  (``current_task_count < max_parallel_tasks``); 0 if at capacity.
* +0.0 (tie-break) — small deterministic bonus derived from the
  lexicographically-first skill tag, used to produce a stable
  ranking when scores tie.

Load / conflict detection (AC-5) is independent of the score and
attaches a :class:`LoadAlert` to the recommendation when triggered:

* ``OverloadReason.AT_CAPACITY`` — current == max.
* ``OverloadReason.WINDOW_CONFLICT`` — requested window does not
  overlap availability.
* ``OverloadReason.OVER_CAPACITY`` — current > max (data corruption
  in the source pool; the model layer already rejects this at
  construction, so the recommender surfaces it as a runtime
  alert only if the assertion was bypassed — fail-closed).

The recommender NEVER mutates the pool; it returns a fresh tuple
of :class:`Recommendation` sorted by ``(-score, talent_code)`` so the
ranking is deterministic across calls.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-3 确定性人才推荐：预热集合评分，O(R·N) 内环，结果可复现。
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import (
    AvailabilityWindow,
    LoadAlert,
    OverloadReason,
    Recommendation,
    RecommendationReason,
    Talent,
    TalentPool,
    TalentValidationError,
)


# ----------------------- scoring weights -----------------------

_W_SKILL = 2.0
_W_CREDENTIAL = 1.0
_W_WINDOW_FULL = 1.5
_W_WINDOW_PARTIAL = 0.5
_W_LOAD_HEADROOM = 1.0
_W_TIE_BREAK = 0.0  # informational only; no score effect


@dataclass(frozen=True)
class TaskRequirement:
    """A user-supplied requirement for a single task slot.

    ``required_skill_tags`` and ``required_credentials`` are matched
    against the candidate's tags / credentials (set semantics).
    ``window`` is the requested availability window for this task.
    """

    task_type: str
    required_skill_tags: tuple[str, ...]
    required_credentials: tuple[str, ...]
    window: AvailabilityWindow


def score_candidate(
    talent: Talent,
    requirement: TaskRequirement,
) -> tuple[float, tuple[RecommendationReason, ...], tuple[LoadAlert, ...]]:
    """Return ``(score, reasons, alerts)`` for a single candidate.

    Pure function. Deterministic. The tuple shapes match what
    :class:`Recommendation` consumes.
    """
    return _score_candidate(
        talent,
        requirement,
        skill_values=frozenset(tag.value for tag in talent.skill_tags),
        credential_values=frozenset(talent.credentials),
    )


def _match_skills(
    requirement: TaskRequirement,
    skill_values: frozenset[str],
    reasons: list[RecommendationReason],
) -> float:
    """Score the required-skill matches (case-sensitive exact match; +_W_SKILL each)."""
    score = 0.0

    for required in requirement.required_skill_tags:
        if required in skill_values:
            score += _W_SKILL
            reasons.append(
                RecommendationReason(
                    kind="skill_match",
                    weight=_W_SKILL,
                    detail=f"matched skill tag {required!r}",
                )
            )
    return score


def _match_credentials(
    requirement: TaskRequirement,
    credential_values: frozenset[str],
    reasons: list[RecommendationReason],
) -> float:
    """Score the required-credential matches (+_W_CREDENTIAL each)."""
    score = 0.0

    for required in requirement.required_credentials:
        if required in credential_values:
            score += _W_CREDENTIAL
            reasons.append(
                RecommendationReason(
                    kind="credential_match",
                    weight=_W_CREDENTIAL,
                    detail=f"matched credential {required!r}",
                )
            )
    return score


def _window_fit(
    talent: Talent,
    requirement: TaskRequirement,
    reasons: list[RecommendationReason],
    alerts: list[LoadAlert],
) -> float:
    """Score the requested-window fit and emit WINDOW_CONFLICT alerts (full/partial/none)."""
    score = 0.0

    if requirement.window.end <= talent.availability.start or \
            talent.availability.end <= requirement.window.start:
        # No overlap
        alerts.append(
            LoadAlert(
                talent_code=talent.talent_code,
                reason=OverloadReason.WINDOW_CONFLICT,
                detail=(
                    f"requested window {requirement.window.start}..{requirement.window.end} "
                    f"does not overlap availability {talent.availability.start}.."
                    f"{talent.availability.end}"
                ),
            )
        )
    elif (
        requirement.window.start <= talent.availability.start
        and talent.availability.end <= requirement.window.end
    ):
        # Full containment of availability
        score += _W_WINDOW_FULL
        reasons.append(
            RecommendationReason(
                kind="availability_fit",
                weight=_W_WINDOW_FULL,
                detail="availability window fully inside requested window",
            )
        )
    else:
        # Partial overlap
        score += _W_WINDOW_PARTIAL
        reasons.append(
            RecommendationReason(
                kind="availability_fit",
                weight=_W_WINDOW_PARTIAL,
                detail="availability window partially overlaps requested window",
            )
        )
    return score


def _load_headroom(
    talent: Talent,
    reasons: list[RecommendationReason],
    alerts: list[LoadAlert],
) -> float:
    """Score load headroom and emit AT_CAPACITY/OVER_CAPACITY alerts (fail-closed)."""
    score = 0.0

    if talent.current_task_count >= talent.max_parallel_tasks:
        alerts.append(
            LoadAlert(
                talent_code=talent.talent_code,
                reason=(
                    OverloadReason.OVER_CAPACITY
                    if talent.current_task_count > talent.max_parallel_tasks
                    else OverloadReason.AT_CAPACITY
                ),
                detail=(
                    f"current={talent.current_task_count} "
                    f"max={talent.max_parallel_tasks}"
                ),
            )
        )
    else:
        score += _W_LOAD_HEADROOM
        reasons.append(
            RecommendationReason(
                kind="load_capacity",
                weight=_W_LOAD_HEADROOM,
                detail=(
                    f"current={talent.current_task_count} < max={talent.max_parallel_tasks}"
                ),
            )
        )
    return score


def _tie_break(
    talent: Talent,
    reasons: list[RecommendationReason],
) -> None:
    """Append the deterministic, score-neutral tie-break reason (audit only)."""
    if talent.skill_tags:
        first_tag = min(tag.value for tag in talent.skill_tags)
        reasons.append(
            RecommendationReason(
                kind="tie_break",
                weight=_W_TIE_BREAK,
                detail=f"deterministic tie-break key {first_tag!r}",
            )
        )


def _score_candidate(
    talent: Talent,
    requirement: TaskRequirement,
    *,
    skill_values: frozenset[str],
    credential_values: frozenset[str],
) -> tuple[float, tuple[RecommendationReason, ...], tuple[LoadAlert, ...]]:
    """Scoring core with pre-computed candidate indexes.

    ``skill_values`` / ``credential_values`` are hoisted out of the
    per-requirement loop so a full ``recommend(pool, requirements)``
    run pays O(tags + credentials) per talent exactly once instead of
    once per requirement (this is the dominant cost when scoring a
    large pool against many task slots).
    """
    reasons: list[RecommendationReason] = []
    alerts: list[LoadAlert] = []
    score = 0.0

    # Skill match
    score += _match_skills(requirement, skill_values, reasons)
    # Credential match
    score += _match_credentials(requirement, credential_values, reasons)
    # Window fit
    score += _window_fit(talent, requirement, reasons, alerts)
    # Load headroom
    score += _load_headroom(talent, reasons, alerts)
    # Tie-break: deterministic, score-neutral (recorded for audit
    # but contributes 0 to the final score).
    _tie_break(talent, reasons)

    return score, tuple(reasons), tuple(alerts)


def recommend(
    pool: TalentPool,
    requirements: Iterable[TaskRequirement],
    *,
    limit: int | None = None,
) -> tuple[Recommendation, ...]:
    """Recommend candidates for one or more task slots.

    For each :class:`TaskRequirement`, every talent in the pool is
    scored, ranked by ``(-score, talent_code)``, and the top
    ``limit`` (default: all) become :class:`Recommendation` objects
    with 1-based ``rank`` values. ``limit`` is a positive integer or
    ``None`` for "all candidates".
    """
    if limit is not None and limit < 1:
        raise TalentValidationError("limit must be >= 1 or None")
    reqs = list(requirements)
    if not reqs:
        raise TalentValidationError(
            "recommend requires at least one TaskRequirement"
        )

    out: list[Recommendation] = []
    # Precompute per-talent set indexes once for the whole call so the
    # inner loop is O(R x N) with O(1) set lookups instead of O(R x N x S).
    indexed_talents: list[tuple[Talent, frozenset[str], frozenset[str]]] = [
        (
            talent,
            frozenset(tag.value for tag in talent.skill_tags),
            frozenset(talent.credentials),
        )
        for talent in pool.talents
    ]
    for req in reqs:
        scored: list[tuple[float, Talent, tuple[RecommendationReason, ...], tuple[LoadAlert, ...]]] = []
        for talent, skill_values, credential_values in indexed_talents:
            s, reasons, alerts = _score_candidate(
                talent,
                req,
                skill_values=skill_values,
                credential_values=credential_values,
            )
            scored.append((s, talent, reasons, alerts))
        # Sort by score DESC, then talent_code ASC (deterministic tie-break)
        scored.sort(key=lambda item: (-item[0], item[1].talent_code))
        if limit is not None:
            scored = scored[:limit]
        for rank, (s, talent, reasons, alerts) in enumerate(scored, start=1):
            out.append(
                Recommendation(
                    talent=talent,
                    score=s,
                    reasons=reasons,
                    alerts=alerts,
                    rank=rank,
                )
            )
    return tuple(out)
