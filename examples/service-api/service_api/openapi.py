"""OpenAPI 3.0 契约生成：把服务注册表转成机器可读的 API 描述。

一致性 API 的“开放”不仅体现在统一信封，还体现在可消费的契约：调用方
（或网关/文档工具）可直接读取 ``/api/v1/openapi.json`` 获得全部服务、
方法、请求体与响应体 Schema。
"""

from __future__ import annotations

from typing import Any

from .registry import ServiceRegistry


def build_openapi(registry: ServiceRegistry) -> dict[str, Any]:
    """由服务注册表生成 OpenAPI 3.0.3 描述（纯函数）。"""
    paths: dict[str, Any] = {}
    for spec in registry.list():
        path = f"/api/v1/{spec.name}/{{method}}"
        paths[path] = {
            "post": {
                "summary": f"{spec.description}",
                "operationId": f"{spec.name}.invoke",
                "parameters": [
                    {
                        "name": "service",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "method",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ServiceRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "统一响应信封",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ServiceResponse"}
                            }
                        },
                    },
                    "400": {"description": "bad_request / validation_error"},
                    "401": {"description": "unauthorized"},
                    "404": {"description": "not_found"},
                    "409": {"description": "conflict"},
                    "500": {"description": "internal_error"},
                },
            }
        }
    paths["/api/v1/services"] = {
        "get": {
            "summary": "能力目录",
            "operationId": "list.services",
            "responses": {"200": {"description": "服务清单"}},
        }
    }
    paths["/api/v1/health"] = {
        "get": {
            "summary": "健康检查",
            "operationId": "health",
            "responses": {"200": {"description": "服务状态"}},
        }
    }
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Coevo 统一服务框架 API",
            "version": "1.0.0",
            "description": (
                "16 个领域模块经一致性 API 对外开放：统一请求/响应信封、"
                "闭集错误码、令牌鉴权与全程审计。"
            ),
        },
        "paths": paths,
        "components": {
            "schemas": {
                "ServiceRequest": {
                    "type": "object",
                    "required": ["params"],
                    "properties": {
                        "params": {"type": "object"},
                        "actor": {"type": "string"},
                        "request_id": {"type": "string"},
                        "ts": {"type": "string"},
                    },
                },
                "ServiceResponse": {
                    "type": "object",
                    "required": [
                        "ok", "service", "method", "request_id",
                        "code", "message", "data", "ts",
                    ],
                    "properties": {
                        "ok": {"type": "boolean"},
                        "service": {"type": "string"},
                        "method": {"type": "string"},
                        "request_id": {"type": "string"},
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "data": {"type": "object"},
                        "ts": {"type": "string"},
                    },
                },
            }
        },
    }


__all__ = ["build_openapi"]
