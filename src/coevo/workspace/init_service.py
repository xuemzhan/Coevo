"""US-6 workspace initialization service (US-6-AC-1).

Scope
-----
This module is the facade that ties the US-5 atomic-import
service to the US-6 workspace lifecycle. The service consumes
a :class:`ImportOutcome` (US-5-AC-3) and produces an
:class:`InitOutcome` describing the released workspace.

The service is PURE: it never touches the filesystem or any
database. Its job is to:

* derive the canonical quarantine / staging / workspace paths
  (AC-2 / AC-4);
* register the new workspace entry (AC-5 / AC-7);
* enforce AC-8 idempotence (same package_id re-imported for the
  same project + role is a no-op);
* emit an audit-record projection.

Side effects (mkdir, file copy, DB insert) are the persistence
layer's responsibility in a future slice.

AC mapping
----------
* AC-1 / AC-3 — covered by the parent US-5-AC-3 service. This
  slice does not implement directory-monitoring or manual-pick
  import (those are higher-level UI concerns).
* AC-2 — covered by :class:`QuarantinePath` and the
  ``quarantine_root`` parameter.
* AC-4 — covered by :class:`InitOutcome` with ``created=False``
  on rejected imports.
* AC-5 / AC-6 — covered by :class:`WorkspacePath` and the
  in-memory :class:`WorkspaceRegistry`.
* AC-7 — covered by :meth:`WorkspaceRegistry.register` which
  refuses duplicate ``(project_id, role_id)``.
* AC-8 — covered by :meth:`WorkspaceInitService.init_from_import`
  which returns ``created=False`` (and the unchanged registry)
  when the same ``package_id`` is re-imported.
"""
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 工作区初始化服务（US-6 AC-1）：WorkspaceInitService.init_from_import() 把
# US-5 原子导入结果转成工作区初始化结果——非 COMMITTED 拒绝（AC-4）、
# 重复 (project, role) 拒绝（AC-7）、同包幂等（AC-8）、成功返回
# 项目/角色目录路径（AC-5/AC-6）。本层纯函数，路径策略在 paths.py。

from __future__ import annotations

import dataclasses

from src.coevo.protocol import ImportOutcome, ImportTransaction

from .models import (
    InitOutcome,
    WorkspaceEntry,
    WorkspaceInitError,
    WorkspaceInitValidationError,
    WorkspacePaths,
    WorkspaceRegistry,
)
from .paths import (
    WorkspacePathError,
    WorkspacePaths as _Paths,  # re-export
    build_paths,
    default_workspace_root,
    sanitize_id,
)


DEFAULT_QUARANTINE_ROOT: str = "quarantine"
DEFAULT_WORKSPACE_ROOT: str = default_workspace_root()


@dataclasses.dataclass(frozen=True)
class WorkspaceInitService:
    """Deterministic facade for US-6-AC-1.

    No internal state — every method is a pure function of its
    arguments. Callers may safely construct it once at module
    import time.
    """

    quarantine_root: str = DEFAULT_QUARANTINE_ROOT
    workspace_root: str = DEFAULT_WORKSPACE_ROOT

    def init_from_import(
        self,
        import_outcome: ImportOutcome,
        registry: WorkspaceRegistry,
        *,
        role_id: str,
        revision: str | None = None,
    ) -> InitOutcome:
        """Translate a US-5 ImportOutcome into a workspace init result.

        The caller (typically the storage layer) supplies the
        :class:`WorkspaceRegistry`; the service updates it
        atomically on success. On AC-4 / AC-7 / AC-8 rejection
        the registry is returned unchanged.
        """
        if not isinstance(import_outcome, ImportOutcome):
            raise WorkspaceInitError("import_outcome must be ImportOutcome")
        if not isinstance(registry, WorkspaceRegistry):
            raise WorkspaceInitError("registry must be WorkspaceRegistry")
        # role_id validation: surface validation errors as
        # WorkspaceInitValidationError BEFORE the transaction-state
        # check so the caller always sees a ValidationError for
        # caller-fixable inputs.
        if not isinstance(role_id, str) or not role_id:
            raise WorkspaceInitValidationError("role_id must be a non-empty string")
        try:
            sanitize_id(role_id, name="role_id", maximum=64)
        except WorkspacePathError as exc:
            raise WorkspaceInitValidationError(str(exc)) from exc

        env = import_outcome.transaction

        def paths_for(env: ImportTransaction) -> WorkspacePaths:
            return build_paths(
                project_id=env.project_id,
                role_id=role_id,
                package_id=env.package_id,
                quarantine_root=self.quarantine_root,
                workspace_root=self.workspace_root,
            )

        if env.step.value != "committed":
            # AC-4: a non-committed import must not produce a workspace.
            return InitOutcome(
                entry=None,
                paths=paths_for(env),
                registry=registry,
                created=False,
                failure_reason=(
                    f"import transaction is not COMMITTED "
                    f"(step={env.step.value}); refusing to release workspace (AC-4)"
                ),
            )

        # 路径非法（如 import 事务携带不安全 package_id）时 build_paths
        # 失败关闭：直接传播 WorkspacePathError，不产生半成品 InitOutcome。
        paths = paths_for(env)

        # AC-8: same package_id re-imported for the same (project, role)
        # is a no-op. We compare against the registry BEFORE attempting
        # register (which would otherwise raise on duplicate).
        for existing in registry.by_package(env.package_id):
            if existing.project_id == env.project_id and existing.role_id == role_id:
                return InitOutcome(
                    entry=existing,
                    paths=paths,
                    registry=registry,
                    created=False,
                    failure_reason=(
                        f"package_id {env.package_id!r} already initialized for "
                        f"({env.project_id!r}, {role_id!r}) (AC-8)"
                    ),
                )

        entry_revision = revision or env.step.value
        entry = WorkspaceEntry(
            project_id=env.project_id,
            role_id=role_id,
            package_id=env.package_id,
            revision=entry_revision,
        )
        try:
            new_registry = registry.register(entry)
        except WorkspaceInitValidationError as exc:
            return InitOutcome(
                entry=None,
                paths=paths,
                registry=registry,
                created=False,
                failure_reason=str(exc),
            )
        return InitOutcome(
            entry=entry,
            paths=paths,
            registry=new_registry,
            created=True,
        )

    def to_audit_record(self, outcome: InitOutcome) -> dict[str, object]:
        """Produce a deterministic, JSON-safe audit-record projection."""
        if not isinstance(outcome, InitOutcome):
            raise WorkspaceInitError("outcome must be InitOutcome")
        if outcome.entry is None:
            return {
                "kind": "workspace.init",
                "schema_version": "1.0",
                "created": False,
                "failure_reason": outcome.failure_reason,
                "quarantine_path": outcome.paths.quarantine.as_posix(),
                "staging_root": outcome.paths.staging_root,
                "workspace_path": outcome.paths.workspace.as_posix(),
            }
        return {
            "kind": "workspace.init",
            "schema_version": "1.0",
            "created": True,
            "project_id": outcome.entry.project_id,
            "role_id": outcome.entry.role_id,
            "package_id": outcome.entry.package_id,
            "revision": outcome.entry.revision,
            "quarantine_path": outcome.paths.quarantine.as_posix(),
            "staging_root": outcome.paths.staging_root,
            "workspace_path": outcome.paths.workspace.as_posix(),
        }
