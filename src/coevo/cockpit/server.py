"""US-7-AC-2 local cockpit HTTP server (loopback-only, authenticated).

Session management lives in :mod:`.sessions`; the static asset cache
and path policy live in :mod:`.static`. This module keeps the request
handler, server lifecycle and single-instance lock.
"""

from __future__ import annotations



import json
import logging

import mimetypes

import os

import re

import socket

import threading

import time

import urllib.parse

from collections import deque

from dataclasses import dataclass, field

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from pathlib import Path

from typing import Any, Final


logger = logging.getLogger(__name__)



from . import (

    LOOPBACK_HOST,

    STATIC_ROOT,

    CockpitFacade,

    CockpitRequest,

    CockpitResponse,

    CockpitResponseStatus,

    CockpitRoute,

    CockpitServerState,

    CockpitValidationError,

)

from .state_store import CockpitStateStore

from .sessions import (

    DEFAULT_MAX_SESSIONS,

    DEFAULT_SESSION_TIMEOUT_SEC,

    CockpitSessionManager,

    _ISO_UTC_Z,

    now_utc_iso_z,

)

from .static import (

    STATIC_ALLOWED_EXTENSIONS,

    STATIC_CACHE_MAX_BYTES,

    STATIC_CACHE_MAX_ENTRIES,

    STATIC_MAX_BYTES,

    _StaticAssetCache,

    resolve_static_path,

)
_HOST_LITERAL: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9.:\[\]-]+$")

CSRF_HEADER_VALUE: Final[str] = "coevo-cockpit"

AUDIT_MAXLEN: Final[int] = 200

DEFAULT_ALLOWED_HOSTS: Final[frozenset[str]] = frozenset({
    "127.0.0.1", "localhost", "::1",
})



def _default_lock_path() -> Path:
    """Default single-instance lock under the user's local app data."""
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / "KaiwuAgent" / "cockpit.lock"



def _hostname_of(value: str) -> str:
    """Extract the lowercase hostname from a Host/Origin value."""
    if not isinstance(value, str) or not value:
        return ""
    try:
        parsed = urllib.parse.urlsplit(value if "://" in value else f"http://{value}")
    except ValueError:
        return ""
    hostname = parsed.hostname
    return hostname.lower() if isinstance(hostname, str) else ""



