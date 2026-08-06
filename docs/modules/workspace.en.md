# `workspace/` — Workspace (US-6)

## Scope

Pure-function conversion of import outcomes to workspace paths and registry
entries: project/role isolation, safe IDs, traversal prevention, duplicate
import idempotence.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `WorkspaceEntry`, `WorkspaceRegistry`, `WorkspaceRole`, `InitOutcome` | Registry (indexed queries) + init results |
| `paths.py` | `sanitize_id()`, `QuarantinePath`, `WorkspacePath`, `build_paths()` | Safe path policy (dual POSIX/Windows traversal checks, default roots) |
| `init_service.py` | `WorkspaceInitService.init_from_import()` | Init service: only COMMITTED releases, same-package idempotence |

## Security invariants

- Non-COMMITTED transactions never release a workspace; duplicate imports are
  idempotent;
- Paths reject absolute/`..`/device prefixes/symlink escapes (both dialects);
- Workspace directories use generated unique IDs, not raw user input.

## Testing

- `tests/unit/test_workspace_init.py` (30);
  `tests/integration/test_agent_package_atomic_import.py`.
