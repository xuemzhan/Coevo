"""环回 HTTP 服务：通过一致性 API 开放统一服务框架。

安全基线（与生产驾驶舱一致）
----------------------------
* 仅绑定 ``127.0.0.1``：绑定其他地址直接失败（fail-closed）。
* 会话令牌鉴权：除 ``/healthz`` 外，所有请求必须携带
  ``X-Service-Token`` 头，令牌在服务启动时生成并返回给调用方。
* 请求体大小上限（默认 64 KiB），超限直接拒绝。
* Host 头校验：只接受环回主机名。
* 错误响应统一信封，绝不泄漏异常堆栈。

路由
----
* ``GET /healthz``           —— 探活（免鉴权）
* ``GET /api/v1/health``     —— 健康检查（含审计事件数）
* ``GET /api/v1/services``   —— 能力目录（统一服务清单）
* ``POST /api/v1/{service}/{method}`` —— 一致性服务调用

请求体：``{"params": {...}, "actor": "...", "request_id": "...", "ts": "..."}``
响应体：统一信封 ``{"ok": true, "code": "ok", "message": "", "data": {...}}``
"""

from __future__ import annotations

import http.server
import json
import secrets
import threading
import urllib.parse
from typing import Any

from .contract import ErrorCode
from .framework import ServiceFramework


LOOPBACK_HOST = "127.0.0.1"
DEFAULT_MAX_BODY_BYTES = 64 * 1024
DEFAULT_ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


