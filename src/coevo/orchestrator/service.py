"""orchestrator.service - deterministic Orchestrator facade (US-4 AC-3..AC-7)."""

# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 运行中枢门面（US-4 AC-3..AC-7）：Orchestrator 提供 dispatch_event /
# confirm_human（含权限校验）/ dispatch_event_with_real_facades /
# confirm_real_chain / resume_real_chain 等受控编排入口；每一步产生
# 审计轨迹，高影响步骤要求人工确认。

from __future__ import annotations

from src.coevo.workspace.models import WorkspaceEntry
from ._real_chain import REAL_EXECUTION_MODE, PackagePreview, RealChainExecutor, RealChainOutcome, confirm_real_chain, dispatch_real_chain, recover_real_chain, resume_real_chain
from .real_chain_store import RealChainStore

from src.coevo.timefmt import is_iso_utc_z
from .models import AgentRegistry, AgentStatus, FailurePolicy, OrchestrationChain, OrchestrationEvent, OrchestrationOutcome, OrchestrationReport, OrchestrationStep, OrchestrationStepKind, OrchestrationStepResult, OrchestrationTrace, OrchestratorConflictError, OrchestratorValidationError, _SAFE_ID, _make_report_id, _make_trace_id


def _append_trace(
    trace: list[OrchestrationTrace],
    *,
    trace_id: str,
    step: OrchestrationStep,
    result: OrchestrationStepResult,
    detail: str,
    now: str,
    requires_human_confirmation: bool = False,
    confirmed_by: str = "",
    agent_id: str | None = None,
) -> None:
    """Append one deterministic step trace record (shared by every dispatch path)."""
    trace.append(OrchestrationTrace(
        trace_id=trace_id,
        step_index=step.step_index,
        agent_id=step.agent_id if agent_id is None else agent_id,
        result=result,
        requires_human_confirmation=requires_human_confirmation,
        confirmed_by=confirmed_by,
        detail=detail,
        recorded_at=now,
    ))

