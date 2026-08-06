# `progress_capture/` — Progress Capture (US-8)

## Scope

Workspace file watcher (polling + digest reuse + stability gating) and a pure
service mapping evidence to progress items; formal acceptance always requires
user confirmation; file-modification time alone is never completion evidence.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `EvidenceInput/Ref`, `ProgressItem`, `ProgressCapture`, `ProgressDraft` | Models + validation (EvidenceKind closed set, FILE_MTIME_ONLY excluded) |
| `watcher.py` | `WorkspaceWatcher.scan/drain/start/stop` | Watcher: single lstat, symlink skip, digest reuse, stability gating |
| `service.py` | `ProgressCaptureService.extract_progress/revise/reject/accept/to_report_draft` | Pure service: extract/revise/reject/accept/draft |

## Security invariants

- Symlinks skipped, root escape rejected; watcher emits facts only, never
  completion judgments;
- Changes require consecutive stable scans before events are emitted (avoids
  half-written files);
- Items must carry ≥1 evidence reference; audit projections exclude
  text/confidence/reason.

## Testing

- `tests/unit/test_progress_capture.py`, `test_progress_watcher.py`;
  `tests/integration/test_progress_watcher.py`.
