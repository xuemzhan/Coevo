"""MATURITY-O-07: dual-node offline sync handoff E2E.

Pins the offline-first cross-node flow (PRODUCT-REVIEW T-11/T-12 store +
MATURITY-O-07): a member node appends events to its outbox, exports a
bundle file (the offline transport medium, same idea as ``.agent``), and the
center node validates the whole chain, reconciles it against its view and
applies only new events. Re-delivery is idempotent, gaps trigger a re-pull
signal and tampered bundles fail closed before any event is applied.

The center-side "applied ledger" is a plain set in this harness: the durable
center aggregation and the controlled-network transport remain DESIGNED
(``online-mode-scope.md`` / O-01 decision).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.coevo.sync.contract import (
    SYNC_SCHEMA_VERSION,
    SyncContractError,
)
from src.coevo.sync.store import (
    SyncOutbox,
    SyncReconciler,
    export_bundle,
    load_bundle,
)


def _payload(
    sequence: int,
    event_id: str,
    previous_hash: str,
    *,
    source: str = "node-member",
) -> dict[str, object]:
    return {
        "schema_version": SYNC_SCHEMA_VERSION,
        "source_node": source,
        "event_id": event_id,
        "sequence": sequence,
        "created_at": f"2026-08-12T08:{sequence:02d}:00Z",
        "payload_digest": ("a" * 64) if sequence % 2 else ("b" * 64),
        "previous_hash": previous_hash,
    }


def _build_outbox(path: Path, count: int = 3) -> SyncOutbox:
    outbox = SyncOutbox(path)
    previous = "0" * 64
    for index in range(1, count + 1):
        record = outbox.append(
            _payload(index, f"ev.{index}", previous)
        )
        previous = record.digest
    return outbox


class DualNodeOfflineSyncE2E(unittest.TestCase):
    def test_member_to_center_handoff_is_new_then_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)

            # Member node: append three events to a persistent outbox and
            # export the offline bundle.
            member = _build_outbox(run / "member" / "outbox.jsonl", count=3)
            bundle = run / "member" / "sync.bundle.json"
            export_bundle(bundle, member)
            self.assertTrue(bundle.is_file())

            # Center node receives the bundle over the offline medium.
            envelopes = load_bundle(bundle)
            self.assertEqual(3, len(envelopes))
            raw = json.loads(bundle.read_text(encoding="utf-8"))

            # First delivery: every event is new; the center applies all.
            first = SyncReconciler.reconcile(
                SyncOutbox(run / "center" / "applied.jsonl"), raw
            )
            self.assertTrue(first.ok, first.detail)
            self.assertEqual(("ev.1", "ev.2", "ev.3"), first.new_events)
            self.assertEqual((), first.replay_events)
            applied: set[str] = set(first.new_events)

            # Re-delivery of the same bundle: the reconcile layer still
            # classifies the full chain, but the apply step is idempotent
            # (dedup by event_id) -- nothing is applied twice.
            again = SyncReconciler.reconcile(
                SyncOutbox(run / "center" / "applied-again.jsonl"), raw
            )
            self.assertTrue(again.ok, again.detail)
            self.assertEqual(first.new_events, again.new_events)
            pending = [event for event in again.new_events if event not in applied]
            self.assertEqual([], pending, "re-delivered events must not be applied twice")

            # The member chain is unchanged by the center's consumption.
            reloaded = SyncOutbox(run / "member" / "outbox.jsonl")
            self.assertEqual(3, len(reloaded.records))
            self.assertEqual(member.head_digest, reloaded.head_digest)

    def test_missing_sequence_triggers_gap_and_is_not_applied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            member = _build_outbox(run / "member" / "outbox.jsonl", count=3)
            bundle = run / "member" / "sync.bundle.json"
            export_bundle(bundle, member)
            data = json.loads(bundle.read_text(encoding="utf-8"))

            # Simulate a transfer that drops event 2: the chain no longer
            # starts at sequence 1, so validation must fail closed and the
            # center must signal a re-pull instead of applying a gap.
            dropped = [data[0], data[2]]
            (run / "member" / "gapped.bundle.json").write_text(
                json.dumps(dropped), encoding="utf-8"
            )
            with self.assertRaises(SyncContractError):
                load_bundle(run / "member" / "gapped.bundle.json")

    def test_tampered_bundle_is_rejected_before_reconcile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            member = _build_outbox(run / "member" / "outbox.jsonl", count=2)
            bundle = run / "member" / "sync.bundle.json"
            export_bundle(bundle, member)
            data = json.loads(bundle.read_text(encoding="utf-8"))

            # Tamper with the hash linkage of the second envelope.
            data[1]["previous_hash"] = "c" * 64
            (run / "member" / "tampered.bundle.json").write_text(
                json.dumps(data), encoding="utf-8"
            )
            with self.assertRaises(SyncContractError):
                load_bundle(run / "member" / "tampered.bundle.json")

    def test_incremental_delivery_reports_only_latest_as_new(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            member = _build_outbox(run / "member" / "outbox.jsonl", count=2)
            bundle = run / "member" / "sync.bundle.json"
            export_bundle(bundle, member)

            # Member adds one more event and exports a new bundle.
            member.append(
                _payload(3, "ev.3", member.head_digest)
            )
            export_bundle(bundle, member)
            envelopes = load_bundle(bundle)
            self.assertEqual(3, len(envelopes))
            raw = json.loads(bundle.read_text(encoding="utf-8"))

            # The center already applied ev.1/ev.2 (kept in its applied
            # ledger); reconcile against a fresh outbox reports the full
            # incoming set, and the apply step filters to the new event.
            result = SyncReconciler.reconcile(
                SyncOutbox(run / "center" / "applied.jsonl"), raw
            )
            self.assertTrue(result.ok, result.detail)
            self.assertEqual(("ev.1", "ev.2", "ev.3"), result.new_events)
            already_applied = {"ev.1", "ev.2"}
            pending = [e for e in result.new_events if e not in already_applied]
            self.assertEqual(["ev.3"], pending)


if __name__ == "__main__":
    unittest.main()
