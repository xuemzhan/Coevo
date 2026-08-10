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
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, dict(exc.headers), exc.read()
        finally:
            exc.close()


def _raw_request(port: int, payload: bytes) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=20) as sock:
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
                lock_path=None,
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

    def test_healthz_is_unauthenticated_and_ok(self):
        status, _, body = _request(f"{self.base}/healthz")
        self.assertEqual(200, status)
        data = json.loads(body)
        self.assertEqual("ok", data["status"])
        self.assertEqual("coevo-cockpit", data["service"])
        self.assertIn("uptime_sec", data)

    def test_api_health_requires_token(self):
        status, _, _ = _request(f"{self.base}/api/health")
        self.assertEqual(401, status)

    def test_api_health_returns_in_process_status(self):
        status, headers, body = _request(
            f"{self.base}/api/health", token=self.token
        )
        self.assertEqual(200, status)
        data = json.loads(body)
        self.assertTrue(data["service"])
        for field in (
            "service",
            "version",
            "started_at",
            "uptime_sec",
            "session_count",
            "request_count",
            "probe_count",
            "rejected_count",
            "audit_records",
            "log_errors",
        ):
            self.assertIn(field, data, field)
        self.assertGreaterEqual(data["request_count"], 1)
        self.assertGreaterEqual(data["session_count"], 1)
        self.assertGreaterEqual(data["probe_count"], 0)
        self.assertGreaterEqual(data["rejected_count"], 0)
        # API payloads stay uncacheable and never leak the URL token via
        # the browser referrer (same hardening as the index response).
        self.assertEqual("no-store", headers.get("Cache-Control"))
        self.assertEqual("no-referrer", headers.get("Referrer-Policy"))

    def test_healthz_probes_counted_separately_from_requests(self):
        for _ in range(2):
            status, _, _ = _request(f"{self.base}/healthz")
            self.assertEqual(200, status)
        status, _, body = _request(f"{self.base}/api/health", token=self.token)
        self.assertEqual(200, status)
        first = json.loads(body)
        self.assertGreaterEqual(first["probe_count"], 2)
        # /healthz probes never count as authenticated requests.
        status, _, body = _request(f"{self.base}/api/health", token=self.token)
        second = json.loads(body)
        self.assertEqual(second["probe_count"], first["probe_count"])
        self.assertGreater(second["request_count"], first["request_count"])

    def test_index_with_token_serves_page_with_csp(self):
        status, headers, body = _request(f"{self.base}/?token={self.token}")
        self.assertEqual(200, status)
        self.assertIn(b"Coevo Cockpit", body)
        self.assertIn("Content-Security-Policy", headers)
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        # REVIEW-FIX-3 (L-3): the index response must never be cached or
        # leak the URL token via the browser referrer/history.
        self.assertEqual("no-store", headers.get("Cache-Control"))
        self.assertEqual("no-referrer", headers.get("Referrer-Policy"))

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
            # REVIEW-FIX-3 (L-2): text assets must carry an explicit charset;
            # non-text assets must not gain a charset parameter.
            self.assertIn("charset=utf-8", headers.get("Content-Type", ""))
            # Static assets opt into a bounded public cache but still never
            # leak their URL through the browser referrer.
            self.assertEqual(
                "public, max-age=300", headers.get("Cache-Control"), path
            )
            self.assertEqual("no-referrer", headers.get("Referrer-Policy"), path)
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
        # REVIEW2-4: a configured launcher yields STARTED (200) with real
        # launch semantics instead of the old render stub.
        from src.coevo.cockpit.wps import WpsLaunchDecision, WpsLaunchResult

        class _FakeLauncher:
            def launch(self, artifact_path):
                return WpsLaunchResult(
                    WpsLaunchDecision.OK, "h" * 16, "launched", 0
                )

        launcher_port = _free_port()
        launcher_server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=launcher_port,
                request_timeout_sec=3,
                session_timeout_sec=60,
                lock_path=None,
            ),
            workspace_views=(_workspace_view(),),
            role_views=(_role_view(),),
            wps_launcher=_FakeLauncher(),
        )
        self.addCleanup(launcher_server.stop)
        launcher_server.start()
        base = f"http://127.0.0.1:{launcher_port}"
        token = launcher_server.session_manager.create()
        status, _, body = _request(
            f"{base}/api/wps_open",
            token=token,
            headers={
                "Origin": base,
                "X-Requested-With": "coevo-cockpit",
            },
            body={"project_id": "PRJ001", "artifact_path": "docs/report.docx", "confirm": True},
        )
        self.assertEqual(200, status)
        data = json.loads(body)
        self.assertEqual("started", data["payload"]["decision"])
        records = launcher_server.recent_audit()
        wps_records = [r for r in records if r["route"] == "wps_open"]
        self.assertGreaterEqual(len(wps_records), 1)
        self.assertEqual(16, len(wps_records[-1]["artifact_path_hash"]))

    def test_wps_open_without_launcher_reports_not_available(self):
        # REVIEW2-4: without a configured launcher the server must not claim
        # the document was opened -- 503 NOT_AVAILABLE.
        status, _, body = _request(
            f"{self.base}/api/wps_open",
            token=self.token,
            headers={
                "Origin": self.base,
                "X-Requested-With": "coevo-cockpit",
            },
            body={"project_id": "PRJ001", "artifact_path": "docs/report.docx", "confirm": True},
        )
        self.assertEqual(503, status)
        data = json.loads(body)
        self.assertEqual("not_available", data["payload"]["decision"])

    def test_abrupt_client_disconnect_does_not_break_server(self):
        # A client that opens a connection and vanishes mid-request must not
        # wedge the listener: the next well-formed request still succeeds.
        with socket.create_connection(("127.0.0.1", self.port), timeout=5) as sock:
            sock.sendall(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n")
        status, _, body = _request(f"{self.base}/api/list_projects", token=self.token)
        self.assertEqual(200, status)
        self.assertIn(b"PRJ001", body)

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
                lock_path=None,
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


class CockpitLogPersistenceTests(unittest.TestCase):
    def test_access_log_is_written_to_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            port = _free_port()
            log_path = Path(tmp) / "cockpit-access.jsonl"
            server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=port,
                request_timeout_sec=3,
                log_path=log_path,
                lock_path=None,
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
            finally:
                server.stop()
            self.assertTrue(log_path.is_file())
            lines = log_path.read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(lines), 1)
            record = json.loads(lines[-1])
            self.assertEqual("list_projects", record["route"])
            self.assertEqual("ok", record["status"])
            self.assertEqual(0, server.log_errors)


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


