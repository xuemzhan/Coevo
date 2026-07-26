"""US-9 progress / result report package generation (US-9-AC-1).

Scope
-----
US-9 specifies the sender-side ``Report.agent`` generation flow
(US-9 AC-1..AC-8). The full AC list:

  AC-1  report content: status / progress / done / pending / next / risks
  AC-2  report associates evidence files + digest summaries
  AC-3  carries project_id / task_id / original base_revision
  AC-4  carries unique package_id + submission sequence_no
  AC-5  uses the SAME crypto + signature mechanism as the dispatch
        package (US-5-AC-1 / AC-2 / AC-3; the P1 fail-closed path)
  AC-6  user confirms before generating Report.agent
  AC-7  original evidence files stay in the local workspace
  AC-8  export operation forms an audit record

This slice (US-9-AC-1) ships the *deterministic, in-memory* half:

* :class:`ReportManifest` — the report body (AC-1 / AC-2 / AC-3).
* :class:`ReportArtifact` — an evidence file with a 64-char
  lowercase-hex digest (AC-2).
* :class:`ReportBuilder` — facade that consumes a
  :class:`ProjectBaseline` (US-2) and a list of artifacts
  (US-6) and emits a :class:`ReportPackage` whose ``to_bytes()``
  is a wire-precise ``Report.agent`` that re-uses the US-5
  builder (AC-5).
* :class:`ReportPackage` — a thin wrapper over
  :class:`BuiltPackage` plus the report-specific sequence counter.

The slice is PURE: no IO, no LLM, no network. The actual
``to_bytes()`` step delegates to US-5's
:func:`package_builder.build_unsigned_package` so the wire
layout is identical to the dispatch package (AC-5).

What this is NOT
----------------
* No IO. The builder never touches the filesystem.
* No LLM, no model, no network.
* No mutation of US-5 / US-6 / US-2 wire layout. The slice
  consumes those types verbatim.
"""
from .models import (
    ReportArtifact,
    ReportManifest,
    ReportManifestError,
    ReportManifestValidationError,
    ReportStatus,
)
from .builder import (
    DEFAULT_REPORT_PACKAGE_TYPE,
    ReportBuilder,
    ReportBuilderError,
    ReportPackage,
    ReportSubmissionSequence,
)

__all__ = [
    "DEFAULT_REPORT_PACKAGE_TYPE",
    "ReportArtifact",
    "ReportBuilder",
    "ReportBuilderError",
    "ReportManifest",
    "ReportManifestError",
    "ReportManifestValidationError",
    "ReportPackage",
    "ReportStatus",
    "ReportSubmissionSequence",
]