# ---------------------------------------------------------------------------
# HTTP config + single instance lock
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CockpitHttpConfig:
    """Validated server configuration (loopback-only, fail-closed)."""

    bind_host: str = LOOPBACK_HOST
    bind_port: int = 12701
    static_root: Path = STATIC_ROOT
    max_request_bytes: int = 65536
    request_timeout_sec: int = 5
    session_timeout_sec: int = DEFAULT_SESSION_TIMEOUT_SEC
    allowed_hosts: frozenset[str] = DEFAULT_ALLOWED_HOSTS
    lock_path: Path | None = field(default_factory=_default_lock_path)
    state_path: Path | None = None
    log_path: Path | None = None
    max_concurrent_requests: int = 16
    state_snapshot_interval_sec: float | None = 300.0

    def __post_init__(self) -> None:
        if not isinstance(self.bind_host, str) or self.bind_host != LOOPBACK_HOST:
            raise CockpitValidationError(
                f"bind_host must be {LOOPBACK_HOST!r} (loopback-only); got {self.bind_host!r}"
            )
        if not isinstance(self.bind_port, int) or not (1 <= self.bind_port <= 65535):
            raise CockpitValidationError(
                f"bind_port must be 1..65535; got {self.bind_port!r}"
            )
        if not isinstance(self.static_root, Path):
            raise CockpitValidationError("static_root must be a Path")
        try:
            resolved = self.static_root.resolve()
        except OSError as exc:
            raise CockpitValidationError(
                f"static_root must be resolvable; got {self.static_root!r} ({exc})"
            ) from exc
        try:
            resolved.relative_to(STATIC_ROOT.resolve())
        except ValueError as exc:
            raise CockpitValidationError(
                f"static_root must be inside {STATIC_ROOT!r}"
            ) from exc
        for label, value in (
            ("max_request_bytes", self.max_request_bytes),
            ("request_timeout_sec", self.request_timeout_sec),
            ("session_timeout_sec", self.session_timeout_sec),
        ):
            if not isinstance(value, int) or value <= 0:
                raise CockpitValidationError(f"{label} must be a positive integer")
        if not isinstance(self.allowed_hosts, frozenset) or not self.allowed_hosts:
            raise CockpitValidationError("allowed_hosts must be a non-empty frozenset")
        for host in self.allowed_hosts:
            if (
                not isinstance(host, str)
                or not _HOST_LITERAL.match(host)
                or host not in DEFAULT_ALLOWED_HOSTS
            ):
                raise CockpitValidationError(
                    f"allowed_hosts may only contain loopback host literals; got {host!r}"
                )
        if self.lock_path is not None and not isinstance(self.lock_path, Path):
            raise CockpitValidationError("lock_path must be a Path or None")
        if self.state_path is not None and not isinstance(self.state_path, Path):
            raise CockpitValidationError("state_path must be a Path or None")
        if self.log_path is not None and not isinstance(self.log_path, Path):
            raise CockpitValidationError("log_path must be a Path or None")
        if (
            not isinstance(self.max_concurrent_requests, int)
            or isinstance(self.max_concurrent_requests, bool)
            or self.max_concurrent_requests <= 0
        ):
            raise CockpitValidationError(
                "max_concurrent_requests must be a positive integer"
            )
        interval = self.state_snapshot_interval_sec
        if interval is not None and (
            not isinstance(interval, (int, float))
            or isinstance(interval, bool)
            or interval <= 0
        ):
            raise CockpitValidationError(
                "state_snapshot_interval_sec must be positive or None"
            )



