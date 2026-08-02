"""Integration tests for US-7-AC-3 cockpit state persistence."""
from __future__ import annotations

import socket
import tempfile
import unittest
from pathlib import Path

from src.coevo.cockpit import (
    ArtifactSummary,
    CockpitHttpConfig,
    CockpitHttpServer,
    CockpitValidationError,
    MilestoneSummary,
    RoleView,
    TaskSummary,
    WorkspaceView,
)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _workspace_view() -> WorkspaceView:
    return WorkspaceView(
        project_id="PRJ001",
        display_name="Project One",
        roles=("a.eng",),
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
        milestones=(),
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


class CockpitStatePersistenceTests(unittest.TestCase):
    def test_state_saved_on_stop_and_loaded_on_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "cockpit-state.json"
            port = _free_port()
            first = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=port,
                    request_timeout_sec=3,
                    state_path=state_path,
                ),
                workspace_views=(_workspace_view(),),
                role_views=(_role_view(),),
            )
            first.start()
            first.stop()
            self.assertTrue(state_path.exists())

            second = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=_free_port(),
                    request_timeout_sec=3,
                    state_path=state_path,
                ),
            )
            second.start()
            try:
                self.assertEqual(
                    (_workspace_view(),),
                    second.state.workspace_views,
                )
                self.assertEqual((_role_view(),), second.state.role_views)
            finally:
                second.stop()

    def test_explicit_views_override_persisted_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "cockpit-state.json"
            first = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=_free_port(),
                    request_timeout_sec=3,
                    state_path=state_path,
                ),
                workspace_views=(_workspace_view(),),
                role_views=(_role_view(),),
            )
            first.start()
            first.stop()
            other = WorkspaceView(
                project_id="PRJ999",
                display_name="Other",
                roles=(),
                task_count=0,
                milestone_count=0,
                artifact_count=0,
            )
            second = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=_free_port(),
                    request_timeout_sec=3,
                    state_path=state_path,
                ),
                workspace_views=(other,),
                role_views=(),
            )
            second.start()
            try:
                self.assertEqual((other,), second.state.workspace_views)
            finally:
                second.stop()

    def test_corrupt_state_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "cockpit-state.json"
            state_path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(CockpitValidationError):
                CockpitHttpServer(
                    CockpitHttpConfig(
                        bind_port=_free_port(),
                        request_timeout_sec=3,
                        state_path=state_path,
                    ),
                )


if __name__ == "__main__":
    unittest.main()
