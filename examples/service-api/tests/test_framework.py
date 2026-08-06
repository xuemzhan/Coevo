"""统一服务框架单元测试（不依赖加密/生产上下文，纯框架层）。

覆盖：信封契约、错误码、注册表、统一分派（成功/失败/审计钩子）、
环回 HTTP 服务的鉴权与一致性信封。
"""

from __future__ import annotations

import json
import http.server
import socket
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from service_api import (  # noqa: E402
    ErrorCode,
    ServiceApiError,
    ServiceClient,
    ServiceError,
    ServiceFramework,
    ServiceRegistry,
    ServiceRequest,
    ServiceSpec,
    build_openapi,
    error_response,
    ok_response,
)
from service_api.server import ServiceApiServer  # noqa: E402
from service_api.adapters import _require_safe_id  # noqa: E402


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def echo_handler(request, ctx):
    """测试用服务方法：原样回显 params。"""
    return {"echo": request.params}


def fail_handler(request, ctx):
    raise ServiceError(ErrorCode.CONFLICT, "business conflict", detail={"k": 1})


def bad_handler(request, ctx):
    raise ValueError("bad params")


def crash_handler(request, ctx):
    raise RuntimeError("boom")


def build_light_framework():
    """轻量框架：不构建生产上下文，只注册测试服务。"""
    registry = (
        ServiceRegistry()
        .register(ServiceSpec("echo", "1.0", "测试服务", frozenset({"ping"})), echo_handler)
        .register(ServiceSpec("fail", "1.0", "失败服务", frozenset({"conflict"})), fail_handler)
        .register(ServiceSpec("bad", "1.0", "校验失败服务", frozenset({"call"})), bad_handler)
        .register(ServiceSpec("crash", "1.0", "内部错误服务", frozenset({"call"})), crash_handler)
    )
    return ServiceFramework(registry, {"demo": True})


def make_request(service, method, params=None, actor="u.tester"):
    return ServiceRequest(
        service=service,
        method=method,
        params=params or {},
        actor=actor,
        request_id=f"t.{service}.{method}",
        ts="2026-08-01T00:00:00Z",
    )


class ContractTests(unittest.TestCase):
    def test_ok_response_shape(self):
        response = ok_response(
            make_request("echo", "ping", {"a": 1}),
            {"echo": {"a": 1}},
            message="done",
        )
        self.assertTrue(response.ok)
        self.assertEqual(response.code, ErrorCode.OK.value)
        self.assertEqual(response.data["echo"], {"a": 1})
        self.assertEqual(response.to_dict()["request_id"], "t.echo.ping")

    def test_error_response_shape(self):
        response = error_response(
            make_request("echo", "ping"),
            ErrorCode.NOT_FOUND,
            "missing",
        )
        self.assertFalse(response.ok)
        self.assertEqual(response.code, "not_found")
        self.assertNotIn("stack", response.data)

    def test_service_error_validates_code(self):
        with self.assertRaises(TypeError):
            ServiceError("not-an-enum", "x")  # type: ignore[arg-type]

    def test_request_validates_fields(self):
        with self.assertRaises(ServiceError):
            ServiceRequest("", "m", {}, "a", "r", "ts")


class RegistryTests(unittest.TestCase):
    def test_register_get_list(self):
        registry = ServiceRegistry().register(
            ServiceSpec("a", "1.0", "A", frozenset({"x"})), echo_handler
        )
        spec, handler = registry.get("a")
        self.assertEqual(spec.name, "a")
        self.assertIn("x", spec.methods)
        self.assertEqual(len(registry.list()), 1)

    def test_duplicate_registration_rejected(self):
        registry = ServiceRegistry().register(
            ServiceSpec("a", "1.0", "A", frozenset({"x"})), echo_handler
        )
        with self.assertRaises(ValueError):
            registry.register(
                ServiceSpec("a", "1.0", "A", frozenset({"y"})), echo_handler
            )


