"""Security probes for the persistent signed receipt chain."""
from __future__ import annotations

import sys
import unittest
from unittest import mock
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.coevo.merge.repository import (
    MergeReceiptRepository, MergeReceiptRepositoryError,
    MergeReceiptRepositoryRecoveryRequired,
    _ROW_PAYLOAD_MAX_BYTES, _ROW_SIGNATURE_MAX_BYTES,
    _ROW_RECEIPT_ID_PREFIX, _ROW_HASH_HEX_LEN,
    _validate_row_shape,
)
from src.coevo.merge.receipt import _RECEIPT_MAX_BYTES
import src.coevo.merge.repository as repository_module
from src.coevo.report import ReportStatus
from tests.unit.test_merge_commit_receipt import (
    baseline, committed, new_repository, report, repository_for,
)

NOW = datetime(2026, 8, 21, tzinfo=UTC)


class MergeReceiptRepositorySecurityTests(unittest.TestCase):
    @staticmethod
    def _state(repository):
        tail = repository.connection.execute(
            "SELECT store_sequence,receipt_id,receipt_hash FROM merge_receipts "
            "ORDER BY store_sequence DESC LIMIT 1"
        ).fetchone()
        return (
            repository.connection.execute(
                "SELECT COUNT(*) FROM merge_receipts"
            ).fetchone()[0],
            tuple(tail) if tail else None,
            repository._checkpoint(),
            repository.anchor.head.read_bytes(),
            repository.anchor.signature.read_bytes(),
            repository.anchor.marker_signature.read_bytes(),
        )

    @staticmethod
    def _assert_no_pending(repository):
        self_pending = (
            repository.anchor.pending_head,
            repository.anchor.pending_signature,
            repository.anchor.pending_new_signature,
            repository.anchor.pending_old_signature,
        )
        if any(path.exists() for path in self_pending):
            raise AssertionError("repository left a pending anchor artifact")

    def test_signed_chain_binds_store_head_sequence_and_previous_hash(self):
        first = committed()
        repository = repository_for(first)
        second = committed(
            current_baseline=first.proposal.new_baseline,
            manifest=report(
                task_id="TASK-002", status=ReportStatus.COMPLETED,
                version=2, sequence_no=2,
            ),
            store=first.proposal.record.store_post,
            receipt_repository=repository,
        )
        assert first.receipt and second.receipt
        self.assertEqual(first.receipt.store_id, second.receipt.store_id)
        self.assertEqual(2, second.receipt.store_sequence)
        self.assertEqual(first.receipt.receipt_id, second.receipt.previous_receipt_id)
        self.assertEqual(2, len(repository.verified_history(trusted_time=NOW)))

    def test_truncation_is_rejected_by_freshness_checkpoint(self):
        outcome = committed()
        repository = repository_for(outcome)
        repository.connection.execute("DELETE FROM merge_receipts")
        with self.assertRaises(Exception):
            repository.get_verified(outcome.receipt.receipt_id, trusted_time=NOW)

    def test_history_reorder_or_substitution_is_rejected_by_per_row_verification(self):
        first = committed()
        repository = repository_for(first)
        second = committed(
            current_baseline=first.proposal.new_baseline,
            manifest=report(
                task_id="TASK-002", status=ReportStatus.COMPLETED,
                version=2, sequence_no=2,
            ),
            store=first.proposal.record.store_post,
            receipt_repository=repository,
        )
        rows = repository.connection.execute(
            "SELECT store_sequence,payload,signature FROM merge_receipts ORDER BY store_sequence"
        ).fetchall()
        repository.connection.execute(
            "UPDATE merge_receipts SET payload=?,signature=? WHERE store_sequence=1",
            (rows[1]["payload"], rows[1]["signature"]),
        )
        with self.assertRaises(MergeReceiptRepositoryError):
            repository.verified_history(trusted_time=NOW)

    def test_precommit_anchor_failure_leaves_rows_head_and_checkpoint_unchanged(self):
        repository = new_repository()
        before = repository._checkpoint()
        original_prepare = repository.anchor.prepare

        def fail_prepare(checkpoint):
            raise RuntimeError("injected prepare failure")

        repository.anchor.prepare = fail_prepare
        try:
            with self.assertRaises(RuntimeError):
                committed(receipt_repository=repository)
        finally:
            repository.anchor.prepare = original_prepare
        self.assertEqual(before, repository._checkpoint())
        self.assertEqual(0, repository.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])

    def test_promote_failure_requires_recovery_and_reopen_commits_exactly_once(self):
        repository = new_repository()
        database = repository.database
        authority = repository._authority
        signer = repository.anchor.signer
        freshness = repository.anchor.freshness
        original_promote = repository.anchor.promote

        def fail_promote():
            raise RuntimeError("injected promote failure")

        repository.anchor.promote = fail_promote
        with self.assertRaises(MergeReceiptRepositoryRecoveryRequired) as raised:
            committed(receipt_repository=repository)
        receipt_id = raised.exception.receipt_id
        self.assertEqual(1, repository.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])
        repository.anchor.promote = original_promote
        repository.close()
        recovered = MergeReceiptRepository.open(
            database, authority, signer, freshness,
        )
        try:
            history = recovered.verified_history(trusted_time=NOW)
            self.assertEqual(1, len(history))
            self.assertEqual(receipt_id, history[0].receipt_id)
        finally:
            recovered.close()

    def test_stale_baseline_is_rejected_before_insert(self):
        first = committed()
        repository = repository_for(first)
        before = self._state(repository)
        stale = baseline(version=1)
        outcome = committed(
            current_baseline=first.proposal.new_baseline,
            manifest=report(version=1, sequence_no=2),
            store=first.proposal.record.store_post,
            receipt_repository=repository,
        )
        self.assertFalse(outcome.proposal.accepted)
        self.assertEqual(first.proposal.new_baseline, outcome.proposal.new_baseline)
        self.assertEqual(before, self._state(repository))
        self.assertEqual(first.proposal.record.store_post, outcome.proposal.record.store_post)
        self.assertEqual(1, stale.version)
        self._assert_no_pending(repository)

    def test_nonmonotonic_sender_recipient_project_sequence_is_rejected_before_insert(self):
        first = committed(manifest=report(sequence_no=2))
        repository = repository_for(first)
        before = self._state(repository)
        current = first.proposal.new_baseline
        outcome = committed(
            current_baseline=current,
            manifest=report(version=2, sequence_no=1),
            store=first.proposal.record.store_post,
            receipt_repository=repository,
        )
        self.assertFalse(outcome.proposal.accepted)
        self.assertEqual(current, outcome.proposal.new_baseline)
        self.assertEqual(before, self._state(repository))
        self.assertEqual(first.proposal.record.store_post, outcome.proposal.record.store_post)
        self._assert_no_pending(repository)

    def test_package_id_and_digest_replay_are_rejected_before_insert(self):
        first = committed()
        repository = repository_for(first)
        before = self._state(repository)
        current = first.proposal.new_baseline
        outcome = committed(
            current_baseline=current,
            manifest=report(version=2, sequence_no=1),
            receipt_repository=repository,
        )
        self.assertFalse(outcome.proposal.accepted)
        self.assertEqual(current, outcome.proposal.new_baseline)
        self.assertEqual(before, self._state(repository))
        self.assertEqual(0, len(outcome.proposal.record.store_post))
        self._assert_no_pending(repository)

    def test_decode_failure_is_rejected_before_insert_atomically(self):
        first = committed()
        repository = repository_for(first)
        repository.connection.execute(
            "UPDATE merge_receipts SET payload=? WHERE store_sequence=1",
            (b'{"not":"a receipt"}',),
        )
        before = self._state(repository)
        with self.assertRaises(MergeReceiptRepositoryError):
            committed(
                current_baseline=first.proposal.new_baseline,
                manifest=report(
                    task_id="TASK-002", version=2, sequence_no=2,
                ),
                store=first.proposal.record.store_post,
                receipt_repository=repository,
            )
        self.assertEqual(before, self._state(repository))
        self.assertEqual(1, repository.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])
        self._assert_no_pending(repository)

    def test_oversized_history_is_rejected_before_parse_and_insert_atomically(self):
        first = committed()
        repository = repository_for(first)
        repository.connection.execute(
            "UPDATE merge_receipts SET payload=? WHERE store_sequence=1",
            (b"x" * (_RECEIPT_MAX_BYTES + 1),),
        )
        before = self._state(repository)
        guarded_json = mock.Mock(wraps=repository_module.json)
        guarded_json.loads.side_effect = AssertionError(
            "oversized history must not be parsed"
        )
        with mock.patch.object(repository_module, "json", guarded_json):
            with self.assertRaises(MergeReceiptRepositoryError):
                committed(
                    current_baseline=first.proposal.new_baseline,
                    manifest=report(
                        task_id="TASK-002", version=2, sequence_no=2,
                    ),
                    store=first.proposal.record.store_post,
                    receipt_repository=repository,
                )
        self.assertEqual(before, self._state(repository))
        self.assertEqual(first.proposal.new_baseline.version, 2)
        self.assertEqual(1, repository.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])
        self._assert_no_pending(repository)
    def test_oversized_payload_row_is_rejected_before_parse_atomically(self):
        first = committed()
        repository = repository_for(first)
        before = self._state(repository)
        repository.connection.execute(
            "UPDATE merge_receipts SET payload=? WHERE store_sequence=1",
            (b"x" * (_ROW_PAYLOAD_MAX_BYTES + 1),),
        )
        guarded_json = mock.Mock(wraps=repository_module.json)
        guarded_json.loads.side_effect = AssertionError(
            "oversized payload row must not be parsed"
        )
        guarded_b64 = mock.Mock(wraps=repository_module.base64)
        guarded_b64.b64decode.side_effect = AssertionError(
            "oversized payload row must not be base64-decoded"
        )
        with mock.patch.object(repository_module, "json", guarded_json), \
             mock.patch.object(repository_module, "base64", guarded_b64):
            with self.assertRaises(MergeReceiptRepositoryError):
                committed(
                    current_baseline=first.proposal.new_baseline,
                    manifest=report(
                        task_id="TASK-002", version=2, sequence_no=2,
                    ),
                    store=first.proposal.record.store_post,
                    receipt_repository=repository,
                )
        self.assertEqual(before, self._state(repository))
        self.assertEqual(1, repository.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])
        self._assert_no_pending(repository)

    def test_oversized_signature_row_is_rejected_before_parse_atomically(self):
        first = committed()
        repository = repository_for(first)
        before = self._state(repository)
        repository.connection.execute(
            "UPDATE merge_receipts SET signature=? WHERE store_sequence=1",
            (b"s" * (_ROW_SIGNATURE_MAX_BYTES + 1),),
        )
        guarded_json = mock.Mock(wraps=repository_module.json)
        guarded_json.loads.side_effect = AssertionError(
            "oversized signature row must not be parsed"
        )
        with mock.patch.object(repository_module, "json", guarded_json):
            with self.assertRaises(MergeReceiptRepositoryError):
                committed(
                    current_baseline=first.proposal.new_baseline,
                    manifest=report(
                        task_id="TASK-002", version=2, sequence_no=2,
                    ),
                    store=first.proposal.record.store_post,
                    receipt_repository=repository,
                )
        self.assertEqual(before, self._state(repository))
        self.assertEqual(1, repository.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])
        self._assert_no_pending(repository)

    def test_invalid_receipt_id_row_is_rejected_before_parse_atomically(self):
        first = committed()
        repository = repository_for(first)
        repository.connection.execute(
            "UPDATE merge_receipts SET receipt_id=? WHERE store_sequence=1",
            ("not-a-valid-receipt-id",),
        )
        guarded_json = mock.Mock(wraps=repository_module.json)
        guarded_json.loads.side_effect = AssertionError(
            "invalid receipt_id row must not be parsed"
        )
        with mock.patch.object(repository, "_recover", lambda: None):
            with mock.patch.object(repository_module, "json", guarded_json):
                with self.assertRaises(MergeReceiptRepositoryError):
                    repository.verified_history(trusted_time=NOW)
        self.assertEqual(1, repository.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])
        self._assert_no_pending(repository)

    def test_invalid_receipt_hash_row_is_rejected_before_parse_atomically(self):
        first = committed()
        repository = repository_for(first)
        repository.connection.execute(
            "UPDATE merge_receipts SET receipt_hash=? WHERE store_sequence=1",
            ("Z" * _ROW_HASH_HEX_LEN,),
        )
        guarded_json = mock.Mock(wraps=repository_module.json)
        guarded_json.loads.side_effect = AssertionError(
            "invalid receipt_hash row must not be parsed"
        )
        with mock.patch.object(repository, "_recover", lambda: None):
            with mock.patch.object(repository_module, "json", guarded_json):
                with self.assertRaises(MergeReceiptRepositoryError):
                    repository.verified_history(trusted_time=NOW)
        self.assertEqual(1, repository.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])
        self._assert_no_pending(repository)

    def test_row_shape_validator_rejects_each_oversize_and_malformed_column(self):
        class _FakeRow:
            def __init__(self, mapping):
                self._mapping = mapping
            def __getitem__(self, key):
                return self._mapping[key]
        good_id = _ROW_RECEIPT_ID_PREFIX + "a" * 64
        base = {
            "store_sequence": 1,
            "receipt_id": good_id,
            "payload": b"x",
            "signature": b"s",
            "receipt_hash": "0" * 64,
        }
        _validate_row_shape(_FakeRow(base))
        mutated = [
            dict(base, store_sequence=0),
            dict(base, store_sequence="1"),
            dict(base, receipt_id=""),
            dict(base, receipt_id="mcr." + "g" * 64),
            dict(base, receipt_id="pkg.1"),
            dict(base, payload=b""),
            dict(base, payload="x"),
            dict(base, payload=b"x" * (_ROW_PAYLOAD_MAX_BYTES + 1)),
            dict(base, signature=b""),
            dict(base, signature=b"s" * (_ROW_SIGNATURE_MAX_BYTES + 1)),
            dict(base, signature="sig"),
            dict(base, receipt_hash="" * 64),
            dict(base, receipt_hash="Z" * 64),
            dict(base, receipt_hash=1234567890),
        ]
        for index, row_mapping in enumerate(mutated):
            with self.subTest(case=index):
                with self.assertRaises(MergeReceiptRepositoryError):
                    _validate_row_shape(_FakeRow(row_mapping))

    def test_pre_insert_history_iteration_rejects_malformed_row_atomically(self):
        # Exercise the SAME SQL path the INSERT path uses, without
        # triggering the freshness-anchor recover() (which would
        # mask the row guard by failing earlier on the tampered
        # checkpoint). The contract: a malformed first row must
        # short-circuit _iter_verified_history at the row guard,
        # before any subsequent row is materialised and before
        # any INSERT runs.
        bad = committed()
        bad_repo = repository_for(bad)
        bad_repo.connection.execute(
            "UPDATE merge_receipts SET receipt_id=? WHERE store_sequence=1",
            ("definitely-not-mcr-prefixed",),
        )
        guarded_json = mock.Mock(wraps=repository_module.json)
        guarded_json.loads.side_effect = AssertionError(
            "malformed row must not be parsed by json.loads"
        )
        with mock.patch.object(bad_repo, "_recover", lambda: None):
            with mock.patch.object(repository_module, "json", guarded_json):
                with self.assertRaises(MergeReceiptRepositoryError):
                    bad_repo._iter_verified_history(trusted_time=NOW)
        self.assertEqual(1, bad_repo.connection.execute(
            "SELECT COUNT(*) FROM merge_receipts"
        ).fetchone()[0])
        self._assert_no_pending(bad_repo)


if __name__ == "__main__":
    unittest.main()
