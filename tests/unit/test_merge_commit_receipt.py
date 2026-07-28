"""Unit tests for authoritative US-10 merge commit receipts."""
from __future__ import annotations

import dataclasses
import copy
import atexit
import datetime as dt
import hashlib
import base64
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.coevo.merge import MergeEngine
from src.coevo.merge.receipt import (
    MergeCommitReceiptError,
    MergeCommitReceiptStore,
    ReceiptSigningAuthority,
    _RECEIPT_MAX_BYTES,
    _SNAPSHOT_BASE64_MAX_CHARS,
    _SNAPSHOT_MAX_BYTES,
    _encode,
    _normalize_canonical_plain,
    canonical_baseline_digest,
    build_signed_merge_commit_receipt,
    freeze_baseline,
    verify_signed_receipt,
)
from src.coevo.merge.repository import MergeReceiptRepository
from src.coevo.merge.repository import MergeReceiptRepositoryError, _decode_receipt
from src.coevo.identity import PrivateKeyReference, PrivateKeyService
from src.coevo.identity.audit_anchor import AuditAnchorError
from src.coevo.protocol.import_service import ImportOutcome
from src.coevo.protocol.import_transaction import ImportStep, ImportTransaction
from src.coevo.protocol.processed_package_store import (
    ProcessedPackageRecord,
    ProcessedPackageStore,
)
from src.coevo.protocol.replay_detector import ProcessedPackage
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import (
    DependencyEdge,
    Deliverable,
    Milestone,
    ProjectBaseline,
    Task,
    WorkPackage,
)
from src.coevo.task_decomposition.models import Override
from tests.support_identity import TestFreshnessAuthority, TestSigner

_REPOSITORY_RESOURCES: list[tuple[tempfile.TemporaryDirectory, MergeReceiptRepository]] = []


def _cleanup_repositories():
    for temporary, repository in reversed(_REPOSITORY_RESOURCES):
        repository.close()
        temporary.cleanup()


atexit.register(_cleanup_repositories)


class _Freshness(TestFreshnessAuthority):
    def load_retirement(self, tombstone):
        try:
            return super().load_retirement(tombstone)
        except Exception as exc:
            raise AuditAnchorError("test retirement tombstone is missing") from exc


def baseline(*, version: int = 1, title: str = "Alpha") -> ProjectBaseline:
    tasks = tuple(
        Task(
            task_id=task_id, title=task_id, responsible_role="owner",
            plan_start="2026-08-01T00:00:00Z",
            plan_end="2026-08-31T00:00:00Z",
            deliverables=(Deliverable(
                f"D-{task_id}", "Result", "document", ("accepted",),
            ),),
        )
        for task_id in ("TASK-001", "TASK-002", "TASK-003")
    )
    return ProjectBaseline(
        project_id="PRJ001", version=version,
        created_at="2026-08-01T00:00:00Z", title=title,
        process_flow_ref=("unit_a", 1), objective="Ship MVP",
        plan_start="2026-08-01T00:00:00Z",
        plan_end="2026-08-31T00:00:00Z",
        responsible_units=("unit_a",),
        work_packages=(WorkPackage("WP-001", "execution", "Execution", tasks),),
        dependencies=(
            DependencyEdge("TASK-001", "TASK-002", "fs"),
            DependencyEdge("TASK-002", "TASK-003", "fs"),
        ),
        milestones=(Milestone(
            "M-001", "Done", "2026-08-31T00:00:00Z", "WP-001",
        ),),
    )