class CockpitConcurrencyLimitTests(unittest.TestCase):
    """REVIEW-FIX-1: overflow requests get 503 instead of unbounded threads."""

    def test_busy_server_rejects_overflow_with_503(self):
        server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=_free_port(),
                request_timeout_sec=3,
                lock_path=None,
                max_concurrent_requests=2,
            ),
            workspace_views=(_workspace_view(),),
            role_views=(),
        )
        server._concurrency.acquire()
        server._concurrency.acquire()
        try:
            seen: dict[str, object] = {}

            class _FakeRequest:
                def sendall(self, data: bytes) -> None:
                    seen["data"] = data

                def shutdown(self, how: int) -> None:
                    seen["shutdown"] = how

                def close(self) -> None:
                    seen["closed"] = True

            server.process_request(_FakeRequest(), ("127.0.0.1", 1234))
            self.assertIn(b"503", seen["data"])
            self.assertTrue(seen["closed"])
            self.assertGreaterEqual(server.rejected_count, 1)
        finally:
            server._concurrency.release()
            server._concurrency.release()
            server.server_close()

    def test_busy_rejection_is_written_to_access_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "access.jsonl"
            server = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=_free_port(),
                    request_timeout_sec=3,
                    lock_path=None,
                    log_path=log_path,
                    max_concurrent_requests=1,
                ),
                workspace_views=(),
                role_views=(),
            )
            server._concurrency.acquire()
            try:
                class _FakeRequest:
                    def sendall(self, data: bytes) -> None:
                        pass

                    def shutdown(self, how: int) -> None:
                        pass

                    def close(self) -> None:
                        pass

                server.process_request(_FakeRequest(), ("127.0.0.1", 4321))
            finally:
                server._concurrency.release()
                if server._log_writer is not None:
                    server._log_writer.close()
                server.server_close()
            rows = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            busy = [row for row in rows if row.get("event") == "busy_rejected"]
            self.assertEqual(1, len(busy), rows)
            self.assertEqual("concurrency_limit", busy[0]["reason"])
            self.assertEqual("127.0.0.1", busy[0]["client_host"])


if __name__ == "__main__":
    unittest.main()
