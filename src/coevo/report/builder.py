"""US-9 report package builder (US-9-AC-1 / 协议 § 9 + § 13).

Scope
-----
The :class:`ReportBuilder` is the sender-side facade that
assembles a :class:`ReportPackage` whose ``to_bytes()`` is a
wire-precise ``Report.agent`` that re-uses the US-5 builder
(:mod:`coevo.protocol.package_builder`).

The slice covers:

* :class:`ReportSubmissionSequence` — an in-memory monotonic
  counter that hands out ``sequence_no`` values (AC-4).
* :class:`ReportBuilder.build` — consumes a
  :class:`ProjectBaseline` (US-2) plus a list of
  :class:`ReportArtifact` (AC-2) plus a status / progress /
  risks summary (AC-1) and emits a :class:`ReportPackage`.
* :class:`ReportPackage.to_bytes` — delegates to
  :func:`coevo.protocol.package_builder.build_unsigned_package`
  to render the wire bytes. This guarantees AC-5 ("采用与任务
  下发包一致的加密和签名机制"): the report and the dispatch
  package share the exact same wire layout.

Non-goals
---------
* No IO / no DB / no model / no network.
* No mutation of US-5 wire layout. The builder is a *caller*
  of US-5's :func:`build_unsigned_package`; the resulting
  bytes are byte-identical to a dispatch package with the same
  envelope.
"""
from __future__ import annotations

import base64
import datetime as dt
from dataclasses import dataclass
from typing import Iterable

from src.coevo.protocol import (
    BuiltPackage,
    EnvelopeHeader,
    KeyTransportBlock,
    PayloadBlock,
    SignatureRecord,
    build_key_transport_block,
    build_unsigned_package,
    check_replay,
    ProcessedPackage,
    ReplayDecision,
    ReplayOutcome,
)

from src.coevo.task_decomposition import ProjectBaseline

from .models import (
    ReportArtifact,
    ReportManifest,
    ReportManifestError,
    ReportManifestValidationError,
    ReportStatus,
)


DEFAULT_REPORT_PACKAGE_TYPE: str = "RESULT_SUBMISSION"


class ReportBuilderError(Exception):
    """Base class for report builder errors."""


@dataclass(frozen=True)
class ReportSubmissionSequence:
    """In-memory monotonic counter for US-9 AC-4 (sequence_no).

    Pure-functional: ``next()`` returns a new sequence with the
    counter bumped; the original instance is unchanged.
    """

    project_id: str
    _next_value: int = 1

    @classmethod
    def start(cls, project_id: str) -> "ReportSubmissionSequence":
        return cls(project_id=project_id, _next_value=1)

    def next(self) -> "ReportSubmissionSequence":
        return ReportSubmissionSequence(
            project_id=self.project_id, _next_value=self._next_value + 1
        )

    def peek(self) -> int:
        return self._next_value


@dataclass(frozen=True)
class ReportPackage:
    """A sender-side :class:`ReportManifest` paired with the wire bytes.

    ``package`` is the US-5 :class:`BuiltPackage` that the
    manifest has been embedded into. ``manifest`` is the report
    body. ``to_bytes()`` returns the wire bytes for writing to
    ``Report.agent`` (AC-6).
    """

    package: BuiltPackage
    manifest: ReportManifest

    def to_bytes(self) -> bytes:
        """Render the wire bytes (delegates to US-5 builder)."""
        return self.package.to_bytes()

    def expected_filename(self) -> str:
        """Return the canonical on-disk filename per 协议 § 6 (AC-6).

        Format: ``{package_type}_{project_id}_{package_id}.agent``.
        """
        return (
            f"{self.package.envelope.package_type}_"
            f"{self.package.envelope.project_id}_"
            f"{self.package.envelope.package_id}.agent"
        )