def report(
    *,
    task_id: str = "TASK-001",
    status: ReportStatus = ReportStatus.COMPLETED,
    version: int = 1,
    sequence_no: int = 1,
    completed_work: tuple[str, ...] = ("free text",),
) -> ReportManifest:
    return ReportManifest(
        schema_version="1.0", package_id=f"pkg-{sequence_no}",
        package_type="RESULT_SUBMISSION", project_id="PRJ001",
        task_id=task_id, base_revision=f"PRJ001-R{version:04d}",
        sequence_no=sequence_no, submitted_at="2026-08-19T00:00:00Z",
        sender_user_id="USR021", sender_client_id="CLI021",
        sender_organization_id="ORG002", sender_cert_id="CERT-SENDER",
        recipient_user_id="USR001", recipient_client_id="CLI001",
        recipient_organization_id="ORG001", recipient_cert_id="CERT-OWNER",
        status=status, progress_summary="progress",
        completed_work=completed_work, pending_work=(), next_steps=(),
        risks=(), artifacts=(),
    )


def imported(manifest: ReportManifest) -> ImportOutcome:
    digest = hashlib.sha256(manifest.package_id.encode("utf-8")).hexdigest()
    package = ProcessedPackage(
        package_id=manifest.package_id, package_digest=digest,
        sender_cert_id=manifest.sender_cert_id,
        recipient_cert_id=manifest.recipient_cert_id,
        project_id=manifest.project_id, sequence_no=manifest.sequence_no,
    )
    record = ProcessedPackageRecord(
        package=package, package_type=manifest.package_type,
        processed_at="2026-08-19T01:00:00Z", result="committed",
        revision=manifest.base_revision,
    )
    transaction = ImportTransaction(
        package_id=manifest.package_id, project_id=manifest.project_id,
        base_revision=manifest.base_revision,
        current_revision=manifest.base_revision, step=ImportStep.COMMITTED,
    )
    return ImportOutcome(
        transaction=transaction, store=ProcessedPackageStore.empty(),
        record=record,
    )


class _SigningStore:
    def use(self, reference, payload):
        return hashlib.sha256(reference.key_id.encode() + bytes(payload)).digest()

    def verify(self, reference, payload, signature, *, parent_pinned_thumbprint):
        return (
            parent_pinned_thumbprint == "PIN-ROOT"
            and signature == self.use(reference, payload)
        )

    def verify_handle(self, reference):
        return None

    def destroy(self, reference):
        return None

    def revoke(self, reference, *, reason):
        return None

    def store(self, certificate_id, payload, *, parent_pinned_thumbprint=None):
        raise AssertionError("not used")


def signing_authority() -> ReceiptSigningAuthority:
    reference = PrivateKeyReference(
        key_id="CoevoPrivateKey-" + "a" * 32,
        algorithm_oid="1.2.840.113549.1.1.1",
        key_public_sha256="b" * 64,
        valid_from=dt.datetime(2026, 1, 1, tzinfo=dt.UTC),
        valid_to=dt.datetime(2027, 1, 1, tzinfo=dt.UTC),
        bound_certificate_id="CERT-OWNER", revoked=False,
        handle_token_hint="a" * 16,
    )
    return ReceiptSigningAuthority(
        service=PrivateKeyService(_SigningStore()), reference=reference,
        signer_certificate_id="CERT-OWNER",
        parent_pinned_thumbprint="PIN-ROOT",
    )


def committed(
    *,
    current_baseline: ProjectBaseline | None = None,
    manifest: ReportManifest | None = None,
    store: ProcessedPackageStore | None = None,
    receipt_repository: MergeReceiptRepository | None = None,
    authority: ReceiptSigningAuthority | None = None,
):
    base = current_baseline or baseline()
    report_value = manifest or report(version=base.version)
    selected_authority = authority or signing_authority()
    if receipt_repository is None:
        receipt_repository = new_repository(selected_authority)
    return MergeEngine(
        receipt_repository=receipt_repository,
        receipt_authority=selected_authority,
    ).merge_and_commit(
        import_outcome=imported(report_value), report=report_value,
        baseline=base, store=store or ProcessedPackageStore.empty(),
        decided_at="2026-08-20T00:00:00Z",
    )


