"""PRODUCT-REVIEW T-12: sync outbox / reconciliation / file transport."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


from src.coevo.sync.contract import (
    SYNC_SCHEMA_VERSION,
    SyncContractError,
    envelope_digest,
)
from src.coevo.sync.store import (
    ReconcileResult,
    SyncOutbox,
    SyncReconciler,
    export_bundle,
    load_bundle,
)


def _payload(sequence, event_id, previous_hash):
    return {
        "schema_version": SYNC_SCHEMA_VERSION,
        "source_node": "node-a",
        "event_id": event_id,
        "sequence": sequence,
        "created_at": f"2026-08-12T00:00:{sequence:02d}Z",
        "payload_digest": ("a" * 64) if sequence % 2 else ("b" * 64),
        "previous_hash": previous_hash,
    }


def _build_outbox(path: Path, count: int = 3) -> SyncOutbox:
    outbox = SyncOutbox(path)
    previous = "0" * 64
    for index in range(1, count + 1):
        data = _payload(index, f"ev.{index}", previous)
        record = outbox.append(data)
        previous = record.digest
    return outbox


class SyncOutboxTests(unittest.TestCase):
    def test_append_builds_linked_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = _build_outbox(Path(tmp) / "outbox.jsonl")
            self.assertEqual(3, len(outbox.records))
            self.assertEqual(
                outbox.records[-1].digest, outbox.head_digest
            )
            self.assertEqual(
                outbox.records[1].envelope.previous_hash,
                outbox.records[0].digest,
            )

    def test_append_rejects_sequence_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = SyncOutbox(Path(tmp) / "outbox.jsonl")
            outbox.append(_payload(1, "ev.1", "0" * 64))
            with self.assertRaises(SyncContractError):
                outbox.append(_payload(3, "ev.3", outbox.head_digest))

    def test_append_rejects_broken_linkage(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = SyncOutbox(Path(tmp) / "outbox.jsonl")
            outbox.append(_payload(1, "ev.1", "0" * 64))
            with self.assertRaises(SyncContractError):
                outbox.append(_payload(2, "ev.2", "f" * 64))

    def test_append_rejects_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = SyncOutbox(Path(tmp) / "outbox.jsonl")
            outbox.append(_payload(1, "ev.1", "0" * 64))
            record = outbox.append(_payload(2, "ev.2", outbox.head_digest))
            with self.assertRaises(SyncContractError):
                outbox.append(_payload(3, "ev.1", record.digest))

    def test_append_enforces_single_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = SyncOutbox(Path(tmp) / "outbox.jsonl")
            outbox.append(_payload(1, "ev.1", "0" * 64))
            other = _payload(2, "ev.2", outbox.head_digest)
            other["source_node"] = "node-b"
            with self.assertRaises(SyncContractError):
                outbox.append(other)

    def test_outbox_persists_across_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "outbox.jsonl"
            _build_outbox(path)
            reloaded = SyncOutbox(path)
            self.assertEqual(3, len(reloaded.records))
            self.assertEqual(
                reloaded.records[-1].digest, reloaded.head_digest
            )

    def test_corrupt_outbox_fails_closed_on_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "outbox.jsonl"
            path.write_text("{not json\n", encoding="utf-8")
            with self.assertRaises(SyncContractError):
                SyncOutbox(path)


class SyncReconcileTests(unittest.TestCase):
    def test_reconcile_detects_new_replay_and_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = _build_outbox(Path(tmp) / "outbox.jsonl", count=2)
            incoming = [
                _payload(1, "ev.1", "0" * 64),
                _payload(2, "ev.2", envelope_digest(
                    outbox.records[0].envelope
                )),
                _payload(3, "ev.3", outbox.records[1].digest),
            ]
            result = SyncReconciler.reconcile(outbox, incoming)
            self.assertTrue(result.ok)
            self.assertEqual(("ev.3",), result.new_events)
            self.assertEqual(("ev.1", "ev.2"), result.replay_events)
            # 本地对账视角：缺口指本地尚缺的序号。
            self.assertEqual((3,), result.gaps)

    def test_reconcile_rejects_invalid_incoming(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = _build_outbox(Path(tmp) / "outbox.jsonl")
            bad = [
                _payload(1, "ev.1", "0" * 64),
                _payload(3, "ev.3", "f" * 64),
            ]
            result = SyncReconciler.reconcile(outbox, bad)
            self.assertFalse(result.ok)
            self.assertTrue(result.detail)


class SyncBundleTests(unittest.TestCase):
    def test_export_import_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = _build_outbox(Path(tmp) / "outbox.jsonl", count=3)
            bundle = Path(tmp) / "sync.bundle.json"
            export_bundle(bundle, outbox)
            envelopes = load_bundle(bundle)
            self.assertEqual(3, len(envelopes))
            self.assertEqual(
                [e.sequence for e in envelopes], [1, 2, 3]
            )

    def test_tampered_bundle_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = _build_outbox(Path(tmp) / "outbox.jsonl", count=2)
            bundle = Path(tmp) / "sync.bundle.json"
            export_bundle(bundle, outbox)
            data = json.loads(bundle.read_text(encoding="utf-8"))
            # 链完整性篡改（破坏哈希链接）必须被拒绝；负载完整性校验
            # 依赖未来的信封签名层（见 sync-protocol.md §6）。
            data[1]["previous_hash"] = "c" * 64
            bundle.write_text(
                json.dumps(data), encoding="utf-8"
            )
            with self.assertRaises(SyncContractError):
                load_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
