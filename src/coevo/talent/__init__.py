"""US-3 team formation (talent recommender) - US-3-AC-1.

Scope (AC closed loop in this slice)
------------------------------------
* ``models.py`` - frozen dataclasses for TalentPool, Talent, SkillTag,
  AvailabilityWindow, Recommendation, RecommendationReason, LoadAlert,
  plus a strict-monotonic-version ProjectAssignment snapshot that ties
  the recommender's output to a US-2 ProjectBaseline.
* ``redaction.py`` - deterministic redaction that turns free-form
  identity attributes (name, email, organization) into stable codes
  + hashes, without ever leaking the raw input. This is the AC-1 / AC-2
  field-minimum contract: every persisted record carries ONLY the
  redacted fields, never the raw PII.
* ``recommender.py`` - deterministic recommender that scores every
  candidate against a (task_type, required_skill_tags, window) tuple
  and returns ranked :class:`Recommendation` objects with explicit
  reasons + load / conflict alerts.
* ``service.py`` - :class:`TalentRecommenderService` facade that
  accepts a :class:`TalentPool` and a task description, returns a
  list of :class:`Recommendation`.

AC test matrix (each TestCase class locks one AC):
  AC-2  ``test_model_*``        - field-minimum schema + invariants.
  AC-3  ``test_recommend_*``    - task-type-to-candidate ranking.
  AC-4  ``test_reason_*``       - per-candidate reasons emitted.
  AC-5  ``test_load_*``         - overload + conflict detection.

What this is NOT
----------------
* No I/O. The pool is supplied as a Python object. Persistence +
  redaction-on-import live in ``store.py`` (US-3-AC-2).
* No LLM call. Recommendations are produced by a deterministic
  scoring function; extracting candidate requirements from a US-2
  baseline is wired in the composition layer, not in this service.
* No PII leak. The redaction layer is irreversible within the slice.
"""
from .models import (
    AvailabilityWindow,
    LoadAlert,
    OverloadReason,
    Recommendation,
    RecommendationReason,
    SkillTag,
    Talent,
    TalentPool,
    TalentRecommenderError,
    TalentValidationError,
)
from .redaction import (
    RedactedIdentity,
    redact_identity,
    stable_pool_code,
)
from .recommender import (
    recommend,
    score_candidate,
)
from .service import TalentRecommenderService
from .store import (
    TalentStore,
    TalentStoreDuplicateError,
    TalentStoreError,
    TalentStoreIntegrityError,
    talent_from_import,
)

__all__ = [
    "AvailabilityWindow",
    "LoadAlert",
    "OverloadReason",
    "Recommendation",
    "RecommendationReason",
    "RedactedIdentity",
    "SkillTag",
    "Talent",
    "TalentPool",
    "TalentRecommenderError",
    "TalentRecommenderService",
    "TalentStore",
    "TalentStoreDuplicateError",
    "TalentStoreError",
    "TalentStoreIntegrityError",
    "TalentValidationError",
    "recommend",
    "redact_identity",
    "score_candidate",
    "stable_pool_code",
    "talent_from_import",
]