API_BROWSER_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Coevo 统一服务框架 · API 浏览器</title>
<style>
  body { font-family: "Microsoft YaHei", sans-serif; margin: 0; background: #f4f6f9; color: #1f2937; }
  header { background: #0f2a43; color: #fff; padding: 18px 28px; }
  header h1 { margin: 0 0 6px; font-size: 20px; }
  header p { margin: 0; color: #b9c8d8; font-size: 12px; }
  main { max-width: 980px; margin: 20px auto; padding: 0 20px 40px; }
  .token { display: flex; gap: 8px; margin: 14px 0; }
  .token input { flex: 1; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; }
  button { padding: 8px 14px; border: 0; border-radius: 6px; background: #0f2a43; color: #fff; cursor: pointer; }
  .service { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 12px; padding: 12px 16px; }
  .service h3 { margin: 0 0 4px; font-size: 15px; }
  .service .desc { color: #64748b; font-size: 12px; margin-bottom: 8px; }
  .method { display: inline-block; background: #eef3f8; border-radius: 6px; padding: 6px 10px; margin: 4px 6px 4px 0; font-size: 13px; cursor: pointer; }
  .method:hover { background: #dbe7f3; }
  .panel { display: none; background: #0f172a; color: #d7e3f0; border-radius: 6px; padding: 10px; margin-top: 8px; font-size: 12px; }
  .panel textarea { width: 100%; box-sizing: border-box; min-height: 80px; background: #0b1220; color: #d7e3f0; border: 1px solid #1e293b; border-radius: 6px; font-family: Consolas, monospace; }
  .panel pre { white-space: pre-wrap; word-break: break-all; margin: 8px 0 0; }
</style>
</head>
<body>
<header>
  <h1>Coevo 统一服务框架 · API 浏览器</h1>
  <p>本地环回服务（仅 127.0.0.1）。输入会话令牌后可浏览能力目录并在线调用，返回统一信封。</p>
</header>
<main>
  <div class="token">
    <input id="token" placeholder="X-Service-Token（在演示启动输出中获取）">
    <button onclick="loadServices()">加载能力目录</button>
  </div>
  <div id="services"></div>
</main>
<script>
  function token() { return document.getElementById("token").value.trim(); }
  async function api(path, options) {
    const headers = { "X-Service-Token": token() };
    if (options && options.body) headers["Content-Type"] = "application/json; charset=utf-8";
    const resp = await fetch(path, Object.assign({ headers: headers }, options || {}));
    return resp.json();
  }
  async function loadServices() {
    const box = document.getElementById("services");
    box.innerHTML = "加载中…";
    try {
      const data = await api("api/v1/services");
      box.innerHTML = data.services.map(renderService).join("");
    } catch (err) {
      box.innerHTML = "<p>加载失败：" + err + "</p>";
    }
  }
  function renderService(s) {
    const methods = s.methods.map(function (m) {
      return '<span class="method" onclick="openPanel(\'' + s.name + '\',\'' + m + '\')">' + m + "</span>";
    }).join("");
    return '<div class="service"><h3>' + s.name + ' <small>v' + s.version + "</small></h3>" +
      '<div class="desc">' + s.description + "</div>" + methods + "</div>";
  }
  function openPanel(service, method) {
    const id = "panel-" + service + "-" + method;
    let panel = document.getElementById(id);
    if (panel) { panel.style.display = panel.style.display === "none" ? "block" : "none"; return; }
    panel = document.createElement("div");
    panel.className = "panel";
    panel.id = id;
    panel.innerHTML = '<div>POST /api/v1/' + service + '/' + method + '</div>' +
      '<textarea placeholder=\'{"params": {} }\'></textarea>' +
      '<button onclick="invoke(\'' + service + '\',\'' + method + '\',this)">调用</button>' +
      "<pre></pre>";
    document.getElementById("services").appendChild(panel);
    panel.style.display = "block";
  }
  async function invoke(service, method, button) {
    const panel = button.parentElement;
    const pre = panel.querySelector("pre");
    let params = {};
    try { params = JSON.parse(panel.querySelector("textarea").value || "{}"); }
    catch (err) { pre.textContent = "参数 JSON 解析失败：" + err; return; }
    pre.textContent = "调用中…";
    const envelope = await api("api/v1/" + service + "/" + method, {
      method: "POST",
      body: JSON.stringify({ params: params, actor: "u.pm" })
    });
    pre.textContent = JSON.stringify(envelope, null, 2);
  }
</script>
</body>
</html>
"""


class ServiceApiServer(http.server.HTTPServer):
    """环回顺序 HTTP 服务，持有框架引用与会话令牌。

    使用顺序处理（非线程池）：请求在主线程内依次处理，保证共享 SQLite
    存储（知识库/身份仓库）在同一线程内使用，避免跨线程连接错误；也
    简化了并发与审计一致性。演示场景为顺序调用，无需并发吞吐。
    """

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        framework: ServiceFramework,
        *,
        bind_port: int,
        max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    ) -> None:
        self.framework = framework
        self.max_body_bytes = max_body_bytes
        self.token = secrets.token_hex(16)
        self.request_count = 0
        self._lock = threading.Lock()
        super().__init__((LOOPBACK_HOST, bind_port), _ServiceApiHandler)

    def _count_request(self) -> None:
        with self._lock:
            self.request_count += 1

    @property
    def url(self) -> str:
        host, port = self.server_address[:2]
        return f"http://{host}:{port}/"

class _ServiceApiHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "CoevoServiceApi/1"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        # 结构化审计由框架负责；抑制默认 stderr 日志，避免令牌入日志
        return

    # ------------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlsplit(self.path)
        if not self._check_host():
            return
        if parsed.path == "/healthz":
            self._send_json(
                200,
                {"status": "ok", "service": "coevo-service-api"},
            )
            return
        if parsed.path == "/":
            # API 浏览器（离线内嵌页，无外部资源；调用 API 仍需令牌）
            body = API_BROWSER_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header(
                "Referrer-Policy", "no-referrer"
            )
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'unsafe-inline'; "
                "style-src 'unsafe-inline'; img-src 'self' data:; "
                "connect-src 'self'; object-src 'none'; base-uri 'none'",
            )
            self.end_headers()
            self.wfile.write(body)
            return
        if not self._check_token():
            return
        self.server._count_request()
        if parsed.path == "/api/v1/health":
            self._send_json(
                200,
                {
                    "status": "ok",
                    "service": "coevo-service-api",
                    "request_count": self.server.request_count,
                    "audit_event_count": len(
                        self.server.framework.context.get("audit_events", [])
                    ),
                },
            )
        elif parsed.path == "/api/v1/services":
            self._send_json(
                200,
                {
                    "services": [
                        {
                            "name": spec.name,
                            "version": spec.version,
                            "description": spec.description,
                            "methods": sorted(spec.methods),
                        }
                        for spec in self.server.framework.registry.list()
                    ]
                },
            )
        elif parsed.path == "/api/v1/openapi.json":
            from .openapi import build_openapi

            self._send_json(200, build_openapi(self.server.framework.registry))
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlsplit(self.path)
        if not self._check_host():
            return
        if not self._check_token():
            return
        self.server._count_request()
        parts = parsed.path.strip("/").split("/")
        if len(parts) != 4 or parts[:2] != ["api", "v1"]:
            self._send_json(404, {"error": "not found"})
            return
        service, method = parts[2], parts[3]
        body = self._read_body()
        if body is None:
            return
        payload = dict(body)
        payload["service"] = service
        payload["method"] = method
        envelope = self.server.framework.invoke_json(payload)
        status = _status_for_code(str(envelope.get("code", "")))
        self._send_json(status, envelope)

    # ------------------------------------------------------------------
    def _check_host(self) -> bool:
        host = (self.headers.get("Host", "") or "").split(":")[0].lower()
        if host in DEFAULT_ALLOWED_HOSTS:
            return True
        self._send_json(403, {"error": "invalid Host header"})
        return False

    def _check_token(self) -> bool:
        token = self.headers.get("X-Service-Token", "")
        if token and secrets.compare_digest(token, self.server.token):
            return True
        self._send_json(
            401,
            {"error": "authentication required", "code": ErrorCode.UNAUTHORIZED.value},
        )
        return False

    def _read_body(self) -> dict[str, Any] | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid Content-Length"})
            return None
        if length < 0 or length > self.server.max_body_bytes:
            self._send_json(413, {"error": "request body too large"})
            return None
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid JSON body"})
            return None
        if not isinstance(data, dict):
            self._send_json(400, {"error": "body must be a JSON object"})
            return None
        return data

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def _status_for_code(code: str) -> int:
    """统一信封错误码 → HTTP 状态映射。"""
    return {
        ErrorCode.OK.value: 200,
        ErrorCode.BAD_REQUEST.value: 400,
        ErrorCode.VALIDATION.value: 400,
        ErrorCode.UNAUTHORIZED.value: 401,
        ErrorCode.NOT_FOUND.value: 404,
        ErrorCode.CONFLICT.value: 409,
        ErrorCode.INTERNAL.value: 500,
        ErrorCode.BUSY.value: 503,
    }.get(code, 500)


__all__ = ["DEFAULT_MAX_BODY_BYTES", "ServiceApiServer"]
