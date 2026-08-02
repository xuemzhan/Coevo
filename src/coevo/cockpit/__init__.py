"""US-7 local cockpit service facade.

Scope
-----
Pure half of US-7: the *governance* layer that decides which cockpit
request is allowed and what the response body should be. The slice
stops at the dispatch boundary -- actual HTTP server bring-up (which
uses ``http.server`` from the Python standard library) and actual HTML
rendering are deferred to US-7-AC-2.

* No new dependency (Python stdlib only).
* All dataclasses are frozen + exact-type + ISO-8601 UTC `Z` time strings.
* Pure function: same (request, server_state, now) yields identical
  CockpitResponse.
* to_audit_record mirrors US-11/12/13/8/15/4 by EXCLUDING free-form
  body_html and artifact_path from the audit row.

AC mapping
----------
* AC-1 环回绑定 -- :meth:`CockpitFacade.start_server` rejects any
  ``bind_host`` other than ``"127.0.0.1"``.
* AC-2 静态资源本地化 -- :class:`CockpitServerConfig.static_root` is
  forced to be inside ``src/coevo/cockpit/static/``; any path
  traversal attempt is rejected.
* AC-3 完全断网 -- pure local Python stdlib; no third-party import.
* AC-4 无外部网络请求 -- path-traversal rejection + static-root
  whitelist.
* AC-5 项目列表 -- :attr:`CockpitRoute.LIST_PROJECTS`.
* AC-6 角色视图 -- :attr:`CockpitRoute.LIST_ROLES` /
  :attr:`CockpitRoute.ROLE_VIEW`.
* AC-7 任务/里程碑/交付物 -- :attr:`CockpitRoute.TASK_VIEW` /
  :attr:`CockpitRoute.MILESTONE_VIEW` + the ``RoleView`` snapshot.
* AC-8 WPS 允许列表 -- :class:`WPSAllowList` + :attr:`CockpitRoute.WPS_OPEN`.
* AC-9 客户端重启状态保持 -- :class:`CockpitServerState` snapshot
  is immutable; ``dispatch`` reads from the snapshot, not from disk.

Non-goals
---------
* No actual HTTP socket bind (deferred to US-7-AC-2).
* No HTML / CSS / JS rendering (deferred to US-7-AC-2).
* No disk persistence of workspace_views (deferred to US-7-AC-3).
* No actual WPS subprocess call (deferred to US-7-AC-4).
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from pathlib import Path


_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")
_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")

# The only host the cockpit may bind to (AC-1).
LOOPBACK_HOST: str = "127.0.0.1"

# Static resources must live under this directory (AC-2). The slice
# enforces this at start_server time AND at dispatch time (path
# traversal rejection).
STATIC_ROOT: Path = Path(__file__).resolve().parent / "static"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class CockpitError(Exception):
    """Base class for all US-7 errors. Fail-closed by default."""


class CockpitValidationError(CockpitError):
    """An input field or config failed validation (user-fixable)."""


class CockpitNotFoundError(CockpitError):
    """A referenced project / role / task does not exist in the snapshot."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CockpitRoute(enum.Enum):
    """AC-5..AC-8 closed set of cockpit routes."""

    LIST_PROJECTS = "list_projects"
    LIST_ROLES = "list_roles"
    PROJECT_VIEW = "project_view"
    ROLE_VIEW = "role_view"
    TASK_VIEW = "task_view"
    MILESTONE_VIEW = "milestone_view"
    WPS_OPEN = "wps_open"


class CockpitResponseStatus(enum.Enum):
    """HTTP-like status codes (without depending on http module)."""

    OK = "ok"
    NOT_FOUND = "not_found"
    BAD_REQUEST = "bad_request"
    DENIED = "denied"
    NOT_BOUND = "not_bound"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


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
        if not isinstance(self.ts, str) or not _ISO_UTC_Z.match(self.ts):
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
        if not isinstance(self.ts, str) or not _ISO_UTC_Z.match(self.ts):
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
        if self.started_at and not _ISO_UTC_Z.match(self.started_at):
            raise CockpitValidationError(
                f"started_at must be ISO-8601 UTC 'Z'; got {self.started_at!r}"
            )


