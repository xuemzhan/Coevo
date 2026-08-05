"""US-6 workspace path strategy (US-6-AC-1 / 协议 § 15 step 2-3).

Scope
-----
This module produces the canonical filesystem path strings for
the three states of an imported package:

* ``QuarantinePath`` — where the raw `.agent` file lands before
  the atomic-import transaction validates it (AC-2).
* ``WorkspacePath`` — the final per-project + per-role root where
  the released payload lives after a successful import (AC-5).
* ``WorkspacePaths`` — a small record carrying both, plus the
  staging root used during the transaction.

All paths are PURE strings; this slice does not touch the
filesystem. The persistence layer (future slice) is
responsible for the actual mkdir / write operations.

Path invariants (US-6 / 协议 § 19.1)
-----------------------------------
* No absolute paths in the released tree.
* No ``..`` traversal anywhere.
* No device / network / drive-letter prefixes.
* No symlinks pointing outside the workspace root.
* No nested archives (协议 § 19.4).
* All segments are restricted to a safe-id alphabet.

The path strategy is the one component that produces the
canonical names; downstream code MUST NOT compose its own paths.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-6 工作区路径策略：安全 ID、防穿越、默认根与完整路径装配。
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import Final

class WorkspacePathError(Exception):
    """Raised when a path does not satisfy the safe-id / no-traversal rules."""


# Allowed id alphabet: starts with letter/underscore, then
# letters / digits / underscores / hyphens / dots. Mirrors the
# safe-id used in identity / protocol layers so all components
# share one canonical id shape.
_SAFE_ID: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")
PROJECT_ID_MAX: Final[int] = 64
ROLE_ID_MAX: Final[int] = 64
_PACKAGE_ID_MAX: Final[int] = 64


def _has_parent_traversal(value: str) -> bool:
    """True when ``value`` contains a ``..`` segment under either path dialect.

    The path strings are pure and later consumed on Windows, so a
    ``..`` that is only visible when backslashes are treated as
    separators (e.g. ``a\\..\\b``) must be rejected as well as the
    POSIX form. Both dialects are checked so the result is
    host-independent.
    """
    for parts in (PurePosixPath(value).parts, PureWindowsPath(value).parts):
        if ".." in parts:
            return True
    return False


def sanitize_id(value: str, *, name: str, maximum: int = 64) -> str:
    """Validate a free-form identifier against the safe-id alphabet.

    Returns ``value`` unchanged on success; raises
    :class:`WorkspacePathError` with a precise cause on failure.
    """
    if not isinstance(value, str) or not value:
        raise WorkspacePathError(f"{name} must be a non-empty string")
    if len(value) > maximum:
        raise WorkspacePathError(
            f"{name} exceeds the {maximum}-char limit; got {len(value)} chars"
        )
    if not _SAFE_ID.match(value):
        raise WorkspacePathError(
            f"{name} must match ^[a-zA-Z_][a-zA-Z0-9_.\\-]{{0,{maximum}}}$; got {value!r}"
        )
    return value


@dataclass(frozen=True)
class QuarantinePath:
    """The path where the raw `.agent` file lands before validation.

    ``quarantine_root`` is supplied by the caller (typically
    ``DEFAULT_QUARANTINE_ROOT``); the package_id is appended as a
    final segment. The full path uses forward slashes for
    portability (Windows accepts both; the persistence layer
    translates on the way to the OS).
    """

    quarantine_root: str
    package_id: str

    def __post_init__(self) -> None:
        sanitize_id(self.package_id, name="package_id", maximum=_PACKAGE_ID_MAX)
        if not self.quarantine_root:
            raise WorkspacePathError("quarantine_root must be a non-empty string")
        if _has_parent_traversal(self.quarantine_root):
            raise WorkspacePathError(
                f"quarantine_root must not contain '..': {self.quarantine_root!r}"
            )

    def as_posix(self) -> str:
        root = self.quarantine_root.rstrip("/")
        return f"{root}/{self.package_id}.agent"


@dataclass(frozen=True)
class WorkspacePath:
    """The final per-project + per-role root for a released workspace.

    ``workspace_root`` is supplied by the caller; the
    ``project_id`` and ``role_id`` are appended as canonical
    sub-directories. The full path is::

        {workspace_root}/{project_id}/{role_id}

    which is the layout US-6-AC-1 AC-5 ("成功导入后创建独立项目
    和角色目录") and AC-6 ("释放任务描述、流程要求、交付物要求
    和文档模板") assume.
    """

    workspace_root: str
    project_id: str
    role_id: str

    def __post_init__(self) -> None:
        sanitize_id(self.project_id, name="project_id", maximum=PROJECT_ID_MAX)
        sanitize_id(self.role_id, name="role_id", maximum=ROLE_ID_MAX)
        if not self.workspace_root:
            raise WorkspacePathError("workspace_root must be a non-empty string")
        if _has_parent_traversal(self.workspace_root):
            raise WorkspacePathError(
                f"workspace_root must not contain '..': {self.workspace_root!r}"
            )

    def as_posix(self) -> str:
        root = self.workspace_root.rstrip("/")
        return f"{root}/{self.project_id}/{self.role_id}"


@dataclass(frozen=True)
class WorkspacePaths:
    """The full set of paths associated with one import transaction.

    ``staging_root`` is the temporary root used during the
    atomic-import transaction (协议 § 15 step 2-4); it is
    deleted on success (step 7) and on rollback.
    """

    quarantine: QuarantinePath
    staging_root: str
    workspace: WorkspacePath

    def __post_init__(self) -> None:
        if not self.staging_root:
            raise WorkspacePathError("staging_root must be a non-empty string")
        if _has_parent_traversal(self.staging_root):
            raise WorkspacePathError(
                f"staging_root must not contain '..': {self.staging_root!r}"
            )


def default_workspace_root() -> str:
    """Return the canonical default workspace root (AC-7 fail-closed default).

    Callers MAY override this with their own root; the default
    follows 协议 § 19.1's "relative paths only" rule by NOT
    starting with a drive letter or ``/``.
    """
    return "workspaces"


def build_paths(
    *,
    project_id: str,
    role_id: str,
    package_id: str,
    quarantine_root: str = "quarantine",
    workspace_root: str | None = None,
    staging_root: str | None = None,
) -> WorkspacePaths:
    """Build the full :class:`WorkspacePaths` for one import.

    ``workspace_root`` defaults to :func:`default_workspace_root`.
    ``staging_root`` defaults to ``f"staging/{package_id}"`` —
    a per-package temp dir that the persistence layer is expected
    to create and delete.
    """
    if workspace_root is None:
        workspace_root = default_workspace_root()
    if staging_root is None:
        staging_root = f"staging/{package_id}"
    return WorkspacePaths(
        quarantine=QuarantinePath(
            quarantine_root=quarantine_root,
            package_id=package_id,
        ),
        staging_root=staging_root,
        workspace=WorkspacePath(
            workspace_root=workspace_root,
            project_id=project_id,
            role_id=role_id,
        ),
    )
