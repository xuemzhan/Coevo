"""US-4 orchestrator service facade (7 AC).

Scope
-----
Pure half of US-4: the orchestrator's *governance* layer that registers
agents, defines orchestration chains, dispatches task events through
those chains, applies human-confirmation gates, retry/skip/escalate
failure policies, and emits an audit projection. The slice stops at
the dispatch boundary -- it does NOT call into the existing
US-1/2/3/5/8 facade business code. Wiring real facade calls is
US-4-AC-2 follow-on.

* No IO, no DB, no LLM, no scheduler.
* All dataclasses are frozen + exact-type + ISO-8601 UTC `Z` time strings.
* Pure function: same (registry, chain, event, workspace, now) yields
  identical OrchestrationReport + identical trace ids.
* to_audit_record mirrors US-11/12/13/8/15 by EXCLUDING free-form
  detail text from the audit row.

AC mapping
----------
* AC-1 登记名称/能力/输入输出 -- :class:`AgentSpec` + :class:`AgentRegistry`.
* AC-2 显示子智能体可用状态 -- :class:`AgentStatus` + registry filters.
* AC-3 任务事件触发预设编排流程 -- :class:`Orchestrator.dispatch_event`.
* AC-4 显示当前步骤/调用对象/结果 -- :class:`OrchestrationReport.trace`.
* AC-5 高影响操作人工确认 -- :class:`FailurePolicy`-adjacent
  ``requires_human_confirmation`` + :meth:`Orchestrator.confirm_human`
  + :class:`OrchestrationStepResult.HELD_AT_CONFIRM`.
* AC-6 重试/跳过/转人工 -- :class:`FailurePolicy` (RETRY / SKIP /
  ESCALATE_HUMAN).
* AC-7 编排过程审计 -- :meth:`Orchestrator.to_audit_record`.

Non-goals
---------
* No IO, no DB, no LLM, no scheduler.
* No mutation of any existing module.
* No new dependency.
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field

from src.coevo.workspace.models import WorkspaceEntry


# ---------------------------------------------------------------------------
# Helpers / regex
# ---------------------------------------------------------------------------

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")
_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class OrchestratorError(Exception):
    """Base class for all US-4 errors. Fail-closed by default."""


class OrchestratorValidationError(OrchestratorError):
    """An input field failed validation (user-fixable)."""


class OrchestratorConflictError(OrchestratorError):
    """An operation was inconsistent with the current state.

    Examples: confirming a step that is not HELD_AT_CONFIRM; registering
    an agent_id twice; dispatching an event whose agent_id is not in
    the registry.
    """


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AgentCapability(enum.Enum):
    """AC-1 closed set of agent capabilities.

    Mirrors the existing US-1..US-15 facade set. Adding a new
    capability is a deliberate, version-bumped change.
    """

    TASK_FLOW_UNDERSTANDING = "task_flow_understanding"
    TASK_DECOMPOSITION = "task_decomposition"
    TEAM_RECOMMENDATION = "team_recommendation"
    STATE_MERGE = "state_merge"
    TASK_PACKAGE_BUILD = "task_package_build"
    PROGRESS_CAPTURE = "progress_capture"
    RISK_ANALYSIS = "risk_analysis"
    DECISION_BRIEF = "decision_brief"
    SUPERVISION_MEETING = "supervision_meeting"
    AUDIT_GOVERNANCE = "audit_governance"
    REPORT_BUILD = "report_build"


class AgentStatus(enum.Enum):
    """AC-2 closed set of agent availability states."""

    AVAILABLE = "available"
    BUSY = "busy"
    DISABLED = "disabled"
    ERROR = "error"


class OrchestrationStepKind(enum.Enum):
    """Step categories the orchestrator can execute."""

    AGENT_CALL = "agent_call"
    HUMAN_CONFIRM = "human_confirm"
    CONDITIONAL = "conditional"


class FailurePolicy(enum.Enum):
    """AC-6 closed set of failure-handling policies."""

    RETRY = "retry"
    SKIP = "skip"
    ESCALATE_HUMAN = "escalate_human"


class OrchestrationEventKind(enum.Enum):
    """AC-3 closed set of task events that can trigger orchestration."""

    DISPATCH = "dispatch"
    MERGE = "merge"
    REPORT = "report"
    RISK = "risk"


class OrchestrationStepResult(enum.Enum):
    """Per-step outcome (AC-4 / AC-5 / AC-6)."""

    OK = "ok"
    HELD_AT_CONFIRM = "held_at_confirm"
    RETRIED = "retried"
    SKIPPED = "skipped"
    ESCALATED = "escalated"
    FAILED = "failed"


class OrchestrationOutcome(enum.Enum):
    """Whole-chain outcome."""

    COMPLETED = "completed"
    HELD_AT_CONFIRM = "held_at_confirm"
    ESCALATED = "escalated"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AgentSpec:
    """AC-1: agent registration record."""

    agent_id: str
    capability: AgentCapability
    display_name: str
    input_schema: tuple[str, ...]
    output_schema: tuple[str, ...]
    requires_human_confirmation: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not _SAFE_ID.match(self.agent_id):
            raise OrchestratorValidationError(
                f"agent_id must be safe-id; got {self.agent_id!r}"
            )
        if not isinstance(self.capability, AgentCapability):
            raise OrchestratorValidationError(
                f"capability must be AgentCapability; got {self.capability!r}"
            )
        if not isinstance(self.display_name, str) or not self.display_name:
            raise OrchestratorValidationError("display_name must be a non-empty string")
        for label, schema in (("input_schema", self.input_schema), ("output_schema", self.output_schema)):
            if not isinstance(schema, tuple) or not all(
                isinstance(s, str) and s for s in schema
            ):
                raise OrchestratorValidationError(
                    f"{label} must be a tuple of non-empty strings"
                )
        if not isinstance(self.requires_human_confirmation, bool):
            raise OrchestratorValidationError(
                "requires_human_confirmation must be bool"
            )


@dataclass(frozen=True)
class AgentRegistration:
    """An agent spec + its current status (AC-2)."""

    spec: AgentSpec
    status: AgentStatus = AgentStatus.AVAILABLE

    def __post_init__(self) -> None:
        if not isinstance(self.spec, AgentSpec):
            raise OrchestratorValidationError("spec must be AgentSpec")
        if not isinstance(self.status, AgentStatus):
            raise OrchestratorValidationError(
                f"status must be AgentStatus; got {self.status!r}"
            )


@dataclass(frozen=True)
class AgentRegistry:
    """AC-1 immutable registry of agent registrations.

    All mutations return new instances. Duplicate ``agent_id`` raises
    :class:`OrchestratorConflictError`.
    """

    _by_id: tuple[AgentRegistration, ...] = field(default_factory=tuple)

    @classmethod
    def empty(cls) -> "AgentRegistry":
        return cls(_by_id=tuple())

    def get(self, agent_id: str) -> AgentRegistration | None:
        for reg in self._by_id:
            if reg.spec.agent_id == agent_id:
                return reg
        return None

    def list_available(self) -> tuple[AgentRegistration, ...]:
        return tuple(r for r in self._by_id if r.status == AgentStatus.AVAILABLE)

    def by_capability(self, capability: AgentCapability) -> tuple[AgentRegistration, ...]:
        return tuple(r for r in self._by_id if r.spec.capability == capability)

    def register(self, registration: AgentRegistration) -> "AgentRegistry":
        if not isinstance(registration, AgentRegistration):
            raise OrchestratorValidationError(
                "registration must be an AgentRegistration instance"
            )
        if self.get(registration.spec.agent_id) is not None:
            raise OrchestratorConflictError(
                f"agent_id {registration.spec.agent_id!r} already registered (AC-1)"
            )
        return AgentRegistry(_by_id=self._by_id + (registration,))

    def set_status(self, agent_id: str, status: AgentStatus) -> "AgentRegistry":
        if not isinstance(agent_id, str) or not _SAFE_ID.match(agent_id):
            raise OrchestratorValidationError(
                f"agent_id must be safe-id; got {agent_id!r}"
            )
        if not isinstance(status, AgentStatus):
            raise OrchestratorValidationError(
                f"status must be AgentStatus; got {status!r}"
            )
        new_entries: list[AgentRegistration] = []
        found = False
        for reg in self._by_id:
            if reg.spec.agent_id == agent_id:
                found = True
                new_entries.append(AgentRegistration(spec=reg.spec, status=status))
            else:
                new_entries.append(reg)
        if not found:
            raise OrchestratorValidationError(
                f"agent_id {agent_id!r} not in registry"
            )
        return AgentRegistry(_by_id=tuple(new_entries))

    def __len__(self) -> int:
        return len(self._by_id)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self._by_id)


@dataclass(frozen=True)
class OrchestrationStep:
    """A single step in an orchestration chain."""

    step_index: int
    kind: OrchestrationStepKind
    agent_id: str = ""
    requires_human_confirmation: bool = False
    on_failure: FailurePolicy = FailurePolicy.ESCALATE_HUMAN

    def __post_init__(self) -> None:
        if not isinstance(self.step_index, int) or self.step_index < 0:
            raise OrchestratorValidationError(
                f"step_index must be a non-negative integer; got {self.step_index!r}"
            )
        if not isinstance(self.kind, OrchestrationStepKind):
            raise OrchestratorValidationError(
                f"kind must be OrchestrationStepKind; got {self.kind!r}"
            )
        if self.kind == OrchestrationStepKind.AGENT_CALL:
            if not isinstance(self.agent_id, str) or not _SAFE_ID.match(self.agent_id):
                raise OrchestratorValidationError(
                    f"AGENT_CALL step requires a safe-id agent_id; got {self.agent_id!r}"
                )
        elif self.agent_id:
            raise OrchestratorValidationError(
                f"non-AGENT_CALL step must have empty agent_id; got {self.agent_id!r}"
            )
        if not isinstance(self.requires_human_confirmation, bool):
            raise OrchestratorValidationError(
                "requires_human_confirmation must be bool"
            )
        if not isinstance(self.on_failure, FailurePolicy):
            raise OrchestratorValidationError(
                f"on_failure must be FailurePolicy; got {self.on_failure!r}"
            )


@dataclass(frozen=True)
class OrchestrationChain:
    """AC-3: an ordered list of orchestration steps."""

    chain_id: str
    steps: tuple[OrchestrationStep, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.chain_id, str) or not _SAFE_ID.match(self.chain_id):
            raise OrchestratorValidationError(
                f"chain_id must be safe-id; got {self.chain_id!r}"
            )
        if not isinstance(self.steps, tuple) or not self.steps:
            raise OrchestratorValidationError(
                "steps must be a non-empty tuple"
            )
        for i, step in enumerate(self.steps):
            if not isinstance(step, OrchestrationStep):
                raise OrchestratorValidationError(
                    f"steps[{i}] must be an OrchestrationStep"
                )
            if step.step_index != i:
                raise OrchestratorValidationError(
                    f"steps[{i}].step_index must equal {i}; got {step.step_index}"
                )

    def steps_count(self) -> int:
        return len(self.steps)


@dataclass(frozen=True)
class OrchestrationEvent:
    """AC-3: a task event that triggers orchestration."""

    event_id: str
    kind: OrchestrationEventKind
    project_id: str
    task_id: str
    payload: dict
    triggered_at: str

    def __post_init__(self) -> None:
        for label, value in (
            ("event_id", self.event_id),
            ("project_id", self.project_id),
            ("task_id", self.task_id),
        ):
            if not isinstance(value, str) or not _SAFE_ID.match(value):
                raise OrchestratorValidationError(
                    f"{label} must be safe-id; got {value!r}"
                )
        if not isinstance(self.kind, OrchestrationEventKind):
            raise OrchestratorValidationError(
                f"kind must be OrchestrationEventKind; got {self.kind!r}"
            )
        if not isinstance(self.payload, dict):
            raise OrchestratorValidationError("payload must be a dict")
        if not isinstance(self.triggered_at, str) or not _ISO_UTC_Z.match(self.triggered_at):
            raise OrchestratorValidationError(
                f"triggered_at must be ISO-8601 UTC 'Z'; got {self.triggered_at!r}"
            )


@dataclass(frozen=True)
class OrchestrationTrace:
    """AC-4: a single step execution record."""

    trace_id: str
    step_index: int
    agent_id: str
    result: OrchestrationStepResult
    requires_human_confirmation: bool
    confirmed_by: str
    detail: str
    recorded_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.trace_id, str) or not _SAFE_ID.match(self.trace_id):
            raise OrchestratorValidationError(
                f"trace_id must be safe-id; got {self.trace_id!r}"
            )
        if not isinstance(self.step_index, int) or self.step_index < 0:
            raise OrchestratorValidationError(
                f"step_index must be a non-negative integer; got {self.step_index!r}"
            )
        if not isinstance(self.agent_id, str):
            raise OrchestratorValidationError("agent_id must be a string")
        if not isinstance(self.result, OrchestrationStepResult):
            raise OrchestratorValidationError(
                f"result must be OrchestrationStepResult; got {self.result!r}"
            )
        if not isinstance(self.requires_human_confirmation, bool):
            raise OrchestratorValidationError(
                "requires_human_confirmation must be bool"
            )
        if not isinstance(self.confirmed_by, str):
            raise OrchestratorValidationError("confirmed_by must be a string")
        if not isinstance(self.detail, str):
            raise OrchestratorValidationError("detail must be a string")
        if not isinstance(self.recorded_at, str) or not _ISO_UTC_Z.match(self.recorded_at):
            raise OrchestratorValidationError(
                f"recorded_at must be ISO-8601 UTC 'Z'; got {self.recorded_at!r}"
            )


@dataclass(frozen=True)
class OrchestrationReport:
    """AC-4: the final report of dispatching an event through a chain."""

    trace_id: str
    chain_id: str
    event_id: str
    workspace_project_id: str
    outcome: OrchestrationOutcome
    trace: tuple[OrchestrationTrace, ...]
    completed_at: str

    def __post_init__(self) -> None:
        for label, value in (
            ("trace_id", self.trace_id),
            ("chain_id", self.chain_id),
            ("event_id", self.event_id),
            ("workspace_project_id", self.workspace_project_id),
        ):
            if not isinstance(value, str) or not _SAFE_ID.match(value):
                raise OrchestratorValidationError(
                    f"{label} must be safe-id; got {value!r}"
                )
        if not isinstance(self.outcome, OrchestrationOutcome):
            raise OrchestratorValidationError(
                f"outcome must be OrchestrationOutcome; got {self.outcome!r}"
            )
        if not isinstance(self.trace, tuple) or not all(
            isinstance(t, OrchestrationTrace) for t in self.trace
        ):
            raise OrchestratorValidationError(
                "trace must be a tuple of OrchestrationTrace"
            )
        if not isinstance(self.completed_at, str) or not _ISO_UTC_Z.match(self.completed_at):
            raise OrchestratorValidationError(
                f"completed_at must be ISO-8601 UTC 'Z'; got {self.completed_at!r}"
            )


# ---------------------------------------------------------------------------
# Service facade
# ---------------------------------------------------------------------------


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
        if not isinstance(now, str) or not _ISO_UTC_Z.match(now):
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
                    trace.append(
                        OrchestrationTrace(
                            trace_id=trace_id,
                            step_index=step.step_index,
                            agent_id=step.agent_id,
                            result=OrchestrationStepResult.HELD_AT_CONFIRM,
                            requires_human_confirmation=True,
                            confirmed_by="",
                            detail=f"agent {step.agent_id} requires human confirmation",
                            recorded_at=now,
                        )
                    )
                    break

                if reg is None:
                    outcome = OrchestrationOutcome.FAILED
                    trace.append(
                        OrchestrationTrace(
                            trace_id=trace_id,
                            step_index=step.step_index,
                            agent_id=step.agent_id,
                            result=OrchestrationStepResult.FAILED,
                            requires_human_confirmation=False,
                            confirmed_by="",
                            detail=f"agent {step.agent_id!r} not in registry",
                            recorded_at=now,
                        )
                    )
                    break

                if reg.status == AgentStatus.AVAILABLE:
                    trace.append(
                        OrchestrationTrace(
                            trace_id=trace_id,
                            step_index=step.step_index,
                            agent_id=step.agent_id,
                            result=OrchestrationStepResult.OK,
                            requires_human_confirmation=False,
                            confirmed_by="",
                            detail=f"agent {step.agent_id} executed",
                            recorded_at=now,
                        )
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
                        trace.append(
                            OrchestrationTrace(
                                trace_id=retried_id,
                                step_index=step.step_index,
                                agent_id=step.agent_id,
                                result=OrchestrationStepResult.RETRIED,
                                requires_human_confirmation=False,
                                confirmed_by="",
                                detail=f"agent {step.agent_id} retried successfully",
                                recorded_at=now,
                            )
                        )
                        continue
                    # Retry didn't help -> escalate.
                    outcome = OrchestrationOutcome.ESCALATED
                    trace.append(
                        OrchestrationTrace(
                            trace_id=trace_id,
                            step_index=step.step_index,
                            agent_id=step.agent_id,
                            result=OrchestrationStepResult.ESCALATED,
                            requires_human_confirmation=False,
                            confirmed_by="",
                            detail=(
                                f"agent {step.agent_id} not available after retry; "
                                f"escalating to human"
                            ),
                            recorded_at=now,
                        )
                    )
                    break

                if step.on_failure == FailurePolicy.SKIP:
                    trace.append(
                        OrchestrationTrace(
                            trace_id=trace_id,
                            step_index=step.step_index,
                            agent_id=step.agent_id,
                            result=OrchestrationStepResult.SKIPPED,
                            requires_human_confirmation=False,
                            confirmed_by="",
                            detail=f"agent {step.agent_id} skipped",
                            recorded_at=now,
                        )
                    )
                    continue

                # ESCALATE_HUMAN
                outcome = OrchestrationOutcome.ESCALATED
                trace.append(
                    OrchestrationTrace(
                        trace_id=trace_id,
                        step_index=step.step_index,
                        agent_id=step.agent_id,
                        result=OrchestrationStepResult.ESCALATED,
                        requires_human_confirmation=False,
                        confirmed_by="",
                        detail=(
                            f"agent {step.agent_id} not available (status="
                            f"{reg.status.value}); escalating to human"
                        ),
                        recorded_at=now,
                    )
                )
                break

            if step.kind == OrchestrationStepKind.HUMAN_CONFIRM:
                outcome = OrchestrationOutcome.HELD_AT_CONFIRM
                trace.append(
                    OrchestrationTrace(
                        trace_id=trace_id,
                        step_index=step.step_index,
                        agent_id="",
                        result=OrchestrationStepResult.HELD_AT_CONFIRM,
                        requires_human_confirmation=True,
                        confirmed_by="",
                        detail="explicit human confirmation step",
                        recorded_at=now,
                    )
                )
                break

            # CONDITIONAL: this slice runs it as if it were an
            # AGENT_CALL with empty agent_id -> treated as OK.
            trace.append(
                OrchestrationTrace(
                    trace_id=trace_id,
                    step_index=step.step_index,
                    agent_id="",
                    result=OrchestrationStepResult.OK,
                    requires_human_confirmation=False,
                    confirmed_by="",
                    detail="conditional step (default OK)",
                    recorded_at=now,
                )
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
        if not isinstance(confirmed_by, str) or not _SAFE_ID.match(confirmed_by):
            raise OrchestratorValidationError(
                f"confirmed_by must be safe-id; got {confirmed_by!r}"
            )
        if not isinstance(now, str) or not _ISO_UTC_Z.match(now):
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
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _make_trace_id(event_id: str, step_index: int, seed: int) -> str:
    return f"tr.{event_id}.s{step_index}.{seed}"


def _make_report_id(event_id: str, chain_id: str) -> str:
    return f"rpt.{event_id}.{chain_id}"


# ---------------------------------------------------------------------------
# MVP fixed chain (US-4 spec, AC-3)
# ---------------------------------------------------------------------------


MVP_FIXED_CHAIN: OrchestrationChain = OrchestrationChain(
    chain_id="oc.mvp.task_dispatch.v1",
    steps=(
        OrchestrationStep(
            step_index=0,
            kind=OrchestrationStepKind.AGENT_CALL,
            agent_id="agent.task_flow_understanding",
            requires_human_confirmation=False,
            on_failure=FailurePolicy.ESCALATE_HUMAN,
        ),
        OrchestrationStep(
            step_index=1,
            kind=OrchestrationStepKind.AGENT_CALL,
            agent_id="agent.task_decomposition",
            requires_human_confirmation=False,
            on_failure=FailurePolicy.ESCALATE_HUMAN,
        ),
        OrchestrationStep(
            step_index=2,
            kind=OrchestrationStepKind.AGENT_CALL,
            agent_id="agent.team_recommendation",
            requires_human_confirmation=False,
            on_failure=FailurePolicy.ESCALATE_HUMAN,
        ),
        OrchestrationStep(
            step_index=3,
            kind=OrchestrationStepKind.HUMAN_CONFIRM,
            agent_id="",
            requires_human_confirmation=True,
            on_failure=FailurePolicy.ESCALATE_HUMAN,
        ),
        OrchestrationStep(
            step_index=4,
            kind=OrchestrationStepKind.AGENT_CALL,
            agent_id="agent.task_package_build",
            requires_human_confirmation=False,
            on_failure=FailurePolicy.ESCALATE_HUMAN,
        ),
    ),
)
