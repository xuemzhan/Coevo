"""service_api.adapters 包 —— 16 个领域模块 → 统一服务处理方法（架构分组）。

按领域拆分为可独立维护的模块：
* ``_core``            —— 上下文装配与共享助手（build_context / close_context /
                          参数与安全标识校验 / 证书句柄）
* ``identity_flow``    —— 身份、流程理解、任务分解、人才推荐
* ``orchestration``    —— 运行中枢固定编排链（含失败升级演示）
* ``package_workspace``—— 任务包、工作区、驾驶舱、进展采集、成果回传
* ``chain``            —— 状态合并、风险、督办、简报、知识沉淀
* ``audit_services``   —— 安全审计查询/拦截/导出/检查点

公共 API 保持与拆分前一致：build_context / close_context / build_registry。
"""
from __future__ import annotations

from typing import Any

from ..contract import ErrorCode, ServiceError  # noqa: F401
from ..registry import ServiceRegistry, ServiceSpec  # noqa: F401
from ._core import build_context, close_context, _require_safe_id  # noqa: F401
from .audit_services import (  # noqa: F401
    audit_checkpoint,
    audit_export,
    audit_intercept,
    audit_query,
)
from .chain import (  # noqa: F401
    brief_generate,
    knowledge_aggregate,
    merge_analyze,
    risk_analyze,
    supervision_coordinate,
)
from .identity_flow import (  # noqa: F401
    decomposition_propose,
    flow_understand,
    identity_describe,
    identity_register,
    talent_recommend,
)
from .orchestration import (  # noqa: F401
    orchestration_confirm,
    orchestration_dispatch,
    orchestration_fail_demo,
    orchestration_resume,
)
from .package_workspace import (  # noqa: F401
    cockpit_snapshot,
    package_build,
    progress_extract,
    report_build,
    workspace_init,
)


def _build_handler(methods: dict[str, Any]) -> Any:
    """把 {method: handler} 包成带方法检查的统一调用器。"""
    def handler(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
        method = request.method
        fn = methods.get(method)
        if fn is None:
            raise ServiceError(
                ErrorCode.NOT_FOUND, f"method {method!r} not implemented"
            )
        return fn(request, ctx)

    return handler

def build_registry() -> ServiceRegistry:
    """把 16 个领域模块注册为统一服务（一致性 API 的能力目录）。"""
    registry = ServiceRegistry()
    specs: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
        ("identity", "1.0", "身份与信任：角色/证书/授权/注册", ("describe", "register")),
        ("flow", "1.0", "任务流程理解：解析与阶段映射", ("understand",)),
        ("decomposition", "1.0", "任务分解：结构化基线", ("propose",)),
        ("talent", "1.0", "团队组建：脱敏人才推荐", ("recommend",)),
        (
            "orchestration",
            "1.0",
            "运行中枢：固定编排链",
            ("dispatch", "confirm", "resume", "fail_demo"),
        ),
        ("package", "1.0", "加密任务包生成与校验", ("build",)),
        ("workspace", "1.0", "工作区初始化", ("init",)),
        ("cockpit", "1.0", "本地驾驶舱视图", ("snapshot",)),
        ("progress", "1.0", "进展采集", ("extract",)),
        ("report", "1.0", "成果回传包", ("build",)),
        ("merge", "1.0", "状态合并与版本更新", ("analyze",)),
        ("risk", "1.0", "风险预警", ("analyze",)),
        ("supervision", "1.0", "督办与会议协同", ("coordinate",)),
        ("brief", "1.0", "决策简报", ("generate",)),
        ("knowledge", "1.0", "知识沉淀与复用", ("aggregate",)),
        ("audit", "1.0", "安全审计", ("query", "intercept", "export", "checkpoint")),
    )
    handlers: dict[str, Any] = {
        "identity": {"describe": identity_describe, "register": identity_register},
        "flow": {"understand": flow_understand},
        "decomposition": {"propose": decomposition_propose},
        "talent": {"recommend": talent_recommend},
        "orchestration": {
            "dispatch": orchestration_dispatch,
            "confirm": orchestration_confirm,
            "resume": orchestration_resume,
            "fail_demo": orchestration_fail_demo,
        },
        "package": {"build": package_build},
        "workspace": {"init": workspace_init},
        "cockpit": {"snapshot": cockpit_snapshot},
        "progress": {"extract": progress_extract},
        "report": {"build": report_build},
        "merge": {"analyze": merge_analyze},
        "risk": {"analyze": risk_analyze},
        "supervision": {"coordinate": supervision_coordinate},
        "brief": {"generate": brief_generate},
        "knowledge": {"aggregate": knowledge_aggregate},
        "audit": {
            "query": audit_query,
            "intercept": audit_intercept,
            "export": audit_export,
            "checkpoint": audit_checkpoint,
        },
    }
    for name, version, description, methods in specs:
        registry = registry.register(
            ServiceSpec(name, version, description, frozenset(methods)),
            _build_handler(handlers[name]),
        )
    return registry

__all__ = ["build_context", "close_context", "build_registry", "_require_safe_id"]
