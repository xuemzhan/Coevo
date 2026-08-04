"""ServiceFramework —— 统一服务框架核心。

职责
----
1. 持有 :class:`ServiceRegistry`（能力目录）与共享上下文（各领域门面的
   装配对象，例如加密 provider、授权器、人才库、流程服务等）。
2. 提供唯一的调用入口 :meth:`invoke`：把 :class:`ServiceRequest` 分派到
   对应服务的处理方法，参数校验失败关闭，业务异常统一包装成
   :class:`ServiceResponse` 信封。
3. 调用审计钩子：每次调用（成功/失败）都产生一条审计事件（复用生产
   ``AuditEvent`` 模型），保证“一致性 API”本身可追溯。

处理流程（invoke）
------------------
* 查服务注册表：服务不存在 → NOT_FOUND；方法不存在 → NOT_FOUND。
* 调用前校验：方法必须是可调用对象；异常按类型映射错误码：
  - :class:`ServiceError` → 保留其 code/status/detail
  - :class:`ValueError`/类型错误 → VALIDATION（fail-closed）
  - 其余异常 → INTERNAL（不泄漏堆栈）
* 统一返回信封；同步写审计。
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import traceback
import uuid
from typing import Any, Callable

from .contract import (
    ErrorCode,
    ServiceError,
    ServiceRequest,
    ServiceResponse,
    error_response,
    ok_response,
)
from .registry import ServiceRegistry


class ServiceFramework:
    """统一服务框架：注册表 + 共享上下文 + 一致性分派 + 审计。"""

    def __init__(
        self,
        registry: ServiceRegistry,
        context: dict[str, Any],
        *,
        audit: Callable[[ServiceRequest, ServiceResponse], None] | None = None,
        max_params_depth: int = 8,
        permissions: dict[str, frozenset[str]] | None = None,
    ) -> None:
        """统一服务框架。

        ``permissions``：可选的调用权限策略，映射 ``actor -> 允许的动作集合``
        （动作格式 ``"<service>.<method>"``；``"*"`` 表示该主体全部允许）。
        未提供时不做权限检查（向后兼容）；提供时对未列出的主体一律拒绝
        （fail-closed），返回 UNAUTHORIZED 信封。
        """
        self.registry = registry
        self.context = context
        self._audit = audit
        self._max_params_depth = max_params_depth
        self._permissions = permissions

    # ------------------------------------------------------------------
    # 一致性分派
    # ------------------------------------------------------------------
    def invoke(self, request: ServiceRequest) -> ServiceResponse:
        """分派一次服务调用并返回统一信封（永不抛出业务异常）。"""
        try:
            self._validate_request(request)
            entry = self.registry.get(request.service)
            if entry is None:
                response = error_response(
                    request, ErrorCode.NOT_FOUND,
                    f"service {request.service!r} not found",
                )
            else:
                spec, handler = entry
                if request.method not in spec.methods:
                    response = error_response(
                        request, ErrorCode.NOT_FOUND,
                        f"method {request.method!r} not found on "
                        f"service {request.service!r}",
                    )
                else:
                    self._check_permission(request)
                    data = self._call_handler(handler, request)
                    response = ok_response(request, data)
        except ServiceError as exc:
            response = error_response(
                request, exc.code, str(exc), detail=exc.detail
            )
        except (TypeError, ValueError) as exc:
            # 参数/返回值结构错误 → 校验失败（fail-closed，不泄漏细节之外的内部状态）
            response = error_response(
                request, ErrorCode.VALIDATION, f"invalid invocation: {exc}"
            )
        except Exception:
            # 未预期内部错误：仅返回稳定错误码，不泄漏堆栈
            traceback.print_exc()
            response = error_response(
                request, ErrorCode.INTERNAL, "internal service error"
            )
        if self._audit is not None:
            try:
                self._audit(request, response)
            except Exception:  # 审计失败不允许影响业务响应
                traceback.print_exc()
        return response

    def invoke_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        """HTTP 层入口：dict → 信封 dict（缺失字段按 BAD_REQUEST 处理）。"""
        try:
            now = _dt.datetime.now(_dt.timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
            request = ServiceRequest(**{
                "service": str(payload.get("service", "")),
                "method": str(payload.get("method", "")),
                "params": payload.get("params") or {},
                "actor": str(payload.get("actor") or "anonymous"),
                "request_id": str(
                    payload.get("request_id") or f"req.{uuid.uuid4().hex[:12]}"
                ),
                "ts": str(payload.get("ts") or now),
            })
        except (ServiceError, TypeError) as exc:
            code = exc.code if isinstance(exc, ServiceError) else ErrorCode.BAD_REQUEST
            return error_response(None, code, str(exc)).to_dict()
        return self.invoke(request).to_dict()

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    def _validate_request(self, request: ServiceRequest) -> None:
        """信封结构校验（fail-closed）：params 必须是 JSON 对象且深度有界。"""
        self._check_depth(request.params, depth=0)

    def _check_depth(self, value: Any, *, depth: int) -> None:
        if depth > self._max_params_depth:
            raise ServiceError(
                ErrorCode.BAD_REQUEST,
                f"params nesting exceeds limit {self._max_params_depth}",
            )
        if isinstance(value, dict):
            for item in value.values():
                self._check_depth(item, depth=depth + 1)
        elif isinstance(value, list):
            for item in value:
                self._check_depth(item, depth=depth + 1)

    def _check_permission(self, request: ServiceRequest) -> None:
        """调用权限校验（可选策略，fail-closed）。"""
        if self._permissions is None:
            return
        allowed = self._permissions.get(request.actor, frozenset())
        action = f"{request.service}.{request.method}"
        if "*" in allowed or action in allowed:
            return
        raise ServiceError(
            ErrorCode.UNAUTHORIZED,
            f"actor {request.actor!r} is not allowed to call {action!r}",
            status=403,
        )

    def _call_handler(
        self,
        handler: Callable[..., Any],
        request: ServiceRequest,
    ) -> dict[str, Any]:
        """调用服务处理方法，并强制返回 JSON 可序列化 dict。"""
        result = handler(request, self.context)
        if not isinstance(result, dict):
            raise TypeError(
                f"service handler for {request.service}.{request.method} "
                "must return a dict"
            )
        return result


__all__ = ["ServiceFramework"]
