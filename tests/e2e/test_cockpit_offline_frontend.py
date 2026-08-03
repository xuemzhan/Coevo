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
        return exc.code, dict(exc.headers), exc.read()


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
        self.assertIn("<title>Coevo Cockpit</title>", html)
        self.assertIn('href="/static/style.css"', html)
        self.assertIn('src="/static/app.js"', html)
        csp = headers.get("Content-Security-Policy", "")
        self.assertIn("default-src 'self'", csp)
        self.assertEqual("nosniff", headers.get("X-Content-Type-Options"))

    def test_local_assets_load_and_have_no_external_urls(self):
        for asset in ("/static/style.css", "/static/app.js"):
            status, headers, body = _request(f"{self.base}{asset}", token=self.token)
            self.assertEqual(200, status, asset)
            self.assertEqual("nosniff", headers.get("X-Content-Type-Options"))
            if asset.endswith(".js"):
                text = body.decode("utf-8")
                self.assertNotIn("http://", text)
                self.assertNotIn("https://", text)
                self.assertIn("X-Cockpit-Token", text)
                self.assertIn('"/api/list_projects"', text)

    def test_api_endpoints_drive_the_ui(self):
        status, _, body = _request(f"{self.base}/api/list_projects", token=self.token)
        self.assertEqual(200, status)
        data = json.loads(body)
        self.assertIn("PRJ001", data["payload"]["projects"])

        status, _, body = _request(
            f"{self.base}/api/role_view?project_id=PRJ001&role_id=a.eng",
            token=self.token,
        )
        self.assertEqual(200, status)
        role = json.loads(body)
        self.assertEqual("Engineering", role["payload"]["display_name"])

    def test_unknown_asset_is_not_served(self):
        status, _, _ = _request(f"{self.base}/static/missing.png", token=self.token)
        self.assertEqual(404, status)


if __name__ == "__main__":
    unittest.main()
