"""一致性 API 的请求/响应信封与错误码（本框架的公共契约）。

设计要点
--------
* 所有数据类型为 frozen dataclass，构建时即校验，失败关闭。
* ``data`` 必须是 JSON 可序列化对象（dict/list/str/int/float/bool/None）。
* ``ErrorCode`` 是闭集；新增错误码必须显式扩展并同步文档。
* ``request_id`` 用于全链路追溯，与审计事件的 request_id 对齐。
"""

from __future__ import annotations

import dataclasses
import enum
from typing import Any


class ErrorCode(enum.Enum):
    """闭集错误码：调用方据 code 分支处理，不依赖异常类型。"""

    OK = "ok"
    BAD_REQUEST = "bad_request"          # 信封/参数结构非法
    VALIDATION = "validation_error"      # 业务参数校验失败（fail-closed）
    UNAUTHORIZED = "unauthorized"        # 令牌/权限不足
    NOT_FOUND = "not_found"              # 服务或方法不存在
    CONFLICT = "conflict"                # 状态冲突（重复/幂等冲突等）
    INTERNAL = "internal_error"          # 未预期的内部错误
    BUSY = "busy"                        # 服务繁忙/并发上限


@dataclasses.dataclass(frozen=True)
class ServiceRequest:
    """一次服务调用的统一请求信封。"""

    service: str
    method: str
    params: dict[str, Any]
    actor: str
    request_id: str
    ts: str  # ISO-8601 UTC 'Z'

    def __post_init__(self) -> None:
        for name in ("service", "method", "actor", "request_id", "ts"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ServiceError(ErrorCode.BAD_REQUEST, f"{name} must be non-empty")
        if not isinstance(self.params, dict):
            raise ServiceError(ErrorCode.BAD_REQUEST, "params must be a JSON object")


@dataclasses.dataclass(frozen=True)
class ServiceResponse:
    """统一响应信封：成功与失败使用同一结构。"""

    ok: bool
    service: str
    method: str
    request_id: str
    code: str
    message: str
    data: dict[str, Any]
    ts: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class ServiceError(Exception):
    """业务层可预期的失败，携带闭集错误码与 HTTP 状态。"""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        status: int = 400,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        if not isinstance(code, ErrorCode):
            raise TypeError("code must be ErrorCode")
        self.code = code
        self.status = status
        self.detail = detail or {}


def ok_response(
    request: ServiceRequest,
    data: dict[str, Any],
    *,
    message: str = "",
) -> ServiceResponse:
    """构建成功信封。"""
    return ServiceResponse(
        ok=True,
        service=request.service,
        method=request.method,
        request_id=request.request_id,
        code=ErrorCode.OK.value,
        message=message,
        data=data,
        ts=request.ts,
    )


def error_response(
    request: ServiceRequest | None,
    code: ErrorCode,
    message: str,
    *,
    service: str = "",
    method: str = "",
    detail: dict[str, Any] | None = None,
) -> ServiceResponse:
    """构建失败信封：错误永不泄漏内部异常栈。"""
    return ServiceResponse(
        ok=False,
        service=service or (request.service if request else ""),
        method=method or (request.method if request else ""),
        request_id=request.request_id if request else "",
        code=code.value,
        message=message,
        data=detail or {},
        ts=request.ts if request else "",
    )
