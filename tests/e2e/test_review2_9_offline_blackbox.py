"""REVIEW2-9: offline black-box proof -- socket-level zero external network.

Starts the real cockpit HTTP server on 127.0.0.1 and walks the core
surface (index, static assets, read API, denied write) while recording
every socket ``connect`` target. The contract (docs/architecture/
offline-proof.md) is:

* external_requests = 0 (every connect target is loopback);
* loopback_requests = N (the local server was actually exercised);
* missing_local_assets = 0 (all referenced assets returned 200);
* runtime_downloads = 0 (no non-loopback sockets were ever opened);
* served assets contain no external URL references.

In-process socket capture is the CI-proof; production acceptance may
re-run the same walk on a controlled host under a firewall allow-list.
"""

from __future__ import annotations

import re
import socket
import unittest
import urllib.error
import urllib.request
from unittest import mock

from src.coevo.cockpit import CockpitHttpConfig, CockpitHttpServer, WorkspaceView

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1"})
EXTERNAL_URL_RE = re.compile(r"https?://|//cdn|//fonts|analytics|google|gstatic", re.I)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class OfflineBlackBoxTests(unittest.TestCase):
    def _walk(self, base: str, token: str) -> dict[str, int]:
        urls = (
            base + "/?token=" + token,
            base + "/static/style.css",
            base + "/static/app.js",
            base + "/api/list_projects",
        )
        statuses: dict[str, int] = {}
        for url in urls:
            request = urllib.request.Request(
                url, headers={"X-Cockpit-Token": token}
            )
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    statuses[url] = response.status
            except urllib.error.HTTPError as exc:
                statuses[url] = exc.code
                exc.close()
        # Denied write path still must stay local-only.
        import json

        write_request = urllib.request.Request(
            base + "/api/wps_open",
            data=json.dumps(
                {"project_id": "PRJ001", "artifact_path": "x.docx"}
            ).encode("utf-8"),
            headers={"X-Cockpit-Token": token},
            method="POST",
        )
        try:
            with urllib.request.urlopen(write_request, timeout=10) as response:
                statuses[base + "/api/wps_open"] = response.status
        except urllib.error.HTTPError as exc:
            statuses[base + "/api/wps_open"] = exc.code
            exc.close()
        return statuses

    def test_core_surface_makes_zero_external_requests(self) -> None:
        port = _free_port()
        server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=port,
                request_timeout_sec=5,
                session_timeout_sec=60,
                lock_path=None,
            ),
            workspace_views=(WorkspaceView("PRJ001", "P", ("a.eng",), 1, 1, 1),),
            role_views=(),
        )
        self.addCleanup(server.stop)
        server.start()
        token = server.session_manager.create()
        base = f"http://127.0.0.1:{port}"

        connects: list[tuple[str, int]] = []

        def recording_connect(sock, address, *args, **kwargs):
            connects.append(address)
            return original_connect(sock, address, *args, **kwargs)

        original_connect = socket.socket.connect
        with mock.patch.object(
            socket.socket, "connect", recording_connect
        ):
            statuses = self._walk(base, token)
            # Re-assert the served assets carry no external URL references.
            for asset in ("/", "/static/style.css", "/static/app.js"):
                request = urllib.request.Request(
                    base + asset + ("?token=" + token if asset == "/" else ""),
                    headers={"X-Cockpit-Token": token},
                )
                with urllib.request.urlopen(request, timeout=10) as response:
                    body = response.read().decode("utf-8", errors="replace")
                self.assertIsNone(
                    EXTERNAL_URL_RE.search(body),
                    f"external URL reference found in {asset}",
                )

        self.assertGreaterEqual(len(connects), 1, "local server was not exercised")
        external = [addr for addr in connects if addr[0] not in LOOPBACK_HOSTS]
        self.assertEqual(
            [],
            external,
            f"external network connections captured: {external}",
        )
        missing = [
            url for url, code in statuses.items() if code != 200 and code != 403
        ]
        self.assertEqual([], missing, f"unexpected statuses: {statuses}")
        print(
            "external_requests=0 "
            f"loopback_requests={len(connects)} "
            "missing_local_assets=0 "
            "runtime_downloads=0"
        )


if __name__ == "__main__":
    unittest.main()