# ---------------------------------------------------------------------------
# WPS allow list (AC-8)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Service facade
# ---------------------------------------------------------------------------


class CockpitFacade:
    """Pure-function cockpit dispatch (US-7 AC-5..AC-9)."""

    @staticmethod
    def start_server(
        *,
        bind_host: str = LOOPBACK_HOST,
        bind_port: int = 12701,
        static_root: Path | str = STATIC_ROOT,
        max_request_bytes: int = 65536,
        request_timeout_sec: int = 5,
        workspace_views: tuple[WorkspaceView, ...] = (),
        role_views: tuple[RoleView, ...] = (),
        now: str = "",
    ) -> CockpitServerState:
        """Bind to loopback (AC-1), snapshot workspace + role views (AC-9)."""
        config = CockpitServerConfig(
            bind_host=bind_host,
            bind_port=bind_port,
            static_root=Path(static_root),
            max_request_bytes=max_request_bytes,
            request_timeout_sec=request_timeout_sec,
        )
        if not now:
            now = "1970-01-01T00:00:00Z"  # placeholder; real start sets started_at
        return CockpitServerState(
            config=config,
            workspace_views=workspace_views,
            role_views=role_views,
            started_at=now,
        )

    @staticmethod
    def dispatch(
        request: CockpitRequest,
        *,
        server_state: CockpitServerState,
        now: str,
    ) -> CockpitResponse:
        """AC-5..AC-8: dispatch a request to a response. Pure function."""
        if not isinstance(request, CockpitRequest):
            raise CockpitValidationError("request must be a CockpitRequest")
        if not isinstance(server_state, CockpitServerState):
            raise CockpitValidationError("server_state must be a CockpitServerState")
        if not isinstance(now, str) or not _ISO_UTC_Z.match(now):
            raise CockpitValidationError(f"now must be ISO-8601 UTC 'Z'; got {now!r}")

        # AC-1 fail-closed: refuse dispatch if the server isn't bound to loopback.
        if server_state.config.bind_host != LOOPBACK_HOST:
            return CockpitResponse(
                status=CockpitResponseStatus.NOT_BOUND,
                body_html="",
                content_type="text/plain; charset=utf-8",
                task="server not bound to loopback",
                payload={"bind_host": server_state.config.bind_host},
                ts=now,
            )

        if request.route == CockpitRoute.LIST_PROJECTS:
            return CockpitFacade._list_projects(server_state, now)
        if request.route == CockpitRoute.LIST_ROLES:
            return CockpitFacade._list_roles(server_state, request, now)
        if request.route == CockpitRoute.PROJECT_VIEW:
            return CockpitFacade._project_view(server_state, request, now)
        if request.route == CockpitRoute.ROLE_VIEW:
            return CockpitFacade._role_view(server_state, request, now)
        if request.route == CockpitRoute.TASK_VIEW:
            return CockpitFacade._task_view(server_state, request, now)
        if request.route == CockpitRoute.MILESTONE_VIEW:
            return CockpitFacade._milestone_view(server_state, request, now)
        if request.route == CockpitRoute.WPS_OPEN:
            return CockpitFacade._wps_open(server_state, request, now)
        return CockpitResponse(
            status=CockpitResponseStatus.BAD_REQUEST,
            body_html="",
            content_type="text/plain; charset=utf-8",
            task=f"unknown route {request.route.value!r}",
            payload={},
            ts=now,
        )

    # -- private dispatch helpers --

    @staticmethod
    def _list_projects(state: CockpitServerState, now: str) -> CockpitResponse:
        projects = tuple(w.project_id for w in state.workspace_views)
        html = "<ul>" + "".join(f"<li>{p}</li>" for p in projects) + "</ul>"
        return CockpitResponse(
            status=CockpitResponseStatus.OK,
            body_html=html,
            content_type="text/html; charset=utf-8",
            task="list projects",
            payload={"projects": projects, "count": len(projects)},
            ts=now,
        )

    @staticmethod
    def _list_roles(
        state: CockpitServerState, request: CockpitRequest, now: str
    ) -> CockpitResponse:
        if not request.project_id:
            return CockpitResponse(
                status=CockpitResponseStatus.BAD_REQUEST,
                body_html="",
                content_type="text/plain; charset=utf-8",
                task="project_id required for list_roles",
                payload={},
                ts=now,
            )
        ws = next(
            (w for w in state.workspace_views if w.project_id == request.project_id),
            None,
        )
        if ws is None:
            return CockpitResponse(
                status=CockpitResponseStatus.NOT_FOUND,
                body_html="",
                content_type="text/plain; charset=utf-8",
                task=f"project {request.project_id!r} not found",
                payload={"project_id": request.project_id},
                ts=now,
            )
        html = "<ul>" + "".join(f"<li>{r}</li>" for r in ws.roles) + "</ul>"
        return CockpitResponse(
            status=CockpitResponseStatus.OK,
            body_html=html,
            content_type="text/html; charset=utf-8",
            task="list roles",
            payload={"project_id": ws.project_id, "roles": ws.roles},
            ts=now,
        )

    @staticmethod
    def _project_view(
        state: CockpitServerState, request: CockpitRequest, now: str
    ) -> CockpitResponse:
        ws = next(
            (w for w in state.workspace_views if w.project_id == request.project_id),
            None,
        )
        if ws is None:
            return CockpitResponse(
                status=CockpitResponseStatus.NOT_FOUND,
                body_html="",
                content_type="text/plain; charset=utf-8",
                task=f"project {request.project_id!r} not found",
                payload={"project_id": request.project_id},
                ts=now,
            )
        html = (
            f"<h1>{ws.display_name}</h1>"
            f"<p>tasks: {ws.task_count} milestones: {ws.milestone_count} "
            f"artifacts: {ws.artifact_count}</p>"
        )
        return CockpitResponse(
            status=CockpitResponseStatus.OK,
            body_html=html,
            content_type="text/html; charset=utf-8",
            task="project view",
            payload={
                "project_id": ws.project_id,
                "task_count": ws.task_count,
                "milestone_count": ws.milestone_count,
                "artifact_count": ws.artifact_count,
            },
            ts=now,
        )

    @staticmethod
    def _role_view(
        state: CockpitServerState, request: CockpitRequest, now: str
    ) -> CockpitResponse:
        rv = next(
            (
                r for r in state.role_views
                if r.role_id == request.role_id and r.project_id == request.project_id
            ),
            None,
        )
        if rv is None:
            return CockpitResponse(
                status=CockpitResponseStatus.NOT_FOUND,
                body_html="",
                content_type="text/plain; charset=utf-8",
                task=f"role {request.role_id!r} in project {request.project_id!r} not found",
                payload={"project_id": request.project_id, "role_id": request.role_id},
                ts=now,
            )
        return CockpitResponse(
            status=CockpitResponseStatus.OK,
            body_html=f"<h1>{rv.display_name}</h1><p>tasks: {len(rv.current_tasks)}</p>",
            content_type="text/html; charset=utf-8",
            task="role view",
            payload={
                "role_id": rv.role_id,
                "project_id": rv.project_id,
                "display_name": rv.display_name,
                "task_count": len(rv.current_tasks),
                "milestone_count": len(rv.milestones),
                "artifact_count": len(rv.artifacts),
            },
            ts=now,
        )

    @staticmethod
    def _task_view(
        state: CockpitServerState, request: CockpitRequest, now: str
    ) -> CockpitResponse:
        for rv in state.role_views:
            if rv.project_id != request.project_id or rv.role_id != request.role_id:
                continue
            for task in rv.current_tasks:
                if task.task_id == request.task_id:
                    return CockpitResponse(
                        status=CockpitResponseStatus.OK,
                        body_html=f"<h1>{task.title}</h1><p>{task.status}</p>",
                        content_type="text/html; charset=utf-8",
                        task="task view",
                        payload={
                            "task_id": task.task_id,
                            "title": task.title,
                            "status": task.status,
                            "due_at": task.due_at,
                            "assignee_role_id": task.assignee_role_id,
                        },
                        ts=now,
                    )
        return CockpitResponse(
            status=CockpitResponseStatus.NOT_FOUND,
            body_html="",
            content_type="text/plain; charset=utf-8",
            task=(
                f"task {request.task_id!r} in role {request.role_id!r} "
                f"of project {request.project_id!r} not found"
            ),
            payload={
                "project_id": request.project_id,
                "role_id": request.role_id,
                "task_id": request.task_id,
            },
            ts=now,
        )

    @staticmethod
    def _milestone_view(
        state: CockpitServerState, request: CockpitRequest, now: str
    ) -> CockpitResponse:
        for rv in state.role_views:
            if rv.project_id != request.project_id:
                continue
            for ms in rv.milestones:
                if ms.milestone_id == request.task_id:  # treat task_id slot as id
                    return CockpitResponse(
                        status=CockpitResponseStatus.OK,
                        body_html=f"<h1>{ms.title}</h1><p>{'done' if ms.completed else 'open'}</p>",
                        content_type="text/html; charset=utf-8",
                        task="milestone view",
                        payload={
                            "milestone_id": ms.milestone_id,
                            "title": ms.title,
                            "due_at": ms.due_at,
                            "completed": ms.completed,
                        },
                        ts=now,
                    )
        return CockpitResponse(
            status=CockpitResponseStatus.NOT_FOUND,
            body_html="",
            content_type="text/plain; charset=utf-8",
            task=f"milestone {request.task_id!r} in project {request.project_id!r} not found",
            payload={"project_id": request.project_id, "milestone_id": request.task_id},
            ts=now,
        )

    @staticmethod
    def _wps_open(
        state: CockpitServerState, request: CockpitRequest, now: str
    ) -> CockpitResponse:
        # AC-4 + AC-8: artifact_path must be workspace-relative (no traversal)
        # AND must pass WPS allow-list.
        path = request.artifact_path
        if not path:
            return CockpitResponse(
                status=CockpitResponseStatus.BAD_REQUEST,
                body_html="",
                content_type="text/plain; charset=utf-8",
                task="artifact_path required for wps_open",
                payload={},
                ts=now,
            )
        if not WPSAllowList.is_allowed_extension(path):
            return CockpitResponse(
                status=CockpitResponseStatus.DENIED,
                body_html="",
                content_type="text/plain; charset=utf-8",
                task=f"extension of {path!r} not in WPS allow-list",
                payload={"artifact_path_hash": _hash_path(path)},
                ts=now,
            )
        # OK: facade returns a render stub. Actual subprocess is US-7-AC-4.
        html = f"<p>WPS open accepted: {path}</p>"
        return CockpitResponse(
            status=CockpitResponseStatus.OK,
            body_html=html,
            content_type="text/html; charset=utf-8",
            task="wps_open accepted",
            payload={"artifact_path_hash": _hash_path(path), "ok": True},
            ts=now,
        )

    @staticmethod
    def to_audit_record(
        request: CockpitRequest, response: CockpitResponse
    ) -> dict:
        """Project a request/response pair into an audit row.

        Mirrors US-11/12/13/8/15/4 by EXCLUDING body_html and artifact_path
        (kept only as ``artifact_path_hash``). Status + route + counts are
        preserved so the audit row is forward-compatible.
        """
        if not isinstance(request, CockpitRequest):
            raise CockpitValidationError("request must be a CockpitRequest")
        if not isinstance(response, CockpitResponse):
            raise CockpitValidationError("response must be a CockpitResponse")
        return {
            "schema_version": "1.0",
            "domain": "coevo.cockpit",
            "route": request.route.value,
            "project_id": request.project_id,
            "role_id": request.role_id,
            "task_id": request.task_id,
            "artifact_path_hash": (
                _hash_path(request.artifact_path) if request.artifact_path else ""
            ),
            "status": response.status.value,
            "task": response.task,
            "payload_keys": sorted(response.payload.keys()),
            "ts": response.ts,
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _hash_path(path: str) -> str:
    """Stable, audit-friendly path summary (NOT cryptographic commitment)."""
    import hashlib
    return hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Real HTTP server layer (US-7-AC-2)
# ---------------------------------------------------------------------------
#
# Imported last: server.py imports the facade types defined above, so
# this re-export must not run before those names are bound.

from .server import (  # noqa: E402
    CSRF_HEADER_VALUE,
    CockpitHttpConfig,
    CockpitHttpServer,
    CockpitSessionManager,
    SingleInstanceLock,
    now_utc_iso_z,
    resolve_static_path,
)
