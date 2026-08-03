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
* No new dependency."""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from src.coevo.workspace.models import WorkspaceEntry

from .models import (AgentCapability, AgentRegistration, AgentRegistry, AgentSpec, AgentStatus, FailurePolicy, MVP_FIXED_CHAIN, OrchestrationChain, OrchestrationEvent, OrchestrationEventKind, OrchestrationOutcome, OrchestrationReport, OrchestrationStep, OrchestrationStepKind, OrchestrationStepResult, OrchestrationTrace, OrchestratorConflictError, OrchestratorError, OrchestratorValidationError, _ISO_UTC_Z, _SAFE_ID, _make_report_id, _make_trace_id)

from .service import (Orchestrator)

from ._real_chain import REAL_EXECUTION_MODE, PackagePreview, RealChainExecutor, RealChainOutcome, confirm_real_chain, dispatch_real_chain, recover_real_chain, resume_real_chain
from .real_chain_store import RealChainAuditEntry, RealChainStore, RealChainStoreError, RealChainStoreRecoveryRequired, canonical_digest, canonical_json_bytes