def new_repository(authority=None):
    selected_authority = authority or signing_authority()
    temporary = tempfile.TemporaryDirectory(delete=False)
    repository = MergeReceiptRepository.create(
        Path(temporary.name) / "receipts.sqlite3", selected_authority,
        TestSigner(), _Freshness(),
    )
    _REPOSITORY_RESOURCES.append((temporary, repository))
    return repository


def commit_override_receipt(source):
    authority = signing_authority()
    repository = new_repository(authority)
    trusted_time = dt.datetime(2026, 8, 20, tzinfo=dt.UTC)

    def builder(store_id, store_sequence, previous_id, previous_hash):
        return build_signed_merge_commit_receipt(
            authority=authority, trusted_time=trusted_time, baseline=source,
            store_id=store_id, store_sequence=store_sequence,
            previous_receipt_id=previous_id,
            previous_receipt_hash=previous_hash,
            package_id="pkg-override",
            package_digest=hashlib.sha256(b"pkg-override").hexdigest(),
            sender_cert_id="CERT-SENDER", recipient_cert_id="CERT-OWNER",
            sequence_no=1, package_type="RESULT_SUBMISSION",
            import_processed_at="2026-08-19T01:00:00Z",
            project_id=source.project_id, task_id="TASK-001",
            report_status=ReportStatus.COMPLETED, status_decision="accept",
            base_revision="PRJ001-R0001", current_revision="PRJ001-R0001",
            merged_revision="PRJ001-R0002",
            commit_decided_at="2026-08-20T00:00:00Z",
            decision_maker="CERT-OWNER",
            baseline_digest_algorithm="sha256",
            baseline_schema="coevo.project-baseline/1.0",
            completed_task_id="TASK-001",
        )

    receipt = repository.commit(builder, trusted_time=trusted_time)
    return repository, receipt


