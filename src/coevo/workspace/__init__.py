"""US-6 workspace initialization (US-6-AC-1).

Scope
-----
US-6 describes the receiver-side workspace lifecycle for an
imported .agent package. The full AC has eight sub-requirements
(AC-1..AC-8 in ``docs/requirements/mvp-user-stories.md``); this
slice (US-6-AC-1) ships the *deterministic, in-memory* half:

* a path strategy that produces the canonical quarantine,
  staging, and final-workspace roots (AC-2 / AC-4);
* an in-memory workspace registry that prevents duplicate
  project + role pairs (AC-5 / AC-7 / AC-8) and that survives
  a single import's lifecycle so a re-import is idempotent
  (AC-8);
* a ``WorkspaceInitService`` facade that consumes a
  :class:`ImportOutcome` from :mod:`coevo.protocol.import_service`
  and emits an :class:`InitOutcome` describing the released
  workspace.

The slice is PURE: the service generates path strings, updates
an in-memory registry, and emits an audit record. The actual
filesystem writes and database inserts are the persistence
layer's job in a future slice (out of scope for AC-1).

What this is NOT
----------------
* No IO. The service never touches the filesystem or any
  database.
* No LLM, no model, no network.
* No mutation of US-5 wire layout. The service consumes a
  :class:`ImportOutcome` (US-5-AC-3) verbatim.
"""
from .models import (
    InitOutcome,
    WorkspaceEntry,
    WorkspaceInitError,
    WorkspaceInitValidationError,
    WorkspaceRegistry,
    WorkspaceRole,
)
from .paths import (
    PROJECT_ID_MAX,
    QuarantinePath,
    ROLE_ID_MAX,
    WorkspacePath,
    WorkspacePathError,
    WorkspacePaths,
    build_paths,
    default_workspace_root,
    sanitize_id,
)
from .init_service import (
    DEFAULT_QUARANTINE_ROOT,
    DEFAULT_WORKSPACE_ROOT,
    WorkspaceInitService,
)

__all__ = [
    "DEFAULT_QUARANTINE_ROOT",
    "DEFAULT_WORKSPACE_ROOT",
    "InitOutcome",
    "PROJECT_ID_MAX",
    "QuarantinePath",
    "ROLE_ID_MAX",
    "WorkspaceEntry",
    "WorkspaceInitError",
    "WorkspaceInitService",
    "WorkspaceInitValidationError",
    "WorkspacePath",
    "WorkspacePathError",
    "WorkspacePaths",
    "WorkspaceRegistry",
    "WorkspaceRole",
    "build_paths",
    "default_workspace_root",
    "sanitize_id",
]