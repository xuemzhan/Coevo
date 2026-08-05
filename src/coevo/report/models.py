"""US-9 report manifest domain model (US-9-AC-1 / 协议 § 9).

Scope
-----
The :class:`ReportManifest` is the body of a ``Report.agent``
package (US-9). It is the sender-side analogue of the dispatch
manifest that US-5-AC-1 reads: 协议 § 9 specifies the dispatch
manifest fields; US-9-AC-1 / AC-3 / AC-4 add the report-specific
status / progress / risk / artifact fields.

Field mapping (US-9 AC-1..AC-4)
-------------------------------
* :attr:`status` / :attr:`progress_summary` / :attr:`completed_work`
  / :attr:`pending_work` / :attr:`next_steps` / :attr:`risks` — AC-1.
* :attr:`artifacts` (a tuple of :class:`ReportArtifact`) — AC-2.
* :attr:`project_id` / :attr:`task_id` / :attr:`base_revision` — AC-3.
* :attr:`package_id` / :attr:`sequence_no` — AC-4.

Non-goals
---------
* No IO / no DB / no model / no network.
* No mutation of US-5 wire layout. The manifest is a *value*
  consumed by :class:`ReportBuilder`; the builder is responsible
  for assembling the wire bytes via US-5's
  :mod:`package_builder`.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-9 回传清单领域模型：状态/工件/覆盖与校验。
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field

from src.coevo.task_decomposition import ProjectBaseline


# 协议 § 9: schema_version is 1.0
SCHEMA_VERSION: str = "1.0"

# Re-use the safe-id from identity / protocol layers.
_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")


class ReportManifestError(Exception):
    """Base class for US-9 manifest errors. Fail-closed by default."""


class ReportManifestValidationError(ReportManifestError):
    """Raised when an input cannot be reconciled.

    Distinct from :class:`ReportManifestError` so callers can
    branch on "validation failed (user-fixable)" vs "structural
    invariant violated (engineering bug)".
    """


class ReportStatus(enum.Enum):
    """The status of a report package (US-9 AC-1)."""

    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
    COMPLETED = "completed"


@dataclass(frozen=True)
class ReportArtifact:
    """A single evidence file attached to a report (AC-2)."""

    path: str           # relative path inside the workspace
    role: str           # closed set, validated at construction
    media_type: str
    size: int
    digest_hex: str     # 64-char lowercase hex (SM3, GB/T 32905)
    classification: str  # "INTERNAL" / "CONFIDENTIAL" / etc.
    required: bool

    def __post_init__(self) -> None:
        if not isinstance(self.path, str) or not self.path or ".." in self.path.split("/"):
            raise ReportManifestValidationError(
                f"artifact path must be a non-empty relative path without '..': {self.path!r}"
            )
        if not isinstance(self.role, str) or not self.role:
            raise ReportManifestValidationError("artifact role must be a non-empty string")
        if not isinstance(self.media_type, str) or not self.media_type:
            raise ReportManifestValidationError("artifact media_type must be a non-empty string")
        if not isinstance(self.size, int) or self.size < 0:
            raise ReportManifestValidationError("artifact size must be a non-negative integer")
        if not isinstance(self.digest_hex, str) or not _HEX_64.match(self.digest_hex):
            raise ReportManifestValidationError(
                f"artifact digest must be 64-char lowercase hex; got {self.digest_hex!r}"
            )
        if not isinstance(self.classification, str) or not self.classification:
            raise ReportManifestValidationError("artifact classification must be a non-empty string")
        if not isinstance(self.required, bool):
            raise ReportManifestValidationError("artifact required must be a bool")


@dataclass(frozen=True)
class ReportManifest:
    """The body of a ``Report.agent`` package (US-9 AC-1..AC-4).

    The manifest is FROZEN. Mutations produce new instances via
    :meth:`with_overrides` (mirrors US-2's
    :meth:`ProjectBaseline.with_overrides`).
    """

    schema_version: str
    package_id: str        # AC-4 unique package_id
    package_type: str      # closed set; for US-9 = "RESULT_SUBMISSION"
    project_id: str
    task_id: str
    base_revision: str     # AC-3 协议 § 16.2
    sequence_no: int       # AC-4
    submitted_at: str      # ISO-8601 UTC 'Z'
    sender_user_id: str
    sender_client_id: str
    sender_organization_id: str
    sender_cert_id: str
    recipient_user_id: str
    recipient_client_id: str
    recipient_organization_id: str
    recipient_cert_id: str
    status: ReportStatus
    progress_summary: str
    completed_work: tuple[str, ...]
    pending_work: tuple[str, ...]
    next_steps: tuple[str, ...]
    risks: tuple[str, ...]
    artifacts: tuple[ReportArtifact, ...]
    overrides: tuple["ReportOverride", ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name, value in (
            ("package_id", self.package_id),
            ("project_id", self.project_id),
            ("task_id", self.task_id),
            ("base_revision", self.base_revision),
            ("sender_user_id", self.sender_user_id),
            ("sender_client_id", self.sender_client_id),
            ("sender_organization_id", self.sender_organization_id),
            ("sender_cert_id", self.sender_cert_id),
            ("recipient_user_id", self.recipient_user_id),
            ("recipient_client_id", self.recipient_client_id),
            ("recipient_organization_id", self.recipient_organization_id),
            ("recipient_cert_id", self.recipient_cert_id),
        ):
            if not isinstance(value, str) or not value or not _SAFE_ID.match(value):
                raise ReportManifestValidationError(
                    f"{name} must match safe-id; got {value!r}"
                )
        if self.schema_version != SCHEMA_VERSION:
            raise ReportManifestValidationError(
                f"unsupported schema_version {self.schema_version!r}; "
                f"only {SCHEMA_VERSION!r} is supported"
            )
        if not isinstance(self.sequence_no, int) or self.sequence_no < 1:
            raise ReportManifestValidationError("sequence_no must be a positive integer")
        if not isinstance(self.submitted_at, str) or not self.submitted_at:
            raise ReportManifestValidationError("submitted_at must be a non-empty string")
        if self.status not in ReportStatus:
            raise ReportManifestValidationError(
                f"status must be a ReportStatus; got {self.status!r}"
            )
        # progress_summary is a single non-empty string (AC-1).
        if not isinstance(self.progress_summary, str) or not self.progress_summary:
            raise ReportManifestValidationError(
                "progress_summary must be a non-empty string"
            )
        # The four list-style fields are tuples of non-empty strings.
        for field_name in (
            "completed_work", "pending_work", "next_steps", "risks",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, tuple) or not all(
                isinstance(x, str) and x for x in value
            ):
                raise ReportManifestValidationError(
                    f"{field_name} must be a tuple of non-empty strings"
                )
        if not isinstance(self.artifacts, tuple) or not all(
            isinstance(a, ReportArtifact) for a in self.artifacts
        ):
            raise ReportManifestValidationError(
                "artifacts must be a tuple of ReportArtifact"
            )

    def with_overrides(
        self,
        overrides: tuple["ReportOverride", ...],
        new_submitted_at: str,
    ) -> "ReportManifest":
        """Return a new manifest with a fresh ``submitted_at`` and a recorded override list.

        The actual value substitutions are the caller's
        responsibility (the model layer is pure data); this
        helper just bumps :attr:`submitted_at` and records the
        override list (mirrors US-2's
        :meth:`ProjectBaseline.with_overrides`).
        """
        if not overrides:
            raise ReportManifestError("with_overrides requires non-empty overrides")
        if not isinstance(new_submitted_at, str) or not new_submitted_at:
            raise ReportManifestError("new_submitted_at must be a non-empty string")
        return _replace(self, submitted_at=new_submitted_at, overrides=overrides)


def _replace(obj, **changes):
    """Cheap dataclass ``replace`` that works on frozen dataclasses."""
    from dataclasses import replace
    return replace(obj, **changes)


@dataclass(frozen=True)
class ReportOverride:
    """A reviewer edit applied to a report manifest."""

    target_path: str
    original_value: object
    edited_value: object
    reason: str