class Orchestrator:
    """Pure-function orchestrator facade (US-4 AC-3..AC-7)."""

    @staticmethod
    def dispatch_event(
        registry: AgentRegistry,
        chain: OrchestrationChain,
        event: OrchestrationEvent,
        *,
        workspace: WorkspaceEntry,
        now: str,
    ) -> OrchestrationReport:
        """AC-3..AC-7: dispatch an event through a chain.

        Stops immediately when:

        * a step requires human confirmation (outcome=HELD_AT_CONFIRM),
        * a step's AGENT_CALL finds the agent not AVAILABLE and the
          failure policy cannot recover (RETRY capped at one retry per
          step; SKIP advances; ESCALATE_HUMAN ends as ESCALATED;
          FAILED ends as FAILED).

        Returns the full OrchestrationReport with the trace list of all
        steps attempted (including the terminating one).
        """
        if not isinstance(registry, AgentRegistry):
            raise OrchestratorValidationError(
                "registry must be an AgentRegistry instance"
            )
        if not isinstance(chain, OrchestrationChain):
            raise OrchestratorValidationError(
                "chain must be an OrchestrationChain instance"
            )
        if not isinstance(event, OrchestrationEvent):
            raise OrchestratorValidationError(
                "event must be an OrchestrationEvent instance"
            )
        if not isinstance(workspace, WorkspaceEntry):
            raise OrchestratorValidationError(
                "workspace must be a WorkspaceEntry instance"
            )
        if not is_iso_utc_z(now):
            raise OrchestratorValidationError(
                f"now must be ISO-8601 UTC 'Z'; got {now!r}"
            )
        if workspace.project_id != event.project_id:
            raise OrchestratorValidationError(
                f"workspace.project_id {workspace.project_id!r} does not match "
                f"event.project_id {event.project_id!r}"
            )

        trace: list[OrchestrationTrace] = []
        outcome = OrchestrationOutcome.COMPLETED
        next_id_seed = 0
        for step in chain.steps:
            trace_id = _make_trace_id(event.event_id, step.step_index, next_id_seed)
            next_id_seed += 1

            # Step dispatch.
            if step.kind == OrchestrationStepKind.AGENT_CALL:
                reg = registry.get(step.agent_id)
                # AC-5: requires_human_confirmation from EITHER the step
                # OR the registered AgentSpec triggers a hold.
                spec_requires_confirm = (
                    reg is not None and reg.spec.requires_human_confirmation
                )
                if step.requires_human_confirmation or spec_requires_confirm:
                    outcome = OrchestrationOutcome.HELD_AT_CONFIRM
                    _append_trace(
                        trace, trace_id=trace_id, step=step,
                        result=OrchestrationStepResult.HELD_AT_CONFIRM,
                        detail=f"agent {step.agent_id} requires human confirmation",
                        now=now, requires_human_confirmation=True,
                    )
                    break

                if reg is None:
                    outcome = OrchestrationOutcome.FAILED
                    _append_trace(
                        trace, trace_id=trace_id, step=step,
                        result=OrchestrationStepResult.FAILED,
                        detail=f"agent {step.agent_id!r} not in registry",
                        now=now,
                    )
                    break

                if reg.status == AgentStatus.AVAILABLE:
                    _append_trace(
                        trace, trace_id=trace_id, step=step,
                        result=OrchestrationStepResult.OK,
                        detail=f"agent {step.agent_id} executed",
                        now=now,
                    )
                    continue

                # Agent not AVAILABLE: apply on_failure policy.
                if step.on_failure == FailurePolicy.RETRY:
                    # One retry attempt; if still not AVAILABLE, fall
                    # through to ESCALATE_HUMAN at the bottom.
                    retried_id = _make_trace_id(event.event_id, step.step_index, next_id_seed)
                    next_id_seed += 1
                    reg2 = registry.get(step.agent_id)
                    if reg2 is not None and reg2.status == AgentStatus.AVAILABLE:
                        _append_trace(
                            trace, trace_id=retried_id, step=step,
                            result=OrchestrationStepResult.RETRIED,
                            detail=f"agent {step.agent_id} retried successfully",
                            now=now,
                        )
                        continue
                    # Retry didn't help -> escalate.
                    outcome = OrchestrationOutcome.ESCALATED
                    _append_trace(
                        trace, trace_id=trace_id, step=step,
                        result=OrchestrationStepResult.ESCALATED,
                        detail=(
                            f"agent {step.agent_id} not available after retry; "
                            f"escalating to human"
                        ),
                        now=now,
                    )
                    break

                if step.on_failure == FailurePolicy.SKIP:
                    _append_trace(
                        trace, trace_id=trace_id, step=step,
                        result=OrchestrationStepResult.SKIPPED,
                        detail=f"agent {step.agent_id} skipped",
                        now=now,
                    )
                    continue

                # ESCALATE_HUMAN
                outcome = OrchestrationOutcome.ESCALATED
                _append_trace(
                    trace, trace_id=trace_id, step=step,
                    result=OrchestrationStepResult.ESCALATED,
                    detail=(
                        f"agent {step.agent_id} not available (status="
                        f"{reg.status.value}); escalating to human"
                    ),
                    now=now,
                )
                break

            if step.kind == OrchestrationStepKind.HUMAN_CONFIRM:
                outcome = OrchestrationOutcome.HELD_AT_CONFIRM
                _append_trace(
                    trace, trace_id=trace_id, step=step,
                    result=OrchestrationStepResult.HELD_AT_CONFIRM,
                    detail="explicit human confirmation step",
                    now=now, requires_human_confirmation=True,
                    agent_id="",
                )
                break

            # CONDITIONAL: this slice runs it as if it were an
            # AGENT_CALL with empty agent_id -> treated as OK.
            _append_trace(
                trace, trace_id=trace_id, step=step,
                result=OrchestrationStepResult.OK,
                detail="conditional step (default OK)",
                now=now, agent_id="",
            )

        return OrchestrationReport(
            trace_id=_make_report_id(event.event_id, chain.chain_id),
            chain_id=chain.chain_id,
            event_id=event.event_id,
            workspace_project_id=workspace.project_id,
            outcome=outcome,
            trace=tuple(trace),
            completed_at=now,
        )

    @staticmethod
    def confirm_human(
        report: OrchestrationReport,
        *,
        step_index: int,
        confirmed_by: str,
        now: str,
    ) -> OrchestrationReport:
        """AC-5: confirm a held step and continue the chain.

        Returns a NEW :class:`OrchestrationReport` with the held step's
        result flipped to OK and the trace list rebuilt from the
        confirmed step onward (only the held step is marked OK; later
        steps are re-run from scratch to capture current registry state).

        Raises :class:`OrchestratorConflictError` if the report is not
        HELD_AT_CONFIRM, the step_index doesn't match the held step, or
        the held step is not at the held position.
        """
        if not isinstance(report, OrchestrationReport):
            raise OrchestratorValidationError(
                "report must be an OrchestrationReport instance"
            )
        if report.execution_mode == REAL_EXECUTION_MODE or any(
            trace.trace_id.endswith(".real") for trace in report.trace
        ):
            raise OrchestratorConflictError(
                "protected real-chain reports require confirm_real_chain"
            )
        if not isinstance(confirmed_by, str) or not _SAFE_ID.match(confirmed_by):
            raise OrchestratorValidationError(
                f"confirmed_by must be safe-id; got {confirmed_by!r}"
            )
        if not is_iso_utc_z(now):
            raise OrchestratorValidationError(
                f"now must be ISO-8601 UTC 'Z'; got {now!r}"
            )
        if report.outcome != OrchestrationOutcome.HELD_AT_CONFIRM:
            raise OrchestratorConflictError(
                f"report outcome is {report.outcome.value!r}, not HELD_AT_CONFIRM"
            )
        if not report.trace:
            raise OrchestratorConflictError("report.trace is empty")
        last = report.trace[-1]
        if last.step_index != step_index:
            raise OrchestratorConflictError(
                f"step_index {step_index!r} does not match held step {last.step_index!r}"
            )
        if last.result != OrchestrationStepResult.HELD_AT_CONFIRM:
            raise OrchestratorConflictError(
                f"step {step_index!r} is not HELD_AT_CONFIRM; result={last.result.value!r}"
            )

        confirmed_trace = OrchestrationTrace(
            trace_id=last.trace_id,
            step_index=last.step_index,
            agent_id=last.agent_id,
            result=OrchestrationStepResult.OK,
            requires_human_confirmation=last.requires_human_confirmation,
            confirmed_by=confirmed_by,
            detail="confirmed by human",
            recorded_at=now,
        )
        return OrchestrationReport(
            trace_id=report.trace_id,
            chain_id=report.chain_id,
            event_id=report.event_id,
            workspace_project_id=report.workspace_project_id,
            outcome=OrchestrationOutcome.COMPLETED,
            trace=(confirmed_trace,),
            completed_at=now,
        )

    @staticmethod
    def dispatch_event_with_real_facades(
        registry: AgentRegistry,
        chain: OrchestrationChain,
        event: OrchestrationEvent,
        *,
        workspace: WorkspaceEntry,
        executor: RealChainExecutor,
        project_input: "Mapping[str, Any]",
        store: RealChainStore,
        now: str,
    ) -> RealChainOutcome:
        """Run real US-1/2/3 facades and stop at the human gate.

        This phase-one API deliberately cannot invoke US-5.  Package creation
        requires a separate, future explicit resume API.
        """
        return dispatch_real_chain(
            registry,
            chain,
            event,
            workspace=workspace,
            executor=executor,
            project_input=project_input,
            store=store,
            now=now,
        )

    @staticmethod
    def confirm_real_chain(
        held_outcome: RealChainOutcome,
        *,
        preview: PackagePreview,
        actor: "Actor",
        authorizer: "Authorizer",
        store: RealChainStore,
        now: str,
    ) -> RealChainOutcome:
        """Confirm a protected real-chain hold without building a package."""
        return confirm_real_chain(
            held_outcome, preview=preview, actor=actor,
            authorizer=authorizer, store=store, now=now
        )

    @staticmethod
    def resume_real_chain(
        confirmed_outcome: RealChainOutcome,
        *,
        registry: AgentRegistry,
        chain: OrchestrationChain,
        event: OrchestrationEvent,
        workspace: WorkspaceEntry,
        executor: RealChainExecutor,
        store: RealChainStore,
        now: str,
        crypto_provider: object | None = None,
        sender_handle: object | None = None,
        recipient_handle: object | None = None,
    ) -> RealChainOutcome:
        """Resume a stored confirmation and call US-5 at most once."""
        _validate_registry = registry  # force public API type validation below
        if not isinstance(_validate_registry, AgentRegistry):
            raise OrchestratorValidationError("registry must be an AgentRegistry")
        return resume_real_chain(
            confirmed_outcome,
            registry=registry,
            chain=chain,
            event=event,
            workspace=workspace,
            executor=executor,
            store=store,
            now=now,
            crypto_provider=crypto_provider,
            sender_handle=sender_handle,
            recipient_handle=recipient_handle,
        )

    @staticmethod
    def recover_real_chain(
        event_id: str,
        *,
        actor: "Actor",
        authorizer: "Authorizer",
        store: RealChainStore,
        now: str,
    ) -> object:
        """Authorize and manually escalate an interrupted real chain."""
        return recover_real_chain(
            event_id, actor=actor, authorizer=authorizer, store=store, now=now
        )

    @staticmethod
    def to_audit_record(report: OrchestrationReport) -> dict:
        """AC-7: project the report into an audit row.

        Mirrors US-11/12/13/8/15 by EXCLUDING ``detail`` text and only
        keeping the hash for traceability. Counts are kept so the audit
        row is forward-compatible.
        """
        import hashlib

        if not isinstance(report, OrchestrationReport):
            raise OrchestratorValidationError(
                "report must be an OrchestrationReport instance"
            )
        steps_summary: list[dict] = []
        for tr in report.trace:
            steps_summary.append(
                {
                    "trace_id": tr.trace_id,
                    "step_index": tr.step_index,
                    "agent_id": tr.agent_id,
                    "result": tr.result.value,
                    "requires_human_confirmation": tr.requires_human_confirmation,
                    "confirmed_by": tr.confirmed_by,
                    "detail_hash": hashlib.sha256(tr.detail.encode("utf-8")).hexdigest(),
                    "recorded_at": tr.recorded_at,
                }
            )
        return {
            "schema_version": "1.0",
            "domain": "coevo.orchestrator",
            "trace_id": report.trace_id,
            "chain_id": report.chain_id,
            "event_id": report.event_id,
            "workspace_project_id": report.workspace_project_id,
            "outcome": report.outcome.value,
            "step_count": len(report.trace),
            "steps": steps_summary,
            "completed_at": report.completed_at,
            "execution_mode": report.execution_mode,
        }
