"""US-7-AC-3 cockpit state persistence (JSON, atomic, fail-closed).

The store persists only the *views* (workspace_views + role_views) that
the pure facade dispatches against. Loading is fail-closed: a missing
file yields ``None``, but a present-but-corrupt file raises
:class:`CockpitValidationError` instead of silently starting empty.
Saving is atomic (temporary file + ``os.replace``) and never clobbers
an existing state on failure.

No new dependency; Python stdlib only.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-7-AC-3 状态持久化：JSON 序列化 + 原子写（临时文件 + 换名），失败关闭。
from __future__ import annotations

import json
import functools
import os
import uuid
from pathlib import Path
from typing import Any

from src.coevo.canon import canonical_json_bytes
from src.coevo.jsonutil import reject_duplicate_pairs
from . import (
    ArtifactSummary,
    CockpitValidationError,
    MilestoneSummary,
    RoleView,
    TaskSummary,
    WorkspaceView,
)


SCHEMA_VERSION: str = "1.0"
STATE_MAX_BYTES: int = 4 * 1024 * 1024
_ALLOWED_TOP_LEVEL: frozenset[str] = frozenset({
    "schema_version", "workspace_views", "role_views",
})


def _require(mapping: dict[str, Any], key: str, expected: type) -> Any:
    if not isinstance(mapping, dict):
        raise CockpitValidationError("state payload must be a JSON object")
    value = mapping.get(key)
    if not isinstance(value, expected):
        raise CockpitValidationError(
            f"{key} must be {expected.__name__}; got {type(value).__name__}"
        )
    return value


def _workspace_view_to_mapping(view: WorkspaceView) -> dict[str, Any]:
    return {
        "project_id": view.project_id,
        "display_name": view.display_name,
        "roles": list(view.roles),
        "task_count": view.task_count,
        "milestone_count": view.milestone_count,
        "artifact_count": view.artifact_count,
    }


def _mapping_to_workspace_view(data: dict[str, Any]) -> WorkspaceView:
    allowed = frozenset({
        "project_id", "display_name", "roles",
        "task_count", "milestone_count", "artifact_count",
    })
    if not isinstance(data, dict) or set(data) != allowed:
        raise CockpitValidationError("workspace_view fields are invalid")
    roles = tuple(_require(data, "roles", list))
    if not all(isinstance(role, str) for role in roles):
        raise CockpitValidationError("workspace_view roles must be strings")
    return WorkspaceView(
        project_id=_require(data, "project_id", str),
        display_name=_require(data, "display_name", str),
        roles=roles,
        task_count=_require(data, "task_count", int),
        milestone_count=_require(data, "milestone_count", int),
        artifact_count=_require(data, "artifact_count", int),
    )


def _task_summary_to_mapping(task: TaskSummary) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "title": task.title,
        "status": task.status,
        "due_at": task.due_at,
        "assignee_role_id": task.assignee_role_id,
    }


def _mapping_to_task_summary(data: dict[str, Any]) -> TaskSummary:
    allowed = frozenset({
        "task_id", "title", "status", "due_at", "assignee_role_id",
    })
    if not isinstance(data, dict) or set(data) != allowed:
        raise CockpitValidationError("task_summary fields are invalid")
    return TaskSummary(
        task_id=_require(data, "task_id", str),
        title=_require(data, "title", str),
        status=_require(data, "status", str),
        due_at=_require(data, "due_at", str),
        assignee_role_id=_require(data, "assignee_role_id", str),
    )


def _milestone_summary_to_mapping(milestone: MilestoneSummary) -> dict[str, Any]:
    return {
        "milestone_id": milestone.milestone_id,
        "title": milestone.title,
        "due_at": milestone.due_at,
        "completed": milestone.completed,
    }


def _mapping_to_milestone_summary(data: dict[str, Any]) -> MilestoneSummary:
    allowed = frozenset({"milestone_id", "title", "due_at", "completed"})
    if not isinstance(data, dict) or set(data) != allowed:
        raise CockpitValidationError("milestone_summary fields are invalid")
    return MilestoneSummary(
        milestone_id=_require(data, "milestone_id", str),
        title=_require(data, "title", str),
        due_at=_require(data, "due_at", str),
        completed=_require(data, "completed", bool),
    )


def _artifact_summary_to_mapping(artifact: ArtifactSummary) -> dict[str, Any]:
    return {
        "path": artifact.path,
        "role": artifact.role,
        "media_type": artifact.media_type,
        "size_bytes": artifact.size_bytes,
        "digest_hex": artifact.digest_hex,
    }


def _mapping_to_artifact_summary(data: dict[str, Any]) -> ArtifactSummary:
    allowed = frozenset({
        "path", "role", "media_type", "size_bytes", "digest_hex",
    })
    if not isinstance(data, dict) or set(data) != allowed:
        raise CockpitValidationError("artifact_summary fields are invalid")
    return ArtifactSummary(
        path=_require(data, "path", str),
        role=_require(data, "role", str),
        media_type=_require(data, "media_type", str),
        size_bytes=_require(data, "size_bytes", int),
        digest_hex=_require(data, "digest_hex", str),
    )


def _role_view_to_mapping(view: RoleView) -> dict[str, Any]:
    return {
        "role_id": view.role_id,
        "project_id": view.project_id,
        "display_name": view.display_name,
        "current_tasks": [_task_summary_to_mapping(task) for task in view.current_tasks],
        "milestones": [
            _milestone_summary_to_mapping(milestone) for milestone in view.milestones
        ],
        "artifacts": [
            _artifact_summary_to_mapping(artifact) for artifact in view.artifacts
        ],
    }


def _mapping_to_role_view(data: dict[str, Any]) -> RoleView:
    allowed = frozenset({
        "role_id", "project_id", "display_name",
        "current_tasks", "milestones", "artifacts",
    })
    if not isinstance(data, dict) or set(data) != allowed:
        raise CockpitValidationError("role_view fields are invalid")
    tasks = tuple(
        _mapping_to_task_summary(item) for item in _require(data, "current_tasks", list)
    )
    milestones = tuple(
        _mapping_to_milestone_summary(item)
        for item in _require(data, "milestones", list)
    )
    artifacts = tuple(
        _mapping_to_artifact_summary(item)
        for item in _require(data, "artifacts", list)
    )
    return RoleView(
        role_id=_require(data, "role_id", str),
        project_id=_require(data, "project_id", str),
        display_name=_require(data, "display_name", str),
        current_tasks=tasks,
        milestones=milestones,
        artifacts=artifacts,
    )


def serialize_views(
    workspace_views: tuple[WorkspaceView, ...],
    role_views: tuple[RoleView, ...],
) -> dict[str, Any]:
    """Serialize the views into a canonical, schema-versioned payload."""
    if not isinstance(workspace_views, tuple) or not all(
        isinstance(view, WorkspaceView) for view in workspace_views
    ):
        raise CockpitValidationError("workspace_views must be a tuple of WorkspaceView")
    if not isinstance(role_views, tuple) or not all(
        isinstance(view, RoleView) for view in role_views
    ):
        raise CockpitValidationError("role_views must be a tuple of RoleView")
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_views": [
            _workspace_view_to_mapping(view) for view in workspace_views
        ],
        "role_views": [_role_view_to_mapping(view) for view in role_views],
    }


def deserialize_views(
    data: dict[str, Any],
) -> tuple[tuple[WorkspaceView, ...], tuple[RoleView, ...]]:
    """Strictly parse a persisted payload; any deviation raises."""
    if set(data) != _ALLOWED_TOP_LEVEL:
        raise CockpitValidationError("state payload has unknown top-level fields")
    if _require(data, "schema_version", str) != SCHEMA_VERSION:
        raise CockpitValidationError("unsupported state schema_version")
    workspace = tuple(
        _mapping_to_workspace_view(item)
        for item in _require(data, "workspace_views", list)
    )
    roles = tuple(
        _mapping_to_role_view(item) for item in _require(data, "role_views", list)
    )
    return workspace, roles


class CockpitStateStore:
    """Atomic, fail-closed JSON persistence for cockpit views."""

    def __init__(self, path: Path) -> None:
        if not isinstance(path, Path):
            raise CockpitValidationError("state path must be a Path")
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def save(
        self,
        workspace_views: tuple[WorkspaceView, ...],
        role_views: tuple[RoleView, ...],
    ) -> None:
        """Atomically persist the current server state snapshot."""
        payload = serialize_views(workspace_views, role_views)
        body = canonical_json_bytes(payload, ensure_ascii=False)
        if len(body) > STATE_MAX_BYTES:
            raise CockpitValidationError("serialized cockpit state exceeds size limit")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_name(f"{self._path.name}.{uuid.uuid4().hex}.tmp")
        try:
            fd = os.open(str(tmp), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(body)
                    stream.flush()
                    os.fsync(stream.fileno())
            except Exception:
                try:
                    tmp.unlink()
                except OSError:
                    pass
                raise
            os.replace(str(tmp), str(self._path))
        finally:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass

    def load(
        self,
    ) -> tuple[tuple[WorkspaceView, ...], tuple[RoleView, ...]] | None:
        """Return persisted views, ``None`` when absent, raise on corruption."""
        if not self._path.exists():
            return None
        try:
            body = self._path.read_bytes()
        except OSError as exc:
            raise CockpitValidationError(f"cannot read cockpit state ({exc})") from exc
        if len(body) > STATE_MAX_BYTES:
            raise CockpitValidationError("cockpit state file exceeds size limit")
        try:
            data = json.loads(
                body.decode("utf-8"),
                object_pairs_hook=functools.partial(
                    reject_duplicate_pairs, error_factory=CockpitValidationError
                ),
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CockpitValidationError("cockpit state is not valid JSON") from exc
        return deserialize_views(data)
