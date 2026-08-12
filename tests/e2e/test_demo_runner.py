"""E2E tests for the offline demo composition root (US priority 1)."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.app import DEMO_PROFILE, run_demo_pipeline  # noqa: E402
from src.coevo.knowledge_base import KnowledgeStore  # noqa: E402
from src.coevo.orchestrator import OrchestrationOutcome  # noqa: E402
from src.coevo.protocol import (  # noqa: E402
    open_encrypted_package,
    parse_package_bytes,
)


class DemoRunnerTests(unittest.TestCase):
    def test_pipeline_with_cockpit_server_serves_and_stops(self):
        import socket
        import urllib.request

        with tempfile.TemporaryDirectory() as tmp:
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            result = run_demo_pipeline(
                Path(tmp),
                with_cockpit=True,
                cockpit_port=port,
            )
            try:
                self.assertTrue(result.cockpit_url)
                self.assertIsNotNone(result.cockpit_server)
                # 演示运行必须产出可直接打开驾驶舱的会话令牌。
                self.assertTrue(result.cockpit_token)
                page_url = result.cockpit_url + "?token=" + result.cockpit_token
                with urllib.request.urlopen(page_url, timeout=20) as resp:
                    self.assertLess(resp.status, 400)
                token = result.cockpit_server.session_manager.create()
                page_url = result.cockpit_url + "?token=" + token
                with urllib.request.urlopen(page_url, timeout=20) as resp:
                    self.assertLess(resp.status, 400)
                # 驾驶舱必须展示真实审计链活动，而不是空列表。
                import json as _json
                import urllib.request as _urlopen
                req = _urlopen.Request(
                    result.cockpit_url + "/api/list_projects",
                    headers={"X-Cockpit-Token": result.cockpit_token},
                )
                with _urlopen.urlopen(req, timeout=20) as resp:
                    projects = _json.loads(resp.read().decode())
                activity = projects["payload"]["views"][0]["activity"]
                self.assertGreaterEqual(len(activity), 3)
                actions = {entry["action"] for entry in activity}
                self.assertIn("dispatch", actions)
                self.assertIn("confirmation", actions)
            finally:
                if result.cockpit_server is not None:
                    result.cockpit_server.stop()
                result.store.close()

    def test_pipeline_completes_with_real_package_and_persistence(self):
        from src.coevo.crypto import GmsslPrototypeProvider

        with tempfile.TemporaryDirectory() as tmp:
            result = run_demo_pipeline(Path(tmp))
            try:
                self.assertEqual(
                    OrchestrationOutcome.COMPLETED.value,
                    result.outcome,
                )
                self.assertIsNotNone(result.package_path)
                self.assertTrue(result.package_path.is_file())
                self.assertEqual(64, len(result.package_wire_sha256))
                self.assertEqual(3, result.audit_event_count)
                self.assertTrue(result.store.verify_audit_chain())

                # The exported package must be a real signed/encrypted .agent
                # that parses, decrypts and verifies back.
                provider = GmsslPrototypeProvider(ROOT)
                sender = provider.sender_handle(DEMO_PROFILE, "CERT-SENDER")
                recipient = provider.recipient_handle(DEMO_PROFILE, "CERT-RECIPIENT")
                wire = result.package_path.read_bytes()
                parsed = parse_package_bytes(wire)
                opened = open_encrypted_package(
                    parsed,
                    provider=provider,
                    recipient_handle=recipient,
                    sender_handle=sender,
                )
                self.assertEqual("t.1", opened.manifest["task_id"])
                self.assertTrue(opened.signature.signature)

                # Knowledge bundle must be persisted and reloadable.
                store = KnowledgeStore.open(
                    result.runtime_dir / "knowledge.db"
                )
                try:
                    bundle = store.load(result.knowledge_bundle_id)
                    self.assertIsNotNone(bundle)
                    self.assertEqual("PRJ001", bundle.project_id)
                finally:
                    store.close()
            finally:
                result.store.close()

    def test_cli_smoke_run_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_demo.py"),
                    "--smoke",
                    "--runtime-dir",
                    tmp,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=300,
            )
            self.assertEqual(0, completed.returncode, completed.stderr[-2000:])
            self.assertIn("DEMO OK", completed.stdout)

    def test_cli_run_shows_progress_wizard(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_demo.py"),
                    "--no-server",
                    "--runtime-dir",
                    tmp,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=300,
            )
            self.assertEqual(
                0, completed.returncode, completed.stderr[-2000:]
            )
            self.assertIn("Coevo 离线演示开始", completed.stdout)
            self.assertIn("[3/7] 负责人确认通过，恢复编排链", completed.stdout)
            self.assertIn("演示完成", completed.stdout)
            self.assertIn("加密任务包", completed.stdout)
            self.assertIn("审计链：", completed.stdout)
            self.assertIn("--resume", completed.stdout)
            self.assertIn("人工确认：", completed.stdout)
            # --no-server 时不应提示停止驾驶舱服务。
            self.assertNotIn("停止驾驶舱服务", completed.stdout)

    def test_cli_interactive_confirmation_accepts_and_completes(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_demo.py"),
                    "--interactive",
                    "--no-server",
                    "--runtime-dir",
                    tmp,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                input="y\n",
                timeout=300,
            )
            self.assertEqual(
                0, completed.returncode, completed.stderr[-2000:]
            )
            self.assertIn("到达人工确认节点", completed.stdout)
            self.assertIn("已授权，继续执行", completed.stdout)
            self.assertIn("演示完成", completed.stdout)

    def test_cli_interactive_confirmation_rejection_stops_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_demo.py"),
                    "--interactive",
                    "--no-server",
                    "--runtime-dir",
                    tmp,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                input="n\n",
                timeout=300,
            )
            self.assertEqual(1, completed.returncode)
            self.assertIn("演示中止", completed.stderr)
            self.assertIn("负责人拒绝了任务下发", completed.stderr)

    def test_cli_json_output_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_demo.py"),
                    "--json",
                    "--no-server",
                    "--runtime-dir",
                    tmp,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300,
            )
            self.assertEqual(
                0, completed.returncode, completed.stderr[-2000:]
            )
            import json as _json

            data = _json.loads(completed.stdout)
            self.assertEqual("completed", data["outcome"])
            self.assertEqual(64, len(data["package_sha256"]))
            self.assertTrue(data["package_path"])
            self.assertTrue(data["knowledge_bundle_id"])
            self.assertEqual(3, data["audit_event_count"])
            self.assertGreaterEqual(data["audit_chain_entries"], 3)
            self.assertEqual(64, len(data["audit_chain_head"]))
            self.assertTrue(data["audit_chain_valid"])

    def test_demo_run_persists_state_for_resume(self):
        import json as _json
        import urllib.request as _urlopen

        with tempfile.TemporaryDirectory() as tmp:
            result = run_demo_pipeline(Path(tmp))
            try:
                run_dir = next(Path(tmp).glob("run-*"))
                state_path = run_dir / "cockpit-state.json"
                self.assertTrue(state_path.is_file())
                # 重开已完成的运行：加载快照并提供驾驶舱。
                with socket.socket() as probe:
                    probe.bind(("127.0.0.1", 0))
                    port = probe.getsockname()[1]
                lock_path = Path(tmp) / "resume.lock"
                from src.coevo.cockpit.server import (
                    CockpitHttpConfig,
                    CockpitHttpServer,
                )

                server = CockpitHttpServer(
                    CockpitHttpConfig(
                        bind_port=port,
                        request_timeout_sec=5,
                        state_path=state_path,
                        lock_path=lock_path,
                    )
                )
                try:
                    server.start()
                    token = server.session_manager.create()
                    req = _urlopen.Request(
                        f"http://127.0.0.1:{port}/api/list_projects",
                        headers={"X-Cockpit-Token": token},
                    )
                    with _urlopen.urlopen(req, timeout=10) as resp:
                        data = _json.loads(resp.read().decode())
                    view = data["payload"]["views"][0]
                    self.assertEqual("离线 MVP 演示交付", view["display_name"])
                    self.assertEqual(5, len(view["trace"]))
                    self.assertGreaterEqual(len(view["activity"]), 3)
                    # 并行项目：第二个项目停在待确认节点。
                    views = data["payload"]["views"]
                    self.assertEqual(2, len(views))
                    prj2 = views[1]
                    self.assertEqual("PRJ002", prj2["project_id"])
                    pending_steps = [
                        t for t in prj2["trace"]
                        if t["requires_human_confirmation"]
                    ]
                    self.assertTrue(pending_steps)
                    self.assertEqual("", pending_steps[0]["confirmed_by"])
                finally:
                    server.stop()
            finally:
                result.store.close()

    def test_cli_incompatible_flag_combinations_are_rejected(self):
        for flags in (
            ("--interactive", "--json"),
            ("--interactive", "--quiet"),
            ("--resume", "some-dir", "--open"),
            ("--resume", "some-dir", "--json"),
            ("--session-hours", "0"),
            ("--session-hours", "99999"),
        ):
            with self.subTest(flags=flags):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "run_demo.py"),
                        *flags,
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=60,
                )
                self.assertEqual(2, completed.returncode)
                self.assertTrue(
                    "mutually exclusive" in completed.stderr
                    or "standalone mode" in completed.stderr
                    or "--session-hours must be" in completed.stderr,
                    completed.stderr,
                )

    def test_serve_gate_confirms_via_cockpit(self):
        import json as _json
        import threading as _threading
        import urllib.request as _urlopen
        import urllib.error as _url_error

        with tempfile.TemporaryDirectory() as tmp:
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            base = Path(tmp)
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            proc = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_demo.py"),
                    "--serve-gate",
                    "--port", str(port),
                    "--lock-path", str(base / "gate.lock"),
                    "--runtime-dir", str(base / "runs"),
                ],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=flags,
            )
            lines: list[str] = []
            stop = _threading.Event()

            def _reader(stream, sink):
                for line in iter(stream.readline, ""):
                    sink.append(line)
                    if stop.is_set():
                        break

            t1 = _threading.Thread(target=_reader, args=(proc.stdout, lines), daemon=True)
            t2 = _threading.Thread(target=_reader, args=(proc.stderr, lines), daemon=True)
            t1.start()
            t2.start()
            try:
                token = None
                deadline = time.time() + 90
                while time.time() < deadline and token is None:
                    for line in lines:
                        if line.startswith("open cockpit: "):
                            token = line.strip().split("token=", 1)[1]
                    if token:
                        break
                    time.sleep(0.2)
                self.assertIsNotNone(
                    token, "serve-gate must print the cockpit URL before confirming"
                )
                # 待确认状态：人工确认步骤尚未被确认
                req = _urlopen.Request(
                    f"http://127.0.0.1:{port}/api/list_projects",
                    headers={"X-Cockpit-Token": token},
                )
                with _urlopen.urlopen(req, timeout=10) as resp:
                    data = _json.loads(resp.read().decode())
                trace = data["payload"]["views"][0]["trace"]
                confirm_steps = [
                    t for t in trace if t["requires_human_confirmation"]
                ]
                self.assertTrue(confirm_steps)
                self.assertEqual("", confirm_steps[0]["confirmed_by"])

                body = _json.dumps({"action": "confirm"}).encode("utf-8")
                confirm_req = _urlopen.Request(
                    f"http://127.0.0.1:{port}/api/pending_confirm",
                    data=body,
                    method="POST",
                    headers={
                        "X-Cockpit-Token": token,
                        "Origin": f"http://127.0.0.1:{port}",
                        "X-Requested-With": "coevo-cockpit",
                        "Content-Type": "application/json",
                    },
                )
                with _urlopen.urlopen(confirm_req, timeout=15) as resp:
                    result = _json.loads(resp.read().decode())
                self.assertEqual("approved", result["payload"]["decision"])

                deadline = time.time() + 120
                while time.time() < deadline:
                    if any("演示完成" in line for line in lines):
                        break
                    time.sleep(0.2)
                self.assertTrue(
                    any("演示完成" in line for line in lines),
                    "demo must complete after the cockpit confirmation",
                )
            finally:
                stop.set()
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=10)
                for stream in (proc.stdout, proc.stderr):
                    try:
                        if stream:
                            stream.close()
                    except Exception:
                        pass

    def test_serve_gate_reject_aborts_demo(self):
        import json as _json
        import threading as _threading
        import urllib.request as _urlopen
        import urllib.error as _url_error

        with tempfile.TemporaryDirectory() as tmp:
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            base = Path(tmp)
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            proc = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_demo.py"),
                    "--serve-gate",
                    "--port", str(port),
                    "--lock-path", str(base / "gate.lock"),
                    "--runtime-dir", str(base / "runs"),
                ],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=flags,
            )
            lines: list[str] = []
            stop = _threading.Event()

            def _reader(stream, sink):
                for line in iter(stream.readline, ""):
                    sink.append(line)
                    if stop.is_set():
                        break

            t1 = _threading.Thread(target=_reader, args=(proc.stdout, lines), daemon=True)
            t2 = _threading.Thread(target=_reader, args=(proc.stderr, lines), daemon=True)
            t1.start()
            t2.start()
            try:
                token = None
                deadline = time.time() + 90
                while time.time() < deadline and token is None:
                    for line in lines:
                        if line.startswith("open cockpit: "):
                            token = line.strip().split("token=", 1)[1]
                    if token:
                        break
                    time.sleep(0.2)
                self.assertIsNotNone(token)
                body = _json.dumps({"action": "reject"}).encode("utf-8")
                reject_req = _urlopen.Request(
                    f"http://127.0.0.1:{port}/api/pending_confirm",
                    data=body,
                    method="POST",
                    headers={
                        "X-Cockpit-Token": token,
                        "Origin": f"http://127.0.0.1:{port}",
                        "X-Requested-With": "coevo-cockpit",
                        "Content-Type": "application/json",
                    },
                )
                with self.assertRaises(_url_error.HTTPError) as ctx:
                    _urlopen.urlopen(reject_req, timeout=15)
                self.assertEqual(403, ctx.exception.code)
                deadline = time.time() + 30
                while time.time() < deadline:
                    if any("演示中止" in line for line in lines):
                        break
                    if proc.poll() is not None:
                        break
                    time.sleep(0.2)
                self.assertTrue(
                    any("演示中止" in line for line in lines),
                    "demo must abort after the cockpit rejection",
                )
            finally:
                stop.set()
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=10)
                for stream in (proc.stdout, proc.stderr):
                    try:
                        if stream:
                            stream.close()
                    except Exception:
                        pass


if __name__ == "__main__":
    unittest.main()
