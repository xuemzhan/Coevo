"""REVIEW-FIX-3 (M-2): quality gate mutual-exclusion unit tests."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "quality_gate", SCRIPTS / "quality_gate.py"
)
quality_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quality_gate)


class QualityGateLockTests(unittest.TestCase):
    def test_gate_uses_loop_local_exclusive_lock(self):
        self.assertEqual(".quality-gate.lock", quality_gate.GATE_LOCK.name)
        self.assertEqual(ROOT / "loop", quality_gate.GATE_LOCK.parent)
        self.assertTrue(callable(quality_gate.exclusive_lock))

    def test_gate_body_runs_inside_exclusive_lock(self):
        source = (SCRIPTS / "quality_gate.py").read_text(encoding="utf-8")
        self.assertIn("with exclusive_lock(GATE_LOCK)", source)
        self.assertLess(
            source.index("with exclusive_lock(GATE_LOCK)"),
            source.index("for argv in argvs"),
        )

    def test_lint_target_includes_records_archive_check(self):
        lint = quality_gate.TARGETS["lint"]
        archive_check = [
            sys.executable,
            str(ROOT / "scripts" / "archive_records.py"),
            "--check",
        ]
        self.assertIn(archive_check, lint)

    def test_exclusive_lock_serializes_holders(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "gate.lock"
            entered = threading.Event()
            release = threading.Event()
            order: list[str] = []

            def holder(name: str, wait_for_release: bool) -> None:
                with quality_gate.exclusive_lock(lock_path):
                    order.append(f"{name}-in")
                    if wait_for_release:
                        entered.set()
                        release.wait(timeout=10)
                    order.append(f"{name}-out")

            first = threading.Thread(target=holder, args=("a", True))
            second = threading.Thread(target=holder, args=("b", False))
            first.start()
            self.assertTrue(entered.wait(timeout=10))
            second.start()
            time.sleep(0.3)
            self.assertNotIn("b-in", order)
            release.set()
            first.join(timeout=10)
            second.join(timeout=10)
            self.assertFalse(first.is_alive())
            self.assertFalse(second.is_alive())
            self.assertEqual(["a-in", "a-out", "b-in", "b-out"], order)


if __name__ == "__main__":
    unittest.main()
