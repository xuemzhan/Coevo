"""E2E verification of the production cockpit launcher lifecycle.

Starts ``scripts/run_cockpit.py`` as a real subprocess with a hermetic
data/log/lock directory, probes ``/healthz``, then requests a graceful
shutdown (Windows CTRL+BREAK) and asserts:

* exit code 0 (graceful, not killed);
* cockpit state snapshot and JSONL access log are flushed to disk;
* the single-instance lock file is released.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class CockpitLauncherE2ETest(unittest.TestCase):
    def test_preflight_exits_zero_on_healthy_repo(self):
        # AVAIL-1: fail-fast preflight must pass on the sealed gate context
        # (audit fully-sealed, dirs writable, model config offline-loadable).
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_cockpit.py"), "--preflight"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_launcher_serves_healthz_and_stops_gracefully(self):
        if not hasattr(signal, "CTRL_BREAK_EVENT"):
            self.skipTest("graceful shutdown via CTRL+BREAK is Windows-only")
        with tempfile.TemporaryDirectory(prefix="coevo-launcher-e2e-") as tmp:
            base = Path(tmp)
            env = dict(os.environ)
            env["COEVO_DATA_DIR"] = str(base / "data")
            env["COEVO_LOG_DIR"] = str(base / "log")
            env["COEVO_LOCK_PATH"] = str(base / "cockpit.lock")
            port = _free_port()
            flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_cockpit.py"),
                    "--port",
                    str(port),
                ],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=flags,
            )
            try:
                healthy = False
                for _ in range(80):
                    if process.poll() is not None:
                        break
                    try:
                        with urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/healthz", timeout=1
                        ) as response:
                            body = response.read().decode()
                            healthy = (
                                response.status == 200
                                and '"status":"ok"' in body
                            )
                            if healthy:
                                break
                    except Exception:
                        time.sleep(0.25)
                self.assertTrue(
                    healthy,
                    f"cockpit did not become healthy (poll={process.poll()})",
                )

                process.send_signal(signal.CTRL_BREAK_EVENT)
                try:
                    exit_code = process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
                    self.fail("cockpit did not exit gracefully after CTRL+BREAK")
                self.assertEqual(0, exit_code)

                self.assertTrue(
                    (base / "data" / "cockpit-state.json").is_file(),
                    "cockpit state must be flushed on graceful shutdown",
                )
                self.assertTrue(
                    (base / "log" / "cockpit-access.jsonl").is_file(),
                    "cockpit access log must be created",
                )
                self.assertFalse(
                    (base / "cockpit.lock").exists(),
                    "single-instance lock must be released on shutdown",
                )
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=10)

    def test_print_token_issues_usable_session(self):
        if not hasattr(signal, "CTRL_BREAK_EVENT"):
            self.skipTest("graceful shutdown via CTRL+BREAK is Windows-only")
        with tempfile.TemporaryDirectory(prefix="coevo-token-e2e-") as tmp:
            base = Path(tmp)
            env = dict(os.environ)
            env["COEVO_DATA_DIR"] = str(base / "data")
            env["COEVO_LOG_DIR"] = str(base / "log")
            env["COEVO_LOCK_PATH"] = str(base / "cockpit.lock")
            port = _free_port()
            flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_cockpit.py"),
                    "--port",
                    str(port),
                    "--print-token",
                ],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=flags,
            )
            token = None
            try:
                deadline = time.time() + 30
                while time.time() < deadline and token is None:
                    line = process.stdout.readline()
                    if not line:
                        if process.poll() is not None:
                            break
                        time.sleep(0.1)
                        continue
                    if line.startswith("session token: "):
                        token = line.strip().split("session token: ", 1)[1]
                self.assertIsNotNone(
                    token,
                    "session token was not printed by --print-token",
                )
                request = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/health",
                    headers={"X-Cockpit-Token": token},
                )
                with urllib.request.urlopen(request, timeout=3) as response:
                    self.assertEqual(200, response.status)
                    data = json.loads(response.read().decode())
                self.assertIn("request_count", data)
                process.send_signal(signal.CTRL_BREAK_EVENT)
                try:
                    exit_code = process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
                    self.fail("cockpit did not exit gracefully after CTRL+BREAK")
                self.assertEqual(0, exit_code)
                access_log = base / "log" / "cockpit-access.jsonl"
                if access_log.is_file():
                    log_text = access_log.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    self.assertNotIn(token, log_text)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
