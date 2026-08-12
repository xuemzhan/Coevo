"""Offline frontend E2E for the cockpit (HTTP + static policy checks).

Real-browser automation is not available in this session, so this suite
verifies the offline contract a browser would rely on:

* the index page is served with the local asset links and a strict CSP;
* every static asset loads locally (200, no CDN/external URLs);
* the API endpoints the JavaScript calls return the expected JSON;
* the served JavaScript never references external network locations.
"""
from __future__ import annotations

import json
import socket
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from src.coevo.cockpit import (
    ArtifactSummary,
    CockpitHttpConfig,
    CockpitHttpServer,
    MilestoneSummary,
    RoleView,
    TaskSummary,
    WorkspaceView,
)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _request(url, *, token=""):
    headers = {"X-Cockpit-Token": token} if token else {}
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, dict(exc.headers), exc.read()
        finally:
            # REVIEW-FIX-3 (M-1): close the error response so the suite
            # never leaves unclosed HTTPError resources behind.
            exc.close()


class OfflineFrontendTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.port = _free_port()
        workspace_view = WorkspaceView(
            "PRJ001", "Offline Project", ("a.eng",), 1, 1, 1
        )
        role_view = RoleView(
            "a.eng",
            "PRJ001",
            "Engineering",
            (
                TaskSummary(
                    "t.1", "draft spec", "in_progress", "2026-09-01", "a.eng"
                ),
            ),
            (MilestoneSummary("m.1", "review", "2026-09-15", False),),
            (
                ArtifactSummary(
                    "docs/report.docx",
                    "document",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    128,
                    "0" * 64,
                ),
            ),
        )
        self.server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=self.port,
                request_timeout_sec=5,
                lock_path=None,
            ),
            workspace_views=(workspace_view,),
            role_views=(role_view,),
        )
        self.addCleanup(self.server.stop)
        self.server.start()
        self.token = self.server.session_manager.create()
        self.base = f"http://127.0.0.1:{self.port}"

    def test_index_serves_local_page_with_csp(self):
        status, headers, body = _request(f"{self.base}/?token={self.token}")
        self.assertEqual(200, status)
        html = body.decode("utf-8")
        self.assertIn("<title>Coevo 驾驶舱</title>", html)
        self.assertIn('lang="zh-CN"', html)
        self.assertIn('href="/static/style.css"', html)
        self.assertIn('src="/static/app.js"', html)
        self.assertIn('id="trace-panel"', html)
        self.assertIn('id="activity-panel"', html)
        self.assertIn('id="copy-url-btn"', html)
        self.assertIn('id="health-info"', html)
        self.assertIn('id="sidebar-hint"', html)
        self.assertIn('id="login-panel"', html)
        self.assertIn('id="token-input"', html)
        self.assertIn('id="relogin-btn"', html)
        self.assertIn('id="login-message"', html)
        self.assertIn('id="task-filter"', html)
        self.assertIn('id="pending-badge"', html)
        self.assertIn('id="global-pending"', html)
        # 中文界面：项目/刷新等入口必须在页面上。
        self.assertIn("刷新", html)
        self.assertIn("项目", html)
        csp = headers.get("Content-Security-Policy", "")
        self.assertIn("default-src 'self'", csp)
        self.assertEqual("nosniff", headers.get("X-Content-Type-Options"))
        # REVIEW-FIX-3 (L-3): the token-bearing index response must not be
        # cached nor leak the token through the referrer/history.
        self.assertEqual("no-store", headers.get("Cache-Control"))
        self.assertEqual("no-referrer", headers.get("Referrer-Policy"))

    def test_local_assets_load_and_have_no_external_urls(self):
        for asset in ("/static/style.css", "/static/app.js"):
            status, headers, body = _request(f"{self.base}{asset}", token=self.token)
            self.assertEqual(200, status, asset)
            self.assertEqual("nosniff", headers.get("X-Content-Type-Options"))
            # REVIEW-FIX-3 (L-2): text assets carry an explicit charset.
            self.assertIn("charset=utf-8", headers.get("Content-Type", ""))
            if asset.endswith(".js"):
                text = body.decode("utf-8")
                self.assertNotIn("http://", text)
                self.assertNotIn("https://", text)
                self.assertIn("X-Cockpit-Token", text)
                self.assertIn('"/api/list_projects"', text)

    def test_frontend_wires_role_switch_refresh_and_task_detail(self):
        # 前端必须接线角色切换（/api/list_roles + /api/role_view）、
        # 任务下钻（任务行点击）与刷新（/api/list_projects 轮询）。
        status, _, body = _request(f"{self.base}/static/app.js", token=self.token)
        self.assertEqual(200, status)
        text = body.decode("utf-8")
        self.assertIn('"/api/list_roles?project_id="', text)
        self.assertIn('"/api/role_view?project_id="', text)
        self.assertIn("renderRoleTabs", text)
        self.assertIn("openTaskDetail", text)
        self.assertIn("REFRESH_INTERVAL_MS", text)
        self.assertIn("refresh-btn", text)
        self.assertIn("confirmWpsOpen", text)
        self.assertIn("renderTrace", text)
        self.assertIn("待人工确认", text)
        self.assertIn("renderActivity", text)
        self.assertIn("审计动态", text)
        self.assertIn("renderPackageSummary", text)
        self.assertIn("copyCockpitUrl", text)
        self.assertIn("loadHealth", text)
        self.assertIn("roleCounts", text)
        self.assertIn("readHashState", text)
        self.assertIn("pushHash", text)
        self.assertIn('hashchange', text)
        self.assertIn("formatDate", text)
        self.assertIn("isWpsOpenable", text)
        self.assertIn("formatBytes", text)
        self.assertIn("roleLabel", text)
        self.assertIn("不支持 WPS 打开", text)
        self.assertIn("会话已过期", text)
        self.assertIn("project-counts", text)
        self.assertIn(".sort(", text)
        self.assertIn("renderTaskRow", text)
        self.assertIn("token-form", text)
        self.assertIn("验证中…", text)
        self.assertIn("令牌无效，请检查后重试", text)
        self.assertIn("activity-seq", text)
        self.assertIn("activity-hash", text)
        self.assertIn("milestoneProgress", text)
        self.assertIn("milestone-row", text)
        self.assertIn("formatRelative", text)
        self.assertIn('Escape', text)
        self.assertIn("handleAuthError", text)
        self.assertIn("showLoginPanel", text)
        self.assertIn("会话已过期，请重新连接", text)
        self.assertIn("openMilestoneDetail", text)
        self.assertIn("没有符合筛选条件的任务", text)
        self.assertIn("renderPendingBadge", text)
        self.assertIn("applyProjectsPayload", text)
        self.assertIn("submitPendingAction", text)
        self.assertIn('"/api/pending_confirm"', text)
        self.assertIn("has-pending", text)
        self.assertIn("无待确认事项", text)
        self.assertIn("copyText", text)
        self.assertIn("路径已复制", text)
        self.assertIn('event.key === "Enter"', text)
        # 复制地址必须带上当前视图 hash，方便分享深链。
        copy_idx = text.find("function copyCockpitUrl")
        copy_segment = text[copy_idx:copy_idx + 400]
        self.assertIn("location.hash", copy_segment)

    def test_api_endpoints_drive_the_ui(self):
        status, _, body = _request(f"{self.base}/api/list_projects", token=self.token)
        self.assertEqual(200, status)
        data = json.loads(body)
        self.assertIn("PRJ001", data["payload"]["projects"])
        self.assertEqual(1, len(data["payload"]["views"]))
        self.assertEqual("Offline Project", data["payload"]["views"][0]["display_name"])
        self.assertEqual(["a.eng"], data["payload"]["views"][0]["roles"])

        status, _, body = _request(
            f"{self.base}/api/role_view?project_id=PRJ001&role_id=a.eng",
            token=self.token,
        )
        self.assertEqual(200, status)
        role = json.loads(body)
        self.assertEqual("Engineering", role["payload"]["display_name"])
        self.assertEqual(1, role["payload"]["task_count"])
        self.assertEqual("draft spec", role["payload"]["current_tasks"][0]["title"])
        self.assertEqual(
            "docs/report.docx", role["payload"]["artifacts"][0]["path"]
        )

    def test_unknown_asset_is_not_served(self):
        status, _, _ = _request(f"{self.base}/static/missing.png", token=self.token)
        self.assertEqual(404, status)


if __name__ == "__main__":
    unittest.main()
