"""REVIEW2-5: cockpit HTTP full-path authentication black-box matrix.

Contract (docs/architecture/http-auth-matrix.md): every write path must
require session + CSRF (X-Requested-With) + Origin + explicit confirmation,
and Host spoofing, expired sessions and revoked-token replays must be
rejected -- measured over the real HTTP server, not just the facade.
"""

from __future__ import annotations

import json
import socket
import time
import unittest
import urllib.error
import urllib.request

from src.coevo.cockpit import (
    ArtifactSummary,
    CockpitHttpConfig,
    CockpitHttpServer,
    RoleView,
    WorkspaceView,
)
from src.coevo.cockpit.wps import WpsLaunchDecision, WpsLaunchResult


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
        current_tasks=(),
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


class _FakeLauncher:
    def launch(self, artifact_path: str) -> WpsLaunchResult:
        return WpsLaunchResult(WpsLaunchDecision.OK, "h" * 16, "launched", 0)


def _request(url, *, token="", headers=None, method="GET", body=None):
    request_headers = dict(headers or {})
    if token:
        request_headers["X-Cockpit-Token"] = token
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        method = "POST"
    request = urllib.request.Request(
        url, data=data, headers=request_headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, exc.read()
        finally:
            exc.close()


def _raw_request(port: int, raw: bytes) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=10) as sock:
        sock.sendall(raw)
        chunks = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
    return b"".join(chunks)


def _wps_body() -> dict[str, object]:
    return {
        "project_id": "PRJ001",
        "artifact_path": "docs/report.docx",
        "confirm": True,
    }


class HttpAuthMatrixTests(unittest.TestCase):
    """Black-box matrix over the real HTTP server (REVIEW2-5)."""

    def setUp(self) -> None:
        self.port = _free_port()
        self.server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=self.port,
                request_timeout_sec=3,
                session_timeout_sec=60,
                lock_path=None,
            ),
            workspace_views=(_workspace_view(),),
            role_views=(_role_view(),),
            wps_launcher=_FakeLauncher(),
        )
        self.addCleanup(self.server.stop)
        self.server.start()
        self.token = self.server.session_manager.create()
        self.base = f"http://127.0.0.1:{self.port}"

    def _write_headers(self):
        return {
            "Origin": self.base,
            "X-Requested-With": "coevo-cockpit",
        }

    def test_authenticated_write_with_csrf_origin_confirm_succeeds(self) -> None:
        status, body = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers=self._write_headers(),
            body=_wps_body(),
        )
        self.assertEqual(200, status)
        self.assertEqual("started", json.loads(body)["payload"]["decision"])

    def test_unauthenticated_write_is_rejected(self) -> None:
        status, _ = _request(
            f"{self.base}/api/wps_open",
            headers=self._write_headers(),
            body=_wps_body(),
        )
        self.assertIn(status, (401, 403))

    def test_wrong_host_on_write_is_rejected(self) -> None:
        body = json.dumps(_wps_body()).encode("utf-8")
        raw = (
            b"POST /api/wps_open HTTP/1.1\r\n"
            b"Host: evil.example\r\n"
            + f"Content-Length: {len(body)}\r\n".encode("ascii")
            + f"X-Cockpit-Token: {self.token}\r\n".encode("ascii")
            + f"Origin: {self.base}\r\n".encode("ascii")
            + b"X-Requested-With: coevo-cockpit\r\n"
            + b"Connection: close\r\n\r\n"
            + body
        )
        response = _raw_request(self.port, raw)
        first_line = response.split(b"\r\n", 1)[0]
        self.assertIn(b"403", first_line)

    def test_write_requires_csrf_and_origin_together(self) -> None:
        # X-Requested-With without Origin.
        status, _ = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers={"X-Requested-With": "coevo-cockpit"},
            body=_wps_body(),
        )
        self.assertEqual(403, status)
        # Origin without X-Requested-With.
        status, _ = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers={"Origin": self.base},
            body=_wps_body(),
        )
        self.assertEqual(403, status)

    def test_write_without_explicit_confirmation_is_rejected(self) -> None:
        body = dict(_wps_body())
        body["confirm"] = False
        status, _ = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers=self._write_headers(),
            body=body,
        )
        self.assertEqual(403, status)

    def test_expired_session_write_is_rejected(self) -> None:
        port = _free_port()
        server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=port,
                request_timeout_sec=3,
                session_timeout_sec=1,
                lock_path=None,
            ),
            workspace_views=(_workspace_view(),),
            role_views=(_role_view(),),
            wps_launcher=_FakeLauncher(),
        )
        self.addCleanup(server.stop)
        server.start()
        base = f"http://127.0.0.1:{port}"
        token = server.session_manager.create()
        status, _ = _request(
            f"{base}/api/wps_open",
            token=token,
            headers={"Origin": base, "X-Requested-With": "coevo-cockpit"},
            body=_wps_body(),
        )
        self.assertEqual(200, status)
        time.sleep(1.4)
        status, _ = _request(
            f"{base}/api/wps_open",
            token=token,
            headers={"Origin": base, "X-Requested-With": "coevo-cockpit"},
            body=_wps_body(),
        )
        self.assertEqual(401, status)

    def test_replayed_write_token_after_revoke_is_rejected(self) -> None:
        status, _ = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers=self._write_headers(),
            body=_wps_body(),
        )
        self.assertEqual(200, status)
        self.assertTrue(self.server.session_manager.revoke(self.token))
        status, _ = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers=self._write_headers(),
            body=_wps_body(),
        )
        self.assertEqual(401, status)


if __name__ == "__main__":
    unittest.main()
