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

import hashlib
import json
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
    cockpit_server: Any | None = None

def run_demo_pipeline(
    runtime_dir: Path,
    *,
    now: str | None = None,
    with_cockpit: bool = False,
    cockpit_port: int = 12751,
) -> DemoResult:
    """Execute the whole offline MVP loop and return the results."""
    from src.coevo.crypto import GmsslPrototypeProvider
    from src.coevo.identity.models import Actor
    from src.coevo.identity.service import StaticAuthorizer
    from src.coevo.knowledge_base import (
        KnowledgeBaseFacade,
        KnowledgeStore,
    )
    from src.coevo.orchestrator import (
        MVP_FIXED_CHAIN,
        AgentCapability,
        AgentRegistration,
        AgentRegistry,
        AgentSpec,
        OrchestrationEvent,
        OrchestrationEventKind,
        OrchestrationOutcome,
        Orchestrator,
        RealChainExecutor,
        RealChainStore,
        canonical_digest,
    )
    from src.coevo.audit_governance import (
        AuditEvent,
        AuditEventSource,
        AuditStreamHub,
    )
    from src.coevo.cockpit import (
        ArtifactSummary,
        CockpitHttpConfig,
        CockpitHttpServer,
        MilestoneSummary,
        RoleView,
        TaskSummary,
        WorkspaceView,
    )
    from src.coevo.talent.models import (
        AvailabilityWindow,
        RedactedIdentity,
        SkillTag,
        Talent,
        TalentPool,
    )
    from src.coevo.talent.service import TalentRecommenderService
    from src.coevo.task_decomposition.service import TaskDecompositionService
    from src.coevo.task_flow.service import FlowUnderstandingService
    from src.coevo.workspace.models import WorkspaceEntry

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
    registry = AgentRegistry.empty()
    for agent_id, capability in (
        ("agent.task_flow_understanding", AgentCapability.TASK_FLOW_UNDERSTANDING),
        ("agent.task_decomposition", AgentCapability.TASK_DECOMPOSITION),
        ("agent.team_recommendation", AgentCapability.TEAM_RECOMMENDATION),
        ("agent.task_package_build", AgentCapability.TASK_PACKAGE_BUILD),
    ):
        registry = registry.register(AgentRegistration(AgentSpec(
            agent_id, capability, capability.value, ("input",), ("output",)
        )))
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

    # 3. Run the guarded five-step chain.
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

    # 5. Cockpit snapshot (views) + optional live server.
    workspace_view = WorkspaceView(
        "PRJ001",
        "Ship offline MVP demo",
        ("a.pm", "a.eng"),
        1,
        1,
        1,
    )
    role_view = RoleView(
        "a.eng",
        "PRJ001",
        "Engineering",
        (TaskSummary("t.1", "Implement demo", "in_progress",
                     "2026-08-31T00:00:00Z", "a.eng"),),
        (MilestoneSummary("m.1", "Demo ready", "2026-08-31T00:00:00Z", False),),
        (ArtifactSummary("docs/report.docx", "document",
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                         128, "0" * 64),),
    )
    cockpit_url = ""
    server = None
    if with_cockpit:
        server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=cockpit_port,
                request_timeout_sec=5,
                state_path=run_dir / "cockpit-state.json",
            ),
            workspace_views=(workspace_view,),
            role_views=(role_view,),
        )
        server.start()
        cockpit_url = server.url

    # 6. Knowledge bundle + persistent store.
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

    # 7. Audit stream (push notifications).
    hub = AuditStreamHub()
    pushed: list[AuditEvent] = []
    hub.subscribe("u.auditor", pushed.append)
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

    return DemoResult(
        runtime_dir=run_dir,
        outcome=completed.orch_report.outcome.value,
        package_path=package_path,
        package_wire_sha256=export_digest or wire_sha256,
        knowledge_bundle_id=bundle.bundle_id,
        audit_event_count=hub.event_count,
        cockpit_url=cockpit_url,
        store=store,
        hub=hub,
        cockpit_server=server,
    )
