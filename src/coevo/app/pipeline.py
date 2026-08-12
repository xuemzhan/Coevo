"""app.pipeline —— 离线演示组合根（下发链 E2E）与结果值对象。

职责
----
把 `src/coevo` 各领域模块按“固定编排链”装配成一个可离线复现的端到端
演示闭环，是 `scripts/run_demo.py` 与 `tests/e2e/test_demo_runner.py` 的
官方入口。本模块只做**装配与调度**，不包含领域逻辑；所有业务能力来自
被组合的各领域门面。

七阶段流水线（`run_demo_pipeline`）
----------------------------------
1. 加密与 PKI：`ensure_demo_profile` 引导 SM2 测试 PKI；创建
   `GmsslPrototypeProvider`（Python 进程不接触私钥字节）。
2. 真实链环境：`RealChainStore`（编排记录 + 审计链）、脱敏人才池、
   `RealChainExecutor`（流程理解/分解/推荐三服务 + 人才库）、
   `AgentRegistry`（四个子智能体登记）。
3. 固定链执行：`dispatch_event_with_real_facades` 前三步原子执行并停在第 4 步
   人工确认 → `confirm_real_chain`（负责人授权）→ `resume_real_chain`
   （第 5 步生成加密包并回读校验）。
4. 加密包导出：`build_encrypted_package` → `parse_package_bytes` →
   `open_encrypted_package` 三方回环校验后落盘 outbox。
5. 驾驶舱：`WorkspaceView`/`RoleView` 快照；可选启动环回
   `CockpitHttpServer`。
6. 知识包：`KnowledgeBaseFacade.aggregate` → `KnowledgeStore` 持久化。
7. 审计流：`AuditStreamHub` 订阅者收到链完成/包导出/知识入库事件。

安全与约束
----------
* 全流程离线：无网络请求、无运行时下载；密钥不落明文。
* 演示性替身集中在 `demo_support.py`（HMAC 签名/内存新鲜度权威），
  生产路径见受保护密钥句柄与国密认证模块。
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 离线演示组合根：把各领域门面按固定编排链装配成可复现的端到端演示，
# 是 run_demo.py 与 e2e 测试的官方入口。只做装配与调度，不包含领域逻辑。

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .demo_support import DEMO_ACTOR, DEMO_PROFILE, DEMO_REVISION, DemoFreshnessAuthority, DemoSigner, ROOT, ensure_demo_profile, now_utc_iso_z, sample_project_input

@dataclass(frozen=True)
class DemoResult:
    """Everything the demo run produced, for verification and display."""

    runtime_dir: Path
    outcome: str
    package_path: Path | None
    package_wire_sha256: str
    knowledge_bundle_id: str
    audit_event_count: int
    cockpit_url: str
    store: Any
    hub: Any
    cockpit_token: str = ""
    cockpit_server: Any | None = None


class _AllowAllScopeRbac:
    """Demo composition-root gate checkers (structural allow-all).

    The framework plan gate validates the chain shape, policy invariants and
    L18/L19; RBAC / tool-scope enforcement is a structural allow-all for the
    demo and the product wiring plugs real authorizers here later.
    """

    def within_scope(self, tool_ref: str, policy_profile: str) -> bool:
        return True

    def authorized(self, plan: object, actor: str) -> bool:
        return True


# Shared immutable gate-checker instance for the demo composition root.
_ALLOW_ALL_SCOPE_RBAC = _AllowAllScopeRbac()


def _export_demo_package(
    run_dir: Path,
    project_input: dict[str, Any],
    now: str,
    completed: Any,
    provider: Any,
    sender_handle: Any,
    recipient_handle: Any,
) -> tuple[Path, str]:
    """DEMO-ONLY: build, round-trip-verify and export the encrypted package."""

    import hashlib
    import json

    from src.coevo.protocol import (
        build_encrypted_package,
        build_envelope_template,
        open_encrypted_package,
        parse_package_bytes,
    )

    outbox = run_dir / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    envelope = build_envelope_template(
        sender_cert_id="CERT-SENDER",
        recipient_cert_id="CERT-RECIPIENT",
        project_id="PRJ001",
        package_type="TASK_ASSIGNMENT",
        sequence_no=1,
        payload_length=0,
        created_at=now,
        expires_at="2027-08-02T00:00:00Z",
    )
    manifest = {
        "event_id": "ev.demo.001",
        "project_id": "PRJ001",
        "task_id": "t.1",
        "base_revision": DEMO_REVISION,
        "payload_digest": project_input["payload_digest"],
    }
    content = json.dumps(
        {
            "title": project_input["title"],
            "objective": project_input["objective"],
            "flow_summary": list(completed.flow_understanding_summary),
            "baseline_summary": list(completed.baseline_summary),
            "recommendations": list(completed.recommendation_summary),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    package = build_encrypted_package(
        envelope=envelope,
        manifest=manifest,
        content=content,
        provider=provider,
        sender_handle=sender_handle,
        recipient_handle=recipient_handle,
        signed_at=now,
    )
    parsed = parse_package_bytes(package.to_bytes())
    opened = open_encrypted_package(
        parsed,
        provider=provider,
        recipient_handle=recipient_handle,
        sender_handle=sender_handle,
    )
    if opened.content != content:
        raise RuntimeError("demo package round-trip verification failed")
    package_path = outbox / (
        f"TASK_ASSIGNMENT_PRJ001_{parsed.envelope.package_id}.agent"
    )
    package_path.write_bytes(package.to_bytes())
    export_digest = hashlib.sha256(package.to_bytes()).hexdigest()
    return package_path, export_digest


def _build_demo_cockpit_views(
    completed: Any = None,
    store: Any = None,
    *,
    package_path: str = "",
    package_digest: str = "",
    knowledge_bundle_id: str = "",
) -> tuple[Any, Any]:
    """DEMO-ONLY: build the cockpit workspace/role snapshots."""

    from src.coevo.cockpit import (
        ActivityEntry,
        ArtifactSummary,
        MilestoneSummary,
        RoleView,
        TaskSummary,
        TraceStepSummary,
        WorkspaceView,
    )

    trace = tuple(
        TraceStepSummary(
            step_index=step.step_index,
            agent_id=step.agent_id or "human",
            result=step.result.value,
            requires_human_confirmation=step.requires_human_confirmation,
            confirmed_by=step.confirmed_by or "",
            detail=step.detail,
        )
        for step in (completed.orch_report.trace if completed is not None else ())
    )
    activity = ()
    if store is not None:
        try:
            entries = getattr(store, "audit_entries", ())
        except Exception:
            entries = ()
        activity = tuple(
            ActivityEntry(
                sequence=entry.sequence,
                event_id=entry.event_id,
                action=entry.action,
                result=entry.result,
                digest=entry.payload_digest,
                recorded_at=entry.recorded_at,
            )
            for entry in entries
        )
    workspace_view = WorkspaceView(
        "PRJ001",
        "离线 MVP 演示交付",
        ("a.pm", "a.eng"),
        1,
        1,
        1,
        package_path,
        package_digest,
        knowledge_bundle_id,
        trace,
        activity,
    )
    pm_role_view = RoleView(
        "a.pm",
        "PRJ001",
        "负责人",
        (),
        (),
        (),
    )
    eng_role_view = RoleView(
        "a.eng",
        "PRJ001",
        "工程",
        (TaskSummary("t.1", "Implement demo", "in_progress",
                     "2026-08-31T00:00:00Z", "a.eng"),),
        (MilestoneSummary("m.1", "Demo ready", "2026-08-31T00:00:00Z", False),),
        (ArtifactSummary("docs/report.docx", "document",
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                         128, "0" * 64),),
    )
    # 并行项目演示：PRJ002 停在人工确认节点，用于展示多项目流转与
    # 跨项目"待确认"汇总（DEMO 视图数据，非伪造真实链）。
    prj002_trace = (
        TraceStepSummary(
            0, "agent.task_flow_understanding", "ok", False, "",
            "real facade completed",
        ),
        TraceStepSummary(
            1, "agent.task_decomposition", "ok", False, "",
            "real facade completed",
        ),
        TraceStepSummary(
            2, "agent.team_recommendation", "ok", False, "",
            "real facade completed",
        ),
        TraceStepSummary(
            3, "human", "ok", True, "",
            "waiting for operator confirmation",
        ),
    )
    prj002_view = WorkspaceView(
        "PRJ002",
        "知识复用试点项目",
        ("a.pm",),
        1,
        0,
        0,
        trace=prj002_trace,
    )
    prj002_role = RoleView(
        "a.pm",
        "PRJ002",
        "负责人",
        (TaskSummary(
            "t.2", "复用演示模板生成基线", "pending",
            "2026-08-25T00:00:00Z", "a.pm",
        ),),
        (),
        (),
    )
    return (
        (workspace_view, prj002_view),
        (pm_role_view, eng_role_view, prj002_role),
    )


def _store_demo_knowledge(run_dir: Path, now: str) -> str:
    """DEMO-ONLY: aggregate and persist the knowledge bundle."""

    from src.coevo.knowledge_base import KnowledgeBaseFacade, KnowledgeStore

    bundle = KnowledgeBaseFacade.aggregate(
        project_id="PRJ001",
        baseline={
            "title": "Ship offline MVP demo",
            "summary": "demo baseline",
            "stages": ["plan", "execute", "review"],
            "work_packages": ["wp.1"],
        },
        merge_records=(),
        risk_reports=(),
        meeting_conclusions=(),
        decision_briefs=(),
        progress_captures=(),
        model_summaries=({"id": "ms.1", "title": "demo model summary"},),
        now=now,
    )
    knowledge_store = KnowledgeStore.create(run_dir / "knowledge.db")
    knowledge_store.save(bundle, now=now)
    knowledge_store.close()
    return bundle.bundle_id


def _publish_demo_audit(hub: Any, now: str) -> None:
    """DEMO-ONLY: publish the three demo completion audit events."""

    from src.coevo.audit_governance import AuditEvent, AuditEventSource

    for action, result in (
        ("chain.completed", "ok"),
        ("package.exported", "ok"),
        ("knowledge.stored", "ok"),
    ):
        hub.publish(
            AuditEvent.from_audit_record(
                {
                    "ts": now,
                    "actor": "u.pm",
                    "action": action,
                    "result": result,
                    "project_id": "PRJ001",
                    "task_id": "t.1",
                    "tool": "coevo.demo",
                },
                source=AuditEventSource.STATE,
            )
        )


def run_demo_pipeline(
    runtime_dir: Path,
    *,
    now: str | None = None,
    with_cockpit: bool = False,
    cockpit_port: int = 12751,
    progress: Any = None,
    confirm_callback: Any = None,
    session_timeout_sec: int = 8 * 3600,
    confirm_via_web: bool = False,
    gate_ready: Any = None,
    cockpit_lock_path: Path | None = None,
) -> DemoResult:
    """Execute the whole offline MVP loop and return the results."""
    from src.coevo.crypto import GmsslPrototypeProvider
    from src.coevo.orchestrator import RealChainStore

    now = now or now_utc_iso_z()
    runtime_dir = Path(runtime_dir)
    run_dir = runtime_dir / f"run-{uuid.uuid4().hex[:12]}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. Crypto provider + test PKI (mvp-prototype scope).
    ensure_demo_profile()
    provider = GmsslPrototypeProvider(ROOT)
    sender_handle = provider.sender_handle(DEMO_PROFILE, "CERT-SENDER")
    recipient_handle = provider.recipient_handle(DEMO_PROFILE, "CERT-RECIPIENT")

    # 2. Real chain environment.
    store = RealChainStore.create(
        run_dir / "real-chain.db",
        signer=DemoSigner(),
        freshness=DemoFreshnessAuthority(),
    )
    try:
        return _run_demo_pipeline_with_store(
            run_dir,
            now,
            store,
            provider,
            sender_handle,
            recipient_handle,
            with_cockpit,
            cockpit_port,
            progress,
            confirm_callback,
            session_timeout_sec,
            confirm_via_web,
            gate_ready,
            cockpit_lock_path,
        )
    except BaseException:
        # 失败路径也必须释放资源：关闭数据库句柄并停止已启动的驾驶舱，
        # 否则测试/运行环境会残留文件锁与单实例锁。
        store.close()
        raise


def _run_demo_pipeline_with_store(
    run_dir: Path,
    now: str,
    store: Any,
    provider: Any,
    sender_handle: Any,
    recipient_handle: Any,
    with_cockpit: bool,
    cockpit_port: int,
    progress: Any = None,
    confirm_callback: Any = None,
    session_timeout_sec: int = 8 * 3600,
    confirm_via_web: bool = False,
    gate_ready: Any = None,
    cockpit_lock_path: Path | None = None,
) -> DemoResult:
    """执行演示主流程；驾驶舱服务器若已启动由调用方负责停止。"""
    from src.coevo.audit_governance import AuditStreamHub
    from src.coevo.cockpit import (
        CockpitHttpConfig,
        CockpitHttpServer,
    )
    from src.coevo.identity.models import Actor
    from src.coevo.identity.service import StaticAuthorizer
    from src.coevo.orchestrator import (
        MVP_FIXED_CHAIN,
        AgentRegistry,
        OrchestrationEvent,
        OrchestrationEventKind,
        OrchestrationOutcome,
        Orchestrator,
        RealChainExecutor,
        canonical_digest,
    )
    from src.coevo.task_decomposition.service import TaskDecompositionService
    from src.coevo.task_flow.service import FlowUnderstandingService
    from src.coevo.talent.models import (
        AvailabilityWindow,
        RedactedIdentity,
        SkillTag,
        Talent,
        TalentPool,
    )
    from src.coevo.talent.service import TalentRecommenderService
    from src.coevo.workspace.models import WorkspaceEntry

    talent = Talent(
        "talent.1",
        (SkillTag("tech:python"),),
        (),
        0,
        2,
        AvailabilityWindow("2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"),
        RedactedIdentity("pool.1", "T-1", "a" * 64),
    )
    executor = RealChainExecutor(
        FlowUnderstandingService(),
        TaskDecompositionService(),
        TalentRecommenderService(),
        TalentPool("pool.1", "1.0", (talent,)),
    )
    # FRAMEWORK-INTEGRATION-4 / FRAMEWORK-OPTIMIZE-1: agents may only enter
    # the registry after the framework manifest-checker accepts their manifest
    # (assembly converged into demo_support.register_demo_agents).
    from src.coevo.app.demo_support import register_demo_agents

    registry = AgentRegistry.empty()
    registry, _ = register_demo_agents(registry)
    project_input = sample_project_input()
    event = OrchestrationEvent(
        "ev.demo.001",
        OrchestrationEventKind.DISPATCH,
        "PRJ001",
        "t.1",
        {
            "schema_version": project_input["schema_version"],
            "base_revision": project_input["base_revision"],
            "project_input_digest": canonical_digest(project_input),
        },
        now,
    )
    workspace = WorkspaceEntry("PRJ001", "a.pm", "pkg.input", DEMO_REVISION)
    if callable(progress):
        progress("初始化身份、加密与真实链环境")

    # 3. Framework gate (FRAMEWORK-INTEGRATION-3): validate the fixed chain
    #    with the framework plan gate before the real dispatch.  RBAC / L4
    #    scope checkers are structural allow-all for the demo; the product
    #    wiring plugs real authorizers here later.
    from src.coevo.framework.integration import validate_product_chain
    from src.coevo.framework.policy import get_default_profile

    gate = validate_product_chain(
        MVP_FIXED_CHAIN,
        registry,
        get_default_profile("INTERACTIVE"),
        scope_checker=_ALLOW_ALL_SCOPE_RBAC,
        rbac_checker=_ALLOW_ALL_SCOPE_RBAC,
        actor=DEMO_ACTOR,
        validated_at=now,
    )
    if not gate.accepted:
        raise RuntimeError(
            "framework plan gate rejected the MVP fixed chain: "
            + (gate.failure_reason or "unknown")
        )

    # 4. Run the guarded five-step chain.
    held = Orchestrator.dispatch_event_with_real_facades(
        registry,
        MVP_FIXED_CHAIN,
        event,
        workspace=workspace,
        executor=executor,
        project_input=project_input,
        store=store,
        now=now,
    )
    server = None
    cockpit_url = ""
    cockpit_token = ""
    if callable(progress):
        progress("编排链前三步完成，等待负责人确认")
    if confirm_via_web:
        # 网页确认：启动驾驶舱并挂接确认处理器，阻塞等待负责人在页面确认。
        gate_event = threading.Event()
        gate_state: dict[str, Any] = {}

        def _web_handler(action: str) -> dict[str, str]:
            if action == "reject":
                gate_state["decision"] = "rejected"
                gate_event.set()
                return {"decision": "rejected"}
            _confirmed = Orchestrator.confirm_real_chain(
                held,
                preview=held.package_preview,
                actor=Actor(DEMO_ACTOR),
                authorizer=StaticAuthorizer({
                    DEMO_ACTOR: frozenset({"orchestrator:confirm-package:PRJ001"}),
                }),
                store=store,
                now=now,
            )
            _completed = Orchestrator.resume_real_chain(
                _confirmed,
                registry=registry,
                chain=MVP_FIXED_CHAIN,
                event=event,
                workspace=workspace,
                executor=executor,
                store=store,
                now=now,
                crypto_provider=provider,
                sender_handle=sender_handle,
                recipient_handle=recipient_handle,
            )
            gate_state["decision"] = "approved"
            gate_state["completed"] = _completed
            gate_event.set()
            return {"decision": "approved"}

        pending_views = _build_demo_cockpit_views(held, store)
        try:
            from src.coevo.cockpit import CockpitHttpConfig, CockpitHttpServer

            server = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=cockpit_port,
                    request_timeout_sec=5,
                    state_path=run_dir / "cockpit-state.json",
                    session_timeout_sec=session_timeout_sec,
                    lock_path=cockpit_lock_path,
                ),
                workspace_views=pending_views[0],
                role_views=pending_views[1],
                pending_action_handler=_web_handler,
            )
            server.start()
        except BaseException:
            if server is not None:
                try:
                    server.stop()
                except Exception:
                    pass
            raise
        cockpit_url = server.url
        cockpit_token = server.session_manager.create()
        if callable(gate_ready):
            gate_ready(cockpit_url, cockpit_token)
        if callable(progress):
            progress("已启动驾驶舱，等待负责人在网页上确认")
        gate_event.wait()
        if gate_state.get("decision") != "approved":
            raise RuntimeError("demo rejected by operator at the confirmation gate")
        completed = gate_state["completed"]
    else:
        if callable(confirm_callback):
            approved = confirm_callback(held.package_preview)
            if not approved:
                raise RuntimeError(
                    "demo rejected by operator at the confirmation gate"
                )
        confirmed = Orchestrator.confirm_real_chain(
            held,
            preview=held.package_preview,
            actor=Actor(DEMO_ACTOR),
            authorizer=StaticAuthorizer({
                DEMO_ACTOR: frozenset({"orchestrator:confirm-package:PRJ001"}),
            }),
            store=store,
            now=now,
        )
        if callable(progress):
            progress("负责人确认通过，恢复编排链")
        completed = Orchestrator.resume_real_chain(
            confirmed,
            registry=registry,
            chain=MVP_FIXED_CHAIN,
            event=event,
            workspace=workspace,
            executor=executor,
            store=store,
            now=now,
            crypto_provider=provider,
            sender_handle=sender_handle,
            recipient_handle=recipient_handle,
        )
    if completed.orch_report.outcome != OrchestrationOutcome.COMPLETED:
        raise RuntimeError(
            f"demo chain did not complete: {completed.orch_report.outcome}"
        )
    wire_sha256 = (
        completed.package_summary[-1].split("sha256=", 1)[1].split(";", 1)[0]
        if completed.package_summary
        else ""
    )

    # 4. Export a real encrypted package to the outbox and verify it.
    if callable(progress):
        progress("生成加密任务包并回读校验")
    package_path, export_digest = _export_demo_package(
        run_dir, project_input, now, completed,
        provider, sender_handle, recipient_handle,
    )

    # 5. Knowledge bundle + persistent store (视图需要知识包 ID).
    if callable(progress):
        progress("沉淀知识库")
    knowledge_bundle_id = _store_demo_knowledge(run_dir, now)

    # 6. Cockpit snapshot (views) + optional live server.
    if callable(progress):
        progress("组装驾驶舱视图")
    workspace_views, role_views = _build_demo_cockpit_views(
        completed,
        store,
        package_path=str(package_path),
        package_digest=export_digest or wire_sha256,
        knowledge_bundle_id=knowledge_bundle_id,
    )
    # 无论是否启动驾驶舱服务，都把视图快照落盘，供 --resume 重开。
    from src.coevo.cockpit.state_store import CockpitStateStore

    state_store = CockpitStateStore(run_dir / "cockpit-state.json")
    state_store.save(workspace_views, role_views)
    if confirm_via_web:
        # 网页确认模式下服务器已在确认前启动：重建完成态视图并替换快照。
        from src.coevo.cockpit import CockpitFacade

        server.state = CockpitFacade.start_server(
            workspace_views=workspace_views,
            role_views=role_views,
            now=now,
        )
    elif with_cockpit:
        try:
            server = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=cockpit_port,
                    request_timeout_sec=5,
                    state_path=run_dir / "cockpit-state.json",
                    session_timeout_sec=session_timeout_sec,
                    lock_path=cockpit_lock_path,
                ),
                workspace_views=workspace_views,
                role_views=role_views,
            )
            server.start()
        except BaseException:
            # 服务器启动失败（例如单实例锁被占用）时立即释放已获取的资源，
            # 避免残留文件句柄与单实例锁。
            if server is not None:
                try:
                    server.stop()
                except Exception:
                    pass
            raise
        cockpit_url = server.url
        cockpit_token = server.session_manager.create()
        if callable(progress):
            progress("启动本地驾驶舱并提供会话入口")

    # 7. Audit stream (push notifications).
    if callable(progress):
        progress("发布审计事件并封口")
    hub = AuditStreamHub()
    pushed: list[Any] = []
    hub.subscribe("u.auditor", pushed.append)
    _publish_demo_audit(hub, now)

    return DemoResult(
        runtime_dir=run_dir,
        outcome=completed.orch_report.outcome.value,
        package_path=package_path,
        package_wire_sha256=export_digest or wire_sha256,
        knowledge_bundle_id=knowledge_bundle_id,
        audit_event_count=hub.event_count,
        cockpit_url=cockpit_url,
        cockpit_token=cockpit_token,
        store=store,
        hub=hub,
        cockpit_server=server,
    )