class MergeCommitReceiptTests(unittest.TestCase):
    def test_canonical_plain_exact_types_order_and_legacy_bytes(self):
        first = {"z": (None, "text", 7), "a": {"nested": True}}
        second = {"a": {"nested": True}, "z": [None, "text", 7]}
        normalized_first = _normalize_canonical_plain(first)
        normalized_second = _normalize_canonical_plain(second)
        self.assertEqual(normalized_first, normalized_second)
        self.assertEqual(["a", "z"], list(normalized_first))
        self.assertEqual(
            "353a4061ddbfda48850d5a1eb00af38f04c5c389f5b172b520d1de56b754da10",
            freeze_baseline(dataclasses.replace(
                baseline(),
                overrides=(Override("x", None, ("s", 3), "r"),),
            )).digest,
        )

        class StringSubclass(str):
            pass

        class IntegerSubclass(int):
            pass

        class ListSubclass(list):
            pass

        class DictSubclass(dict):
            pass

        forbidden = (
            1.0, b"bytes", {1}, object(), StringSubclass("x"),
            IntegerSubclass(1), ListSubclass(), DictSubclass(), {1: "value"},
        )
        for value in forbidden:
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(MergeCommitReceiptError):
                    _normalize_canonical_plain(value)

    def test_canonical_plain_limits_have_exact_boundaries_and_global_budget(self):
        def nested(levels):
            value = "leaf"
            for _ in range(levels):
                value = [value]
            return value

        self.assertEqual(nested(32), _normalize_canonical_plain(nested(32)))
        with self.assertRaises(MergeCommitReceiptError):
            _normalize_canonical_plain(nested(33))
        self.assertEqual(4096, len(_normalize_canonical_plain([None] * 4096)))
        with self.assertRaises(MergeCommitReceiptError):
            _normalize_canonical_plain([None] * 4097)
        self.assertEqual("x" * (1024 * 1024), _normalize_canonical_plain(
            "x" * (1024 * 1024),
        ))
        with self.assertRaises(MergeCommitReceiptError):
            _normalize_canonical_plain("x" * (1024 * 1024 + 1))

        at_limit = {f"k{index:02d}": [None] * 4096 for index in range(24)}
        at_limit["k24"] = [None] * 1670
        self.assertEqual(at_limit, _normalize_canonical_plain(at_limit))
        over_limit = dict(at_limit)
        over_limit["k24"] = [None] * 1671
        with self.assertRaises(MergeCommitReceiptError):
            _normalize_canonical_plain(over_limit)

    def test_canonical_plain_total_utf8_counts_keys_values_and_alias_occurrences(self):
        at_limit = {
            "a": "x" * (1024 * 1024 - 1),
            "b": "y" * (1024 * 1024 - 1),
        }
        self.assertEqual(at_limit, _normalize_canonical_plain(at_limit))
        over_limit = dict(at_limit)
        over_limit["b"] += "z"
        with self.assertRaises(MergeCommitReceiptError):
            _normalize_canonical_plain(over_limit)

        shared = "s" * (1024 * 1024)
        self.assertEqual([shared, shared], _normalize_canonical_plain(
            [shared, shared],
        ))
        with self.assertRaises(MergeCommitReceiptError):
            _normalize_canonical_plain([shared] * 4096)

    def test_bounded_encoder_rejects_escaped_structure_and_huge_int_before_join(self):
        escaped = _normalize_canonical_plain("\x00" * 400000)
        with self.assertRaises(MergeCommitReceiptError):
            _encode(escaped, max_bytes=_SNAPSHOT_MAX_BYTES)
        structural = _normalize_canonical_plain({
            "a": "x" * (1024 * 1024 - 1),
            "b": "y" * (1024 * 1024 - 1),
        })
        with self.assertRaises(MergeCommitReceiptError):
            _encode(structural, max_bytes=_SNAPSHOT_MAX_BYTES)

        huge = 1 << 7000000
        with mock.patch.object(
            json.JSONEncoder, "iterencode",
            side_effect=AssertionError("encoder must not materialize huge integer"),
        ):
            with self.assertRaises(MergeCommitReceiptError):
                _encode(huge, max_bytes=_SNAPSHOT_MAX_BYTES)

    def test_repository_size_guards_run_before_parse_or_base64_decode(self):
        import src.coevo.merge.repository as repository_module

        with mock.patch.object(
            repository_module.json, "loads",
            side_effect=AssertionError("oversized receipt must not be parsed"),
        ):
            with self.assertRaises(MergeReceiptRepositoryError):
                _decode_receipt(
                    "mcr.test", b"x" * (_RECEIPT_MAX_BYTES + 1), b"sig",
                )

        for snapshot_base64 in (
            "A" * (_SNAPSHOT_BASE64_MAX_CHARS + 1),
            "A" * _SNAPSHOT_BASE64_MAX_CHARS,
        ):
            with self.subTest(length=len(snapshot_base64)):
                with (
                    mock.patch.object(
                        repository_module.json, "loads",
                        return_value={"snapshot_payload_base64": snapshot_base64},
                    ),
                    mock.patch.object(
                        repository_module.base64, "b64decode",
                        side_effect=AssertionError(
                            "oversized base64 must not be decoded"
                        ),
                    ),
                ):
                    with self.assertRaises(MergeReceiptRepositoryError):
                        _decode_receipt("mcr.test", b"{}", b"sig")

        loads = mock.Mock(return_value={"snapshot_payload_base64": "AAAA"})
        with (
            mock.patch.object(repository_module.json, "loads", loads),
            mock.patch.object(
                repository_module.base64, "b64decode",
                return_value=b"x" * (_SNAPSHOT_MAX_BYTES + 1),
            ),
        ):
            with self.assertRaises(MergeReceiptRepositoryError):
                _decode_receipt("mcr.test", b"{}", b"sig")
        self.assertEqual(1, loads.call_count)

    def test_canonical_plain_rejects_cycles_and_decode_rejects_tuple(self):
        cyclic = []
        cyclic.append(cyclic)
        with self.assertRaises(MergeCommitReceiptError):
            _normalize_canonical_plain(cyclic)
        with self.assertRaises(MergeCommitReceiptError):
            _normalize_canonical_plain(("allowed-for-freeze",), allow_tuple=False)

    def test_freeze_copies_override_values_and_detects_snapshot_mutation(self):
        original_value = [{"z": 1, "a": [None, True]}]
        edited_value = {"items": ["first", "second"]}
        source = dataclasses.replace(
            baseline(),
            overrides=(Override(
                "title", original_value, edited_value, "approved",
            ),),
        )
        snapshot = freeze_baseline(source)
        original_value[0]["a"].append("caller mutation")
        edited_value["items"].reverse()
        frozen_override = snapshot.baseline.overrides[0]
        self.assertEqual([{"a": [None, True], "z": 1}], frozen_override.original_value)
        self.assertEqual({"items": ["first", "second"]}, frozen_override.edited_value)
        self.assertIsNot(source, snapshot.baseline)
        self.assertIsNot(source.overrides[0], frozen_override)

        frozen_override.edited_value["items"].append(1.5)
        with self.assertRaises(MergeCommitReceiptError):
            freeze_baseline(snapshot.baseline)

        _, receipt = commit_override_receipt(source)
        receipt.snapshot.baseline.overrides[0].edited_value["items"].append(
            "snapshot mutation"
        )
        with self.assertRaises(MergeCommitReceiptError):
            verify_signed_receipt(
                receipt, authority=signing_authority(),
                trusted_time=dt.datetime(2026, 8, 21, tzinfo=dt.UTC),
            )

    def test_signing_uses_detached_override_copy_under_caller_mutation(self):
        authority = signing_authority()
        original = [{"nested": ["before"]}]
        edited = {"status": [True, 2, None]}
        source = dataclasses.replace(
            baseline(), version=2, created_at="2026-08-20T00:00:00Z",
            overrides=(Override("title", original, edited, "approved"),),
        )
        repository, receipt = commit_override_receipt(source)
        payload = receipt.payload
        original[0]["nested"].append("after")
        edited["status"].clear()
        verified = repository.get_verified(
            receipt.receipt_id,
            trusted_time=dt.datetime(2026, 8, 21, tzinfo=dt.UTC),
        )
        self.assertEqual(payload, verified.payload)
        self.assertEqual(
            [{"nested": ["before"]}],
            verified.snapshot.baseline.overrides[0].original_value,
        )
        self.assertEqual(
            {"status": [True, 2, None]},
            verified.snapshot.baseline.overrides[0].edited_value,
        )

    def test_override_target_and_reason_must_be_exact_nonempty_strings(self):
        for override in (
            Override("", None, "x", "reason"),
            Override("title", None, "x", ""),
            Override(7, None, "x", "reason"),
            Override("title", None, "x", 7),
        ):
            with self.subTest(override=override):
                with self.assertRaises(MergeCommitReceiptError):
                    freeze_baseline(dataclasses.replace(
                        baseline(), overrides=(override,),
                    ))

    def test_success_binds_import_report_merge_and_baseline(self):
        outcome = committed()
        self.assertTrue(outcome.proposal.accepted)
        receipt = outcome.receipt
        self.assertIsNotNone(receipt)
        assert receipt is not None
        self.assertEqual("pkg-1", receipt.package_id)
        self.assertEqual(
            hashlib.sha256(b"pkg-1").hexdigest(), receipt.package_digest,
        )
        self.assertEqual("CERT-SENDER", receipt.sender_cert_id)
        self.assertEqual("CERT-OWNER", receipt.recipient_cert_id)
        self.assertEqual(1, receipt.sequence_no)
        self.assertEqual("RESULT_SUBMISSION", receipt.package_type)
        self.assertEqual("2026-08-19T01:00:00Z", receipt.import_processed_at)
        self.assertEqual("PRJ001", receipt.project_id)
        self.assertEqual("TASK-001", receipt.task_id)
        self.assertEqual(ReportStatus.COMPLETED, receipt.report_status)
        self.assertEqual("accept", receipt.status_decision)
        self.assertEqual("PRJ001-R0001", receipt.base_revision)
        self.assertEqual("PRJ001-R0001", receipt.current_revision)
        self.assertEqual("TASK-001", receipt.completed_task_id)
        self.assertEqual("PRJ001-R0002", receipt.merged_revision)
        self.assertEqual("2026-08-20T00:00:00Z", receipt.commit_decided_at)
        self.assertEqual("CERT-OWNER", receipt.decision_maker)
        self.assertEqual("sha256", receipt.baseline_digest_algorithm)
        self.assertEqual("coevo.project-baseline/1.0", receipt.baseline_schema)
        self.assertEqual(
            canonical_baseline_digest(outcome.proposal.new_baseline),
            receipt.baseline_digest,
        )
        self.assertIs(receipt, outcome.receipt_store.get(receipt.receipt_id))

    def test_canonical_digest_changes_with_baseline_content(self):
        original = baseline()
        changed = dataclasses.replace(original, title="Beta")
        self.assertEqual(
            canonical_baseline_digest(original),
            canonical_baseline_digest(dataclasses.replace(original)),
        )
        self.assertNotEqual(
            canonical_baseline_digest(original),
            canonical_baseline_digest(changed),
        )

    def test_each_receipt_field_is_covered_by_content_address(self):
        receipt = committed().receipt
        assert receipt is not None
        replacements = {
            "receipt_id": "mcr." + "0" * 64,
            "package_id": "pkg-other",
            "package_digest": "b" * 64,
            "sender_cert_id": "other-sender",
            "recipient_cert_id": "other-recipient",
            "sequence_no": 2,
            "package_type": "TASK_PROGRESS",
            "import_processed_at": "2026-08-18T00:00:00Z",
            "project_id": "PRJ002",
            "task_id": "TASK-002",
            "report_status": ReportStatus.ON_TRACK,
            "status_decision": "manual",
            "base_revision": "PRJ001-R0000",
            "current_revision": "PRJ001-R0000",
            "merged_revision": "PRJ001-R0003",
            "commit_decided_at": "2026-08-21T00:00:00Z",
            "decision_maker": "other-owner",
            "baseline_digest_algorithm": "sha512",
            "baseline_schema": "other-schema",
            "baseline_digest": "c" * 64,
            "completed_task_id": None,
        }
        for field_name, replacement in replacements.items():
            with self.subTest(field_name=field_name):
                with self.assertRaises(MergeCommitReceiptError):
                    dataclasses.replace(receipt, **{field_name: replacement})

    def test_hold_duplicate_and_receipt_failure_produce_no_receipt(self):
        hold_report = report(status=ReportStatus.AT_RISK)
        hold = committed(manifest=hold_report)
        self.assertFalse(hold.proposal.accepted)
        self.assertIsNone(hold.receipt)
        self.assertEqual(0, len(hold.receipt_store))

        first = committed()
        duplicate = committed(
            store=first.proposal.record.store_post,
            receipt_repository=repository_for(first),
        )
        self.assertFalse(duplicate.proposal.accepted)
        self.assertIsNone(duplicate.receipt)
        self.assertEqual(tuple(first.receipt_store), tuple(duplicate.receipt_store))

        receipt_conflict = committed(receipt_repository=repository_for(first))
        self.assertFalse(receipt_conflict.proposal.accepted)
        self.assertIsNone(receipt_conflict.receipt)
        self.assertEqual(ProcessedPackageStore.empty(), receipt_conflict.proposal.record.store_post)
        self.assertEqual(tuple(first.receipt_store), tuple(receipt_conflict.receipt_store))

    def test_unknown_task_rolls_back_processed_store(self):
        outcome = committed(manifest=report(task_id="TASK-999"))
        self.assertFalse(outcome.proposal.accepted)
        self.assertIsNone(outcome.receipt)
        self.assertEqual(ProcessedPackageStore.empty(), outcome.proposal.record.store_post)

    def test_import_fact_substitutions_roll_back_without_receipt(self):
        manifest = report()
        authoritative = imported(manifest)
        assert authoritative.record is not None
        substitutions = (
            dataclasses.replace(
                authoritative,
                record=dataclasses.replace(authoritative.record, result="rolled_back"),
            ),
            dataclasses.replace(
                authoritative,
                record=dataclasses.replace(
                    authoritative.record, revision="PRJ001-R9999",
                ),
            ),
            dataclasses.replace(
                authoritative,
                record=dataclasses.replace(
                    authoritative.record,
                    package=dataclasses.replace(
                        authoritative.record.package, sequence_no=99,
                    ),
                ),
            ),
            dataclasses.replace(
                authoritative,
                transaction=dataclasses.replace(
                    authoritative.transaction, current_revision="PRJ001-R9999",
                ),
            ),
        )
        for substituted in substitutions:
            with self.subTest(substituted=substituted):
                temporary = tempfile.TemporaryDirectory(delete=False)
                authority = signing_authority()
                repository = MergeReceiptRepository.create(
                    Path(temporary.name) / "receipts.sqlite3", authority,
                    TestSigner(), _Freshness(),
                )
                _REPOSITORY_RESOURCES.append((temporary, repository))
                outcome = MergeEngine(
                    receipt_repository=repository,
                    receipt_authority=authority,
                ).merge_and_commit(
                    import_outcome=substituted, report=manifest,
                    baseline=baseline(), store=ProcessedPackageStore.empty(),
                    decided_at="2026-08-20T00:00:00Z",
                )
                self.assertFalse(outcome.proposal.accepted)
                self.assertIsNone(outcome.receipt)
                self.assertEqual(
                    ProcessedPackageStore.empty(),
                    outcome.proposal.record.store_post,
                )

    def test_snapshot_rejects_subclasses_mutable_containers_and_bool_versions(self):
        class EvilBaseline(ProjectBaseline):
            pass

        with self.assertRaises(MergeCommitReceiptError):
            freeze_baseline(EvilBaseline(**dataclasses.asdict(baseline())))
        object.__setattr__(tampered := baseline(), "responsible_units", ["unit_a"])
        with self.assertRaises(MergeCommitReceiptError):
            freeze_baseline(tampered)
        object.__setattr__(tampered_bool := baseline(), "version", True)
        with self.assertRaises(MergeCommitReceiptError):
            freeze_baseline(tampered_bool)

    def test_store_is_sealed_against_construction_subclass_copy_and_replace(self):
        receipt = committed().receipt
        assert receipt is not None
        with self.assertRaises(MergeCommitReceiptError):
            MergeCommitReceiptStore((receipt,))
        with self.assertRaises(TypeError):
            class EvilStore(MergeCommitReceiptStore):
                pass
        store = MergeCommitReceiptStore.empty()
        with self.assertRaises(MergeCommitReceiptError):
            copy.copy(store)
        with self.assertRaises(TypeError):
            dataclasses.replace(store)

    def test_tampered_signature_and_wrong_trust_pin_are_rejected(self):
        authority = signing_authority()
        receipt = committed(authority=authority).receipt
        assert receipt is not None
        with self.assertRaises(MergeCommitReceiptError):
            dataclasses.replace(receipt, signature=b"tampered")
        wrong = dataclasses.replace(authority, parent_pinned_thumbprint="WRONG-PIN")
        with self.assertRaises(MergeCommitReceiptError):
            verify_signed_receipt(
                receipt, authority=wrong,
                trusted_time=dt.datetime(2026, 8, 21, tzinfo=dt.UTC),
            )

    def test_post_freeze_object_mutation_is_detected_before_analysis(self):
        authority = signing_authority()
        receipt = committed(authority=authority).receipt
        assert receipt is not None
        object.__setattr__(receipt.snapshot.baseline, "title", "mutated-after-sign")
        with self.assertRaises(MergeCommitReceiptError):
            verify_signed_receipt(
                receipt, authority=authority,
                trusted_time=dt.datetime(2026, 8, 21, tzinfo=dt.UTC),
            )

    def test_sign_or_immediate_verify_failure_rolls_back_both_stores(self):
        class RejectVerifyStore(_SigningStore):
            def verify(self, reference, payload, signature, *, parent_pinned_thumbprint):
                return False

        base_authority = signing_authority()
        rejected_authority = dataclasses.replace(
            base_authority, service=PrivateKeyService(RejectVerifyStore()),
        )
        outcome = committed(authority=rejected_authority)
        self.assertFalse(outcome.proposal.accepted)
        self.assertIsNone(outcome.receipt)
        self.assertEqual(ProcessedPackageStore.empty(), outcome.proposal.record.store_post)
        self.assertEqual(0, len(outcome.receipt_store))

    def test_override_round_trips_through_persisted_receipt_decoder(self):
        source = dataclasses.replace(
            baseline(), version=2, created_at="2026-08-20T00:00:00Z",
            overrides=(Override(
                target_path="title", original_value="Alpha",
                edited_value="Approved Alpha", reason="owner approved",
            ),),
        )
        _, receipt = commit_override_receipt(source)
        decoded = _decode_receipt(
            receipt.receipt_id, receipt.payload, receipt.signature,
        )
        self.assertEqual(source.overrides, decoded.snapshot.baseline.overrides)

    def test_override_shape_types_and_noncanonical_snapshot_fail_closed(self):
        source = dataclasses.replace(
            baseline(), version=2, created_at="2026-08-20T00:00:00Z",
            overrides=(Override(
                target_path="title", original_value="Alpha",
                edited_value="Approved Alpha", reason="owner approved",
            ),),
        )
        _, receipt = commit_override_receipt(source)
        envelope = json.loads(receipt.payload)
        snapshot = json.loads(base64.b64decode(
            envelope["snapshot_payload_base64"], validate=True,
        ))
        mutations = (
            lambda item: item["baseline"]["overrides"][0].pop("reason"),
            lambda item: item["baseline"]["overrides"][0].update(
                {"unexpected": "forbidden"}
            ),
            lambda item: item["baseline"]["overrides"][0].update(
                {"target_path": 7}
            ),
            lambda item: item["baseline"]["overrides"][0].update(
                {"edited_value": 1.5}
            ),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                changed = copy.deepcopy(snapshot)
                mutate(changed)
                changed_envelope = dict(envelope)
                changed_envelope["snapshot_payload_base64"] = base64.b64encode(
                    json.dumps(
                        changed, ensure_ascii=False, separators=(",", ":"),
                        sort_keys=True,
                    ).encode("utf-8")
                ).decode("ascii")
                tampered = json.dumps(
                    changed_envelope, ensure_ascii=False, separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
                with self.assertRaises(MergeReceiptRepositoryError):
                    _decode_receipt(
                        receipt.receipt_id, tampered, receipt.signature,
                    )

        noncanonical_snapshot = json.dumps(
            snapshot, ensure_ascii=False, indent=2, sort_keys=True,
        ).encode("utf-8")
        raw_envelope = dict(envelope)
        raw_envelope["snapshot_payload_base64"] = base64.b64encode(
            noncanonical_snapshot
        ).decode("ascii")
        raw_payload = json.dumps(
            raw_envelope, ensure_ascii=False, separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        with self.assertRaises(MergeReceiptRepositoryError):
            _decode_receipt(receipt.receipt_id, raw_payload, receipt.signature)


def repository_for(outcome):
    assert outcome.receipt is not None
    for _, repository in reversed(_REPOSITORY_RESOURCES):
        try:
            repository.get_verified(
                outcome.receipt.receipt_id,
                trusted_time=dt.datetime(2026, 8, 21, tzinfo=dt.UTC),
            )
            return repository
        except Exception:
            continue
    raise AssertionError("repository not found")


if __name__ == "__main__":
    unittest.main()
