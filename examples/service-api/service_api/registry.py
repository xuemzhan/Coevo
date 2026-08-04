"""服务注册表：一致性 API 的能力目录。

每个服务用 :class:`ServiceSpec` 声明名称、版本、能力说明与开放的方法集；
:class:`ServiceRegistry` 负责登记、按名查询与列出能力目录。注册表不可变
风格——每次登记返回新实例，重复登记失败关闭。
"""

from __future__ import annotations

import dataclasses
from typing import Any, Callable


@dataclasses.dataclass(frozen=True)
class ServiceSpec:
    """一个服务的元数据声明。"""

    name: str
    version: str
    description: str
    methods: frozenset[str]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("service name must be non-empty")
        if not isinstance(self.version, str) or not self.version:
            raise ValueError("service version must be non-empty")
        if not self.methods:
            raise ValueError("service methods must be non-empty")
        for method in self.methods:
            if not isinstance(method, str) or not method:
                raise ValueError("method must be a non-empty string")


class ServiceRegistry:
    """服务能力目录（登记/查询/列表）。"""

    def __init__(
        self,
        *,
        specs: tuple[tuple[ServiceSpec, Callable[..., Any]], ...] = (),
    ) -> None:
        self._specs = specs
        self._index = {spec.name: (spec, handler) for spec, handler in specs}
        if len(self._index) != len(specs):
            raise ValueError("duplicate service registration")

    def register(
        self,
        spec: ServiceSpec,
        handler: Callable[..., Any],
    ) -> "ServiceRegistry":
        """登记一个服务；同名重复登记失败关闭。"""
        if not isinstance(spec, ServiceSpec):
            raise TypeError("spec must be ServiceSpec")
        if spec.name in self._index:
            raise ValueError(f"service {spec.name!r} already registered")
        return ServiceRegistry(specs=self._specs + ((spec, handler),))

    def get(self, name: str) -> tuple[ServiceSpec, Callable[..., Any]] | None:
        return self._index.get(name)

    def list(self) -> tuple[ServiceSpec, ...]:
        """按名称排序的能力目录（一致性 API 的 GET /services 数据源）。"""
        return tuple(
            spec for spec, _ in sorted(self._specs, key=lambda item: item[0].name)
        )


__all__ = ["ServiceRegistry", "ServiceSpec"]
