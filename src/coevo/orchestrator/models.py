"""orchestrator.models - US-4 domain models, enums, errors, registry and orchestration value objects."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-4 编排领域模型：Agent 注册/状态/失败策略/链/报告与校验。

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field

_SAFE_ID = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$")

_ISO_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")

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
    CONFIRMED_PENDING_PACKAGE = "confirmed_pending_package"
    ESCALATED = "escalated"
    FAILED = "failed"

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

    def __post_init__(self) -> None:
        # Lazy O(1) agent_id -> registration index. Private and
        # excluded from equality / hashing.
        object.__setattr__(self, "_id_cache", None)

    @classmethod
    def empty(cls) -> "AgentRegistry":
        return cls(_by_id=tuple())

    def get(self, agent_id: str) -> AgentRegistration | None:
        cache = self._id_cache
        if cache is None:
            cache = {reg.spec.agent_id: reg for reg in self._by_id}
            object.__setattr__(self, "_id_cache", cache)
        return cache.get(agent_id)

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
    execution_mode: str = ""

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
        if not isinstance(self.execution_mode, str):
            raise OrchestratorValidationError("execution_mode must be a string")

def _make_trace_id(event_id: str, step_index: int, seed: int) -> str:
    return f"tr.{event_id}.s{step_index}.{seed}"

def _make_report_id(event_id: str, chain_id: str) -> str:
    return f"rpt.{event_id}.{chain_id}"

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
