# US-7-AC-2 Slice Plan: real local cockpit HTTP server

> Loop PLAN stage, 2026-08-02. Corresponds to BACKLOG item
> `US-7-AC-2` / `tests/integration/test_cockpit_http_server.py`.
> Follows AGENTS.md document priority and the seven-stage loop; does not
> change `.agent` wire, crypto scheme, or existing modules.

## 1. Scope

Build the real HTTP server layer behind the US-7-AC-1 pure facade:

* `http.server.ThreadingTCPServer` / `BaseHTTPRequestHandler` bound to
  `127.0.0.1` only (AC-1, fail-closed; other binds are rejected at
  config construction).
* Local identity token + session management (mandatory constraints 5.2):
  random bearer token issued by `CockpitSessionManager`; only the
  SHA-256 token hash is stored; constant-time comparison; session
  inactivity timeout; bounded session table.
* Request-source validation: `Host` header must be a loopback host;
  state-changing (`POST`) requests additionally require a loopback
  `Origin` and the `X-Requested-With: coevo-cockpit` header (CSRF).
* Write-op permission + double confirmation: `wps_open` is a POST that
  requires an explicit `confirm: true` in the bounded JSON body.
* Static asset serving from `src/coevo/cockpit/static/` only, with an
  extension allow-list, traversal rejection, bounded file size, and
  `Cache-Control`/CSP/`nosniff` headers; no external URLs (AC-2/AC-4).
* Real HTML/JS rendering: `index.html` + `app.js` + `style.css` render
  projects / roles / tasks / milestones / artifacts by calling the
  local JSON API with the session token (AC-5..AC-8 display).
* Per-request audit rows via `CockpitFacade.to_audit_record` into a
  bounded in-memory log (AC-7; US-15-AC-2 will add push/subscribe).
* Optional single-instance lock file (`config.lock_path`) so two
  cockpit processes cannot serve the same state.

## 2. Non-goals (deferred)

* WPS subprocess invocation (US-7-AC-4); this slice returns the
  facade's `wps_open` accept/stub response.
* Workspace-view persistence to disk (US-7-AC-3).
* Browser-based token persistence beyond sessionStorage; tokens are
  never logged or written to disk.

## 3. Files

| File | Change |
|---|---|
| `src/coevo/cockpit/server.py` | new: config, sessions, lock, handler, server |
| `src/coevo/cockpit/static/index.html` | replace placeholder with real page |
| `src/coevo/cockpit/static/app.js` | new: local rendering + API calls |
| `src/coevo/cockpit/static/style.css` | new: local styles |
| `src/coevo/cockpit/__init__.py` | re-export server layer |
| `tests/unit/test_cockpit_http.py` | new: session/config/lock/static-policy unit tests |
| `tests/integration/test_cockpit_http_server.py` | new: live server tests via `urllib` |

## 4. Verification

* Targeted unit + integration suites green.
* Full `make quality` exit 0, fingerprint recorded.
* Audit seal fully sealed.
* Security review (loopback/auth/CSRF/path/static policy) PASS.
