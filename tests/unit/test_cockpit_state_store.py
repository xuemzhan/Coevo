"""Unit tests for US-7-AC-3 cockpit state persistence."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.coevo.cockpit import (
    ArtifactSummary,
    CockpitStateStore,
    CockpitValidationError,
    MilestoneSummary,
    RoleView,
    TaskSummary,
    WorkspaceView,
    deserialize_views,
    serialize_views,
)


def _workspace_view() -> WorkspaceView:
    return WorkspaceView(
        project_id="PRJ001",
        display_name="Project One",
        roles=("a.pm", "a.eng"),
        task_count=1,
        milestone_count=1,
        artifact_count=1,
    )


def _role_view() -> RoleView:
    return RoleView(
        role_id="a.eng",
        project_id="PRJ001",
        display_name="Engineering",
        current_tasks=(
            TaskSummary(
                task_id="t.1",
                title="draft spec",
                status="in_progress",
                due_at="2026-09-01",
                assignee_role_id="a.eng",
            ),
        ),
        milestones=(
            MilestoneSummary(
                milestone_id="m.1",
                title="spec review",
                due_at="2026-09-15",
                completed=False,
            ),
        ),
        artifacts=(
            ArtifactSummary(
                path="docs/report.docx",
                role="document",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                size_bytes=128,
                digest_hex="0" * 64,
            ),
        ),
    )


class SerializeViewsTests(unittest.TestCase):
    def test_round_trip_preserves_views(self):
        workspace, roles = deserialize_views(
            serialize_views((_workspace_view(),), (_role_view(),))
        )
        self.assertEqual((_workspace_view(),), workspace)
        self.assertEqual((_role_view(),), roles)

    def test_serialize_rejects_bad_types(self):
        with self.assertRaises(CockpitValidationError):
            serialize_views((_workspace_view(),), "roles")  # type: ignore[arg-type]
        with self.assertRaises(CockpitValidationError):
            serialize_views("workspaces", ())  # type: ignore[arg-type]

    def test_serialize_accepts_empty_views(self):
        workspace, roles = deserialize_views(serialize_views((), ()))
        self.assertEqual((), workspace)
        self.assertEqual((), roles)

    def test_deserialize_rejects_unknown_fields(self):
        payload = serialize_views((_workspace_view(),), (_role_view(),))
        payload["extra"] = 1
        with self.assertRaises(CockpitValidationError):
            deserialize_views(payload)

    def test_deserialize_rejects_unknown_nested_fields(self):
        payload = serialize_views((_workspace_view(),), (_role_view(),))
        payload["workspace_views"][0]["surprise"] = True
        with self.assertRaises(CockpitValidationError):
            deserialize_views(payload)

    def test_deserialize_rejects_wrong_schema(self):
        payload = serialize_views((_workspace_view(),), (_role_view(),))
        payload["schema_version"] = "2.0"
        with self.assertRaises(CockpitValidationError):
            deserialize_views(payload)

    def test_deserialize_rejects_duplicate_keys(self):
        payload = serialize_views((_workspace_view(),), (_role_view(),))
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).replace(
            '"schema_version":"1.0"',
            '"schema_version":"1.0","schema_version":"1.0"',
            1,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.json"
            path.write_text(raw, encoding="utf-8")
            store = CockpitStateStore(path)
            with self.assertRaises(CockpitValidationError):
                store.load()


class CockpitStateStoreTests(unittest.TestCase):
    def test_save_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state" / "cockpit.json"
            store = CockpitStateStore(path)
            store.save((_workspace_view(),), (_role_view(),))
            workspace, roles = store.load()
            self.assertEqual((_workspace_view(),), workspace)
            self.assertEqual((_role_view(),), roles)

    def test_load_missing_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CockpitStateStore(Path(tmp) / "absent.json")
            self.assertIsNone(store.load())

    def test_load_corrupt_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.json"
            path.write_text("{not json", encoding="utf-8")
            store = CockpitStateStore(path)
            with self.assertRaises(CockpitValidationError):
                store.load()

    def test_load_oversized_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.json"
            path.write_text("x" * (4 * 1024 * 1024 + 1), encoding="utf-8")
            store = CockpitStateStore(path)
            with self.assertRaises(CockpitValidationError):
                store.load()

    def test_save_does_not_leave_temporary_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.json"
            store = CockpitStateStore(path)
            store.save((_workspace_view(),), (_role_view(),))
            leftovers = [p for p in Path(tmp).iterdir() if p.name.endswith(".tmp")]
            self.assertEqual([], leftovers)

    def test_save_overwrites_previous_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.json"
            store = CockpitStateStore(path)
            store.save((_workspace_view(),), (_role_view(),))
            store.save((), ())
            workspace, roles = store.load()
            self.assertEqual((), workspace)
            self.assertEqual((), roles)


if __name__ == "__main__":
    unittest.main()
