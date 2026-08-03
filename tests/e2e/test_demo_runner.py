"""E2E tests for the offline demo composition root (US priority 1)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
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
                token = result.cockpit_server.session_manager.create()
                page_url = result.cockpit_url + "?token=" + token
                with urllib.request.urlopen(page_url, timeout=20) as resp:
                    self.assertLess(resp.status, 400)
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


if __name__ == "__main__":
    unittest.main()
