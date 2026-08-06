# Root Modules

Standalone modules at the `src/coevo/` root:

| File | Key functions | Responsibility |
|---|---|---|
| `config.py` | `AppConfig`, `from_env()` | Production config: env-driven, fail-closed (loopback, port, level, paths) |
| `version.py` | `VERSION`, `APP_NAME` | Semantic versioning (timestamps forbidden) |
| `logging_setup.py` | `setup_logging()` | stdlib logging bootstrap (rotating files; audit chain kept separate) |
| `records_archive.py` | `archive_plan()` | Pure record-archiving policy helper |

## Config env vars

`COEVO_COCKPIT_HOST/PORT`, `COEVO_DATA_DIR/LOG_DIR`,
`COEVO_SESSION_TIMEOUT_SEC`, `COEVO_COCKPIT_CHECKPOINT_SEC`,
`COEVO_LOG_LEVEL`, `COEVO_STATE_PATH/LOG_PATH/LOCK_PATH` — invalid values raise
`ConfigError`, never silently fall back.

## Testing

- `tests/unit/test_records_archive.py`, `test_production_docs.py`;
  `tests/security/test_loop_state_transaction.py`.
