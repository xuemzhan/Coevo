"""FRAMEWORK-OPTIMIZE-6: demo composition-root staged helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.coevo.app.pipeline import (
    _build_demo_cockpit_views,
    _publish_demo_audit,
    _store_demo_knowledge,
)
from src.coevo.audit_governance import AuditStreamHub


ROOT = Path(__file__).resolve().parents[2]


class CockpitViewsTests(unittest.TestCase):
    def test_views_are_built_with_demo_fields(self) -> None:
        workspace_view, role_view = _build_demo_cockpit_views()
        self.assertEqual("PRJ001", workspace_view.project_id)
        self.assertEqual("a.eng", role_view.role_id)
        self.assertEqual(1, len(role_view.current_tasks))
        self.assertEqual(1, len(role_view.milestones))
        self.assertEqual(1, len(role_view.artifacts))


class AuditPublishTests(unittest.TestCase):
    def test_publish_demo_audit_emits_three_events(self) -> None:
        hub = AuditStreamHub()
        pushed: list[object] = []
        hub.subscribe("u.auditor", pushed.append)
        _publish_demo_audit(hub, "2026-08-08T02:00:00.000000Z")
        self.assertEqual(3, len(pushed))
        self.assertEqual(3, hub.event_count)
        actions = [getattr(event, "action", None) for event in pushed]
        self.assertEqual(
            ["chain.completed", "package.exported", "knowledge.stored"], actions
        )


class KnowledgeStoreTests(unittest.TestCase):
    def test_store_demo_knowledge_creates_db_and_returns_bundle_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle_id = _store_demo_knowledge(
                Path(tmp), "2026-08-08T02:00:00.000000Z"
            )
            self.assertTrue(bundle_id)
            self.assertTrue((Path(tmp) / "knowledge.db").is_file())


class CompositionRootGuardTests(unittest.TestCase):
    def test_inline_stages_are_extracted_to_module_helpers(self) -> None:
        source = (ROOT / "src" / "coevo" / "app" / "pipeline.py").read_text(
            encoding="utf-8"
        )
        # Each stage body must appear exactly once, inside its module helper.
        self.assertEqual(1, source.count("build_encrypted_package("))
        self.assertEqual(1, source.count("KnowledgeBaseFacade.aggregate("))
        self.assertEqual(1, source.count("WorkspaceView("))
        self.assertEqual(1, source.count("AuditEvent.from_audit_record("))


if __name__ == "__main__":
    unittest.main()
