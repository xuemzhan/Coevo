"""FRAMEWORK-GAPS-5: repo-wide ISO regex `\\Z` anchor regression."""

from __future__ import annotations

import unittest

from src.coevo.audit_governance.models import _ISO_UTC_Z as audit_iso
from src.coevo.cockpit.models import _ISO_UTC_Z as cockpit_iso
from src.coevo.cockpit.sessions import _ISO_UTC_Z as sessions_iso
from src.coevo.crypto.cng_handle import _ISO_RE as cng_iso
from src.coevo.knowledge_base.models import _ISO_UTC_Z as kb_iso
from src.coevo.orchestrator.models import _ISO_UTC_Z as orch_iso
from src.coevo.progress_capture.models import _ISO_UTC_Z as pc_iso
from src.coevo.progress_capture.watcher import _ISO_UTC_Z as watcher_iso
from src.coevo.talent.models import _ISO_Z as talent_iso
from src.coevo.task_decomposition.agent import _ISO_Z as td_agent_iso
from src.coevo.task_decomposition.baseline import _ISO_Z as td_base_iso


class IsoAnchorRegressionTests(unittest.TestCase):
    """GAPS-5: Python `$` matches before a final newline; `\\Z` must not."""

    def test_trailing_newline_rejected_repo_wide(self) -> None:
        for name, pattern in (
            ("audit_governance", audit_iso),
            ("cockpit.models", cockpit_iso),
            ("cockpit.sessions", sessions_iso),
            ("crypto.cng_handle", cng_iso),
            ("knowledge_base", kb_iso),
            ("orchestrator", orch_iso),
            ("progress_capture.models", pc_iso),
            ("progress_capture.watcher", watcher_iso),
            ("talent", talent_iso),
            ("task_decomposition.agent", td_agent_iso),
            ("task_decomposition.baseline", td_base_iso),
        ):
            with self.subTest(module=name):
                self.assertIsNone(
                    pattern.match("2026-08-08T08:00:00Z\n"),
                    f"{name}: trailing newline must be rejected",
                )
                self.assertIsNotNone(
                    pattern.match("2026-08-08T08:00:00Z"),
                    f"{name}: clean timestamp must be accepted",
                )
                self.assertIsNotNone(
                    pattern.match("2026-08-08T08:00:00.123456Z"),
                    f"{name}: fractional seconds must be accepted",
                )


if __name__ == "__main__":
    unittest.main()
