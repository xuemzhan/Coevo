"""REVIEW2-10: audit-log generation re-anchor guard tests.

Contract (docs/architecture/audit-reanchor.md):

* the whole current generation is archived (bytes preserved);
* a genesis record anchors the new generation to the archived digest and
  starts a fresh chain (prev_hash = 0*64);
* the legacy checkpoint is reset to the genesis line;
* no existing record is rewritten -- append-only integrity holds within
  each generation;
* re-anchor fails closed unless the current chain is fully sealed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


audit_seal = _load("audit_seal", SCRIPTS / "audit_seal.py")
audit_log = _load("audit_log", SCRIPTS / "audit_log.py")


class ReanchorPlanTests(unittest.TestCase):
    def test_plan_rejects_too_few_lines(self) -> None:
        with self.assertRaises(ValueError):
            audit_seal.reanchor_plan(
                [b'{"a":1}\n'],
                previous_head_sequence=5,
                now="2026-08-10T00:00:00Z",
            )

    def test_plan_builds_genesis_and_checkpoint(self) -> None:
        lines = [b'{"x":1}\n', b'{"x":2}\n']
        plan = audit_seal.reanchor_plan(
            lines,
            previous_head_sequence=7,
            now="2026-08-10T00:00:00Z",
        )
        self.assertEqual(plan["archived_line_count"], 2)
        self.assertEqual(
            plan["archived_sha256"],
            hashlib.sha256(b"".join(lines)).hexdigest(),
        )
        genesis = plan["genesis_item"]
        self.assertEqual(genesis["prev_hash"], "0" * 64)
        self.assertEqual(genesis["event"], "audit_generation")
        self.assertEqual(
            genesis["previous_generation_sha256"], plan["archived_sha256"]
        )
        self.assertEqual(genesis["previous_head_sequence"], 7)
        self.assertEqual(genesis["record_hash"][:8], hashlib.sha256(
            json.dumps({k: v for k, v in genesis.items() if k != "record_hash"},
                       sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:8])
        checkpoint = plan["checkpoint_item"]
        self.assertEqual(checkpoint["legacy_line_count"], 0)
        self.assertEqual(checkpoint["legacy_byte_count"], 0)
        self.assertEqual(
            checkpoint["legacy_sha256"],
            hashlib.sha256(b"").hexdigest(),
        )
        self.assertTrue(checkpoint["checkpoint_hash"])

    def test_new_generation_chain_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit = root / "audit.jsonl"
            checkpoint = root / "checkpoint.json"
            for index in range(3):
                audit_log.append_record(
                    {"actor": "t", "tool": "test", "event": "e", "n": index},
                    audit,
                )
            audit_log.create_legacy_checkpoint(audit, checkpoint)
            lines = audit.read_bytes().splitlines(keepends=True)
            plan = audit_seal.reanchor_plan(
                lines,
                previous_head_sequence=1,
                now="2026-08-10T00:00:00Z",
            )
            new_audit = root / "audit-new.jsonl"
            new_checkpoint = root / "checkpoint-new.json"
            new_audit.write_bytes(plan["genesis_raw"])
            new_checkpoint.write_text(
                plan["checkpoint_rendered"], encoding="utf-8"
            )
            problems = audit_log.verify(new_audit, new_checkpoint)
            self.assertEqual([], problems)
            # The archived generation digest binds old -> new.
            genesis = json.loads(plan["genesis_raw"])
            self.assertEqual(
                genesis["previous_generation_sha256"],
                hashlib.sha256(b"".join(lines)).hexdigest(),
            )

    def test_reanchor_fails_closed_on_unsealed_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit = root / "audit.jsonl"
            checkpoint = root / "checkpoint.json"
            audit_log.append_record(
                {"actor": "t", "tool": "test", "event": "e"},
                audit,
            )
            with self.assertRaises(ValueError):
                audit_seal.reanchor(
                    audit=audit,
                    head=root / "head.json",
                    signature=root / "head.p7s",
                    checkpoint=checkpoint,
                    archive_dir=root / "archive",
                )
            self.assertFalse((root / "archive").exists())
            self.assertTrue(audit.is_file())

    def test_archive_records_points_to_reanchor_flow(self) -> None:
        source = (SCRIPTS / "archive_records.py").read_text(encoding="utf-8")
        self.assertIn("audit_seal.py re-anchor", source)


if __name__ == "__main__":
    unittest.main()
