"""US-6 workspace domain model (US-6-AC-1).

Scope
-----
The data model for the in-memory workspace registry and the
``InitOutcome`` record returned by
:class:`WorkspaceInitService`.

* :class:`WorkspaceRole` — the per-project role binding.
* :class:`WorkspaceEntry` — a single registered workspace.
* :class:`WorkspaceRegistry` — the in-memory table of
  :class:`WorkspaceEntry` records. Pure-functional; every
  mutation returns a new instance.
* :class:`InitOutcome` — the per-import result. The registry
  inside ``InitOutcome`` reflects the post-init state (which
  is identical to the pre-init state on rollback).

AC mapping
----------
* AC-5 / AC-7 / AC-8 — covered by
  :class:`WorkspaceRegistry.register`'s idempotence rules.
* AC-4 — covered by the explicit ``InitOutcome.created=False``
  flag on duplicate or rollback paths.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .paths import WorkspacePaths


class WorkspaceInitError(Exception):
    """Base class for all US-6 errors. Fail-closed by default."""


class WorkspaceInitValidationError(WorkspaceInitError):
    """Raised when an input cannot be reconciled.

    Distinct from :class:`WorkspaceInitError` so callers can
    branch on "validation failed (user-fixable)" vs "structural
    invariant violated (engineering bug)".
    """


class WorkspacePathError(WorkspaceInitError):
    """Raised when a path does not satisfy the safe-id / no-traversal rules."""


@dataclass(frozen=True)
class WorkspaceRole:
    """A role binding inside a project workspace.

    ``role_id`` is the unique role identifier (e.g.
    ``"a.pm"`` or ``"a.eng"``); ``display_name`` is a
    human-readable label and is OPTIONAL (callers may leave it
    empty when the role is implicit).
    """

    role_id: str
    display_name: str = ""


@dataclass(frozen=True)
class WorkspaceEntry:
    """A single registered workspace (project + role + package)."""

    project_id: str
    role_id: str
    package_id: str
    revision: str  # 协议 § 16.1 master revision at init time


@dataclass(frozen=True)
class WorkspaceRegistry:
    """In-memory workspace registry.

    All mutating operations are pure: ``register`` returns a new
    registry instance. The registry keeps a fast-lookup index
    by ``(project_id, role_id)`` so duplicate-bind attempts raise
    ``WorkspaceInitValidationError`` immediately.
    """

    _entries: tuple[WorkspaceEntry, ...] = field(default_factory=tuple)
    _by_role: tuple[tuple[tuple[str, str], int], ...] = field(default_factory=tuple)

    @classmethod
    def empty(cls) -> "WorkspaceRegistry":
        return cls(_entries=tuple(), _by_role=tuple())

    def get(self, project_id: str, role_id: str) -> WorkspaceEntry | None:
        for key, idx in self._by_role:
            if key == (project_id, role_id):
                return self._entries[idx]
        return None

    def by_package(self, package_id: str) -> tuple[WorkspaceEntry, ...]:
        # ?????? package_id -> ????? O(1) ????
        # ???????????????????????????
        by_package: dict[str, list[WorkspaceEntry]] = {}
        for entry in self._entries:
            by_package.setdefault(entry.package_id, []).append(entry)
        return tuple(by_package.get(package_id, ()))

    def register(self, entry: WorkspaceEntry) -> "WorkspaceRegistry":
        """Atomically insert ``entry``.

        Refuses duplicate ``(project_id, role_id)`` (AC-7 / AC-8
        "同一任务包重复导入时不得重复创建任务"). Refuses duplicate
        ``package_id`` for the same ``(project_id, role_id)`` pair
        to enforce AC-8's idempotence rule.
        """
        if not isinstance(entry, WorkspaceEntry):
            raise WorkspaceInitError("entry must be WorkspaceEntry")
        if self.get(entry.project_id, entry.role_id) is not None:
            raise WorkspaceInitValidationError(
                f"workspace for project_id={entry.project_id!r} "
                f"role_id={entry.role_id!r} already exists (AC-7)"
            )
        for existing in self._entries:
            if (
                existing.project_id == entry.project_id
                and existing.role_id == entry.role_id
                and existing.package_id == entry.package_id
            ):
                raise WorkspaceInitValidationError(
                    f"package_id {entry.package_id!r} already initialized for "
                    f"project_id={entry.project_id!r} role_id={entry.role_id!r} (AC-8)"
                )
        new_idx = len(self._entries)
        return WorkspaceRegistry(
            _entries=self._entries + (entry,),
            _by_role=self._by_role + (((entry.project_id, entry.role_id), new_idx),),
        )

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)


@dataclass(frozen=True)
class InitOutcome:
    """The result of a :meth:`WorkspaceInitService.init_from_import` call.

    ``created`` is ``True`` only on a fresh registration; it is
    ``False`` when the call was a duplicate-package no-op (AC-8)
    OR when the call was rejected (AC-4 / AC-7). The
    ``registry`` reflects the post-call state (which is identical
    to the pre-call state when ``created is False``).
    """

    entry: WorkspaceEntry | None
    paths: WorkspacePaths
    registry: WorkspaceRegistry
    created: bool
    failure_reason: str = ""
