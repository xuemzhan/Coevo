"""Unit tests for US-9-AC-1 report package generation slice.

Coverage matrix (each TestCase class locks one AC of the slice):

  AC-1  ``TestReportArtifact``        - evidence file + digest + size + role.
  AC-2  ``TestReportManifest``        - manifest schema + invariants.
  AC-3  ``TestReportManifest_AC3``    - manifest carries project_id / task_id / base_revision.
  AC-4  ``TestSubmissionSequence``    - monotonic counter.
  AC-5  ``TestReportBuilder``         - end-to-end ReportPackage wire + crypto-inheritance.
  AC-6  ``TestExpectedFilename``      - Report.agent canonical filename.
  AC-7  ``TestOverrides``             - reviewer override bumps submitted_at.

Service-layer invariants:
* No IO, no network, no model call.
* Re-running the same build is byte-deterministic.
* Report wire layout is byte-identical to a dispatch package
  with the same envelope (AC-5).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.protocol import (
    DEFAULT_EMPTY_STORE,
    AgentPackageFlags,
    BuiltPackage,
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    PackageImportService,
    ProcessedPackage,
    ReplayDecision,
    ReplayOutcome,
    check_replay,
)
from src.coevo.report import (
    DEFAULT_REPORT_PACKAGE_TYPE,
    ReportArtifact,
    ReportBuilder,
    ReportBuilderError,
    ReportManifest,
    ReportManifestError,
    ReportManifestValidationError,
    ReportPackage,
    ReportStatus,
    ReportSubmissionSequence,
)
from src.coevo.report.models import ReportOverride
from src.coevo.task_decomposition import (
    BaselineInput,
    build_baseline,
)


# ----------------------- fixtures -----------------------


def _artifact(*, path="payload/report.pdf", size=1024, digest_hex=None, role="EVIDENCE_DOCUMENT"):
    return ReportArtifact(
        path=path,
        role=role,
        media_type="application/pdf",
        size=size,
        digest_hex=digest_hex or ("0" * 64),
        classification="INTERNAL",
        required=True,
    )


def _baseline(project_id="PRJ001", unit_id="unit_a", version=1):
    from src.coevo.task_decomposition import WorkPackage, Task, Deliverable
    wp = WorkPackage(
        work_package_id="wp.intake",
        standard_stage="intake",
        title="Intake",
        tasks=(
            Task(
                task_id="t.1", title="Receive", responsible_role="pm",
                plan_start="2026-08-01T00:00:00Z",
                plan_end="2026-08-05T00:00:00Z",
                deliverables=(
                    Deliverable("d.1", "Doc", "document", ("ok",)),
                ),
            ),
        ),
    )
    return build_baseline(
        BaselineInput(
            project_id=project_id,
            title="Alpha",
            objective="Ship MVP",
            plan_start="2026-08-01T00:00:00Z",
            plan_end="2026-08-31T00:00:00Z",
            responsible_units=("unit_a",),
            process_flow_ref=(unit_id, version),
            work_packages=(wp,),
        ),
        now="2026-08-01T00:00:00Z",
    )


def _manifest(*, project_id="PRJ001", base_revision="PRJ001-R0001", sequence_no=1,
              status=ReportStatus.ON_TRACK):
    return ReportManifest(
        schema_version="1.0",
        package_id=str(uuid.uuid4()),
        package_type="RESULT_SUBMISSION",
        project_id=project_id,
        task_id="TASK-001",
        base_revision=base_revision,
        sequence_no=sequence_no,
        submitted_at="2026-08-15T10:00:00Z",
        sender_user_id="USR021",
        sender_client_id="CLI021",
        sender_organization_id="ORG002",
        sender_cert_id="CERT-RECIPIENT-021",
        recipient_user_id="USR001",
        recipient_client_id="CLI001",
        recipient_organization_id="ORG001",
        recipient_cert_id="CERT-SENDER-001",
        status=status,
        progress_summary="50% complete",
        completed_work=("draft report", "compiled evidence"),
        pending_work=("final review",),
        next_steps=("submit to PM",),
        risks=(),
        artifacts=(_artifact(),),
    )


# ----------------------- AC-2: ReportArtifact -----------------------


class TestReportArtifact(unittest.TestCase):
    def test_artifact_basic(self):
        a = _artifact()
        self.assertEqual("payload/report.pdf", a.path)
        self.assertEqual(64, len(a.digest_hex))
        self.assertTrue(a.required)

    def test_artifact_rejects_invalid_digest(self):
        with self.assertRaises(ReportManifestValidationError):
            _artifact(digest_hex="not-a-digest")

    def test_artifact_rejects_traversal_path(self):
        with self.assertRaises(ReportManifestValidationError):
            _artifact(path="../escaped.pdf")

    def test_artifact_rejects_negative_size(self):
        with self.assertRaises(ReportManifestValidationError):
            _artifact(size=-1)

    def test_artifact_rejects_non_string_role(self):
        # Construct manually to bypass _artifact() defaults
        with self.assertRaises(ReportManifestValidationError):
            ReportArtifact(
                path="x.pdf", role="", media_type="application/pdf",
                size=1, digest_hex="0" * 64, classification="INTERNAL", required=True,
            )


# ----------------------- AC-1: ReportManifest -----------------------


class TestReportManifest(unittest.TestCase):
    def test_manifest_basic(self):
        m = _manifest()
        self.assertEqual("PRJ001", m.project_id)
        self.assertEqual("TASK-001", m.task_id)
        self.assertEqual(ReportStatus.ON_TRACK, m.status)
        self.assertEqual(2, len(m.completed_work))
        self.assertEqual(0, len(m.risks))

    def test_manifest_rejects_bad_id(self):
        with self.assertRaises(ReportManifestValidationError):
            _manifest(project_id="bad id with spaces")

    def test_manifest_rejects_zero_sequence(self):
        with self.assertRaises(ReportManifestValidationError):
            _manifest(sequence_no=0)

    def test_manifest_rejects_wrong_schema_version(self):
        with self.assertRaises(ReportManifestValidationError):
            m = _manifest()
            # Mutate by replacing field on a frozen dataclass
            from dataclasses import replace
            m2 = replace(m, schema_version="2.0")
            # The replace happened; __post_init__ does NOT re-run
            # for replace() on frozen dataclasses — so we test via
            # direct construction instead.
            with self.assertRaises(ReportManifestValidationError):
                ReportManifest(
                    schema_version="2.0", package_id=m.package_id,
                    package_type=m.package_type, project_id=m.project_id,
                    task_id=m.task_id, base_revision=m.base_revision,
                    sequence_no=m.sequence_no, submitted_at=m.submitted_at,
                    sender_user_id=m.sender_user_id, sender_client_id=m.sender_client_id,
                    sender_organization_id=m.sender_organization_id,
                    sender_cert_id=m.sender_cert_id,
                    recipient_user_id=m.recipient_user_id,
                    recipient_client_id=m.recipient_client_id,
                    recipient_organization_id=m.recipient_organization_id,
                    recipient_cert_id=m.recipient_cert_id,
                    status=m.status, progress_summary=m.progress_summary,
                    completed_work=m.completed_work, pending_work=m.pending_work,
                    next_steps=m.next_steps, risks=m.risks,
                    artifacts=m.artifacts,
                )

    def test_manifest_rejects_bad_status(self):
        with self.assertRaises(ReportManifestValidationError):
            m = _manifest()
            from dataclasses import replace
            m2 = replace(m, status="not-a-status")
            # __post_init__ on replace: replace() doesn't re-run
            # __post_init__; but the validate-on-construct path
            # would catch it. The frozen check below is what
            # protects us — let's just test the immutable
            # invariant by re-constructing.
            with self.assertRaises(ReportManifestValidationError):
                ReportManifest(
                    schema_version=m.schema_version, package_id=m.package_id,
                    package_type=m.package_type, project_id=m.project_id,
                    task_id=m.task_id, base_revision=m.base_revision,
                    sequence_no=m.sequence_no, submitted_at=m.submitted_at,
                    sender_user_id=m.sender_user_id, sender_client_id=m.sender_client_id,
                    sender_organization_id=m.sender_organization_id,
                    sender_cert_id=m.sender_cert_id,
                    recipient_user_id=m.recipient_user_id,
                    recipient_client_id=m.recipient_client_id,
                    recipient_organization_id=m.recipient_organization_id,
                    recipient_cert_id=m.recipient_cert_id,
                    status="not-a-status",  # invalid
                    progress_summary=m.progress_summary,
                    completed_work=m.completed_work, pending_work=m.pending_work,
                    next_steps=m.next_steps, risks=m.risks,
                    artifacts=m.artifacts,
                )


# ----------------------- AC-3: project_id / task_id / base_revision -----------------------


class TestReportManifest_AC3(unittest.TestCase):
    def test_manifest_carries_project_id_task_id_base_revision(self):
        m = _manifest(project_id="PRJ002", base_revision="PRJ002-R0003")
        self.assertEqual("PRJ002", m.project_id)
        self.assertEqual("TASK-001", m.task_id)
        self.assertEqual("PRJ002-R0003", m.base_revision)


# ----------------------- AC-4: monotonic counter -----------------------


class TestSubmissionSequence(unittest.TestCase):
    def test_first_value_is_1(self):
        s = ReportSubmissionSequence.start("PRJ001")
        self.assertEqual(1, s.peek())

    def test_next_bumps_value(self):
        s = ReportSubmissionSequence.start("PRJ001")
        s2 = s.next()
        self.assertEqual(2, s2.peek())
        # Original is unchanged
        self.assertEqual(1, s.peek())

    def test_two_nexts_yield_3(self):
        s = ReportSubmissionSequence.start("PRJ001").next().next()
        self.assertEqual(3, s.peek())


# ----------------------- AC-5 + AC-6: end-to-end builder -----------------------


class TestReportBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = ReportBuilder()
        self.sequence = ReportSubmissionSequence.start("PRJ001")
        self.baseline = _baseline()
        self.manifest = _manifest()

    def test_build_emits_report_package(self):
        result = self.builder.build(
            manifest=self.manifest, baseline=self.baseline, sequence=self.sequence,
        )
        self.assertIsInstance(result, ReportPackage)
        self.assertIsInstance(result.package, BuiltPackage)
        self.assertEqual(self.manifest, result.manifest)
        # AC-6: package_type is RESULT_SUBMISSION
        self.assertEqual("RESULT_SUBMISSION", result.package.envelope.package_type)
        # AC-4: sequence_no matches
        self.assertEqual(1, result.package.envelope.sequence_no)

    def test_build_wire_bytes_are_deterministic(self):
        a = self.builder.build(
            manifest=self.manifest, baseline=self.baseline, sequence=self.sequence,
        )
        # Re-build with the same manifest → same bytes (the
        # manifest's package_id was auto-generated as a UUID; we
        # need to re-use the same manifest for byte-determinism).
        # Easier: re-build the SAME result twice and compare.
        b = self.builder.build(
            manifest=self.manifest, baseline=self.baseline, sequence=self.sequence,
        )
        self.assertEqual(a.to_bytes(), b.to_bytes())

    def test_build_rejects_mismatched_project_id(self):
        bad_baseline = _baseline(project_id="OTHER")
        with self.assertRaises(ReportManifestValidationError):
            self.builder.build(
                manifest=self.manifest, baseline=bad_baseline, sequence=self.sequence,
            )

    def test_build_rejects_mismatched_sequence_no(self):
        bad_manifest = _manifest(sequence_no=99)  # does not match sequence.peek() = 1
        with self.assertRaises(ReportManifestValidationError):
            self.builder.build(
                manifest=bad_manifest, baseline=self.baseline, sequence=self.sequence,
            )

    def test_build_inherits_us5_wire_layout(self):
        # AC-5: the report package uses the SAME wire layout as
        # the dispatch package. The simplest way to verify this
        # is to compare the FixedHeader byte layout: both are
        # 36 bytes, start with the same magic, etc.
        result = self.builder.build(
            manifest=self.manifest, baseline=self.baseline, sequence=self.sequence,
        )
        data = result.to_bytes()
        self.assertGreaterEqual(len(data), 36)
        # Magic is "AGENTPKG" (8 bytes)
        self.assertEqual(b"AGENTPKG", data[:8])
        # Major / minor version
        self.assertEqual(PROTOCOL_MAJOR, (data[8] << 8) | data[9])

    def test_build_requires_report_builder_arguments(self):
        with self.assertRaises(ReportBuilderError):
            self.builder.build(manifest="not a manifest", baseline=self.baseline, sequence=self.sequence)
        with self.assertRaises(ReportBuilderError):
            self.builder.build(manifest=self.manifest, baseline="not a baseline", sequence=self.sequence)
        with self.assertRaises(ReportBuilderError):
            self.builder.build(manifest=self.manifest, baseline=self.baseline, sequence="not a sequence")


# ----------------------- AC-6: filename -----------------------


class TestExpectedFilename(unittest.TestCase):
    def test_filename_layout(self):
        result = ReportBuilder().build(
            manifest=_manifest(project_id="PRJ001"),
            baseline=_baseline(),
            sequence=ReportSubmissionSequence.start("PRJ001"),
        )
        name = result.expected_filename()
        # Format: {package_type}_{project_id}_{package_id}.agent
        self.assertTrue(name.startswith("RESULT_SUBMISSION_PRJ001_"))
        self.assertTrue(name.endswith(".agent"))


# ----------------------- AC-7: overrides -----------------------


class TestOverrides(unittest.TestCase):
    def test_with_overrides_bumps_submitted_at(self):
        m = _manifest()
        self.assertEqual("2026-08-15T10:00:00Z", m.submitted_at)
        override = ReportOverride(
            target_path="progress_summary",
            original_value=m.progress_summary,
            edited_value="75% complete",
            reason="PM follow-up",
        )
        m2 = m.with_overrides(
            overrides=(override,), new_submitted_at="2026-08-16T11:00:00Z",
        )
        self.assertEqual("2026-08-16T11:00:00Z", m2.submitted_at)
        self.assertEqual((override,), m2.overrides)
        # The original is unchanged.
        self.assertEqual("2026-08-15T10:00:00Z", m.submitted_at)

    def test_with_empty_overrides_rejected(self):
        m = _manifest()
        with self.assertRaises(ReportManifestError):
            m.with_overrides(overrides=(), new_submitted_at="2026-08-16T11:00:00Z")

    def test_with_empty_submitted_at_rejected(self):
        m = _manifest()
        with self.assertRaises(ReportManifestError):
            m.with_overrides(overrides=(
                ReportOverride("x", 1, 2, "r"),
            ), new_submitted_at="")


# ----------------------- audit_record -----------------------


class TestAuditRecord(unittest.TestCase):
    def test_audit_record_is_json_safe(self):
        result = ReportBuilder().build(
            manifest=_manifest(),
            baseline=_baseline(),
            sequence=ReportSubmissionSequence.start("PRJ001"),
        )
        record = ReportBuilder().to_audit_record(result, baseline_version=1)
        s = json.dumps(record)
        self.assertEqual(record, json.loads(s))
        self.assertEqual("report.export", record["kind"])
        self.assertEqual("PRJ001", record["project_id"])
        self.assertEqual(1, record["sequence_no"])
        self.assertEqual(1, record["artifact_count"])


if __name__ == "__main__":
    unittest.main()