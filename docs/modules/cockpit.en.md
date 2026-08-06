# `cockpit/` — Local Cockpit (US-7)

## Scope

Loopback-bound local HTTP dashboard: view snapshots, bearer-token sessions,
state persistence, localized static assets and controlled WPS document launch.
Works fully offline.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `CockpitRoute/Request/Response`, `WorkspaceView`, `WPSAllowList` | Routes/status/views/config (loopback enforcement, WPS allow-list) |
| `facade.py` | `CockpitFacade.dispatch/to_audit_record` | Pure-function routing + audit projection |
| `server.py` | `CockpitHttpServer`, `SingleInstanceLock` | Single-instance lock (heartbeat + liveness), HTTP handler, lifecycle, access audit log |
| `sessions.py` | `CockpitSessionManager` | Bearer-token sessions (expiry/rotation/cap) |
| `state_store.py` | `CockpitStateStore` | Atomic JSON state persistence (periodic checkpoint + shutdown flush) |
| `static.py` | `resolve_static_path()`, `_StaticAssetCache` | Static path policy + bounded FIFO cache |
| `wps.py` | `WpsLauncher` | Controlled WPS launch (allow-listed extensions, timeout, fail-closed) |

## Security invariants

- Binds `127.0.0.1` only (fail-closed); every response carries `nosniff`,
  session/API responses `no-store` + `no-referrer` (static may override the
  cache policy), index keeps CSP;
- Token + Host/Origin allow-list + CSRF header required; concurrency bounded
  (default 16, saturated → 503);
- Single-instance lock prevents dual writers; access log never records tokens.

## Config / HTTP semantics

- Env vars via `AppConfig.from_env()` (host/port/session timeout/checkpoint/
  state/log/lock paths); HTTP: 401/403/404/413/500/503 semantics.

## Testing

- Unit: `test_cockpit.py`, `test_cockpit_http.py`, `test_cockpit_state_store.py`;
- Integration: `test_cockpit_http_server.py`, `test_cockpit_state_persistence.py`;
- E2E: `test_cockpit_launcher.py`, `test_cockpit_offline_frontend.py`.
