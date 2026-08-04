"""Coevo 统一服务框架（一致性 API 层）。

目标
----
把 `src/coevo` 下各领域模块（身份、流程理解、任务分解、人才推荐、
运行中枢编排、任务包、工作区、驾驶舱、进展采集、成果回传、状态合并、
风险预警、督办会议、决策简报、知识沉淀、安全审计）统一到一个服务框架中，
对外通过**一致性 API** 开放：

    POST /api/v1/{service}/{method}   JSON 请求 → 统一响应信封
    GET  /api/v1/services             服务能力目录
    GET  /api/v1/health               服务健康检查

一致性约定
----------
* 统一请求信封：``ServiceRequest``（service / method / params / actor /
  request_id / ts）
* 统一响应信封：``ServiceResponse``（ok / code / message / data /
  request_id / ts），无论成功失败都走同一结构
* 统一错误码：``ErrorCode`` 闭集（参数错误、未授权、未找到服务/方法、
  内部错误、冲突等），错误永不泄漏异常栈
* 统一审计：每次调用都产出 ``AuditEvent``（复用生产审计模型），可查询
* 服务注册表：``ServiceSpec`` 声明名称/版本/能力/方法集，``ServiceRegistry``
  负责登记与查询，运行中枢式能力目录

本框架是**应用层演示**，只通过各模块的公开门面调用生产代码，不修改
`src/coevo` 任何领域逻辑；安全基线同样遵循：HTTP 仅绑定环回地址、
会话令牌鉴权、请求体大小上限、失败关闭。
"""

from .contract import (
    ErrorCode,
    ServiceError,
    ServiceRequest,
    ServiceResponse,
    error_response,
    ok_response,
)
from .client import ServiceApiError, ServiceClient
from .framework import ServiceFramework
from .openapi import build_openapi
from .registry import ServiceRegistry, ServiceSpec

__all__ = [
    "ErrorCode",
    "ServiceApiError",
    "ServiceClient",
    "ServiceError",
    "ServiceFramework",
    "ServiceRegistry",
    "ServiceRequest",
    "ServiceResponse",
    "ServiceSpec",
    "error_response",
    "build_openapi",
    "ok_response",
]
