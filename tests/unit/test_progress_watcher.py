"""Unit tests for US-8-AC-2 workspace file watcher."""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from src.coevo.progress_capture import (
    EvidenceKind,
    FileChangeEvent,
    FileEventKind,
    ProgressCaptureValidationError,
    WorkspaceWatcher,
)


NOW = "2026-08-22T00:00:00Z"
NOW2 = "2026-08-22T00:00:01Z"


def _watcher(root: Path, **kwargs) -> WorkspaceWatcher:
    defaults = {
        "stability_checks": 1,
        "poll_interval_sec": 0.05,
        "max_events": 16,
    }
    defaults.update(kwargs)
    return WorkspaceWatcher(root, **defaults)


class WorkspaceWatcherConfigTests(unittest.TestCase):
    def test_missing_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ProgressCaptureValidationError):
                _watcher(Path(tmp) / "absent")

    def test_file_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "file.txt"
            path.write_text("x", encoding="utf-8")
            with self.assertRaises(ProgressCaptureValidationError):
                _watcher(path)

    def test_invalid_poll_interval_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ProgressCaptureValidationError):
                _watcher(root, poll_interval_sec=0.001)
            with self.assertRaises(ProgressCaptureValidationError):
                _watcher(root, poll_interval_sec=61.0)

    def test_invalid_limits_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ProgressCaptureValidationError):
                _watcher(root, max_events=0)
            with self.assertRaises(ProgressCaptureValidationError):
                _watcher(root, stability_checks=0)
            with self.assertRaises(ProgressCaptureValidationError):
                _watcher(root, max_digest_bytes=0)

    def test_invalid_allow_extensions_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ProgressCaptureValidationError):
                _watcher(Path(tmp), allow_extensions={"md"})


class WorkspaceWatcherScanTests(unittest.TestCase):
    def test_created_file_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            watcher = _watcher(root)
            target = root / "docs" / "draft.md"
            target.parent.mkdir()
            target.write_text("hello", encoding="utf-8")
            events = watcher.scan(now=NOW)
            self.assertEqual(1, len(events))
            event = events[0]
            self.assertIs(FileEventKind.CREATED, event.kind)
            self.assertEqual("docs/draft.md", event.relative_path)
            self.assertEqual(5, event.size_bytes)
            self.assertEqual(64, len(event.digest_hex))

    def test_stability_gating_requires_two_scans(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            watcher = _watcher(root, stability_checks=2)
            target = root / "draft.md"
            target.write_text("v1", encoding="utf-8")
            self.assertEqual((), watcher.scan(now=NOW))
            self.assertEqual((), watcher.drain())
            events = watcher.scan(now=NOW2)
            self.assertEqual(1, len(events))
            self.assertIs(FileEventKind.CREATED, events[0].kind)

    def test_modified_file_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            watcher = _watcher(root)
            target = root / "draft.md"
            target.write_text("v1", encoding="utf-8")
            watcher.scan(now=NOW)
            watcher.drain()
            time.sleep(0.02)
            target.write_text("version two", encoding="utf-8")
            events = watcher.scan(now=NOW2)
            self.assertEqual(1, len(events))
            self.assertIs(FileEventKind.MODIFIED, events[0].kind)
            self.assertEqual(11, events[0].size_bytes)

    def test_deleted_file_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            watcher = _watcher(root)
            target = root / "draft.md"
            target.write_text("v1", encoding="utf-8")
            watcher.scan(now=NOW)
            watcher.drain()
            target.unlink()
            events = watcher.scan(now=NOW2)
            self.assertEqual(1, len(events))
            self.assertIs(FileEventKind.DELETED, events[0].kind)
            self.assertEqual("", events[0].digest_hex)

    def test_queue_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            watcher = _watcher(root, max_events=2)
            for index in range(4):
                (root / f"f{index}.txt").write_text(str(index), encoding="utf-8")
            watcher.scan(now=NOW)
            drained = watcher.drain()
            self.assertLessEqual(len(drained), 2)

    def test_hidden_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".hidden").write_text("x", encoding="utf-8")
            (root / "visible.txt").write_text("y", encoding="utf-8")
            watcher = _watcher(root)
            events = watcher.scan(now=NOW)
            paths = {event.relative_path for event in events}
            self.assertEqual({"visible.txt"}, paths)

    def test_extension_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("x", encoding="utf-8")
            (root / "b.exe").write_text("y", encoding="utf-8")
            watcher = _watcher(root, allow_extensions=frozenset({".md"}))
            events = watcher.scan(now=NOW)
            paths = {event.relative_path for event in events}
            self.assertEqual({"a.md"}, paths)

    def test_reset_clears_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("x", encoding="utf-8")
            watcher = _watcher(root)
            watcher.scan(now=NOW)
            self.assertEqual(1, len(watcher.drain()))
            watcher.reset()
            (root / "a.txt").write_text("changed", encoding="utf-8")
            events = watcher.scan(now=NOW2)
            self.assertEqual(1, len(events))
            self.assertIs(FileEventKind.CREATED, events[0].kind)


class BuildEvidenceInputTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.watcher = _watcher(Path(self._temporary.name))

    def _event(self, *, path="docs/draft.md", media="text/markdown", digest="a" * 64):
        return FileChangeEvent(
            FileEventKind.MODIFIED,
            path,
            5,
            1,
            digest,
            media,
            NOW,
        )

    def test_document_content_kind_for_text(self):
        evidence = self.watcher.build_evidence_input(
            self._event(),
            task_id="t.1",
            text="draft complete",
            confidence=0.8,
        )
        self.assertIs(EvidenceKind.DOCUMENT_CONTENT, evidence.kind)
        self.assertEqual(1, len(evidence.evidence_refs))
        self.assertEqual("docs/draft.md", evidence.evidence_refs[0].path)

    def test_artifact_kind_for_binary(self):
        evidence = self.watcher.build_evidence_input(
            self._event(path="results/report.pdf", media="application/pdf"),
            task_id="t.1",
            text="report ready",
            confidence=0.9,
        )
        self.assertIs(EvidenceKind.ARTIFACT_FILE, evidence.kind)

    def test_deleted_event_cannot_be_evidence(self):
        deleted = FileChangeEvent(
            FileEventKind.DELETED, "docs/draft.md", 0, 1, "", "text/markdown", NOW,
        )
        with self.assertRaises(ProgressCaptureValidationError):
            self.watcher.build_evidence_input(
                deleted, task_id="t.1", text="gone", confidence=0.5,
            )

    def test_digest_less_event_cannot_be_evidence(self):
        with self.assertRaises(ProgressCaptureValidationError):
            self.watcher.build_evidence_input(
                self._event(digest=""),
                task_id="t.1",
                text="x",
                confidence=0.5,
            )

    def test_invalid_confidence_is_rejected(self):
        with self.assertRaises(ProgressCaptureValidationError):
            self.watcher.build_evidence_input(
                self._event(), task_id="t.1", text="x", confidence=1.5,
            )


class WorkspaceWatcherThreadTests(unittest.TestCase):
    def test_background_thread_collects_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("v1", encoding="utf-8")
            watcher = _watcher(root, poll_interval_sec=0.05)
            watcher.start()
            try:
                deadline = time.monotonic() + 2.0
                events: tuple[FileChangeEvent, ...] = ()
                while time.monotonic() < deadline:
                    events = watcher.drain()
                    if events:
                        break
                    time.sleep(0.05)
                self.assertGreaterEqual(len(events), 1)
                self.assertIs(FileEventKind.CREATED, events[0].kind)
            finally:
                watcher.stop()


if __name__ == "__main__":
    unittest.main()
