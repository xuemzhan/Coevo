"""一致性 API 的 Python 客户端（消费方视角）。

提供类型化调用体验：``ServiceClient.call`` 直接返回 data，失败抛
:class:`ServiceApiError`（携带闭集错误码），并支持能力目录与健康检查。
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class ServiceApiError(Exception):
    """服务调用失败：携带统一错误码与请求 ID。"""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: int,
        request_id: str = "",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status = status
        self.request_id = request_id


class ServiceClient:
    """环回一致性 API 客户端。"""

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.token = token
        self.timeout = timeout

    def call(
        self,
        service: str,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        actor: str = "anonymous",
        request_id: str = "",
        ts: str = "",
    ) -> dict[str, Any]:
        """调用服务并返回 data；失败抛 :class:`ServiceApiError`。"""
        payload = {
            "params": params or {},
            "actor": actor,
            "request_id": request_id,
            "ts": ts,
        }
        request = urllib.request.Request(
            self.base_url + f"api/v1/{service}/{method}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "X-Service-Token": self.token,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                status = resp.status
                envelope = json.loads(resp.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ServiceApiError(
                code="internal_error",
                message="service returned a non-JSON response",
                status=500,
            ) from exc
        except urllib.error.HTTPError as exc:
            status = exc.code
            try:
                envelope = json.loads(exc.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as parse_exc:
                raise ServiceApiError(
                    code="internal_error",
                    message=f"HTTP {status} with non-JSON body",
                    status=status,
                ) from parse_exc
        if not envelope.get("ok"):
            raise ServiceApiError(
                code=str(envelope.get("code", "internal_error")),
                message=str(envelope.get("message", "call failed")),
                status=status,
                request_id=str(envelope.get("request_id", "")),
            )
        return dict(envelope.get("data", {}))

    def list_services(self) -> list[dict[str, Any]]:
        request = urllib.request.Request(
            self.base_url + "api/v1/services",
            headers={"X-Service-Token": self.token},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return list(body.get("services", []))

    def health(self) -> dict[str, Any]:
        request = urllib.request.Request(
            self.base_url + "api/v1/health",
            headers={"X-Service-Token": self.token},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))


__all__ = ["ServiceApiError", "ServiceClient"]