class SingleInstanceLock:
    """Exclusive-create lock file (Windows-safe) for cockpit single instance."""

    STALE_AFTER_SECONDS: int = 600

    def __init__(self, path: Path) -> None:
        if not isinstance(path, Path):
            raise CockpitValidationError("lock_path must be a Path")
        self._path = path
        self._fd: int | None = None

    def acquire(self) -> None:
        if self._fd is not None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._try_create():
            if not self._recover_stale() or not self._try_create():
                raise CockpitValidationError(
                    f"cockpit single instance already running ({self._path})"
                )
        if self._fd is None:
            raise CockpitValidationError(
                f"cockpit single instance already running ({self._path})"
            )
        try:
            os.write(self._fd, str(os.getpid()).encode("ascii"))
        except OSError:
            pass

    def _try_create(self) -> bool:
        try:
            self._fd = os.open(
                str(self._path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
            return True
        except FileExistsError:
            return False

    def _recover_stale(self) -> bool:
        """Take over a lock file left by a crashed process (mtime heuristic)."""
        try:
            age_seconds = time.time() - self._path.stat().st_mtime
        except OSError:
            return False
        if age_seconds < self.STALE_AFTER_SECONDS:
            return False
        try:
            self._path.unlink()
            return True
        except OSError:
            return False

    def release(self) -> None:
        if self._fd is None:
            return
        try:
            os.close(self._fd)
        finally:
            self._fd = None
            try:
                self._path.unlink()
            except FileNotFoundError:
                pass

    def __enter__(self) -> "SingleInstanceLock":
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()



# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------


class CockpitRequestHandler(BaseHTTPRequestHandler):
    """Authenticated, loopback-only HTTP handler for the cockpit facade."""

    protocol_version = "HTTP/1.1"
    server_version = "CoevoCockpit/1"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        # Structured audit rows are kept server-side; the default stderr
        # logging is suppressed so tokens never reach a log stream.
        return

    # -- entry points -------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 (http.server naming)
        self._handle("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._handle("POST")

    def _handle(self, method: str) -> None:
        # One request per connection: rejections never leave an unread body
        # to poison a reused keep-alive socket, and Windows client-abort
        # races cannot wedge a pooled connection.
        self.close_connection = True
        try:
            if not self._check_host():
                return
            parsed = urllib.parse.urlsplit(self.path)
            path = parsed.path
            if method == "GET" and path == "/healthz":
                # Process-supervisor probe: loopback + Host checked above;
                # intentionally unauthenticated, returns no sensitive data.
                self._send_json(
                    200,
                    {
                        "status": "ok",
                        "service": "coevo-cockpit",
                        "uptime_sec": round(
                            time.monotonic() - self.server._started_monotonic, 1
                        ),
                    },
                )
                return
            if method == "GET":
                if path == "/":
                    self._serve_index(parsed.query)
                    return
                if not self.server.session_manager.validate(
                    self._bearer_token(), self._now()
                ):
                    self._send_json(401, {"error": "authentication required"})
                    return
                if path.startswith("/static/"):
                    self._serve_static(path[len("/static/"):])
                elif path.startswith("/api/"):
                    self._serve_api_get(path, parsed.query)
                else:
                    self._send_json(404, {"error": "not found"})
                return
            if not self.server.session_manager.validate(
                self._bearer_token(), self._now()
            ):
                self._drain_body()
                self._send_json(401, {"error": "authentication required"})
                return
            if not self._check_csrf():
                return
            if path == "/api/wps_open":
                self._serve_wps_open()
            else:
                self._send_json(404, {"error": "not found"})
        except (ValueError, json.JSONDecodeError, CockpitValidationError) as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception:  # noqa: BLE001 - never leak internals to the client
            self._send_json(500, {"error": "internal error"})

    # -- request governance -------------------------------------------------

    def _check_host(self) -> bool:
        hostname = _hostname_of(self.headers.get("Host", ""))
        if hostname in self.server.config.allowed_hosts:
            return True
        self._send_json(403, {"error": "invalid Host header"})
        return False

    def _check_csrf(self) -> bool:
        origin_host = _hostname_of(self.headers.get("Origin", ""))
        if origin_host not in self.server.config.allowed_hosts:
            self._drain_body()
            self._send_json(403, {"error": "invalid Origin header"})
            return False
        if self.headers.get("X-Requested-With", "") != CSRF_HEADER_VALUE:
            self._drain_body()
            self._send_json(403, {"error": "CSRF header required"})
            return False
        return True

    def _drain_body(self) -> None:
        """Consume an unread request body before rejecting the request.

        Closing a connection with unread request bytes pending can make the
        client observe a TCP reset (WinError 10053) instead of the response.
        Reading and discarding the body first lets the rejection finish with
        a clean FIN. Bounded: oversized or malformed bodies are left for the
        connection close and never buffered unboundedly.
        """
        length_header = self.headers.get("Content-Length", "")
        if not length_header:
            return
        try:
            length = int(length_header)
        except ValueError:
            return
        if length < 0 or length > self.server.config.max_request_bytes * 4:
            return
        remaining = length
        try:
            while remaining > 0:
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    return
                remaining -= len(chunk)
        except OSError:
            return

    def _bearer_token(self) -> str:
        authorization = self.headers.get("Authorization", "")
        if authorization.lower().startswith("bearer "):
            return authorization[7:].strip()
        return self.headers.get("X-Cockpit-Token", "")

    # -- routes -------------------------------------------------------------

    def _serve_index(self, query: str) -> None:
        params = urllib.parse.parse_qs(query, keep_blank_values=False)
        token_values = params.get("token", [])
        token = token_values[0] if len(token_values) == 1 else ""
        if not self.server.session_manager.validate(token, self._now()):
            self._send_json(401, {"error": "authentication required"})
            return
        index = resolve_static_path(self.server.config.static_root, "index.html")
        if index is None:
            self._send_json(404, {"error": "index.html missing"})
            return
        body = self.server.static_cache.get(index)
        if body is None:
            body = index.read_bytes()
            self.server.static_cache.put(index, body)
        self._send_bytes(
            200,
            body,
            "text/html; charset=utf-8",
            extra_headers={
                "Content-Security-Policy": (
                    "default-src 'self'; script-src 'self'; style-src 'self'; "
                    "img-src 'self' data:; connect-src 'self'; form-action 'self'; "
                    "frame-ancestors 'none'; base-uri 'none'"
                ),
            },
        )

    def _serve_static(self, relative: str) -> None:
        candidate = resolve_static_path(self.server.config.static_root, relative)
        if candidate is None:
            self._send_json(404, {"error": "static asset not found"})
            return
        media_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        if not media_type.startswith("text/"):
            media_type = f"{media_type}; charset=utf-8"
        body = self.server.static_cache.get(candidate)
        if body is None:
            body = candidate.read_bytes()
            self.server.static_cache.put(candidate, body)
        self._send_bytes(
            200,
            body,
            media_type,
            extra_headers={"Cache-Control": "public, max-age=300"},
        )

    def _serve_api_get(self, path: str, query: str) -> None:
        params = urllib.parse.parse_qs(query, keep_blank_values=False, strict_parsing=True)

        def one(name: str) -> str:
            values = params.get(name, [])
            return values[0] if len(values) == 1 else ""

        route_map = {
            "/api/list_projects": (CockpitRoute.LIST_PROJECTS, "project_id"),
            "/api/list_roles": (CockpitRoute.LIST_ROLES, "project_id"),
            "/api/project_view": (CockpitRoute.PROJECT_VIEW, "project_id"),
            "/api/role_view": (CockpitRoute.ROLE_VIEW, "role_id"),
            "/api/task_view": (CockpitRoute.TASK_VIEW, "task_id"),
            "/api/milestone_view": (CockpitRoute.MILESTONE_VIEW, "task_id"),
        }
        if path not in route_map:
            self._send_json(404, {"error": "not found"})
            return
        route, _ = route_map[path]
        request = CockpitRequest(
            route=route,
            project_id=one("project_id"),
            role_id=one("role_id"),
            task_id=one("task_id"),
            artifact_path="",
            ts=self._now(),
        )
        self._dispatch_and_send(request)

    def _serve_wps_open(self) -> None:
        length_header = self.headers.get("Content-Length", "")
        try:
            length = int(length_header)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length < 0 or length > self.server.config.max_request_bytes:
            self._send_bytes(
                413,
                b'{"error":"request body too large"}',
                "application/json; charset=utf-8",
            )
            return
        body = self.rfile.read(length)
        if len(body) != length:
            raise ValueError("truncated request body")
        data = json.loads(body.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("request body must be a JSON object")
        artifact_path = data.get("artifact_path", "")
        project_id = data.get("project_id", "")
        if not isinstance(artifact_path, str) or not isinstance(project_id, str):
            raise ValueError("artifact_path/project_id must be strings")
        if data.get("confirm") is not True:
            self._send_json(
                403,
                {"error": "sensitive operation requires explicit confirmation"},
            )
            return
        request = CockpitRequest(
            route=CockpitRoute.WPS_OPEN,
            project_id=project_id,
            role_id="",
            task_id="",
            artifact_path=artifact_path,
            ts=self._now(),
        )
        self._dispatch_and_send(request)

    # -- dispatch + response helpers ----------------------------------------

    def _dispatch_and_send(self, request: CockpitRequest) -> None:
        response: CockpitResponse = CockpitFacade.dispatch(
            request,
            server_state=self.server.state,
            now=self._now(),
        )
        self.server.append_audit(CockpitFacade.to_audit_record(request, response))
        status_codes = {
            CockpitResponseStatus.OK: 200,
            CockpitResponseStatus.NOT_FOUND: 404,
            CockpitResponseStatus.BAD_REQUEST: 400,
            CockpitResponseStatus.DENIED: 403,
            CockpitResponseStatus.NOT_BOUND: 403,
            CockpitResponseStatus.ERROR: 500,
        }
        self._send_json(
            status_codes.get(response.status, 500),
            {
                "status": response.status.value,
                "task": response.task,
                "payload": response.payload,
                "ts": response.ts,
            },
        )

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self._send_bytes(code, body, "application/json; charset=utf-8")

    def _send_bytes(
        self,
        code: int,
        body: bytes,
        content_type: str,
        *,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if body:
            try:
                self.wfile.write(body)
            except OSError:
                # The client disconnected mid-response (e.g. user closed the
                # browser tab). There is nothing further to deliver; swallow
                # so the handler thread ends cleanly without a traceback.
                return

    def _now(self) -> str:
        return now_utc_iso_z()



# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------


class _CockpitLogWriter:
    """Size-rotating JSONL access log with fail-isolated writes (OPS-1).

    Rotates by size (default 5 MiB per file, 5 backups) so a long-running
    cockpit never grows an unbounded access log. Rotation failures are
    counted and never break request handling.
    """

    DEFAULT_MAX_BYTES: Final[int] = 5 * 1024 * 1024
    DEFAULT_BACKUP_COUNT: Final[int] = 5

    def __init__(
        self,
        path: Path,
        *,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
    ) -> None:
        if not isinstance(max_bytes, int) or max_bytes <= 0:
            raise CockpitValidationError("access log max_bytes must be positive")
        if not isinstance(backup_count, int) or backup_count < 1:
            raise CockpitValidationError("access log backup_count must be positive")
        self._path = path
        self._lock = threading.Lock()
        self.errors = 0
        self._max_bytes = max_bytes
        self._backup_count = backup_count
        path.parent.mkdir(parents=True, exist_ok=True)
        self._stream = path.open("a", encoding="utf-8")

    def write(self, record: dict) -> None:
        try:
            line = json.dumps(
                record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ) + "\n"
            with self._lock:
                self._maybe_rotate(len(line.encode("utf-8")))
                self._stream.write(line)
                self._stream.flush()
        except OSError:
            self.errors += 1

    def _maybe_rotate(self, incoming_bytes: int) -> None:
        try:
            if self._path.stat().st_size + incoming_bytes <= self._max_bytes:
                return
            self._stream.close()
            for index in range(self._backup_count - 1, 0, -1):
                source = self._path.with_suffix(f".{index}")
                target = self._path.with_suffix(f".{index + 1}")
                if source.exists():
                    os.replace(source, target)
            os.replace(self._path, self._path.with_suffix(".1"))
            self._stream = self._path.open("a", encoding="utf-8")
        except OSError:
            # Rotation must never take request handling down; the next
            # write retries the rotation.
            self.errors += 1
            if self._stream.closed:
                try:
                    self._stream = self._path.open("a", encoding="utf-8")
                except OSError:
                    pass

    def close(self) -> None:
        try:
            self._stream.close()
        except OSError:
            pass



class CockpitHttpServer(ThreadingHTTPServer):
    """Threading loopback HTTP server hosting the cockpit facade."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        config: CockpitHttpConfig,
        *,
        workspace_views: tuple[Any, ...] = (),
        role_views: tuple[Any, ...] = (),
        started_at: str = "",
        session_manager: CockpitSessionManager | None = None,
    ) -> None:
        if not isinstance(config, CockpitHttpConfig):
            raise CockpitValidationError("config must be CockpitHttpConfig")
        self.config = config
        self._lock = (
            SingleInstanceLock(config.lock_path)
            if config.lock_path is not None
            else None
        )
        if self._lock is not None:
            self._lock.acquire()
        self._state_store = (
            CockpitStateStore(config.state_path)
            if config.state_path is not None
            else None
        )
        self.session_manager = session_manager or CockpitSessionManager(
            timeout_sec=config.session_timeout_sec
        )
        started_at = started_at or now_utc_iso_z()
        if (
            not workspace_views
            and not role_views
            and self._state_store is not None
        ):
            loaded = self._state_store.load()
            if loaded is not None:
                workspace_views, role_views = loaded
        self.state: CockpitServerState = CockpitFacade.start_server(
            bind_host=config.bind_host,
            bind_port=config.bind_port,
            static_root=config.static_root,
            max_request_bytes=config.max_request_bytes,
            request_timeout_sec=config.request_timeout_sec,
            workspace_views=workspace_views,
            role_views=role_views,
            now=started_at,
        )
        self._audit_log: deque[dict[str, Any]] = deque(maxlen=AUDIT_MAXLEN)
        self.static_cache = _StaticAssetCache()
        self._log_writer = (
            _CockpitLogWriter(config.log_path)
            if config.log_path is not None
            else None
        )
        self._started_monotonic = time.monotonic()
        self._concurrency = threading.BoundedSemaphore(
            config.max_concurrent_requests
        )
        self._snapshot_stop = threading.Event()
        self._snapshot_thread: threading.Thread | None = None
        try:
            super().__init__(
                (config.bind_host, config.bind_port),
                CockpitRequestHandler,
                bind_and_activate=True,
            )
        except OSError as exc:
            if self._log_writer is not None:
                self._log_writer.close()
            if self._lock is not None:
                self._lock.release()
            raise CockpitValidationError(
                f"cockpit bind failed on {config.bind_host}:{config.bind_port} ({exc})"
            ) from exc

    @property
    def url(self) -> str:
        host, port = self.server_address[:2]
        return f"http://{host}:{port}/"

    def append_audit(self, record: dict[str, Any]) -> None:
        self._audit_log.append(record)
        if self._log_writer is not None:
            self._log_writer.write(record)

    @property
    def log_errors(self) -> int:
        return self._log_writer.errors if self._log_writer is not None else 0

    def recent_audit(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._audit_log)

    def process_request(self, request: Any, client_address: Any) -> None:
        """Bound concurrent handler threads; reject overflow with 503."""
        if not self._concurrency.acquire(blocking=False):
            self._reject_busy(request, client_address)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self._concurrency.release()
            raise

    def process_request_thread(self, request: Any, client_address: Any) -> None:
        """Run one request handler, releasing the concurrency permit on exit."""
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._concurrency.release()

    def _reject_busy(self, request: Any, client_address: Any) -> None:
        """Reply 503 and close the socket when the concurrency limit is reached."""
        try:
            request.sendall(
                b"HTTP/1.1 503 Service Unavailable\r\n"
                b"Content-Length: 0\r\n"
                b"Connection: close\r\n\r\n"
            )
        except OSError:
            pass
        finally:
            try:
                request.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            request.close()

    def _snapshot_once(self) -> None:
        """Persist the current views (fail-isolated: log, never crash the server)."""
        if self._state_store is None:
            return
        try:
            self._state_store.save(
                self.state.workspace_views,
                self.state.role_views,
            )
        except Exception:  # noqa: BLE001 - snapshot must never take the server down
            logger.exception("cockpit periodic state snapshot failed")

    def _snapshot_loop(self) -> None:
        interval = self.config.state_snapshot_interval_sec
        while not self._snapshot_stop.wait(interval):
            self._snapshot_once()

    def start(self) -> None:
        thread = threading.Thread(
            target=self.serve_forever,
            kwargs={"poll_interval": 0.05},
            daemon=True,
        )
        thread.start()
        if (
            self._state_store is not None
            and self.config.state_snapshot_interval_sec is not None
        ):
            self._snapshot_stop.clear()
            self._snapshot_thread = threading.Thread(
                target=self._snapshot_loop,
                name="cockpit-state-snapshot",
                daemon=True,
            )
            self._snapshot_thread.start()

    def stop(self) -> None:
        if self._snapshot_thread is not None:
            self._snapshot_stop.set()
            self._snapshot_thread.join(
                timeout=(self.config.state_snapshot_interval_sec or 0) + 5
            )
            self._snapshot_thread = None
        self.shutdown()
        self.server_close()
        if self._state_store is not None:
            self._state_store.save(
                self.state.workspace_views,
                self.state.role_views,
            )
        if self._log_writer is not None:
            self._log_writer.close()
        if self._lock is not None:
            self._lock.release()

