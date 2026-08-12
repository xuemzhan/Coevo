"""REVIEW-FIX-3 (M-2): quality gate mutual-exclusion unit tests."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "quality_gate", SCRIPTS / "quality_gate.py"
)
quality_gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = quality_gate  # dataclass 注解解析需要模块先注册
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
            # REVIEW2-2: the stage loop now lives inside _run_stages, which
            # is invoked from _run_locked inside the exclusive lock.
            source.index("_run_stages("),
        )

    def test_lint_target_includes_records_archive_check(self):
        lint = quality_gate.TARGETS["lint"]
        archive_check = [
            sys.executable,
            str(ROOT / "scripts" / "archive_records.py"),
            "--check",
        ]
        self.assertIn(archive_check, lint)

    def test_trim_invokes_archive_apply_and_returns_empty_when_nothing_to_do(self):
        completed = subprocess.CompletedProcess(
            [],
            0,
            stdout="[ok] verification: nothing to archive\n"
                   "[ok] decisions: nothing to archive\n",
            stderr="",
        )
        with mock.patch.object(subprocess, "run", return_value=completed) as run:
            note = quality_gate._trim_records_to_policy()
        self.assertEqual("", note)
        argv = run.call_args[0][0]
        self.assertIn("archive_records.py", argv[-2])
        self.assertEqual("--apply", argv[-1])

    def test_trim_returns_summary_when_records_are_archived(self):
        completed = subprocess.CompletedProcess(
            [],
            0,
            stdout=(
                "[verification] archive 3 section(s): size-trimmed 3 kept section(s)\n"
                "  -> wrote loop/archive/20260808/verification-20260808.txt\n"
            ),
            stderr="",
        )
        with mock.patch.object(subprocess, "run", return_value=completed):
            note = quality_gate._trim_records_to_policy()
        self.assertIn("archive", note)
        self.assertIn("-> wrote", note)

    def test_trim_failure_is_isolated_and_reported(self):
        failed = subprocess.CompletedProcess([], 2, stdout="", stderr="boom")
        with mock.patch.object(subprocess, "run", return_value=failed):
            note = quality_gate._trim_records_to_policy()
        self.assertIn("trim failed", note)
        with mock.patch.object(
            subprocess, "run", side_effect=OSError("spawn failed")
        ):
            note = quality_gate._trim_records_to_policy()
        self.assertIn("trim error", note)

    def test_trim_never_touches_audit_chain(self):
        # RECORDS-ARCHIVE-3 excludes audit from the generic archive tool, so
        # the gate's self-trim cannot trim tool-audit.jsonl.
        from src.coevo.records_archive import ARCHIVABLE_KINDS

        self.assertNotIn("audit", ARCHIVABLE_KINDS)

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
