"""Unit tests for US-3-AC-1 talent-recommender slice.

Coverage matrix (each TestCase class locks one AC of the slice):

  AC-2  ``test_model_*``        - field-minimum schema + invariants.
  AC-3  ``test_recommend_*``    - task-type-to-candidate ranking.
  AC-4  ``test_reason_*``       - per-candidate reasons emitted.
  AC-5  ``test_load_*``         - overload + conflict detection.

Service-layer invariants:
* No IO, no network, no model call.
* Re-scoring the same inputs is byte-deterministic.
* Recommendations never carry raw PII (only talent_code +
  redacted identity fields).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.talent import (
    AvailabilityWindow,
    LoadAlert,
    OverloadReason,
    Recommendation,
    RecommendationReason,
    RedactedIdentity,
    SkillTag,
    Talent,
    TalentPool,
    TalentRecommenderError,
    TalentRecommenderService,
    TalentValidationError,
    recommend,
    score_candidate,
)
from src.coevo.talent.redaction import (
    redact_identity,
    stable_pool_code,
)
from src.coevo.talent.recommender import TaskRequirement


# ----------------------- fixtures -----------------------


def _win_full() -> AvailabilityWindow:
    return AvailabilityWindow(
        start="2026-08-01T00:00:00Z",
        end="2026-08-31T00:00:00Z",
    )


def _win_requested() -> AvailabilityWindow:
    return AvailabilityWindow(
        start="2026-08-05T00:00:00Z",
        end="2026-08-25T00:00:00Z",
    )


def _talent(
    code: str,
    skills: tuple[str, ...] = (),
    creds: tuple[str, ...] = (),
    current: int = 0,
    max_parallel: int = 3,
    window: AvailabilityWindow | None = None,
    pool_code: str = "pool_acme",
) -> Talent:
    return Talent(
        talent_code=code,
        skill_tags=tuple(SkillTag(s) for s in skills),
        credentials=creds,
        current_task_count=current,
        max_parallel_tasks=max_parallel,
        availability=window or _win_full(),
        redacted_identity=RedactedIdentity(
            pool_code=pool_code,
            display_hint=f"d_{code[:8]}",
            identity_hash="0" * 64,
        ),
    )


def _pool(talents: tuple[Talent, ...]) -> TalentPool:
    return TalentPool(pool_code="pool_acme", schema_version="1.0", talents=talents)


# ----------------------- AC-2: field minimum -----------------------


class ModelFieldTests(unittest.TestCase):
    def test_talent_carries_only_minimum_fields(self):
        t = _talent("t.7af3", skills=("tech:python",), creds=("cert.pmp",))
        for attr in (
            "talent_code", "skill_tags", "credentials",
            "current_task_count", "max_parallel_tasks",
            "availability", "redacted_identity",
        ):
            self.assertTrue(hasattr(t, attr))
        self.assertNotIn("name", t.__dataclass_fields__)
        self.assertNotIn("email", t.__dataclass_fields__)
        self.assertNotIn("resume", t.__dataclass_fields__)

    def test_invalid_talent_code_rejected(self):
        with self.assertRaises(TalentValidationError):
            _talent("invalid code with spaces")

    def test_duplicate_skill_tag_rejected(self):
        with self.assertRaises(TalentValidationError):
            Talent(
                talent_code="t.1",
                skill_tags=(SkillTag("tech:python"), SkillTag("tech:python")),
                credentials=(),
                current_task_count=0,
                max_parallel_tasks=3,
                availability=_win_full(),
                redacted_identity=RedactedIdentity(
                    pool_code="p", display_hint="x", identity_hash="0" * 64
                ),
            )

    def test_negative_current_load_rejected(self):
        with self.assertRaises(TalentValidationError):
            Talent(
                talent_code="t.1",
                skill_tags=(),
                credentials=(),
                current_task_count=-1,
                max_parallel_tasks=3,
                availability=_win_full(),
                redacted_identity=RedactedIdentity(
                    pool_code="p", display_hint="x", identity_hash="0" * 64
                ),
            )

    def test_max_parallel_zero_rejected(self):
        with self.assertRaises(TalentValidationError):
            Talent(
                talent_code="t.1",
                skill_tags=(),
                credentials=(),
                current_task_count=0,
                max_parallel_tasks=0,
                availability=_win_full(),
                redacted_identity=RedactedIdentity(
                    pool_code="p", display_hint="x", identity_hash="0" * 64
                ),
            )

    def test_current_exceeds_max_rejected(self):
        with self.assertRaises(TalentValidationError):
            Talent(
                talent_code="t.1",
                skill_tags=(),
                credentials=(),
                current_task_count=5,
                max_parallel_tasks=3,
                availability=_win_full(),
                redacted_identity=RedactedIdentity(
                    pool_code="p", display_hint="x", identity_hash="0" * 64
                ),
            )

    def test_invalid_availability_window_rejected(self):
        with self.assertRaises(TalentValidationError):
            AvailabilityWindow(start="2026-08-31T00:00:00Z", end="2026-08-01T00:00:00Z")

    def test_pool_requires_unique_talent_codes(self):
        t1 = _talent("t.dup")
        t2 = _talent("t.dup")
        with self.assertRaises(TalentValidationError):
            _pool((t1, t2))

    def test_pool_rejects_talent_from_other_pool(self):
        t = _talent("t.x", pool_code="pool_other")
        with self.assertRaises(TalentValidationError):
            _pool((t,))

    def test_pool_requires_non_empty_talents(self):
        with self.assertRaises(TalentValidationError):
            _pool(())

    def test_pool_unsupported_schema_version_rejected(self):
        with self.assertRaises(TalentValidationError):
            TalentPool(pool_code="pool_acme", schema_version="2.0", talents=(_talent("t.1"),))


# ----------------------- redaction tests -----------------------


class RedactionTests(unittest.TestCase):
    def test_stable_pool_code_lowercases_and_cleans(self):
        self.assertEqual("acme_corp", stable_pool_code("Acme Corp."))
        self.assertEqual("university_x", stable_pool_code("University-X"))

    def test_stable_pool_code_rejects_empty(self):
        with self.assertRaises(TalentValidationError):
            stable_pool_code("   ")

    def test_redact_identity_is_deterministic(self):
        a = redact_identity(
            pool_code="pool_acme",
            raw_name="Alice Doe",
            raw_email="alice@example.com",
            org_code="unit_a",
        )
        b = redact_identity(
            pool_code="pool_acme",
            raw_name="Alice Doe",
            raw_email="alice@example.com",
            org_code="unit_a",
        )
        self.assertEqual(a, b)
        self.assertEqual(a.identity_hash, b.identity_hash)
        self.assertEqual(64, len(a.identity_hash))

    def test_redact_identity_display_hint_bounded(self):
        ri = redact_identity(
            pool_code="pool_acme",
            raw_name="Bob",
            raw_email="bob@x.org",
            org_code="unit_a",
        )
        self.assertLessEqual(len(ri.display_hint), 16)

    def test_redact_identity_rejects_blank_inputs(self):
        with self.assertRaises(TalentValidationError):
            redact_identity(
                pool_code="pool_acme",
                raw_name="  ",
                raw_email="x@y",
                org_code="unit_a",
            )
        with self.assertRaises(TalentValidationError):
            redact_identity(
                pool_code="pool_acme",
                raw_name="X",
                raw_email="  ",
                org_code="unit_a",
            )
        with self.assertRaises(TalentValidationError):
            redact_identity(
                pool_code="bad pool",
                raw_name="X",
                raw_email="x@y",
                org_code="unit_a",
            )

    def test_redact_identity_canonicalises_case(self):
        a = redact_identity(
            pool_code="pool_acme",
            raw_name="Alice",
            raw_email="alice@x.com",
            org_code="unit_a",
        )
        b = redact_identity(
            pool_code="pool_acme",
            raw_name="ALICE",
            raw_email="ALICE@X.COM",
            org_code="unit_a",
        )
        self.assertEqual(a.identity_hash, b.identity_hash)


# ----------------------- AC-3: ranking -----------------------


class RecommendationRankingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pool = _pool((
            _talent("t.7af3", skills=("tech:python", "domain:audit"), current=0),
            _talent("t.91b2", skills=("tech:python",), current=1),
            _talent("t.4cc0", skills=("tech:java",), current=0),
        ))
        self.requirement = TaskRequirement(
            task_type="execution",
            required_skill_tags=("tech:python",),
            required_credentials=(),
            window=_win_requested(),
        )

    def test_recommend_returns_top_n(self):
        recs = recommend(self.pool, (self.requirement,), limit=2)
        self.assertEqual(2, len(recs))
        self.assertEqual(1, recs[0].rank)
        self.assertEqual(2, recs[1].rank)

    def test_recommend_ranks_by_score_then_talent_code(self):
        recs = recommend(self.pool, (self.requirement,), limit=3)
        codes = [r.talent.talent_code for r in recs]
        self.assertEqual("t.7af3", codes[0])
        self.assertEqual("t.91b2", codes[1])
        self.assertEqual("t.4cc0", codes[2])

    def test_recommend_score_reflects_skill_match(self):
        recs = recommend(self.pool, (self.requirement,))
        top = recs[0]
        # t.7af3 has 1 skill match (+2.0), partial window fit (+0.5),
        # 1 load headroom (+1.0) = 3.5. (Talent availability 8-01..8-31
        # is wider than requested 8-05..8-25, so we get partial, not full.)
        self.assertAlmostEqual(3.5, top.score, places=6)

    def test_recommend_is_deterministic_across_calls(self):
        a = recommend(self.pool, (self.requirement,))
        b = recommend(self.pool, (self.requirement,))
        self.assertEqual(a, b)

    def test_recommend_requires_at_least_one_requirement(self):
        with self.assertRaises(TalentValidationError):
            recommend(self.pool, ())

    def test_recommend_limit_must_be_positive(self):
        with self.assertRaises(TalentValidationError):
            recommend(self.pool, (self.requirement,), limit=0)


# ----------------------- AC-4: per-candidate reasons -----------------------


class RecommendationReasonTests(unittest.TestCase):
    def test_emits_skill_match_reason(self):
        pool = _pool((_talent("t.7af3", skills=("tech:python",)),))
        req = TaskRequirement(
            task_type="execution",
            required_skill_tags=("tech:python",),
            required_credentials=(),
            window=_win_requested(),
        )
        recs = recommend(pool, (req,))
        kinds = [r.kind for r in recs[0].reasons]
        self.assertIn("skill_match", kinds)
        self.assertIn("availability_fit", kinds)
        self.assertIn("load_capacity", kinds)

    def test_emits_credential_match_reason(self):
        pool = _pool((_talent("t.7af3", creds=("cert.pmp",)),))
        req = TaskRequirement(
            task_type="execution",
            required_skill_tags=(),
            required_credentials=("cert.pmp",),
            window=_win_requested(),
        )
        recs = recommend(pool, (req,))
        kinds = [r.kind for r in recs[0].reasons]
        self.assertIn("credential_match", kinds)

    def test_score_candidate_returns_reasons_and_alerts(self):
        t = _talent("t.x", skills=("tech:python",))
        req = TaskRequirement(
            task_type="execution",
            required_skill_tags=("tech:python",),
            required_credentials=(),
            window=_win_requested(),
        )
        score, reasons, alerts = score_candidate(t, req)
        self.assertGreater(score, 0.0)
        self.assertGreater(len(reasons), 0)
        self.assertEqual(0, len(alerts))


# ----------------------- AC-5: load / conflict detection -----------------------


class LoadAlertTests(unittest.TestCase):
    def test_at_capacity_alert_emitted(self):
        pool = _pool((
            Talent(
                talent_code="t.full",
                skill_tags=(SkillTag("tech:python"),),
                credentials=(),
                current_task_count=3,
                max_parallel_tasks=3,
                availability=_win_full(),
                redacted_identity=RedactedIdentity(
                    pool_code="pool_acme", display_hint="x", identity_hash="0" * 64
                ),
            ),
            _talent("t.free", skills=("tech:python",), current=1, max_parallel=3),
        ))
        req = TaskRequirement(
            task_type="execution",
            required_skill_tags=("tech:python",),
            required_credentials=(),
            window=_win_requested(),
        )
        recs = recommend(pool, (req,))
        by_code = {r.talent.talent_code: r for r in recs}
        self.assertIn("t.full", by_code)
        self.assertEqual(OverloadReason.AT_CAPACITY, by_code["t.full"].alerts[0].reason)
        # t.free has +load_capacity, t.full does not, so t.free > t.full.
        self.assertGreater(by_code["t.free"].score, by_code["t.full"].score)
        self.assertEqual(1, by_code["t.free"].rank)

    def test_window_conflict_alert_emitted(self):
        t = Talent(
            talent_code="t.busy",
            skill_tags=(SkillTag("tech:python"),),
            credentials=(),
            current_task_count=0,
            max_parallel_tasks=3,
            availability=AvailabilityWindow(
                start="2026-08-01T00:00:00Z",
                end="2026-08-31T00:00:00Z",
            ),
            redacted_identity=RedactedIdentity(
                pool_code="pool_acme", display_hint="x", identity_hash="0" * 64
            ),
        )
        pool = _pool((t,))
        req = TaskRequirement(
            task_type="execution",
            required_skill_tags=("tech:python",),
            required_credentials=(),
            window=AvailabilityWindow(
                start="2026-09-01T00:00:00Z",
                end="2026-09-30T00:00:00Z",
            ),
        )
        recs = recommend(pool, (req,))
        self.assertEqual(1, len(recs[0].alerts))
        self.assertEqual(OverloadReason.WINDOW_CONFLICT, recs[0].alerts[0].reason)

    def test_partial_window_fit(self):
        t = Talent(
            talent_code="t.partial",
            skill_tags=(SkillTag("tech:python"),),
            credentials=(),
            current_task_count=0,
            max_parallel_tasks=3,
            availability=AvailabilityWindow(
                start="2026-07-15T00:00:00Z",
                end="2026-08-10T00:00:00Z",
            ),
            redacted_identity=RedactedIdentity(
                pool_code="pool_acme", display_hint="x", identity_hash="0" * 64
            ),
        )
        pool = _pool((t,))
        req = TaskRequirement(
            task_type="execution",
            required_skill_tags=("tech:python",),
            required_credentials=(),
            window=AvailabilityWindow(
                start="2026-08-01T00:00:00Z",
                end="2026-08-20T00:00:00Z",
            ),
        )
        score, reasons, alerts = score_candidate(t, req)
        # +2.0 skill + 0.5 partial window + 1.0 load = 3.5
        self.assertAlmostEqual(3.5, score, places=6)
        self.assertEqual(0, len(alerts))
        self.assertIn("availability_fit", {r.kind for r in reasons})


# ----------------------- service-layer tests -----------------------


class ServiceLayerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TalentRecommenderService()
        self.pool = _pool((
            _talent("t.7af3", skills=("tech:python",)),
            _talent("t.91b2", skills=("tech:python",), current=1),
        ))
        self.req = TaskRequirement(
            task_type="execution",
            required_skill_tags=("tech:python",),
            required_credentials=(),
            window=_win_requested(),
        )

    def test_service_recommend_is_passthrough(self):
        a = self.service.recommend_for_requirements(self.pool, (self.req,))
        b = recommend(self.pool, (self.req,))
        self.assertEqual(a, b)

    def test_audit_record_is_json_safe(self):
        recs = self.service.recommend_for_requirements(self.pool, (self.req,))
        record = self.service.to_audit_record(self.pool, recs)
        s = json.dumps(record)
        self.assertEqual(record, json.loads(s))

    def test_audit_record_excludes_raw_pii(self):
        recs = self.service.recommend_for_requirements(self.pool, (self.req,))
        record = self.service.to_audit_record(self.pool, recs)
        self.assertNotIn("name", record)
        self.assertNotIn("email", record)
        self.assertEqual("pool_acme", record["pool_code"])
        self.assertEqual("1.0", record["pool_schema_version"])
        self.assertEqual(2, record["talent_count"])
        self.assertEqual(2, record["recommendation_count"])
        self.assertIn("talent.recommendation", record["kind"])


if __name__ == "__main__":
    unittest.main()