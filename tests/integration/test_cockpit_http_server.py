"""Integration tests for the US-7-AC-2 real cockpit HTTP server."""
from __future__ import annotations

import json
import socket
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from src.coevo.cockpit import (
    CockpitHttpConfig,
    CockpitHttpServer,
    CockpitValidationError,
    ArtifactSummary,
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


def _request(url, *, token="", headers=None, method="GET", body=None):
    request_headers = dict(headers or {})
    if token:
        request_headers["X-Cockpit-Token"] = token
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        method = "POST"
    request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()


def _raw_request(port: int, payload: bytes) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(payload)
        chunks = []
        while True:
            try:
                data = sock.recv(65536)
            except socket.timeout:
                break
            if not data:
                break
            chunks.append(data)
    return b"".join(chunks)


class CockpitHttpServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.port = _free_port()
        self.server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=self.port,
                request_timeout_sec=3,
                session_timeout_sec=60,
            ),
            workspace_views=(_workspace_view(),),
            role_views=(_role_view(),),
        )
        self.addCleanup(self.server.stop)
        self.server.start()
        self.token = self.server.session_manager.create()
        self.base = f"http://127.0.0.1:{self.port}"

    def test_index_requires_token(self):
        status, _, _ = _request(f"{self.base}/")
        self.assertEqual(401, status)

    def test_index_with_token_serves_page_with_csp(self):
        status, headers, body = _request(f"{self.base}/?token={self.token}")
        self.assertEqual(200, status)
        self.assertIn(b"Coevo Cockpit", body)
        self.assertIn("Content-Security-Policy", headers)
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])

    def test_bearer_authorization_header_is_accepted(self):
        status, _, _ = _request(
            f"{self.base}/api/list_projects",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(200, status)

    def test_list_projects_api(self):
        status, _, body = _request(
            f"{self.base}/api/list_projects",
            token=self.token,
        )
        self.assertEqual(200, status)
        data = json.loads(body)
        self.assertEqual("ok", data["status"])
        self.assertIn("PRJ001", data["payload"]["projects"])

    def test_static_assets_are_served_locally(self):
        for path, expected in (
            ("/static/app.js", "text/javascript"),
            ("/static/style.css", "text/css"),
        ):
            status, headers, body = _request(f"{self.base}{path}", token=self.token)
            self.assertEqual(200, status, path)
            self.assertIn(expected, headers.get("Content-Type", ""))
            self.assertTrue(body)

    def test_static_traversal_is_blocked(self):
        raw = (
            b"GET /static/../index.html HTTP/1.1\r\n"
            b"Host: 127.0.0.1\r\n"
            b"X-Cockpit-Token: " + self.token.encode("ascii") + b"\r\n"
            b"Connection: close\r\n\r\n"
        )
        response = _raw_request(self.port, raw)
        self.assertNotIn(b"200", response.split(b"\r\n", 1)[0])

    def test_host_header_spoof_is_rejected(self):
        raw = (
            b"GET / HTTP/1.1\r\n"
            b"Host: evil.example\r\n"
            b"Connection: close\r\n\r\n"
        )
        response = _raw_request(self.port, raw)
        first_line = response.split(b"\r\n", 1)[0]
        self.assertIn(b"403", first_line)

    def test_wps_open_requires_csrf_headers(self):
        status, _, _ = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            body={"project_id": "PRJ001", "artifact_path": "docs/report.docx", "confirm": True},
        )
        self.assertEqual(403, status)

    def test_wps_open_requires_origin(self):
        status, _, _ = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers={"X-Requested-With": "coevo-cockpit"},
            body={"project_id": "PRJ001", "artifact_path": "docs/report.docx", "confirm": True},
        )
        self.assertEqual(403, status)

    def test_wps_open_requires_double_confirmation(self):
        status, _, _ = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers={
                "Origin": self.base,
                "X-Requested-With": "coevo-cockpit",
            },
            body={"project_id": "PRJ001", "artifact_path": "docs/report.docx", "confirm": False},
        )
        self.assertEqual(403, status)

    def test_wps_open_success_and_audit(self):
        status, _, body = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers={
                "Origin": self.base,
                "X-Requested-With": "coevo-cockpit",
            },
            body={"project_id": "PRJ001", "artifact_path": "docs/report.docx", "confirm": True},
        )
        self.assertEqual(200, status)
        data = json.loads(body)
        self.assertTrue(data["payload"]["ok"])
        records = self.server.recent_audit()
        wps_records = [r for r in records if r["route"] == "wps_open"]
        self.assertGreaterEqual(len(wps_records), 1)
        self.assertEqual(16, len(wps_records[-1]["artifact_path_hash"]))

    def test_unknown_path_is_404(self):
        status, _, _ = _request(f"{self.base}/nope", token=self.token)
        self.assertEqual(404, status)

    def test_malformed_query_is_rejected(self):
        status, _, _ = _request(
            f"{self.base}/api/list_roles?project_id=a&c",
            token=self.token,
        )
        self.assertEqual(400, status)


class CockpitHttpServerTimeoutTests(unittest.TestCase):
    def test_expired_session_is_rejected(self):
        port = _free_port()
        server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=port,
                request_timeout_sec=3,
                session_timeout_sec=1,
            ),
            workspace_views=(_workspace_view(),),
            role_views=(),
        )
        server.start()
        try:
            token = server.session_manager.create()
            base = f"http://127.0.0.1:{port}"
            status, _, _ = _request(f"{base}/api/list_projects", token=token)
            self.assertEqual(200, status)
            time.sleep(1.4)
            status, _, _ = _request(f"{base}/api/list_projects", token=token)
            self.assertEqual(401, status)
        finally:
            server.stop()


class CockpitSingleInstanceTests(unittest.TestCase):
    def test_lock_prevents_second_server(self):
        port = _free_port()
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "cockpit.lock"
            first = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=port,
                    request_timeout_sec=3,
                    lock_path=lock_path,
                ),
                workspace_views=(_workspace_view(),),
                role_views=(),
            )
            first.start()
            try:
                with self.assertRaises(CockpitValidationError):
                    CockpitHttpServer(
                        CockpitHttpConfig(
                            bind_port=_free_port(),
                            request_timeout_sec=3,
                            lock_path=lock_path,
                        ),
                        workspace_views=(_workspace_view(),),
                        role_views=(),
                    )
            finally:
                first.stop()
            self.assertFalse(lock_path.exists())


if __name__ == "__main__":
    unittest.main()
