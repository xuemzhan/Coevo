"""BACKUP-1: backup/restore tool pure-logic tests."""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "backup_state", ROOT / "scripts" / "backup_state.py"
)
backup_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup_state)


def _seed_install(tmp: str) -> Path:
    root = Path(tmp)
    (root / "loop").mkdir(parents=True, exist_ok=True)
    (root / "current").write_text("0.2.0\n", encoding="utf-8")
    (root / "cockpit-state.json").write_text('{"schema_version":"1.0"}', encoding="utf-8")
    (root / "loop" / "tool-audit.jsonl").write_text('{"a":1}\n', encoding="utf-8")
    (root / "loop" / "audit-head.json").write_text('{"signer":"x"}', encoding="utf-8")
    return root


class BackupFlowTests(unittest.TestCase):
    def test_backup_verify_restore_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            install = _seed_install(tmp)
            backups = Path(tmp) / "backups"
            manifest = backup_state.backup(install, backups, "b1")
            self.assertGreaterEqual(len(manifest["files"]), 3)
            result = backup_state.verify(backups, "b1")
            self.assertTrue(result["ok"])
            # Tamper a backed-up file -> verify fails.
            victim = backups / "b1" / "current"
            victim.write_text("9.9.9\n", encoding="utf-8")
            self.assertFalse(backup_state.verify(backups, "b1")["ok"])
            # Repair then restore into a fresh install root.
            victim.write_text("0.2.0\n", encoding="utf-8")
            target = Path(tmp) / "restored"
            target.mkdir()
            outcome = backup_state.restore(target, backups, "b1")
            self.assertTrue(outcome["ok"])
            self.assertEqual(
                "0.2.0", (target / "current").read_text(encoding="utf-8").strip()
            )
            self.assertTrue((target / "loop" / "tool-audit.jsonl").is_file())

    def test_restore_refuses_fresh_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            install = _seed_install(tmp)
            backups = Path(tmp) / "backups"
            backup_state.backup(install, backups, "b1")
            lock = install / "cockpit.lock"
            lock.write_text("1\n", encoding="utf-8")
            with self.assertRaises(backup_state.BackupValidationError):
                backup_state.restore(install, backups, "b1")

    def test_safe_relative_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(backup_state.BackupValidationError):
                backup_state._safe_relative("../escape", root)
            with self.assertRaises(backup_state.BackupValidationError):
                backup_state._safe_relative("C:/escape", root)
            self.assertTrue(backup_state._safe_relative("loop/x.json", root).is_absolute())

    def test_label_validation(self):
        for bad in ("../x", "a/b", "a\\b", "", "a b"):
            with self.assertRaises(backup_state.BackupValidationError):
                backup_state._validate_label(bad)
        self.assertEqual("a-b_1.2", backup_state._validate_label("a-b_1.2"))

    def test_list_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            install = _seed_install(tmp)
            backups = Path(tmp) / "backups"
            backup_state.backup(install, backups, "b1")
            backup_state.backup(install, backups, "b2")
            labels = [item["label"] for item in backup_state.list_backups(backups)]
            self.assertEqual(["b1", "b2"], labels)

    def test_backup_label_must_be_unique(self):
        with tempfile.TemporaryDirectory() as tmp:
            install = _seed_install(tmp)
            backups = Path(tmp) / "backups"
            backup_state.backup(install, backups, "b1")
            with self.assertRaises(backup_state.BackupValidationError):
                backup_state.backup(install, backups, "b1")


if __name__ == "__main__":
    unittest.main()
