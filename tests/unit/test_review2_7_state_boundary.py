"""REVIEW2-7: model-suggestion / formal-state typed boundary guard tests.

Contract (docs/architecture/state-change-boundary.md):

* model output enters the business layer ONLY as DraftSuggestion
  (requires_confirmation defaults to True, confidence in [0,1]);
* formal state writes accept ONLY ConfirmedStateChange;
* ensure_confirmed_state_change rejects raw dicts and unconfirmed drafts.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.model import (
    ConfirmedStateChange,
    DraftSuggestion,
    ModelValidationError,
    SuggestionEvidence,
    ensure_confirmed_state_change,
)

ROOT = Path(__file__).resolve().parents[2]


class StateBoundaryTests(unittest.TestCase):
    def test_draft_requires_confirmation_by_default(self) -> None:
        draft = DraftSuggestion(
            source="task_decomposition",
            content={"tasks": ("t.1",)},
        )
        self.assertTrue(draft.requires_confirmation)

    def test_draft_rejects_out_of_range_confidence(self) -> None:
        for bad in (-0.1, 1.5, "0.5", True):
            with self.assertRaises(ModelValidationError):
                DraftSuggestion(
                    source="risk",
                    content={"risk": "late"},
                    confidence=bad,  # type: ignore[arg-type]
                )

    def test_draft_accepts_boundary_confidence(self) -> None:
        for value in (0.0, 1.0, 0.7):
            draft = DraftSuggestion(
                source="risk",
                content={"risk": "late"},
                confidence=value,
                evidence=(SuggestionEvidence("rule", "rules.py", "a" * 64),),
            )
            self.assertEqual(draft.confidence, value)

    def test_confirmed_state_change_validates_fields(self) -> None:
        change = ConfirmedStateChange(
            confirmed_by="u.pm",
            confirmed_at="2026-08-10T00:00:00Z",
            source_draft_id="draft.1",
            changes={"status": "accepted"},
        )
        self.assertEqual(change.confirmed_by, "u.pm")
        with self.assertRaises(ModelValidationError):
            ConfirmedStateChange(
                confirmed_by="u.pm",
                confirmed_at="2026-08-10T00:00:00",  # no trailing Z
                source_draft_id="draft.1",
                changes={"status": "accepted"},
            )
        with self.assertRaises(ModelValidationError):
            ConfirmedStateChange(
                confirmed_by="u.pm",
                confirmed_at="2026-08-10T00:00:00Z",
                source_draft_id="draft.1",
                changes={},
            )

    def test_guard_rejects_raw_dict(self) -> None:
        with self.assertRaises(ModelValidationError):
            ensure_confirmed_state_change({"status": "accepted"})

    def test_guard_rejects_unconfirmed_draft(self) -> None:
        draft = DraftSuggestion(
            source="task_decomposition",
            content={"tasks": ("t.1",)},
        )
        with self.assertRaises(ModelValidationError):
            ensure_confirmed_state_change(draft)

    def test_guard_accepts_confirmed_state_change(self) -> None:
        change = ConfirmedStateChange(
            confirmed_by="u.pm",
            confirmed_at="2026-08-10T00:00:00Z",
            source_draft_id="draft.1",
            changes={"status": "accepted"},
        )
        validated = ensure_confirmed_state_change(change)
        self.assertEqual(validated.changes, {"status": "accepted"})

    def test_doc_exists(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "state-change-boundary.md"
        ).read_text(encoding="utf-8")
        self.assertIn("DraftSuggestion", text)
        self.assertIn("ConfirmedStateChange", text)
        self.assertIn("ensure_confirmed_state_change", text)


if __name__ == "__main__":
    unittest.main()
