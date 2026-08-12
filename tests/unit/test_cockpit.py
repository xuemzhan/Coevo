"""Tests for US-7-AC-1 local cockpit service facade.

Covers AC-1, AC-2, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9 (the ACs in this
slice; AC-3 offline / AC-8 actual subprocess are deferred to US-7-AC-2
and US-7-AC-4). Pure-function tests, no IO.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.cockpit import (
    LOOPBACK_HOST,
    STATIC_ROOT,
    ArtifactSummary,
    CockpitError,
    CockpitFacade,
    CockpitRequest,
    CockpitResponse,
    CockpitResponseStatus,
    CockpitRoute,
    CockpitServerConfig,
    CockpitServerState,
    CockpitValidationError,
    MilestoneSummary,
    RoleView,
    TaskSummary,
    WPSAllowList,
    WorkspaceView,
)


NOW = "2026-08-22T00:00:00Z"
NOW2 = "2026-08-22T00:05:00Z"


def _ws_view() -> WorkspaceView:
    return WorkspaceView(
        project_id="PRJ001",
        display_name="Project One",
        roles=("a.pm", "a.eng"),
        task_count=3,
        milestone_count=2,
        artifact_count=5,
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
                digest_hex="a" * 64,
            ),
        ),
    )


def _state() -> CockpitServerState:
    return CockpitFacade.start_server(
        workspace_views=(_ws_view(),),
        role_views=(_role_view(),),
        now=NOW,
    )


def _req(
    *,
    route: CockpitRoute,
    project_id: str = "PRJ001",
    role_id: str = "a.eng",
    task_id: str = "",
    artifact_path: str = "",
    ts: str = NOW2,
) -> CockpitRequest:
    return CockpitRequest(
        route=route,
        project_id=project_id,
        role_id=role_id,
        task_id=task_id,
        artifact_path=artifact_path,
        ts=ts,
    )


# ---------------------------------------------------------------------------
# AC-1 loopback binding
# ---------------------------------------------------------------------------


class LoopbackBindingTests(unittest.TestCase):
    def test_start_server_rejects_non_loopback_bind(self):
        with self.assertRaises(CockpitValidationError):
            CockpitFacade.start_server(bind_host="0.0.0.0", now=NOW)
        with self.assertRaises(CockpitValidationError):
            CockpitFacade.start_server(bind_host="10.0.0.1", now=NOW)

    def test_start_server_accepts_loopback(self):
        state = CockpitFacade.start_server(now=NOW)
        self.assertEqual(LOOPBACK_HOST, state.config.bind_host)


# ---------------------------------------------------------------------------
# AC-2 static root
# ---------------------------------------------------------------------------


class StaticRootTests(unittest.TestCase):
    def test_start_server_rejects_external_static_root(self):
        external = Path("C:/Windows/Temp")
        with self.assertRaises(CockpitValidationError):
            CockpitFacade.start_server(static_root=external, now=NOW)

    def test_start_server_accepts_default_static_root(self):
        state = CockpitFacade.start_server(now=NOW)
        # Resolved static_root must be inside STATIC_ROOT.
        self.assertTrue(
            state.config.static_root.resolve().is_relative_to(STATIC_ROOT.resolve())
        )

    def test_static_root_constant_points_to_module_static(self):
        self.assertTrue(STATIC_ROOT.is_dir() or STATIC_ROOT.parent.exists())


# ---------------------------------------------------------------------------
# AC-5 list projects
# ---------------------------------------------------------------------------


class ListProjectsTests(unittest.TestCase):
    def test_dispatch_list_projects_returns_workspace_views(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.LIST_PROJECTS, project_id=""),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.OK, r.status)
        self.assertIn("<li>PRJ001</li>", r.body_html)
        self.assertEqual(("PRJ001",), r.payload["projects"])
        # 前端需要视图元数据来渲染项目名称与角色入口。
        self.assertEqual(1, r.payload["count"])
        self.assertEqual(1, len(r.payload["views"]))
        view = r.payload["views"][0]
        self.assertEqual("PRJ001", view["project_id"])
        self.assertEqual("Project One", view["display_name"])
        self.assertEqual(("a.pm", "a.eng"), view["roles"])
        self.assertEqual(3, view["task_count"])
        self.assertEqual([], view["trace"])
        self.assertEqual([], view["activity"])
        self.assertEqual("", view["package_path"])
        self.assertEqual("", view["package_digest"])
        self.assertEqual("", view["knowledge_bundle_id"])


# ---------------------------------------------------------------------------
# AC-6 list roles + role view
# ---------------------------------------------------------------------------


class RoleViewTests(unittest.TestCase):
    def test_dispatch_list_roles_unknown_project_returns_not_found(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.LIST_ROLES, project_id="NOPE"),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.NOT_FOUND, r.status)

    def test_dispatch_list_roles_known_project_returns_role_ids(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.LIST_ROLES),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.OK, r.status)
        self.assertEqual(("a.pm", "a.eng"), r.payload["roles"])

    def test_dispatch_role_view_unknown_role_returns_not_found(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.ROLE_VIEW, role_id="a.unknown"),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.NOT_FOUND, r.status)

    def test_dispatch_role_view_known_role_returns_summary(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.ROLE_VIEW),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.OK, r.status)
        self.assertEqual(1, r.payload["task_count"])
        self.assertEqual(1, r.payload["milestone_count"])
        self.assertEqual(1, r.payload["artifact_count"])
        # 前端下钻需要明细列表，不只是计数。
        self.assertEqual("draft spec", r.payload["current_tasks"][0]["title"])
        self.assertEqual("in_progress", r.payload["current_tasks"][0]["status"])
        self.assertEqual("spec review", r.payload["milestones"][0]["title"])
        self.assertEqual(
            "docs/report.docx", r.payload["artifacts"][0]["path"]
        )


# ---------------------------------------------------------------------------
# AC-7 task view + milestone view
# ---------------------------------------------------------------------------


class TaskMilestoneViewTests(unittest.TestCase):
    def test_dispatch_task_view_unknown_returns_not_found(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.TASK_VIEW, task_id="t.NOPE"),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.NOT_FOUND, r.status)

    def test_dispatch_task_view_known_returns_summary(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.TASK_VIEW, task_id="t.1"),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.OK, r.status)
        self.assertEqual("draft spec", r.payload["title"])
        self.assertEqual("in_progress", r.payload["status"])

    def test_dispatch_milestone_view_known_returns_summary(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.MILESTONE_VIEW, task_id="m.1"),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.OK, r.status)
        self.assertEqual("spec review", r.payload["title"])
        self.assertFalse(r.payload["completed"])


# ---------------------------------------------------------------------------
# AC-8 WPS allow-list
# ---------------------------------------------------------------------------


class WPSOpenTests(unittest.TestCase):
    def _fake_launcher(self, decision="ok", detail="", returncode=0):
        from src.coevo.cockpit.wps import WpsLaunchDecision, WpsLaunchResult

        class _Fake:
            def launch(self, artifact_path):
                return WpsLaunchResult(
                    WpsLaunchDecision(decision),
                    "h" * 16,
                    detail,
                    returncode,
                )

        return _Fake()

    def test_dispatch_wps_open_without_launcher_reports_not_available(self):
        # REVIEW2-4: the facade must not claim the document was opened
        # when no launcher is configured -- NOT_AVAILABLE, not OK.
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.WPS_OPEN, artifact_path="docs/report.docx"),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.NOT_AVAILABLE, r.status)
        self.assertEqual("not_available", r.payload["decision"])

    def test_dispatch_wps_open_launcher_ok_maps_to_started(self):
        for ext in (".docx", ".doc", ".xlsx", ".pptx", ".pdf"):
            r = CockpitFacade.dispatch(
                _req(route=CockpitRoute.WPS_OPEN, artifact_path=f"docs/report{ext}"),
                server_state=_state(),
                now=NOW2,
                wps_launcher=self._fake_launcher(decision="ok", returncode=0),
            )
            self.assertEqual(
                CockpitResponseStatus.STARTED,
                r.status,
                f"expected STARTED for {ext}, got {r.status.value}",
            )
            self.assertEqual("started", r.payload["decision"])
            self.assertEqual(0, r.payload["returncode"])

    def test_dispatch_wps_open_launcher_denied_maps_to_denied(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.WPS_OPEN, artifact_path="docs/report.docx"),
            server_state=_state(),
            now=NOW2,
            wps_launcher=self._fake_launcher(
                decision="denied", detail="extension not in WPS allow-list"
            ),
        )
        self.assertEqual(CockpitResponseStatus.DENIED, r.status)
        self.assertEqual("denied", r.payload["decision"])

    def test_dispatch_wps_open_launcher_not_available_maps_to_not_available(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.WPS_OPEN, artifact_path="docs/report.docx"),
            server_state=_state(),
            now=NOW2,
            wps_launcher=self._fake_launcher(
                decision="not_available", detail="executable unavailable"
            ),
        )
        self.assertEqual(CockpitResponseStatus.NOT_AVAILABLE, r.status)
        self.assertEqual("not_available", r.payload["decision"])

    def test_dispatch_wps_open_launcher_error_maps_to_error(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.WPS_OPEN, artifact_path="docs/report.docx"),
            server_state=_state(),
            now=NOW2,
            wps_launcher=self._fake_launcher(
                decision="error", detail="launch failed", returncode=1
            ),
        )
        self.assertEqual(CockpitResponseStatus.ERROR, r.status)
        self.assertEqual("failed", r.payload["decision"])

    def test_dispatch_wps_open_launcher_raise_fails_closed(self):
        class _Raising:
            def launch(self, artifact_path):
                raise RuntimeError("launcher down")

        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.WPS_OPEN, artifact_path="docs/report.docx"),
            server_state=_state(),
            now=NOW2,
            wps_launcher=_Raising(),
        )
        self.assertEqual(CockpitResponseStatus.ERROR, r.status)
        self.assertEqual("failed", r.payload["decision"])

    def test_dispatch_wps_open_denied_extension_rejected(self):
        for ext in (".exe", ".bat", ".ps1", ".js", ".vbs", ".scr", ".jar"):
            r = CockpitFacade.dispatch(
                _req(route=CockpitRoute.WPS_OPEN, artifact_path=f"bin/payload{ext}"),
                server_state=_state(),
                now=NOW2,
            )
            self.assertEqual(
                CockpitResponseStatus.DENIED,
                r.status,
                f"expected DENIED for {ext}, got {r.status.value}",
            )

    def test_dispatch_wps_open_path_traversal_rejected(self):
        # Path traversal is caught at CockpitRequest construction.
        from src.coevo.cockpit import CockpitValidationError
        with self.assertRaises(CockpitValidationError):
            _req(route=CockpitRoute.WPS_OPEN, artifact_path="../escape.docx")

    def test_dispatch_wps_open_missing_artifact_path_returns_bad_request(self):
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.WPS_OPEN, artifact_path=""),
            server_state=_state(),
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.BAD_REQUEST, r.status)

    def test_allow_list_helper_rejects_known_bad_extensions(self):
        for path in ("x.exe", "x.bat", "x.ps1", "x.sh", "x.js"):
            self.assertFalse(WPSAllowList.is_allowed(path), f"expected deny for {path}")
        for path in ("x.docx", "x.xlsx", "x.pptx", "x.pdf"):
            self.assertTrue(WPSAllowList.is_allowed(path), f"expected allow for {path}")


class PendingConfirmTests(unittest.TestCase):
    """PENDING_CONFIRM 路由：fail-closed，未配置处理器时不可用。"""

    def _dispatch(self, action: str, handler=None):
        return CockpitFacade.dispatch(
            _req(route=CockpitRoute.PENDING_CONFIRM, artifact_path=action),
            server_state=_state(),
            now=NOW2,
            pending_action_handler=handler,
        )

    def test_without_handler_reports_not_available(self):
        r = self._dispatch("confirm")
        self.assertEqual(CockpitResponseStatus.NOT_AVAILABLE, r.status)
        self.assertEqual("not_available", r.payload["decision"])

    def test_approve_maps_to_started(self):
        r = self._dispatch(
            "confirm",
            handler=lambda action: {"decision": "approved"},
        )
        self.assertEqual(CockpitResponseStatus.STARTED, r.status)
        self.assertEqual("approved", r.payload["decision"])

    def test_reject_maps_to_denied(self):
        r = self._dispatch(
            "reject",
            handler=lambda action: {"decision": "rejected"},
        )
        self.assertEqual(CockpitResponseStatus.DENIED, r.status)
        self.assertEqual("rejected", r.payload["decision"])

    def test_invalid_action_is_rejected(self):
        r = self._dispatch(
            "maybe",
            handler=lambda action: {"decision": "approved"},
        )
        self.assertEqual(CockpitResponseStatus.BAD_REQUEST, r.status)

    def test_handler_exception_fails_closed(self):
        def boom(action):
            raise RuntimeError("handler down")

        r = self._dispatch("confirm", handler=boom)
        self.assertEqual(CockpitResponseStatus.ERROR, r.status)
        self.assertEqual("failed", r.payload["decision"])


# ---------------------------------------------------------------------------
# AC-1 fail-closed at dispatch time
# ---------------------------------------------------------------------------


class NotBoundTests(unittest.TestCase):
    def test_cockpit_server_config_rejects_non_loopback_bind_at_construction(self):
        # AC-1 fail-closed: CockpitServerConfig itself rejects non-loopback
        # bind_host at construction time. This is the primary defense;
        # dispatch-time NOT_BOUND is a secondary guard (see dispatch()).
        with self.assertRaises(CockpitValidationError):
            CockpitServerConfig(
                bind_host="0.0.0.0",
                bind_port=12701,
                static_root=STATIC_ROOT,
                max_request_bytes=65536,
                request_timeout_sec=5,
            )

    def test_dispatch_returns_not_bound_via_dispatch_time_guard(self):
        # Build a valid state, then simulate a tampered bind_host by
        # constructing CockpitServerConfig via object.__new__ (bypassing
        # __post_init__), so dispatch-time NOT_BOUND is exercised.
        cfg = CockpitServerConfig.__new__(CockpitServerConfig)
        object.__setattr__(cfg, "bind_host", "0.0.0.0")
        object.__setattr__(cfg, "bind_port", 12701)
        object.__setattr__(cfg, "static_root", STATIC_ROOT)
        object.__setattr__(cfg, "max_request_bytes", 65536)
        object.__setattr__(cfg, "request_timeout_sec", 5)
        state = CockpitServerState.__new__(CockpitServerState)
        object.__setattr__(state, "config", cfg)
        object.__setattr__(state, "workspace_views", ())
        object.__setattr__(state, "role_views", ())
        object.__setattr__(state, "started_at", NOW)
        r = CockpitFacade.dispatch(
            _req(route=CockpitRoute.LIST_PROJECTS, project_id=""),
            server_state=state,
            now=NOW2,
        )
        self.assertEqual(CockpitResponseStatus.NOT_BOUND, r.status)


# ---------------------------------------------------------------------------
# AC-7 audit projection
# ---------------------------------------------------------------------------


class AuditProjectionTests(unittest.TestCase):
    def test_to_audit_record_excludes_sensitive_body(self):
        req = _req(route=CockpitRoute.WPS_OPEN, artifact_path="docs/report.docx")
        r = CockpitFacade.dispatch(
            req, server_state=_state(), now=NOW2
        )
        record = CockpitFacade.to_audit_record(req, r)
        self.assertEqual(record, json.loads(json.dumps(record)))
        # body_html / artifact_path MUST NOT appear in the audit row.
        serialized = json.dumps(record)
        self.assertNotIn("<p>WPS open", serialized)
        self.assertNotIn("docs/report.docx", serialized)
        # 16-char hash for artifact_path_hash.
        self.assertEqual(16, len(record["artifact_path_hash"]))
        # Metadata fields.
        self.assertEqual("coevo.cockpit", record["domain"])
        self.assertEqual("1.0", record["schema_version"])


class PureFunctionTests(unittest.TestCase):
    def test_pure_function_determinism_same_request_same_response(self):
        state = _state()
        a = CockpitFacade.dispatch(
            _req(route=CockpitRoute.LIST_PROJECTS, project_id=""),
            server_state=state,
            now=NOW2,
        )
        b = CockpitFacade.dispatch(
            _req(route=CockpitRoute.LIST_PROJECTS, project_id=""),
            server_state=state,
            now=NOW2,
        )
        self.assertEqual(a.body_html, b.body_html)
        self.assertEqual(a.payload, b.payload)
        self.assertEqual(a.status, b.status)


if __name__ == "__main__":
    unittest.main()
