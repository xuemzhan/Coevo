"""cockpit.models - US-7 cockpit domain models, enums, errors, view summaries, config/state and the WPS allow list."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-7 驾驶舱领域模型：路由/响应状态/视图快照/会话与服务器配置，
# 含 AC-1 环回绑定失败关闭与 AC-8 WPS 允许列表。

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from pathlib import Path

from src.coevo.ids import SAFE_ID as _SAFE_ID

from src.coevo.timefmt import is_iso_utc_z

from src.coevo.ids import HEX_64 as _HEX_64

from src.coevo.supervision import EscalationLevel as _EscalationLevel
from src.coevo.supervision import ReminderKind as _ReminderKind

LOOPBACK_HOST: str = "127.0.0.1"

STATIC_ROOT: Path = Path(__file__).resolve().parent / "static"

class CockpitError(Exception):
    """Base class for all US-7 errors. Fail-closed by default."""

class CockpitValidationError(CockpitError):
    """An input field or config failed validation (user-fixable)."""

class CockpitNotFoundError(CockpitError):
    """A referenced project / role / task does not exist in the snapshot."""

class CockpitRoute(enum.Enum):
    """AC-5..AC-8 closed set of cockpit routes."""

    LIST_PROJECTS = "list_projects"
    LIST_ROLES = "list_roles"
    PROJECT_VIEW = "project_view"
    ROLE_VIEW = "role_view"
    TASK_VIEW = "task_view"
    MILESTONE_VIEW = "milestone_view"
    WPS_OPEN = "wps_open"
    PENDING_CONFIRM = "pending_confirm"
    SUPERVISION_VIEW = "supervision_view"

class CockpitResponseStatus(enum.Enum):
    """HTTP-like status codes (without depending on http module)."""

    OK = "ok"
    STARTED = "started"
    NOT_FOUND = "not_found"
    BAD_REQUEST = "bad_request"
    DENIED = "denied"
    NOT_BOUND = "not_bound"
    NOT_AVAILABLE = "not_available"
    ERROR = "error"

@dataclass(frozen=True)
class TaskSummary:
    task_id: str
    title: str
    status: str
    due_at: str
    assignee_role_id: str

    def __post_init__(self) -> None:
        for label, value in (
            ("task_id", self.task_id),
            ("assignee_role_id", self.assignee_role_id),
        ):
            if not isinstance(value, str) or not _SAFE_ID.match(value):
                raise CockpitValidationError(
                    f"{label} must be safe-id; got {value!r}"
                )
        if not isinstance(self.title, str) or not self.title:
            raise CockpitValidationError("title must be a non-empty string")
        if not isinstance(self.status, str) or not self.status:
            raise CockpitValidationError("status must be a non-empty string")
        if not isinstance(self.due_at, str) or not self.due_at:
            raise CockpitValidationError("due_at must be a non-empty string")

@dataclass(frozen=True)
class MilestoneSummary:
    milestone_id: str
    title: str
    due_at: str
    completed: bool

    def __post_init__(self) -> None:
        if not isinstance(self.milestone_id, str) or not _SAFE_ID.match(self.milestone_id):
            raise CockpitValidationError(
                f"milestone_id must be safe-id; got {self.milestone_id!r}"
            )
        if not isinstance(self.title, str) or not self.title:
            raise CockpitValidationError("title must be a non-empty string")
        if not isinstance(self.due_at, str) or not self.due_at:
            raise CockpitValidationError("due_at must be a non-empty string")
        if not isinstance(self.completed, bool):
            raise CockpitValidationError("completed must be bool")

@dataclass(frozen=True)
class ArtifactSummary:
    path: str
    role: str
    media_type: str
    size_bytes: int
    digest_hex: str

    def __post_init__(self) -> None:
        if not isinstance(self.path, str) or not self.path:
            raise CockpitValidationError("path must be a non-empty string")
        if ".." in self.path.split("/") or self.path.startswith("/"):
            raise CockpitValidationError(
                f"artifact path must be a non-traversing workspace-relative path; got {self.path!r}"
            )
        if self.role not in {"document", "feedback", "artifact", "dependency"}:
            raise CockpitValidationError(
                f"artifact role must be one of document/feedback/artifact/dependency; got {self.role!r}"
            )
        if not isinstance(self.media_type, str) or not self.media_type:
            raise CockpitValidationError("media_type must be a non-empty string")
        if not isinstance(self.size_bytes, int) or self.size_bytes < 0:
            raise CockpitValidationError("size_bytes must be a non-negative integer")
        if not _HEX_64.match(self.digest_hex):
            raise CockpitValidationError(
                f"digest_hex must be 64-char lowercase hex; got {self.digest_hex!r}"
            )

@dataclass(frozen=True)
class TraceStepSummary:
    """Orchestration trace step projected for the cockpit (read-only)."""

    step_index: int
    agent_id: str
    result: str
    requires_human_confirmation: bool
    confirmed_by: str
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(self.step_index, int) or self.step_index < 0:
            raise CockpitValidationError(
                f"step_index must be a non-negative integer; got {self.step_index!r}"
            )
        if not isinstance(self.agent_id, str):
            raise CockpitValidationError("agent_id must be a string")
        if not isinstance(self.result, str) or not self.result:
            raise CockpitValidationError("result must be a non-empty string")
        if not isinstance(self.requires_human_confirmation, bool):
            raise CockpitValidationError(
                "requires_human_confirmation must be bool"
            )
        if not isinstance(self.confirmed_by, str):
            raise CockpitValidationError("confirmed_by must be a string")
        if not isinstance(self.detail, str):
            raise CockpitValidationError("detail must be a string")


@dataclass(frozen=True)
class ActivityEntry:
    """One audit-chain row projected for the cockpit (read-only)."""

    sequence: int
    event_id: str
    action: str
    result: str
    digest: str
    recorded_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.sequence, int) or self.sequence <= 0:
            raise CockpitValidationError(
                f"sequence must be a positive integer; got {self.sequence!r}"
            )
        if not isinstance(self.event_id, str) or not self.event_id:
            raise CockpitValidationError("event_id must be a non-empty string")
        if not isinstance(self.action, str) or not self.action:
            raise CockpitValidationError("action must be a non-empty string")
        if not isinstance(self.result, str) or not self.result:
            raise CockpitValidationError("result must be a non-empty string")
        if not isinstance(self.digest, str) or not self.digest:
            raise CockpitValidationError("digest must be a non-empty string")
        if not isinstance(self.recorded_at, str) or not self.recorded_at:
            raise CockpitValidationError("recorded_at must be a non-empty string")


@dataclass(frozen=True)
class RoleView:
    role_id: str
    project_id: str
    display_name: str
    current_tasks: tuple[TaskSummary, ...]
    milestones: tuple[MilestoneSummary, ...]
    artifacts: tuple[ArtifactSummary, ...]

    def __post_init__(self) -> None:
        for label, value in (
            ("role_id", self.role_id),
            ("project_id", self.project_id),
        ):
            if not isinstance(value, str) or not _SAFE_ID.match(value):
                raise CockpitValidationError(
                    f"{label} must be safe-id; got {value!r}"
                )
        if not isinstance(self.display_name, str) or not self.display_name:
            raise CockpitValidationError("display_name must be a non-empty string")
        for label, schema in (
            ("current_tasks", self.current_tasks),
            ("milestones", self.milestones),
            ("artifacts", self.artifacts),
        ):
            if not isinstance(schema, tuple):
                raise CockpitValidationError(f"{label} must be a tuple")
        for t in self.current_tasks:
            if not isinstance(t, TaskSummary):
                raise CockpitValidationError("current_tasks must contain TaskSummary")
        for m in self.milestones:
            if not isinstance(m, MilestoneSummary):
                raise CockpitValidationError("milestones must contain MilestoneSummary")
        for a in self.artifacts:
            if not isinstance(a, ArtifactSummary):
                raise CockpitValidationError("artifacts must contain ArtifactSummary")

@dataclass(frozen=True)
class WorkspaceView:
    project_id: str
    display_name: str
    roles: tuple[str, ...]
    task_count: int
    milestone_count: int
    artifact_count: int
    package_path: str = ""
    package_digest: str = ""
    knowledge_bundle_id: str = ""
    trace: tuple[TraceStepSummary, ...] = ()
    activity: tuple[ActivityEntry, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.project_id, str) or not _SAFE_ID.match(self.project_id):
            raise CockpitValidationError(
                f"project_id must be safe-id; got {self.project_id!r}"
            )
        if not isinstance(self.display_name, str) or not self.display_name:
            raise CockpitValidationError("display_name must be a non-empty string")
        if not isinstance(self.roles, tuple) or not all(
            isinstance(r, str) and _SAFE_ID.match(r) for r in self.roles
        ):
            raise CockpitValidationError("roles must be a tuple of safe-id role_ids")
        for label, value in (
            ("task_count", self.task_count),
            ("milestone_count", self.milestone_count),
            ("artifact_count", self.artifact_count),
        ):
            if not isinstance(value, int) or value < 0:
                raise CockpitValidationError(
                    f"{label} must be a non-negative integer; got {value!r}"
                )
        if not isinstance(self.trace, tuple) or not all(
            isinstance(t, TraceStepSummary) for t in self.trace
        ):
            raise CockpitValidationError(
                "trace must be a tuple of TraceStepSummary"
            )
        if not isinstance(self.activity, tuple) or not all(
            isinstance(a, ActivityEntry) for a in self.activity
        ):
            raise CockpitValidationError(
                "activity must be a tuple of ActivityEntry"
            )
        if not isinstance(self.package_path, str):
            raise CockpitValidationError("package_path must be a string")
        if not isinstance(self.package_digest, str) or (
            self.package_digest
            and not _HEX_64.match(self.package_digest)
        ):
            raise CockpitValidationError(
                "package_digest must be empty or a 64-char lowercase hex"
            )
        if not isinstance(self.knowledge_bundle_id, str):
            raise CockpitValidationError("knowledge_bundle_id must be a string")


@dataclass(frozen=True)
class SupervisionSummary:
    """US-12 supervision/meeting snapshot for the cockpit (MATURITY-O-06).

    A minimal, sensitive-free projection of one supervision item plus its
    escalation/reminder/meeting state. ``from_outcome`` converts a real
    :class:`~src.coevo.supervision.SupervisionOutcome` into the snapshot so
    the return chain can feed the cockpit without leaking business phrasing
    (basis / recommendation / rationale / closing_condition).
    """

    project_id: str
    item_id: str
    risk_id: str
    risk_kind: str
    responsible_subject: str
    due_at: str
    escalation_level: str = ""
    reminder_kind: str = ""
    meeting_proposal_id: str = ""
    requires_confirmation: bool = True

    _ESCALATION_VALUES: frozenset[str] = frozenset(
        level.value for level in _EscalationLevel
    ) | frozenset({""})
    _REMINDER_VALUES: frozenset[str] = frozenset(
        kind.value for kind in _ReminderKind
    ) | frozenset({""})

    def __post_init__(self) -> None:
        for label, value in (
            ("project_id", self.project_id),
            ("item_id", self.item_id),
            ("risk_id", self.risk_id),
            ("responsible_subject", self.responsible_subject),
        ):
            if not isinstance(value, str) or not _SAFE_ID.match(value):
                raise CockpitValidationError(
                    f"{label} must be safe-id; got {value!r}"
                )
        if not isinstance(self.risk_kind, str) or not self.risk_kind:
            raise CockpitValidationError("risk_kind must be a non-empty string")
        if not is_iso_utc_z(self.due_at):
            raise CockpitValidationError(
                f"due_at must be ISO-8601 UTC 'Z'; got {self.due_at!r}"
            )
        if self.escalation_level not in self._ESCALATION_VALUES:
            raise CockpitValidationError(
                f"escalation_level {self.escalation_level!r} not in supervision closed set"
            )
        if self.reminder_kind not in self._REMINDER_VALUES:
            raise CockpitValidationError(
                f"reminder_kind {self.reminder_kind!r} not in supervision closed set"
            )
        if self.meeting_proposal_id and not _SAFE_ID.match(self.meeting_proposal_id):
            raise CockpitValidationError(
                f"meeting_proposal_id must be safe-id when present; got {self.meeting_proposal_id!r}"
            )
        if self.requires_confirmation is not True:
            raise CockpitValidationError(
                "supervision summary must require owner confirmation (fail-closed)"
            )

    @classmethod
    def from_outcome(
        cls, outcome: object
    ) -> tuple["SupervisionSummary", ...]:
        """Project a SupervisionOutcome into cockpit supervision summaries."""

        from src.coevo.supervision import SupervisionOutcome

        if not isinstance(outcome, SupervisionOutcome):
            raise CockpitValidationError("outcome must be a SupervisionOutcome")
        escalations = {e.item_id: e.level.value for e in outcome.escalations}
        reminders = {r.item_id: r.kind.value for r in outcome.reminders}
        meeting_proposal_id = (
            outcome.meeting_proposal.proposal_id
            if outcome.meeting_proposal is not None
            else ""
        )
        return tuple(
            cls(
                project_id=item.project_id,
                item_id=item.item_id,
                risk_id=item.risk_id,
                risk_kind=item.risk_kind.value,
                responsible_subject=item.responsible_subject,
                due_at=item.due_at,
                escalation_level=escalations.get(item.item_id, ""),
                reminder_kind=reminders.get(item.item_id, ""),
                meeting_proposal_id=meeting_proposal_id,
                requires_confirmation=outcome.requires_owner_confirmation,
            )
            for item in outcome.items
        )


@dataclass(frozen=True)
class CockpitRequest:
    route: CockpitRoute
    project_id: str
    role_id: str
    task_id: str
    artifact_path: str
    ts: str

    def __post_init__(self) -> None:
        if not isinstance(self.route, CockpitRoute):
            raise CockpitValidationError(
                f"route must be CockpitRoute; got {self.route!r}"
            )
        for label, value in (
            ("project_id", self.project_id),
            ("role_id", self.role_id),
            ("task_id", self.task_id),
        ):
            if not isinstance(value, str):
                raise CockpitValidationError(f"{label} must be a string")
            if value and not _SAFE_ID.match(value):
                raise CockpitValidationError(
                    f"{label} must be safe-id when present; got {value!r}"
                )
        if not isinstance(self.artifact_path, str):
            raise CockpitValidationError("artifact_path must be a string")
        if self.artifact_path:
            if ".." in self.artifact_path.split("/") or self.artifact_path.startswith("/"):
                raise CockpitValidationError(
                    f"artifact_path must be a non-traversing workspace-relative path; "
                    f"got {self.artifact_path!r}"
                )
        if not is_iso_utc_z(self.ts):
            raise CockpitValidationError(
                f"ts must be ISO-8601 UTC 'Z'; got {self.ts!r}"
            )

@dataclass(frozen=True)
class CockpitResponse:
    status: CockpitResponseStatus
    body_html: str
    content_type: str
    task: str
    payload: dict
    ts: str

    def __post_init__(self) -> None:
        if not isinstance(self.status, CockpitResponseStatus):
            raise CockpitValidationError(
                f"status must be CockpitResponseStatus; got {self.status!r}"
            )
        for label, value in (
            ("body_html", self.body_html),
            ("content_type", self.content_type),
            ("task", self.task),
        ):
            if not isinstance(value, str):
                raise CockpitValidationError(f"{label} must be a string")
        if not isinstance(self.payload, dict):
            raise CockpitValidationError("payload must be a dict")
        if not is_iso_utc_z(self.ts):
            raise CockpitValidationError(
                f"ts must be ISO-8601 UTC 'Z'; got {self.ts!r}"
            )

@dataclass(frozen=True)
class CockpitServerConfig:
    bind_host: str
    bind_port: int
    static_root: Path
    max_request_bytes: int
    request_timeout_sec: int

    def __post_init__(self) -> None:
        # AC-1 fail-closed: bind_host MUST be the loopback literal.
        if not isinstance(self.bind_host, str) or self.bind_host != LOOPBACK_HOST:
            raise CockpitValidationError(
                f"bind_host must be {LOOPBACK_HOST!r} (AC-1 fail-closed); got {self.bind_host!r}"
            )
        if not isinstance(self.bind_port, int) or not (1 <= self.bind_port <= 65535):
            raise CockpitValidationError(
                f"bind_port must be 1..65535; got {self.bind_port!r}"
            )
        if not isinstance(self.static_root, Path):
            raise CockpitValidationError("static_root must be a Path")
        # AC-2 fail-closed: static_root MUST live under the cockpit static dir.
        try:
            resolved = self.static_root.resolve()
        except OSError as exc:
            raise CockpitValidationError(
                f"static_root must be a resolvable path; got {self.static_root!r} ({exc})"
            )
        try:
            resolved.relative_to(STATIC_ROOT.resolve())
        except ValueError:
            raise CockpitValidationError(
                f"static_root must be inside {STATIC_ROOT!r} (AC-2 fail-closed); "
                f"got {self.static_root!r}"
            )
        if not isinstance(self.max_request_bytes, int) or self.max_request_bytes <= 0:
            raise CockpitValidationError("max_request_bytes must be a positive integer")
        if not isinstance(self.request_timeout_sec, int) or self.request_timeout_sec <= 0:
            raise CockpitValidationError("request_timeout_sec must be a positive integer")

@dataclass(frozen=True)
class CockpitServerState:
    config: CockpitServerConfig
    workspace_views: tuple[WorkspaceView, ...] = field(default_factory=tuple)
    role_views: tuple[RoleView, ...] = field(default_factory=tuple)
    supervision_views: tuple[SupervisionSummary, ...] = field(default_factory=tuple)
    started_at: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.config, CockpitServerConfig):
            raise CockpitValidationError("config must be CockpitServerConfig")
        if not isinstance(self.workspace_views, tuple) or not all(
            isinstance(w, WorkspaceView) for w in self.workspace_views
        ):
            raise CockpitValidationError(
                "workspace_views must be a tuple of WorkspaceView"
            )
        if not isinstance(self.role_views, tuple) or not all(
            isinstance(r, RoleView) for r in self.role_views
        ):
            raise CockpitValidationError(
                "role_views must be a tuple of RoleView"
            )
        if not isinstance(self.supervision_views, tuple) or not all(
            isinstance(s, SupervisionSummary) for s in self.supervision_views
        ):
            raise CockpitValidationError(
                "supervision_views must be a tuple of SupervisionSummary"
            )
        if self.started_at and not is_iso_utc_z(self.started_at):
            raise CockpitValidationError(
                f"started_at must be ISO-8601 UTC 'Z'; got {self.started_at!r}"
            )

class WPSAllowList:
    """AC-8: closed allow-list of WPS-eligible file extensions + mime prefixes."""

    ALLOWED_EXTENSIONS: frozenset[str] = frozenset({
        ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".rtf", ".pdf",
    })
    ALLOWED_MIME_PREFIXES: frozenset[str] = frozenset({
        "application/vnd.openxmlformats-officedocument",
        "application/msword",
        "application/vnd.ms-excel",
        "application/vnd.ms-powerpoint",
        "application/pdf",
        "text/",
    })
    FORBIDDEN_EXTENSIONS: frozenset[str] = frozenset({
        ".exe", ".bat", ".cmd", ".ps1", ".sh", ".js", ".vbs", ".scr",
        ".jar", ".com", ".msi", ".lnk", ".scr",
    })

    @staticmethod
    def is_allowed_extension(path: str) -> bool:
        if not isinstance(path, str) or not path:
            return False
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        ext = "." + ext if ext else ""
        if ext in WPSAllowList.FORBIDDEN_EXTENSIONS:
            return False
        return ext in WPSAllowList.ALLOWED_EXTENSIONS

    @staticmethod
    def is_allowed_mime(media_type: str) -> bool:
        if not isinstance(media_type, str) or not media_type:
            return False
        return any(
            media_type.lower().startswith(prefix)
            for prefix in WPSAllowList.ALLOWED_MIME_PREFIXES
        )

    @staticmethod
    def is_allowed(path: str, media_type: str = "") -> bool:
        """AC-8 entry point: check extension AND mime (if provided)."""
        if not WPSAllowList.is_allowed_extension(path):
            return False
        if media_type and not WPSAllowList.is_allowed_mime(media_type):
            return False
        return True

def _hash_path(path: str) -> str:
    """Stable, audit-friendly path summary (NOT cryptographic commitment)."""
    import hashlib
    return hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]
