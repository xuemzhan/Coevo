"""demo_common 公共脚手架单元测试（不依赖加密/生产上下文）。

覆盖：审计钩子结果映射、框架装配（16 服务 + 权限治理）、默认权限策略。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from service_api import (  # noqa: E402
    ErrorCode,
    ServiceRequest,
    ServiceResponse,
)
from service_api.demo_common import (  # noqa: E402
    DEFAULT_PERMISSIONS,
    build_audit_hook,
    build_framework,
)


class _FakeHub:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


def _request(service="echo", method="ping", actor="u.pm"):
    return ServiceRequest(
        service=service,
        method=method,
        params={},
        actor=actor,
        request_id="t.demo",
        ts="2026-08-01T00:00:00Z",
    )


def _response(request, ok, code):
    return ServiceResponse(
        ok=ok,
        service=request.service,
        method=request.method,
        request_id=request.request_id,
        code=code,
        message="",
        data={},
        ts=request.ts,
    )


class AuditHookTests(unittest.TestCase):
    def setUp(self):
        self.ctx = {"audit_hub": _FakeHub(), "audit_events": []}
        self.hook = build_audit_hook(self.ctx, tool="coevo.test")

    def test_ok_mapping(self):
        request = _request()
        self.hook(request, _response(request, True, ErrorCode.OK.value))
        self.assertEqual(len(self.ctx["audit_events"]), 1)
        event = self.ctx["audit_events"][0]
        self.assertEqual(event.result.value, "ok")
        self.assertEqual(event.tool, "coevo.test")
        self.assertEqual(event.action, "echo.ping")

    def test_rejected_mapping(self):
        request = _request()
        self.hook(request, _response(request, False, "conflict"))
        self.assertEqual(self.ctx["audit_events"][0].result.value, "rejected")

    def test_failed_mapping(self):
        request = _request()
        self.hook(request, _response(request, False, "internal_error"))
        self.assertEqual(self.ctx["audit_events"][0].result.value, "failed")


class BuildFrameworkTests(unittest.TestCase):
    def test_registry_has_sixteen_services(self):
        ctx = {"audit_hub": _FakeHub(), "audit_events": []}
        framework = build_framework(ctx, permissions={"u.pm": frozenset({"*"})})
        self.assertEqual(len(framework.registry.list()), 16)

    def test_permission_fail_closed(self):
        ctx = {"audit_hub": _FakeHub(), "audit_events": []}
        framework = build_framework(ctx, permissions={"u.pm": frozenset({"*"})})
        response = framework.invoke(
            _request(service="identity", method="describe", actor="anonymous")
        )
        self.assertFalse(response.ok)
        self.assertEqual(response.code, ErrorCode.UNAUTHORIZED.value)

    def test_default_permissions_shape(self):
        self.assertIn("u.pm", DEFAULT_PERMISSIONS)
        self.assertIn("u.auditor", DEFAULT_PERMISSIONS)
        self.assertIn("*", DEFAULT_PERMISSIONS["u.pm"])


if __name__ == "__main__":
    unittest.main()