class FrameworkTests(unittest.TestCase):
    def setUp(self):
        self.framework = build_light_framework()
        self.audit_calls = []

        def audit(request, response):
            self.audit_calls.append((request.service, request.method, response.ok))

        self.framework = ServiceFramework(
            self.framework.registry,
            self.framework.context,
            audit=audit,
        )

    def test_invoke_success(self):
        response = self.framework.invoke(
            make_request("echo", "ping", {"a": 1})
        )
        self.assertTrue(response.ok)
        self.assertEqual(response.data["echo"], {"a": 1})

    def test_invoke_unknown_service(self):
        response = self.framework.invoke(make_request("nope", "ping"))
        self.assertFalse(response.ok)
        self.assertEqual(response.code, ErrorCode.NOT_FOUND.value)

    def test_invoke_unknown_method(self):
        response = self.framework.invoke(make_request("echo", "nope"))
        self.assertFalse(response.ok)
        self.assertEqual(response.code, ErrorCode.NOT_FOUND.value)

    def test_invoke_service_error_code(self):
        response = self.framework.invoke(make_request("fail", "conflict"))
        self.assertFalse(response.ok)
        self.assertEqual(response.code, ErrorCode.CONFLICT.value)
        self.assertEqual(response.data["k"], 1)

    def test_invoke_validation_error(self):
        response = self.framework.invoke(make_request("bad", "call"))
        self.assertFalse(response.ok)
        self.assertEqual(response.code, ErrorCode.VALIDATION.value)

    def test_invoke_internal_error(self):
        response = self.framework.invoke(make_request("crash", "call"))
        self.assertFalse(response.ok)
        self.assertEqual(response.code, ErrorCode.INTERNAL.value)
        self.assertNotIn("boom", response.message)

    def test_invoke_audits_every_call(self):
        self.framework.invoke(make_request("echo", "ping"))
        self.framework.invoke(make_request("nope", "ping"))
        self.assertEqual(len(self.audit_calls), 2)

    def test_invoke_json_roundtrip(self):
        payload = {
            "service": "echo",
            "method": "ping",
            "params": {"a": 2},
            "actor": "u.tester",
            "request_id": "t.json",
            "ts": "2026-08-01T00:00:00Z",
        }
        envelope = self.framework.invoke_json(payload)
        self.assertTrue(envelope["ok"])
        self.assertEqual(envelope["code"], "ok")


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.server = ServiceApiServer(build_light_framework(), bind_port=free_port())
        self.token = self.server.token
        self._thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self._thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self._thread.join(timeout=10)

    def _get(self, path, token=None):
        headers = {}
        if token is not None:
            headers["X-Service-Token"] = token
        request = urllib.request.Request(self.server.url + path, headers=headers)
        with urllib.request.urlopen(request, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def _post(self, service, method, payload=None, token=None):
        headers = {"Content-Type": "application/json; charset=utf-8"}
        if token is not None:
            headers["X-Service-Token"] = token
        request = urllib.request.Request(
            self.server.url + f"api/v1/{service}/{method}",
            data=json.dumps(payload or {}).encode("utf-8"),
            headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_healthz_without_token(self):
        status, body = self._get("healthz")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_api_requires_token(self):
        with self.assertRaises(urllib.error.HTTPError) as exc:
            self._get("api/v1/health")
        self.assertEqual(exc.exception.code, 401)

    def test_services_catalog(self):
        status, body = self._get("api/v1/services", token=self.token)
        self.assertEqual(status, 200)
        names = {item["name"] for item in body["services"]}
        self.assertEqual(names, {"echo", "fail", "bad", "crash"})

    def test_post_success_envelope(self):
        status, body = self._post(
            "echo",
            "ping",
            {
                "params": {"a": 1},
                "actor": "u.tester",
                "request_id": "t.http",
                "ts": "2026-08-01T00:00:00Z",
            },
            token=self.token,
        )
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["code"], "ok")

    def test_post_unknown_service_envelope(self):
        status, body = self._post(
            "nope", "ping", {"params": {}}, token=self.token
        )
        self.assertEqual(status, 404)
        self.assertFalse(body["ok"])
        self.assertEqual(body["code"], "not_found")

    def test_post_conflict_envelope(self):
        status, body = self._post(
            "fail", "conflict", {"params": {}}, token=self.token
        )
        self.assertEqual(status, 409)
        self.assertFalse(body["ok"])
        self.assertEqual(body["code"], "conflict")

    def test_openapi_endpoint(self):
        status, body = self._get("api/v1/openapi.json", token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(body["openapi"], "3.0.3")
        self.assertIn("/api/v1/echo/{method}", body["paths"])
        self.assertIn("/api/v1/services", body["paths"])

    def test_api_browser_page_offline(self):
        request = urllib.request.Request(self.server.url)
        with urllib.request.urlopen(request, timeout=10) as resp:
            html = resp.read().decode("utf-8")
        self.assertEqual(resp.status, 200)
        self.assertIn("api/v1", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("cdn", html.lower())


class PermissionTests(unittest.TestCase):
    def setUp(self):
        registry = ServiceRegistry().register(
            ServiceSpec("echo", "1.0", "E", frozenset({"ping"})), echo_handler
        )
        self.framework = ServiceFramework(
            registry,
            {"demo": True},
            permissions={
                "u.admin": frozenset({"*"}),
                "u.guest": frozenset({"echo.ping"}),
            },
        )

    def test_wildcard_allowed(self):
        response = self.framework.invoke(
            make_request("echo", "ping", actor="u.admin")
        )
        self.assertTrue(response.ok)

    def test_explicit_allowed(self):
        response = self.framework.invoke(
            make_request("echo", "ping", actor="u.guest")
        )
        self.assertTrue(response.ok)

    def test_denied_actor(self):
        response = self.framework.invoke(
            make_request("echo", "ping", actor="u.stranger")
        )
        self.assertFalse(response.ok)
        self.assertEqual(response.code, ErrorCode.UNAUTHORIZED.value)


class OpenApiTests(unittest.TestCase):
    def test_spec_shape(self):
        spec = build_openapi(build_light_framework().registry)
        self.assertEqual(spec["openapi"], "3.0.3")
        self.assertIn("/api/v1/echo/{method}", spec["paths"])
        self.assertIn("/api/v1/services", spec["paths"])
        self.assertIn("ServiceResponse", spec["components"]["schemas"])


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.server = ServiceApiServer(build_light_framework(), bind_port=free_port())
        self._thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self._thread.start()
        self.client = ServiceClient(self.server.url, self.server.token)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self._thread.join(timeout=10)

    def test_call_success(self):
        data = self.client.call("echo", "ping", {"a": 1})
        self.assertEqual(data["echo"], {"a": 1})

    def test_call_unknown_service_raises(self):
        with self.assertRaises(ServiceApiError) as exc:
            self.client.call("nope", "ping", {})
        self.assertEqual(exc.exception.code, "not_found")
        self.assertEqual(exc.exception.status, 404)

    def test_list_services(self):
        services = self.client.list_services()
        self.assertEqual(len(services), 4)

    def test_health(self):
        health = self.client.health()
        self.assertEqual(health["status"], "ok")


class SafeIdTests(unittest.TestCase):
    def test_valid_safe_id(self):
        self.assertEqual(_require_safe_id("PRJ001", "project_id"), "PRJ001")
        self.assertEqual(_require_safe_id("CERT-OWNER", "cert_id"), "CERT-OWNER")

    def test_traversal_rejected(self):
        for bad in ("../evil", "a/b", "..", "a\\b", "", "a b"):
            with self.assertRaises(ServiceError):
                _require_safe_id(bad, "project_id")


class _NonJsonHandler(http.server.BaseHTTPRequestHandler):
    """返回非 JSON 错误体的测试服务。"""

    def do_POST(self):  # noqa: N802
        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "5")
        self.end_headers()
        self.wfile.write(b"oops!")

    def log_message(self, fmt, *args):
        return


class ClientNonJsonTests(unittest.TestCase):
    def test_non_json_error_raises_service_error(self):
        server = http.server.HTTPServer(("127.0.0.1", 0), _NonJsonHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = ServiceClient(
                f"http://127.0.0.1:{server.server_address[1]}/", "token"
            )
            with self.assertRaises(ServiceApiError) as exc:
                client.call("any", "method", {})
            self.assertEqual(exc.exception.code, "internal_error")
            self.assertEqual(exc.exception.status, 500)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=10)


if __name__ == "__main__":
    unittest.main()
