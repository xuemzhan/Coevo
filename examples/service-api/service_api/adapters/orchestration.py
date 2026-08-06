from __future__ import annotations

from typing import Any

from src.coevo.app.demo_support import (  # noqa: E402
    DemoFreshnessAuthority,
    DemoSigner,
)
from src.coevo.identity.models import Actor  # noqa: E402
from src.coevo.orchestrator import (  # noqa: E402
    MVP_FIXED_CHAIN,
    AgentStatus,
    OrchestrationEvent,
    OrchestrationEventKind,
    Orchestrator,
    RealChainStore,
    canonical_digest,
)
from src.coevo.workspace.models import WorkspaceEntry  # noqa: E402

from ._core import OWNER_CERT, _cert_handle, _require_param
from ..contract import ErrorCode, ServiceError  # noqa: E402


def orchestration_dispatch(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """编排链第一步：流程理解→分解→推荐，停在第 4 步人工确认（US-4）。"""
    event_id = _require_param(request, "event_id")
    project_input = _require_param(request, "project_input")
    workspace = WorkspaceEntry(
        project_input["project_id"], "u.pm", "pkg.input", project_input["base_revision"]
    )
    event = OrchestrationEvent(
        event_id,
        OrchestrationEventKind.DISPATCH,
        project_input["project_id"],
        project_input["task_id"],
        {
            "schema_version": project_input["schema_version"],
            "base_revision": project_input["base_revision"],
            "project_input_digest": canonical_digest(project_input),
        },
        request.ts,
    )
    store = RealChainStore.create(
        ctx["runtime_dir"] / f"chain-{event_id}.db",
        signer=DemoSigner(),
        freshness=DemoFreshnessAuthority(),
    )
    try:
        held = Orchestrator.dispatch_event_with_real_facades(
            ctx["agent_registry"],
            MVP_FIXED_CHAIN,
            event,
            workspace=workspace,
            executor=ctx["chain_executor"],
            project_input=project_input,
            store=store,
            now=request.ts,
        )
    except Exception:
        # 失败路径不泄漏数据库连接：关闭本次会话存储后重抛
        store.close()
        raise
    ctx["chain_sessions"][event_id] = {
        "store": store,
        "held": held,
        "event": event,
        "workspace": workspace,
        "project_input": project_input,
    }
    return {
        "event_id": event_id,
        "outcome": held.orch_report.outcome.value,
        "flow": list(held.flow_understanding_summary),
        "baseline": list(held.baseline_summary),
        "recommendations": list(held.recommendation_summary),
    }
def orchestration_confirm(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """负责人授权确认第 4 步（US-4 人工确认节点）。"""
    event_id = _require_param(request, "event_id")
    actor_id = _require_param(request, "actor")
    session = ctx["chain_sessions"].get(event_id)
    if session is None:
        raise ServiceError(ErrorCode.NOT_FOUND, f"chain session {event_id!r} not found")
    held = session["held"]
    confirmed = Orchestrator.confirm_real_chain(
        held,
        preview=held.package_preview,
        actor=Actor(actor_id),
        authorizer=ctx["authorizer"],
        store=session["store"],
        now=request.ts,
    )
    session["confirmed"] = confirmed
    return {"event_id": event_id, "confirmed": True}
def orchestration_resume(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """生成加密任务包并完成整条编排链（US-4/US-5）。"""
    event_id = _require_param(request, "event_id")
    session = ctx["chain_sessions"].get(event_id)
    if session is None or "confirmed" not in session:
        raise ServiceError(ErrorCode.CONFLICT, f"chain {event_id!r} is not confirmed")
    confirmed = session["confirmed"]
    completed = Orchestrator.resume_real_chain(
        confirmed,
        registry=ctx["agent_registry"],
        chain=MVP_FIXED_CHAIN,
        event=session["event"],
        workspace=session["workspace"],
        executor=ctx["chain_executor"],
        store=session["store"],
        now=request.ts,
        crypto_provider=ctx["provider"],
        sender_handle=_cert_handle(ctx["provider"], OWNER_CERT, "sender"),
        recipient_handle=_cert_handle(
            ctx["provider"], request.params.get("recipient_cert_id", "CERT-DEV"), "recipient"
        ),
    )
    return {
        "event_id": event_id,
        "outcome": completed.orch_report.outcome.value,
        "package_summary": list(completed.package_summary),
    }
def orchestration_fail_demo(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """失败升级演示（US-4 AC-6）：智能体 BUSY 时编排不自动执行，升级人工。

    一致性 API 同样承载失败路径：返回统一信封且 outcome=escalated，
    不产生任务包，也不创建任何正式状态。
    """
    from src.coevo.orchestrator import AgentStatus

    project_input = _require_param(request, "project_input")
    registry_busy = ctx["agent_registry"].set_status(
        "agent.task_flow_understanding", AgentStatus.BUSY
    )
    event = OrchestrationEvent(
        "ev.fail.demo",
        OrchestrationEventKind.DISPATCH,
        project_input["project_id"],
        project_input["task_id"],
        {
            "schema_version": project_input["schema_version"],
            "base_revision": project_input["base_revision"],
            "project_input_digest": canonical_digest(project_input),
        },
        request.ts,
    )
    store = RealChainStore.create(
        ctx["runtime_dir"] / "fail-demo.db",
        signer=DemoSigner(),
        freshness=DemoFreshnessAuthority(),
    )
    try:
        held = Orchestrator.dispatch_event_with_real_facades(
            registry_busy,
            MVP_FIXED_CHAIN,
            event,
            workspace=WorkspaceEntry(
                project_input["project_id"],
                "u.pm",
                "pkg.input",
                project_input["base_revision"],
            ),
            executor=ctx["chain_executor"],
            project_input=project_input,
            store=store,
            now=request.ts,
        )
        return {
            "outcome": held.orch_report.outcome.value,
            "trace": [
                {
                    "step": trace.step_index,
                    "agent": trace.agent_id,
                    "result": trace.result.value,
                    "detail": trace.detail,
                }
                for trace in held.orch_report.trace
            ],
        }
    finally:
        store.close()
