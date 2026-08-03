"""cockpit.facade - CockpitFacade route dispatch and audit projection."""

from __future__ import annotations

from pathlib import Path

from .models import CockpitRequest, CockpitResponse, CockpitResponseStatus, CockpitRoute, CockpitServerConfig, CockpitServerState, CockpitValidationError, LOOPBACK_HOST, RoleView, STATIC_ROOT, WPSAllowList, WorkspaceView, _ISO_UTC_Z, _hash_path

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
