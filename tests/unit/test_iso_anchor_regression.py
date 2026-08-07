"""FRAMEWORK-GAPS-5/6: shared ISO validator anchor regression."""

from __future__ import annotations

import unittest

from src.coevo.knowledge_base.models import _check_iso_utc
from src.coevo.knowledge_base.models import KnowledgeBaseValidationError
from src.coevo.timefmt import is_iso_utc_z
from src.coevo.talent.models import AvailabilityWindow, TalentValidationError


class IsoAnchorRegressionTests(unittest.TestCase):
    """The anchor rule now lives in the shared ``is_iso_utc_z``."""

    def test_shared_validator_boundaries(self) -> None:
        for ok in (
            "2026-08-08T08:00:00Z",
            "2026-08-08T08:00:00.123456Z",
        ):
            self.assertTrue(is_iso_utc_z(ok), ok)
        for bad in (
            "2026-08-08T08:00:00Z\n",
            "2026-08-08T08:00:00.123Z\n",
            "2026-08-08 08:00:00Z",
            "2026-99-99T99:99:99Z",
            "2026-02-30T00:00:00Z",
            "2026-08-08T08:00:00",
            None,
            123,
        ):
            self.assertFalse(is_iso_utc_z(bad), repr(bad))

    def test_knowledge_base_rejects_trailing_newline(self) -> None:
        with self.assertRaises(KnowledgeBaseValidationError):
            _check_iso_utc("2026-08-08T08:00:00Z\n", field="ts")

    def test_talent_window_rejects_trailing_newline(self) -> None:
        with self.assertRaises(TalentValidationError):
            AvailabilityWindow("2026-08-01T00:00:00Z\n", "2026-08-31T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
