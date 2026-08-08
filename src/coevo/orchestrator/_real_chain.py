"""US-4-AC-2 guarded two-phase orchestration over the real US-1/2/3/5 facades."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 本模块实现“固定下发链”的真实门面两阶段编排（US-4 AC-2）：
#   阶段一（dispatch_real_chain）：
#     ① 校验固定链形状（5 步：流程理解→分解→推荐→人工确认→生成包）；
#     ② begin_dispatch 原子占位；步骤 0-2 依次调用真实门面
#        （understand / build_baseline / recommend），任何失败按
#        FailurePolicy 处理（本链禁用 SKIP，失败即升级人工）；
#     ③ 停在第 3 步（HELD_AT_CONFIRM），把中间产物与摘要存入
#        RealChainStore——未经人工确认绝不生成任务包。
#   阶段二（confirm_real_chain → resume_real_chain）：
#     ① confirm：校验 stored hold 与 package_preview 绑定、负责人
#        orchestrator:confirm-package:<project> 权限，生成确认摘要；
#     ② resume：校验确认摘要、注册表状态与事件摘要一致性后，才调用
#        US-5 构建加密包并回读校验，成功写 TERMINAL，失败写 ESCALATED。
#   关键安全不变量：包只能由已确认且摘要可验证的会话生成；事件/确认/
#   包摘要三者绑定存储，防止跳过确认或篡改中间结果。
from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass

from src.coevo.timefmt import is_iso_utc_z
from typing import Any, Mapping

from src.coevo.identity.models import Actor
from src.coevo.identity.service import Authorizer, UnauthorizedError
from src.coevo.talent.models import TalentPool
from src.coevo.talent.recommender import TaskRequirement
from src.coevo.talent.service import TalentRecommenderService
from src.coevo.task_decomposition.service import TaskDecompositionService
from src.coevo.task_flow.service import FlowUnderstandingService

from .real_chain_store import RealChainStore, RealChainStoreError, canonical_digest


REAL_EXECUTION_MODE = "real_fixed_chain"
_AGENTS = (
    "agent.task_flow_understanding",
    "agent.task_decomposition",
    "agent.team_recommendation",
    "",
    "agent.task_package_build",
)


@dataclass(frozen=True)
class RealChainExecutor:
    flow_service: FlowUnderstandingService
    decomp_service: TaskDecompositionService
    talent_service: TalentRecommenderService
    talent_pool: TalentPool

    def __post_init__(self) -> None:
        checks = (
            (self.flow_service, FlowUnderstandingService, "flow_service"),
            (self.decomp_service, TaskDecompositionService, "decomp_service"),
            (self.talent_service, TalentRecommenderService, "talent_service"),
            (self.talent_pool, TalentPool, "talent_pool"),
        )
        for value, expected, name in checks:
            if not isinstance(value, expected):
                raise TypeError(f"{name} must be {expected.__name__}")


@dataclass(frozen=True)
class PackagePreview:
    event_id: str
    project_id: str
    task_id: str
    base_revision: str
    project_input_digest: str
    recipient_cert_id: str
    sender_cert_id: str
    package_type: str
    payload_digest: str

    def __post_init__(self) -> None:
        for name in ("event_id", "project_id", "task_id", "base_revision",
                     "recipient_cert_id", "sender_cert_id", "package_type"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("project_input_digest", "payload_digest"):
            value = getattr(self, name)
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError(f"{name} must be a lowercase SHA-256 digest")


@dataclass(frozen=True)
class RealChainOutcome:
    chain_id: str
    event_id: str
    workspace_project_id: str
    flow_understanding_summary: tuple[str, ...]
    baseline_summary: tuple[str, ...]
    recommendation_summary: tuple[str, ...]
    package_summary: tuple[str, ...]
    orch_report: Any
    event_digest: str
    project_input_digest: str
    confirmation_digest: str = ""
    package_preview: PackagePreview | None = None
    store_id: str = ""


def _event_and_project_digests(event: Any, project_input: Mapping[str, Any]) -> tuple[str, str, PackagePreview]:
    from . import OrchestratorValidationError

    if not isinstance(project_input, dict):
        raise OrchestratorValidationError("project_input must be a JSON object")
    required = (
        "schema_version", "base_revision", "project_id", "task_id",
        "recipient_cert_id", "sender_cert_id", "package_type", "payload_digest",
    )
    for key in required:
        if not isinstance(project_input.get(key), str) or not project_input[key]:
            raise OrchestratorValidationError(f"project_input.{key} must be a non-empty string")
    try:
        project_digest = canonical_digest(project_input)
        event_digest = canonical_digest({
            "event_id": event.event_id,
            "kind": event.kind.value,
            "project_id": event.project_id,
            "task_id": event.task_id,
            "payload": event.payload,
            "triggered_at": event.triggered_at,
        })
    except RealChainStoreError as exc:
        raise OrchestratorValidationError(str(exc)) from exc
    expected_payload = {
        "schema_version": project_input["schema_version"],
        "base_revision": project_input["base_revision"],
        "project_input_digest": project_digest,
    }
    if event.payload != expected_payload:
        raise OrchestratorValidationError(
            "event.payload must exactly bind schema_version, base_revision and project_input_digest"
        )
    if project_input["project_id"] != event.project_id or project_input["task_id"] != event.task_id:
        raise OrchestratorValidationError("project_input project/task binding does not match event")
    try:
        preview = PackagePreview(
            event.event_id, event.project_id, event.task_id,
            project_input["base_revision"], project_digest,
            project_input["recipient_cert_id"], project_input["sender_cert_id"],
            project_input["package_type"], project_input["payload_digest"],
        )
    except ValueError as exc:
        raise OrchestratorValidationError(str(exc)) from exc
    return event_digest, project_digest, preview


def _validate_fixed_chain(registry: Any, chain: Any) -> None:
    from . import (
        AgentCapability, FailurePolicy, OrchestrationStepKind, OrchestratorValidationError,
    )
    expected_kinds = (
        OrchestrationStepKind.AGENT_CALL,
        OrchestrationStepKind.AGENT_CALL,
        OrchestrationStepKind.AGENT_CALL,
        OrchestrationStepKind.HUMAN_CONFIRM,
        OrchestrationStepKind.AGENT_CALL,
    )
    expected_capabilities = (
        AgentCapability.TASK_FLOW_UNDERSTANDING,
        AgentCapability.TASK_DECOMPOSITION,
        AgentCapability.TEAM_RECOMMENDATION,
        None,
        AgentCapability.TASK_PACKAGE_BUILD,
    )
    if len(chain.steps) != 5:
        raise OrchestratorValidationError("real chain must contain exactly five steps")
    for index, step in enumerate(chain.steps):
        if step.step_index != index or step.kind != expected_kinds[index] or step.agent_id != _AGENTS[index]:
            raise OrchestratorValidationError(f"real chain step {index} does not match the fixed chain")
        if step.on_failure == FailurePolicy.SKIP:
            raise OrchestratorValidationError("fixed-chain steps may not use SKIP")
        expected_confirmation = index == 3
        if step.requires_human_confirmation != expected_confirmation:
            raise OrchestratorValidationError(f"real chain step {index} confirmation flag is invalid")
        if registry is not None and expected_capabilities[index] is not None:
            registration = registry.get(step.agent_id)
            if registration is None or registration.spec.capability != expected_capabilities[index]:
                raise OrchestratorValidationError(f"real chain agent capability mismatch at step {index}")
            if registration.spec.requires_human_confirmation:
                raise OrchestratorValidationError(
                    "fixed-chain agent registrations may not add an earlier confirmation gate"
                )


def _trace(event_id: str, step: Any, result: Any, now: str, detail: str,
           *, confirmed_by: str = "") -> Any:
    from . import OrchestrationTrace
    return OrchestrationTrace(
        trace_id=f"tr.{event_id}.s{step.step_index}.real",
        step_index=step.step_index,
        agent_id=step.agent_id,
        result=result,
        requires_human_confirmation=step.requires_human_confirmation,
        confirmed_by=confirmed_by,
        detail=detail,
        recorded_at=now,
    )


def _report(chain: Any, event: Any, workspace: Any, traces: list[Any], outcome: Any, now: str) -> Any:
    from . import OrchestrationReport
    return OrchestrationReport(
        trace_id=f"rpt.{event.event_id}.{chain.chain_id}",
        chain_id=chain.chain_id,
        event_id=event.event_id,
        workspace_project_id=workspace.project_id,
        outcome=outcome,
        trace=tuple(traces),
        completed_at=now,
        execution_mode=REAL_EXECUTION_MODE,
    )


def _outcome(chain: Any, event: Any, workspace: Any, report: Any,
             summaries: dict[str, list[str]], event_digest: str,
             project_digest: str, confirmation_digest: str = "",
             package_preview: PackagePreview | None = None,
             store_id: str = "") -> RealChainOutcome:
    return RealChainOutcome(
        chain.chain_id, event.event_id, workspace.project_id,
        tuple(summaries["flow"]), tuple(summaries["baseline"]),
        tuple(summaries["talent"]), tuple(summaries["package"]), report,
        event_digest, project_digest, confirmation_digest, package_preview, store_id,
    )


def _finish_dispatch_terminal(chain: Any, event: Any, workspace: Any, traces: list[Any],
                              outcome: Any, summaries: dict[str, list[str]],
                              event_digest: str, project_digest: str,
                              package_preview: PackagePreview | None,
                              store: RealChainStore, now: str,
                              result_label: str = "TERMINAL") -> RealChainOutcome:
    """Build the terminal report/outcome, seal the dispatch and return it."""
    report = _report(chain, event, workspace, traces, outcome, now)
    result = _outcome(chain, event, workspace, report, summaries, event_digest,
                      project_digest, package_preview=package_preview,
                      store_id=store.store_id)
    store.finish_dispatch(event.event_id, event_digest, result, result_label, now)
    return result


def _escalate_and_finish(
    chain: Any, event: Any, workspace: Any, traces: list[Any],
    summaries: dict[str, list[str]], event_digest: str, project_digest: str,
    package_preview: PackagePreview | None, store: RealChainStore, now: str,
    step: Any, detail: str,
) -> RealChainOutcome:
    """Append an ESCALATED trace and finish the dispatch as ESCALATED.

    Consolidates the repeated failure paths in ``dispatch_real_chain``
    (FRAMEWORK-OPTIMIZE-7): agent unavailable / facade failed / retry failed.
    """

    from . import OrchestrationOutcome, OrchestrationStepResult

    traces.append(
        _trace(
            event.event_id, step, OrchestrationStepResult.ESCALATED, now, detail
        )
    )
    return _finish_dispatch_terminal(
        chain, event, workspace, traces, OrchestrationOutcome.ESCALATED,
        summaries, event_digest, project_digest, package_preview, store, now,
    )


def project_baseline_to_requirements(baseline: Any) -> tuple[TaskRequirement, ...]:
    from src.coevo.talent.models import AvailabilityWindow
    return tuple(
        TaskRequirement(
            task_type=f"task.{task.task_id}",
            required_skill_tags=(task.responsible_role,),
            required_credentials=(),
            window=AvailabilityWindow(baseline.plan_start, baseline.plan_end),
        )
        for work_package in baseline.work_packages for task in work_package.tasks
    )


def dispatch_real_chain(registry: Any, chain: Any, event: Any, *, workspace: Any,
                        executor: RealChainExecutor, project_input: Mapping[str, Any],
                        store: RealChainStore, now: str) -> RealChainOutcome:
    """Call US-1/2/3 and atomically hold before US-5."""
    from . import (
        AgentStatus, FailurePolicy, OrchestrationOutcome, OrchestrationStepResult,
        Orchestrator, OrchestratorValidationError,
    )
    from src.coevo.task_decomposition.baseline import build_baseline

    Orchestrator.dispatch_event(registry, chain, event, workspace=workspace, now=now)
    if not isinstance(executor, RealChainExecutor) or not isinstance(store, RealChainStore):
        raise OrchestratorValidationError("executor/store type is invalid")
    _validate_fixed_chain(registry, chain)
    event_digest, project_digest, package_preview = _event_and_project_digests(event, project_input)
    if project_input["base_revision"] != workspace.revision:
        raise OrchestratorValidationError(
            "project_input.base_revision must match workspace.revision"
        )
    try:
        cached = store.begin_dispatch(event.event_id, event_digest, event.project_id, now)
    except RealChainStoreError as exc:
        raise OrchestratorValidationError(str(exc)) from exc
    if cached is not None:
        return cached

    traces: list[Any] = []
    outputs: dict[int, Any] = {}
    summaries = {"flow": [], "baseline": [], "talent": [], "package": []}

    def invoke(index: int) -> Any:
        if index == 0:
            raw = dict(project_input)
            raw["format"] = "canonical"
            return executor.flow_service.understand(raw)
        if index == 1:
            return build_baseline(executor.decomp_service.propose(outputs[0], project_input))
        requirements = project_baseline_to_requirements(outputs[1])
        return executor.talent_service.recommend_for_requirements(executor.talent_pool, requirements)

    for step in chain.steps[:3]:
        registration = registry.get(step.agent_id)
        if registration.status != AgentStatus.AVAILABLE:
            return _escalate_and_finish(
                chain, event, workspace, traces, summaries,
                event_digest, project_digest, package_preview, store, now,
                step, "agent unavailable; human escalation required",
            )
        store.record_attempt(event.event_id, event_digest, f"facade.{step.step_index}", "attempt", now)
        try:
            output = invoke(step.step_index)
            trace_result = OrchestrationStepResult.OK
            store.record_attempt(event.event_id, event_digest, f"facade.{step.step_index}", "success", now)
        except Exception:
            store.record_attempt(event.event_id, event_digest, f"facade.{step.step_index}", "failure", now)
            if step.on_failure != FailurePolicy.RETRY:
                return _escalate_and_finish(
                    chain, event, workspace, traces, summaries,
                    event_digest, project_digest, package_preview, store, now,
                    step, "facade failed; human escalation required",
                )
            store.record_attempt(event.event_id, event_digest, f"facade.{step.step_index}", "retry_attempt", now)
            try:
                output = invoke(step.step_index)
                trace_result = OrchestrationStepResult.RETRIED
                store.record_attempt(event.event_id, event_digest, f"facade.{step.step_index}", "retry_success", now)
            except Exception:
                store.record_attempt(event.event_id, event_digest, f"facade.{step.step_index}", "retry_failure", now)
                return _escalate_and_finish(
                    chain, event, workspace, traces, summaries,
                    event_digest, project_digest, package_preview, store, now,
                    step, "facade retry failed; human escalation required",
                )
        outputs[step.step_index] = output
        if step.step_index == 0:
            summaries["flow"].append(f"step0:unit={output.flow.unit_id};version={output.flow.version};stages={len(output.flow.stages)}")
        elif step.step_index == 1:
            summaries["baseline"].append(f"step1:project={output.project_id};version={output.version};packages={len(output.work_packages)}")
        else:
            summaries["talent"].append(f"step2:recommendations={len(output)}")
        traces.append(_trace(event.event_id, step, trace_result, now, "real facade completed"))

    traces.append(_trace(event.event_id, chain.steps[3], OrchestrationStepResult.HELD_AT_CONFIRM,
                         now, "explicit human confirmation required before package build"))
    return _finish_dispatch_terminal(
        chain, event, workspace, traces, OrchestrationOutcome.HELD_AT_CONFIRM,
        summaries, event_digest, project_digest, package_preview, store, now,
        result_label="HELD",
    )


def confirm_real_chain(held: RealChainOutcome, *, preview: PackagePreview,
                       actor: Actor, authorizer: Authorizer,
                       store: RealChainStore, now: str) -> RealChainOutcome:
    """Confirm the stored hold but remain pending package generation."""
    from . import (
        OrchestrationOutcome, OrchestrationReport, OrchestrationStepResult,
        OrchestrationTrace, OrchestratorValidationError, _SAFE_ID,
    )
    if (not isinstance(held, RealChainOutcome) or held.orch_report.execution_mode != REAL_EXECUTION_MODE
            or held.orch_report.outcome != OrchestrationOutcome.HELD_AT_CONFIRM):
        raise OrchestratorValidationError("confirm_real_chain requires a protected held outcome")
    actor_id = getattr(actor, "actor_id", None)
    if not isinstance(actor, Actor) or not isinstance(actor_id, str) or not _SAFE_ID.match(actor_id):
        raise OrchestratorValidationError("actor must carry a safe actor_id")
    if not callable(getattr(authorizer, "is_allowed", None)):
        raise OrchestratorValidationError("authorizer must implement is_allowed")
    if not is_iso_utc_z(now):
        raise OrchestratorValidationError("now must be ISO-8601 UTC Z")
    if not isinstance(preview, PackagePreview) or preview != held.package_preview:
        raise OrchestratorValidationError("package preview does not match held context")
    if not held.store_id or held.store_id != store.store_id:
        raise OrchestratorValidationError("held outcome belongs to a different store")
    try:
        if store.held_outcome(held.event_id, held.event_digest) != held:
            raise OrchestratorValidationError("held outcome does not match stored state")
    except RealChainStoreError as exc:
        raise OrchestratorValidationError(str(exc)) from exc
    permission = f"orchestrator:confirm-package:{held.workspace_project_id}"
    if not authorizer.is_allowed(actor_id, permission):
        store.record_authorization_rejection(
            held.event_id, held.event_digest, "confirmation_authorization",
            actor_id, permission, now,
        )
        raise UnauthorizedError(permission + " permission is required")
    confirmation_digest = canonical_digest({
        "event_digest": held.event_digest,
        "held_report_id": held.orch_report.trace_id,
        "actor_id": actor_id,
        "package_preview": dataclasses.asdict(preview),
        "store_id": held.store_id,
    })

    def build() -> RealChainOutcome:
        prior = held.orch_report.trace[-1]
        confirmed = OrchestrationTrace(
            prior.trace_id, prior.step_index, prior.agent_id, OrchestrationStepResult.OK,
            True, actor_id, "confirmed by authorized human; package build pending", now,
        )
        report = OrchestrationReport(
            held.orch_report.trace_id, held.chain_id, held.event_id,
            held.workspace_project_id, OrchestrationOutcome.CONFIRMED_PENDING_PACKAGE,
            held.orch_report.trace[:-1] + (confirmed,), now, REAL_EXECUTION_MODE,
        )
        return RealChainOutcome(
            held.chain_id, held.event_id, held.workspace_project_id,
            held.flow_understanding_summary, held.baseline_summary,
            held.recommendation_summary, (), report, held.event_digest,
            held.project_input_digest, confirmation_digest, preview, held.store_id,
        )
    try:
        return store.confirm(held.event_id, held.event_digest, confirmation_digest, build, now)
    except RealChainStoreError as exc:
        raise OrchestratorValidationError(str(exc)) from exc


def resume_real_chain(confirmed: RealChainOutcome, *, registry: Any, chain: Any, event: Any,
                      workspace: Any, executor: RealChainExecutor,
                      store: RealChainStore, now: str, crypto_provider: Any | None = None,
                      sender_handle: Any | None = None,
                      recipient_handle: Any | None = None) -> RealChainOutcome:
    """Build the US-5 package only after the stored confirmation is validated."""
    from . import (
        FailurePolicy, OrchestrationOutcome, OrchestrationStepResult,
        OrchestratorValidationError,
    )
    if (not isinstance(confirmed, RealChainOutcome)
            or confirmed.orch_report.outcome != OrchestrationOutcome.CONFIRMED_PENDING_PACKAGE
            or not confirmed.confirmation_digest):
        raise OrchestratorValidationError("resume requires CONFIRMED_PENDING_PACKAGE outcome")
    if not confirmed.store_id or confirmed.store_id != store.store_id:
        raise OrchestratorValidationError("confirmed outcome belongs to a different store")
    _validate_fixed_chain(registry, chain)
    if not isinstance(executor, RealChainExecutor) or not isinstance(store, RealChainStore):
        raise OrchestratorValidationError("executor/store type is invalid")
    if not is_iso_utc_z(now):
        raise OrchestratorValidationError("now must be ISO-8601 UTC Z")
    if (chain.chain_id != confirmed.chain_id or event.event_id != confirmed.event_id
            or workspace.project_id != confirmed.workspace_project_id):
        raise OrchestratorValidationError("resume context does not match confirmed outcome")
    if event.payload.get("base_revision") != workspace.revision:
        raise OrchestratorValidationError(
            "resume workspace revision does not match confirmed base_revision"
        )
    try:
        current_event_digest = canonical_digest({
            "event_id": event.event_id,
            "kind": event.kind.value,
            "project_id": event.project_id,
            "task_id": event.task_id,
            "payload": event.payload,
            "triggered_at": event.triggered_at,
        })
        if current_event_digest != confirmed.event_digest:
            raise OrchestratorValidationError("resume event digest does not match confirmed outcome")
        if store.confirmed_outcome(confirmed.event_id, confirmed.event_digest) != confirmed:
            raise OrchestratorValidationError("confirmed outcome does not match stored state")
    except RealChainStoreError as exc:
        raise OrchestratorValidationError(str(exc)) from exc
    registration = registry.get(chain.steps[4].agent_id)
    from . import AgentCapability, AgentStatus
    if (registration is None
            or registration.spec.capability != AgentCapability.TASK_PACKAGE_BUILD
            or registration.status != AgentStatus.AVAILABLE):
        store.record_attempt(confirmed.event_id, confirmed.event_digest,
                             "resume", "package_agent_unavailable", now)
        raise OrchestratorValidationError("step 4 package agent must be registered and AVAILABLE")
    if confirmed.package_preview is None:
        raise OrchestratorValidationError("confirmed outcome is missing package preview")
    resume_digest = canonical_digest({
        "event_digest": confirmed.event_digest,
        "confirmation_digest": confirmed.confirmation_digest,
        "chain_id": confirmed.chain_id,
        "package_preview": dataclasses.asdict(confirmed.package_preview),
    })
    try:
        store.begin_resume(confirmed.event_id, confirmed.event_digest, resume_digest, now)
    except RealChainStoreError as exc:
        raise OrchestratorValidationError(str(exc)) from exc

    traces = list(confirmed.orch_report.trace)
    summaries = {
        "flow": list(confirmed.flow_understanding_summary),
        "baseline": list(confirmed.baseline_summary),
        "talent": list(confirmed.recommendation_summary),
        "package": [],
    }

    if crypto_provider is not None:
        from src.coevo.protocol import (
            build_encrypted_package, build_envelope_template,
            open_encrypted_package, parse_package_bytes,
        )
        preview = confirmed.package_preview
        try:
            envelope = build_envelope_template(
                sender_cert_id=preview.sender_cert_id,
                recipient_cert_id=preview.recipient_cert_id,
                project_id=preview.project_id,
                package_type=preview.package_type,
                sequence_no=1,
                payload_length=0,
                created_at=now,
            )
            manifest = {
                "event_id": preview.event_id,
                "project_id": preview.project_id,
                "task_id": preview.task_id,
                "base_revision": preview.base_revision,
                "project_input_digest": preview.project_input_digest,
                "payload_digest": preview.payload_digest,
                "confirmation_digest": confirmed.confirmation_digest,
            }
            content = json.dumps(
                {
                    "flow": confirmed.flow_understanding_summary,
                    "baseline": confirmed.baseline_summary,
                    "recommendations": confirmed.recommendation_summary,
                }, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
            package = build_encrypted_package(
                envelope=envelope, manifest=manifest, content=content,
                provider=crypto_provider, sender_handle=sender_handle,
                recipient_handle=recipient_handle, signed_at=now,
            )
            wire = package.to_bytes()
            parsed = parse_package_bytes(wire)
            opened = open_encrypted_package(
                parsed, provider=crypto_provider,
                recipient_handle=recipient_handle, sender_handle=sender_handle,
            )
            if opened.content != content or dict(opened.manifest) != manifest:
                raise ValueError("package round-trip content mismatch")
            wire_digest = hashlib.sha256(wire).hexdigest()
            summaries["package"].append(
                f"step4:package_id={parsed.envelope.package_id};sha256={wire_digest};bytes={len(wire)}"
            )
            traces.append(_trace(event.event_id, chain.steps[4], OrchestrationStepResult.OK,
                                 now, "package encrypted, parsed, opened and verified"))
            report = _report(chain, event, workspace, traces, OrchestrationOutcome.COMPLETED, now)
            result = _outcome(
                chain, event, workspace, report, summaries, confirmed.event_digest,
                confirmed.project_input_digest, confirmed.confirmation_digest,
                confirmed.package_preview, store_id=confirmed.store_id,
            )
            store.finish_resume_success(
                event.event_id, confirmed.event_digest, resume_digest,
                result, wire_digest, now,
            )
            return result
        except Exception as exc:
            code = getattr(exc, "code", "CRYPTO_PACKAGE_VERIFICATION_FAILED")
            traces.append(_trace(event.event_id, chain.steps[4], OrchestrationStepResult.ESCALATED,
                                 now, str(code)))
            report = _report(chain, event, workspace, traces, OrchestrationOutcome.ESCALATED, now)
            result = _outcome(chain, event, workspace, report, summaries, confirmed.event_digest,
                              confirmed.project_input_digest, confirmed.confirmation_digest,
                              confirmed.package_preview, store_id=confirmed.store_id)
            store.finish_resume_failure(
                event.event_id, confirmed.event_digest, resume_digest, result, str(code), now
            )
            return result

    code = "CRYPTO_CAPABILITY_UNAVAILABLE"
    traces.append(_trace(event.event_id, chain.steps[4], OrchestrationStepResult.ESCALATED,
                         now, code))
    report = _report(chain, event, workspace, traces, OrchestrationOutcome.ESCALATED, now)
    result = _outcome(chain, event, workspace, report, summaries, confirmed.event_digest,
                      confirmed.project_input_digest, confirmed.confirmation_digest,
                      confirmed.package_preview, store_id=confirmed.store_id)
    store.finish_resume_failure(
        event.event_id, confirmed.event_digest, resume_digest, result, code, now
    )
    return result


def recover_real_chain(event_id: str, *, actor: Actor, authorizer: Authorizer,
                       store: RealChainStore, now: str) -> Any:
    """Manually terminate an interrupted dispatch/build; never retries work."""
    from src.coevo.timefmt import is_iso_utc_z
    from . import OrchestratorValidationError, _SAFE_ID
    actor_id = getattr(actor, "actor_id", None)
    if not isinstance(actor, Actor) or not isinstance(actor_id, str) or not _SAFE_ID.match(actor_id):
        raise OrchestratorValidationError("actor must carry a safe actor_id")
    if not callable(getattr(authorizer, "is_allowed", None)):
        raise OrchestratorValidationError("authorizer must implement is_allowed")
    if not is_iso_utc_z(now):
        raise OrchestratorValidationError("now must be ISO-8601 UTC Z")
    try:
        context = store.recovery_context(event_id)
        permission = f"orchestrator:recover-package:{context.project_id}"
        if not authorizer.is_allowed(actor_id, permission):
            store.record_authorization_rejection(
                context.event_id, context.event_digest, "recovery_authorization",
                actor_id, permission, now,
            )
            raise UnauthorizedError(permission + " permission is required")
        return store.terminate_recovery(
            event_id, canonical_digest({"actor_id": actor_id}), now
        )
    except RealChainStoreError as exc:
        raise OrchestratorValidationError(str(exc)) from exc
