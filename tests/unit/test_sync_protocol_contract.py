"""PRODUCT-REVIEW T-11: sync protocol contract guard (design slice)."""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from src.coevo.sync.contract import (
    SYNC_SCHEMA_VERSION,
    SyncContractError,
    SyncEnvelope,
    envelope_digest,
    validate_chain,
    validate_envelope,
)


def _env(sequence=1, event_id="ev.1", previous_hash="0" * 64):
    return validate_envelope(
        {
            "schema_version": SYNC_SCHEMA_VERSION,
            "source_node": "node-a",
            "event_id": event_id,
            "sequence": sequence,
            "created_at": "2026-08-12T00:00:00Z",
            "payload_digest": "a" * 64,
            "previous_hash": previous_hash,
        }
    )


class SyncContractTests(unittest.TestCase):
    def test_valid_envelope_round_trips(self):
        env = _env()
        self.assertEqual("node-a", env.source_node)
        self.assertEqual(1, env.sequence)

    def test_rejects_bad_fields(self):
        with self.assertRaises(SyncContractError):
            validate_envelope({"schema_version": "9.9"})
        with self.assertRaises(SyncContractError):
            validate_envelope(
                {
                    "schema_version": SYNC_SCHEMA_VERSION,
                    "source_node": "bad node!",
                    "event_id": "ev.1",
                    "sequence": 0,
                    "created_at": "not-iso",
                    "payload_digest": "x",
                    "previous_hash": "0" * 64,
                }
            )

    def test_chain_hash_linkage_and_ordering(self):
        first = _env(sequence=1, event_id="ev.1")
        second = validate_envelope(
            {
                "schema_version": SYNC_SCHEMA_VERSION,
                "source_node": "node-a",
                "event_id": "ev.2",
                "sequence": 2,
                "created_at": "2026-08-12T00:00:01Z",
                "payload_digest": "b" * 64,
                "previous_hash": envelope_digest(first),
            }
        )
        digests = validate_chain([first, second])
        self.assertEqual(2, len(digests))

    def test_chain_rejects_gap_or_replay(self):
        first = _env(sequence=1, event_id="ev.1")
        gap = validate_envelope(
            {
                "schema_version": SYNC_SCHEMA_VERSION,
                "source_node": "node-a",
                "event_id": "ev.3",
                "sequence": 3,
                "created_at": "2026-08-12T00:00:02Z",
                "payload_digest": "c" * 64,
                "previous_hash": envelope_digest(first),
            }
        )
        with self.assertRaises(SyncContractError):
            validate_chain([first, gap])
        replay = validate_envelope(
            {
                "schema_version": SYNC_SCHEMA_VERSION,
                "source_node": "node-a",
                "event_id": "ev.1",
                "sequence": 2,
                "created_at": "2026-08-12T00:00:01Z",
                "payload_digest": "b" * 64,
                "previous_hash": envelope_digest(first),
            }
        )
        with self.assertRaises(SyncContractError):
            validate_chain([first, replay])

    def test_design_doc_exists_with_required_sections(self):
        doc = (
            ROOT / "docs" / "architecture" / "sync-protocol.md"
        ).read_text(encoding="utf-8")
        for marker in ("版本", "重放防护", "顺序", "冲突"):
            self.assertIn(marker, doc)


if __name__ == "__main__":
    unittest.main()
