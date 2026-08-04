"""US-3 talent-recommender service layer (US-3-AC-1).

Thin facade over :mod:`.recommender`. Accepts a :class:`TalentPool`
plus a list of task-slot requirements and returns ranked
:class:`Recommendation` objects with audit-record projection.

The service does NOT call any model. Scoring is the deterministic
algorithm in :mod:`.recommender`. The "智能体" that produces
candidate requirements from a US-2 :class:`ProjectBaseline` is a
wired in the composition layer; this slice ships only the
deterministic plumbing.

Non-goals (out of scope for US-3-AC-1)
--------------------------------------
* No I/O. The pool is supplied as a Python object.
* No LLM call. Recommendations are produced by deterministic scoring.
* No persistence in the service. Pool persistence + redaction-on-import
  are provided by :class:`TalentStore` (US-3-AC-2, ``store.py``).
"""
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 人才推荐服务层（US-3 AC-1）：TalentRecommenderService.recommend_for_requirements()
# 对每个任务槽位按确定性评分（技能/资质/窗口/负荷）排序，附 LoadAlert
# （满负荷/时间冲突）；to_audit_record() 只记池代号/数量/告警统计。
# 人才池只含脱敏身份（redaction 层保证），本层不接触 PII。

from __future__ import annotations

import dataclasses
from typing import Any, Iterable

from .models import (
    AvailabilityWindow,
    OverloadReason,
    Recommendation,
    TalentPool,
    TalentValidationError,
)
from .recommender import TaskRequirement, recommend


@dataclasses.dataclass(frozen=True)
class TalentRecommenderService:
    """Deterministic facade for the US-3 talent-recommender slice.

    No internal state — every method is a pure function of its inputs.
    """

    def recommend_for_requirements(
        self,
        pool: TalentPool,
        requirements: Iterable[TaskRequirement],
        *,
        limit: int | None = None,
    ) -> tuple[Recommendation, ...]:
        """Rank candidates for the given task requirements.

        Wrapper over :func:`src.coevo.talent.recommender.recommend`
        that exposes the same contract via the service facade. Kept
        separate so other slices (US-4 编排 / US-13 决策简报) can
        depend on the service interface without touching the
        scoring internals.
        """
        return recommend(pool, requirements, limit=limit)

    def to_audit_record(
        self,
        pool: TalentPool,
        recommendations: tuple[Recommendation, ...],
    ) -> dict[str, Any]:
        """Produce a deterministic, JSON-safe audit-record projection.

        Same shape convention as US-1 / US-2 audit helpers. No raw
        PII (the pool only carries redacted identities, but we
        further project to codes + counts to keep the audit log
        small and stable).
        """
        alert_counts: dict[str, int] = {}
        for rec in recommendations:
            for alert in rec.alerts:
                alert_counts[alert.reason.value] = (
                    alert_counts.get(alert.reason.value, 0) + 1
                )
        return {
            "kind": "talent.recommendation",
            "schema_version": "1.0",
            "pool_code": pool.pool_code,
            "pool_schema_version": pool.schema_version,
            "talent_count": len(pool.talents),
            "recommendation_count": len(recommendations),
            "alert_counts": alert_counts,
            "top_score": (
                max((r.score for r in recommendations), default=0.0)
            ),
        }
