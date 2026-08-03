"""Integration tests: US-8-AC-2 watcher feeds the progress capture facade."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.coevo.progress_capture import (
    ProgressCaptureService,
    ProgressItemStatus,
    WorkspaceWatcher,
)
from src.coevo.workspace.models import WorkspaceEntry


NOW = "2026-08-22T00:00:00Z"


class ProgressWatcherIntegrationTests(unittest.TestCase):
    def test_watcher_events_feed_progress_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "docs" / "draft.md"
            target.parent.mkdir()
            target.write_text("draft complete", encoding="utf-8")

            watcher = WorkspaceWatcher(root, stability_checks=1)
            events = watcher.scan(now=NOW)
            created = next(
                event for event in events if event.relative_path == "docs/draft.md"
            )
            evidence = watcher.build_evidence_input(
                created,
                task_id="t.1",
                text="draft complete",
                confidence=0.8,
            )
            workspace = WorkspaceEntry(
                project_id="PRJ001",
                role_id="a.eng",
                package_id="pkg.1",
                revision="r1",
            )
            capture = ProgressCaptureService.extract_progress(
                workspace,
                (evidence,),
                now=NOW,
            )
            self.assertTrue(capture.requires_user_confirmation)
            self.assertFalse(capture.formally_accepted)
            self.assertEqual(1, len(capture.progress_items))
            item = capture.progress_items[0]
            self.assertIs(ProgressItemStatus.PROPOSED, item.status)
            self.assertEqual("t.1", item.task_id)
            self.assertEqual(1, len(item.evidence_refs))
            self.assertEqual("docs/draft.md", item.evidence_refs[0].path)
            self.assertEqual("PRJ001", item.workspace_project_id)

    def test_watcher_background_mode_collects_modified_events(self):
        import time

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "notes.txt"
            target.write_text("one", encoding="utf-8")
            watcher = WorkspaceWatcher(
                root,
                stability_checks=1,
                poll_interval_sec=0.05,
            )
            watcher.scan(now=NOW)  # initial snapshot
            watcher.drain()
            watcher.start()
            try:
                time.sleep(0.05)
                target.write_text("one and two", encoding="utf-8")
                deadline = time.monotonic() + 3.0
                events = ()
                while time.monotonic() < deadline:
                    events = watcher.drain()
                    if events:
                        break
                    time.sleep(0.05)
                self.assertGreaterEqual(len(events), 1)
                self.assertEqual("notes.txt", events[0].relative_path)
            finally:
                watcher.stop()


if __name__ == "__main__":
    unittest.main()