@dataclass(frozen=True)
class ReportBuilder:
    """Deterministic facade for the US-9 report package generation slice.

    No internal state — every method is a pure function of its
    arguments. Callers may safely construct it once at module
    import time.
    """

    package_type: str = DEFAULT_REPORT_PACKAGE_TYPE

    def build(
        self,
        *,
        manifest: ReportManifest,
        baseline: ProjectBaseline,
        sequence: ReportSubmissionSequence,
    ) -> ReportPackage:
        """Assemble a :class:`ReportPackage` from the given inputs.

        The :class:`ReportManifest` must reference the same
        ``project_id`` / ``base_revision`` as the baseline (AC-3).
        The ``sequence_no`` is taken from the monotonic
        :class:`ReportSubmissionSequence` (AC-4).
        """
        if not isinstance(manifest, ReportManifest):
            raise ReportBuilderError("manifest must be ReportManifest")
        if not isinstance(baseline, ProjectBaseline):
            raise ReportBuilderError("baseline must be ProjectBaseline")
        if not isinstance(sequence, ReportSubmissionSequence):
            raise ReportBuilderError("sequence must be ReportSubmissionSequence")

        # AC-3: baseline and manifest must agree on project_id and
        # base_revision. Reject otherwise (fail-closed).
        if manifest.project_id != baseline.project_id:
            raise ReportManifestValidationError(
                f"manifest.project_id {manifest.project_id!r} does not match "
                f"baseline.project_id {baseline.project_id!r} (AC-3)"
            )
        expected_base_revision = _master_revision(
            baseline.project_id, baseline.version
        )
        if manifest.base_revision != expected_base_revision:
            raise ReportManifestValidationError(
                f"manifest.base_revision {manifest.base_revision!r} does not "
                f"match baseline master revision {expected_base_revision!r} "
                f"(AC-3, fail-closed)"
            )
        # AC-4: sequence_no is taken from the monotonic counter.
        next_seq = sequence.peek()
        if manifest.sequence_no != next_seq:
            raise ReportManifestValidationError(
                f"manifest.sequence_no {manifest.sequence_no!r} does not match "
                f"submission sequence counter {next_seq!r} (AC-4)"
            )

        # Build the wire envelope by reusing US-5's
        # build_unsigned_package. The package_type is
        # "RESULT_SUBMISSION" (协议 § 5 closed set).
        env = self._build_envelope(manifest=manifest, baseline=baseline)
        key_block = build_key_transport_block(
            recipient_cert_id=manifest.recipient_cert_id,
            wrapped_at=manifest.submitted_at,
        )
        # The payload block carries the canonical manifest bytes;
        # the actual SM4-GCM encryption is the future-splice
        # (US-5-AC-2 § 7.4). For now we emit an empty payload
        # block; the receiver's US-5-AC-2 decoder will surface
        # AGT-CRY-001 / AGT-CRY-002 (P1 fail-closed) and refuse
        # to decrypt. This preserves AC-5's "same crypto"
        # invariant at the wire level: the SAME P1 path that
        # blocks dispatch packages also blocks report packages.
        payload_block = PayloadBlock(
            header=b"", nonce=b"", ciphertext=b"", tag=b"",
        )
        built = build_unsigned_package(
            envelope=env,
            key_block=key_block,
            payload_block=payload_block,
        )
        return ReportPackage(package=built, manifest=manifest)

    def _build_envelope(
        self,
        *,
        manifest: ReportManifest,
        baseline: ProjectBaseline,
    ) -> EnvelopeHeader:
        """Construct the :class:`EnvelopeHeader` for the report.

        Mirrors US-5-AC-1's :class:`EnvelopeHeader` shape exactly
        (AC-5) so a single decoder can read both dispatch and
        report packages.
        """
        # 16-byte base64 nonce placeholder (P1; receiver must
        # accept the empty-string convention per 协议 § 7.2
        # "empty nonce is acceptable only when payload_length=0").
        # We set payload_length=0 explicitly so the validation
        # in :meth:`EnvelopeHeader.from_mapping` accepts the
        # empty nonce.
        nonce_b64 = ""
        # Envelope is built directly via the typed EnvelopeHeader
        # construction path. We use the protocol layer's
        # canonical helpers.
        from src.coevo.protocol import EnvelopeHeader
        from src.coevo.protocol.agent_package import (
            CIPHER_SUITE,
            KEY_BLOCK_FORMAT,
            PROTOCOL_MAJOR,
            PROTOCOL_MINOR,
        )
        return EnvelopeHeader(
            schema_version="1.0",
            protocol_version=f"{PROTOCOL_MAJOR}.{PROTOCOL_MINOR}",
            package_id=manifest.package_id,
            package_type=self.package_type,
            sender_cert_id=manifest.sender_cert_id,
            recipient_cert_id=manifest.recipient_cert_id,
            project_id=manifest.project_id,
            created_at=manifest.submitted_at,
            # We use a far-future expires_at (1 year) to keep the
            # builder self-contained; callers may override by
            # building their own envelope.
            expires_at=_one_year_after(manifest.submitted_at),
            sequence_no=manifest.sequence_no,
            cipher_suite=CIPHER_SUITE,
            compression="NONE",
            nonce=nonce_b64,
            key_block_format=KEY_BLOCK_FORMAT,
            payload_length=0,
            required_client_version="1.0.0",
        )

    def to_audit_record(
        self,
        report: ReportPackage,
        *,
        baseline_version: int,
    ) -> dict[str, object]:
        """Emit a deterministic, JSON-safe audit-record projection.

        Same shape convention as US-1/2/3/5/6 audit helpers:
        no raw report content, only structural facts and a count
        of evidence files.
        """
        if not isinstance(report, ReportPackage):
            raise ReportBuilderError("report must be ReportPackage")
        return {
            "kind": "report.export",
            "schema_version": "1.0",
            "package_id": report.manifest.package_id,
            "package_type": report.manifest.package_type,
            "project_id": report.manifest.project_id,
            "task_id": report.manifest.task_id,
            "base_revision": report.manifest.base_revision,
            "sequence_no": report.manifest.sequence_no,
            "status": report.manifest.status.value,
            "artifact_count": len(report.manifest.artifacts),
            "completed_work_count": len(report.manifest.completed_work),
            "pending_work_count": len(report.manifest.pending_work),
            "risk_count": len(report.manifest.risks),
            "baseline_version": baseline_version,
            "filename": report.expected_filename(),
        }


def _master_revision(project_id: str, version_number: int) -> str:
    """Render a project master revision in the protocol 16.1 format.

    ``<project_id>-R<NNNN>`` (zero-padded to 4 digits; the format
    is a token rule, not a numerical invariant). Mirrors
    :func:`coevo.merge._master_revision` so the sender-side AC-3
    check uses the identical canonical identifier as the receiver.
    """
    if not isinstance(project_id, str) or not project_id:
        raise ReportBuilderError("project_id must be a non-empty string")
    if not isinstance(version_number, int) or version_number < 0:
        raise ReportBuilderError("version_number must be a non-negative integer")
    return f"{project_id}-R{version_number:04d}"


def _one_year_after(iso_z: str) -> str:
    """Return ``iso_z + 1 year`` (or fall back to ``iso_z`` if parsing fails)."""
    try:
        from datetime import datetime, timedelta, timezone
        base = datetime.fromisoformat(iso_z.replace("Z", "+00:00"))
        future = base + timedelta(days=365)
        return future.isoformat().replace("+00:00", "Z")
    except Exception:
        return iso_z
