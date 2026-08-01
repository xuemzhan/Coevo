# US-4-AC-1 Slice Plan: orchestrator service facade

> Loop-engineer PLAN 阶段产物, 2026-08-01.
> 对应 BACKLOG items[US-4-AC-1].test_orchestrator.
> 本切片遵守 AGENTS.md §1 文档优先级与 §2 七阶段; 不修改 .agent wire, 不修改
> 密码方案, 不修改既有模块 (除测试侧 import 既有 facade).

## 1. 用户故事与 AC

US-4: "运行中枢: 子智能体注册与最小任务编排"
1. 七类专业子智能体能够登记名称、能力、输入和输出要求;
2. 运行中枢显示子智能体可用状态;
3. 能够根据任务事件触发预设编排流程;
4. 界面显示当前步骤、调用对象和执行结果;
5. 高影响操作具有人工确认节点;
6. 调用失败时支持重试、跳过或转人工;
7. 编排过程形成审计记录.

MVP 固定编排链:
> 任务输入 → 任务流程理解 → 任务分解 → 团队推荐 → 负责人确认 → 生成任务包.

## 2. 切片范围

### 2.1 新增模块

- `src/coevo/orchestrator/__init__.py` (≤ 1200 行, 与 US-11/12/13/8/15 单文件风格一致)
- `tests/unit/test_orchestrator.py` (≥ 15 测试)

### 2.2 不修改

- 既有 `src/coevo/{identity,protocol,workspace,report,merge,risk,supervision,decision_brief,progress_capture,audit_governance,task_flow,task_decomposition,talent}` 等任何模块
- `.agent` wire / `loop/audit-signing.json` / `loop/audit-head.{json,p7s}`
- `toolchain-lock.json` (无新增依赖)

### 2.3 边界

- 不引入 IO; Orchestrator 只消费 in-memory 输入 (AgentRegistry / OrchestrationChain / 任务事件 dict)
- 不调用既有 facade 的副作用 API; 只演示"如果调用会得到什么" (本切片做"调度机制 + trace 记录", 真实业务调用留给后续 AC)
- 安全等级 security_review=true; 涉及人工确认 + 审计 + 失败回退

## 3. 数据模型

```text
AgentCapability (Enum, closed set; AC-1 七类专业子智能体)
  TASK_FLOW_UNDERSTANDING  -- US-1
  TASK_DECOMPOSITION       -- US-2
  TEAM_RECOMMENDATION      -- US-3
  STATE_MERGE              -- US-10
  TASK_PACKAGE_BUILD       -- US-5
  PROGRESS_CAPTURE         -- US-8
  RISK_ANALYSIS            -- US-11
  DECISION_BRIEF           -- US-13
  SUPERVISION_MEETING      -- US-12
  AUDIT_GOVERNANCE         -- US-15
  REPORT_BUILD             -- US-9

AgentSpec (AC-1 登记字段; 不可变 dataclass)
  agent_id        -- safe-id (e.g. "agent.task_flow_understanding")
  capability      -- AgentCapability
  display_name    -- str (人类可读, audit 可投影)
  input_schema    -- tuple[str, ...] (输入字段名集合)
  output_schema   -- tuple[str, ...] (输出字段名集合)
  requires_human_confirmation -- bool (AC-5: 高影响操作)

AgentStatus (Enum)
  AVAILABLE      -- 默认 (AC-2)
  BUSY           -- 正在执行
  DISABLED       -- 被禁用
  ERROR          -- 错误状态

AgentRegistration (不可变)
  spec           -- AgentSpec
  status         -- AgentStatus

AgentRegistry (AC-1 不可变注册表; 纯函数)
  _by_id         -- tuple[AgentRegistration, ...]
  list_available()             -- tuple[AgentRegistration, ...]
  by_capability(cap)           -- tuple[AgentRegistration, ...]
  get(agent_id)                -- AgentRegistration | None
  register(reg)                -- AgentRegistry (新实例)
  set_status(agent_id, status) -- AgentRegistry

OrchestrationStepKind (Enum)
  AGENT_CALL      -- 调用子智能体
  HUMAN_CONFIRM   -- 人工确认节点 (AC-5)
  CONDITIONAL     -- 条件分支

OrchestrationStep (不可变)
  step_index      -- int >= 0
  kind            -- OrchestrationStepKind
  agent_id        -- str (only for AGENT_CALL; empty otherwise)
  requires_human_confirmation -- bool (AC-5)
  on_failure      -- FailurePolicy (AC-6)

FailurePolicy (Enum)
  RETRY            -- 重试 (AC-6)
  SKIP             -- 跳过
  ESCALATE_HUMAN   -- 转人工

OrchestrationChain (不可变)
  chain_id        -- safe-id (e.g. "oc.task_dispatch.v1")
  steps           -- tuple[OrchestrationStep, ...]
  steps_count()   -- int

OrchestrationEventKind (Enum)
  DISPATCH        -- 任务下发 (AC-3)
  MERGE           -- 状态合并
  REPORT          -- 成果回传
  RISK            -- 风险

OrchestrationEvent (AC-3)
  event_id        -- safe-id
  kind            -- OrchestrationEventKind
  project_id      -- safe-id
  task_id         -- safe-id
  payload         -- dict (业务侧输入)
  triggered_at    -- ISO-8601 UTC 'Z'

OrchestrationStepResult (Enum)
  OK              -- 步骤完成
  HELD_AT_CONFIRM -- 等待人工确认 (AC-5)
  RETRIED         -- 重试 (AC-6)
  SKIPPED         -- 跳过 (AC-6)
  ESCALATED       -- 转人工 (AC-6)
  FAILED          -- 不可恢复失败

OrchestrationTrace (AC-4/AC-7)
  trace_id        -- safe-id
  step_index      -- int
  agent_id        -- str
  result          -- OrchestrationStepResult
  requires_human_confirmation -- bool
  confirmed_by    -- str (空 if not held)
  detail          -- str (人类可读; 不进 audit)
  recorded_at     -- ISO-8601 UTC 'Z'

OrchestrationOutcome (Enum)
  COMPLETED       -- 全部步骤 OK
  HELD_AT_CONFIRM -- 任一步骤需要人工确认
  ESCALATED       -- 转人工
  FAILED          -- 不可恢复失败

OrchestrationReport (最终产出; AC-4)
  trace_id        -- safe-id
  chain_id        -- safe-id
  event_id        -- safe-id
  workspace       -- WorkspaceEntry
  outcome         -- OrchestrationOutcome
  trace           -- tuple[OrchestrationTrace, ...]
  completed_at    -- ISO-8601 UTC 'Z'
```

## 4. 服务层

```text
class Orchestrator:
    @staticmethod
    def dispatch_event(
        registry: AgentRegistry,
        chain: OrchestrationChain,
        event: OrchestrationEvent,
        *,
        workspace: WorkspaceEntry,
        now: str,
    ) -> OrchestrationReport:
        """AC-3/AC-4/AC-5/AC-6 主入口.

        遍历 chain.steps, 每步:
        - AGENT_CALL: 检查 registry.get(agent_id).status == AVAILABLE;
          否则按 on_failure (RETRY/SKIP/ESCALATE_HUMAN) 处理;
          成功 -> result=OK, 增加 trace;
        - HUMAN_CONFIRM: 强制 result=HELD_AT_CONFIRM, 等用户 confirm_human();
        - CONDITIONAL: 默认按 AGENT_CALL 处理 (本切片不实现条件表达式).

        任一步骤需要人工确认 -> 立即停止, 返回 HELD_AT_CONFIRM.
        任一步骤不可恢复失败 -> 立即停止, 返回 FAILED.
        """

    @staticmethod
    def confirm_human(
        report: OrchestrationReport,
        *,
        step_index: int,
        confirmed_by: str,
        now: str,
    ) -> OrchestrationReport:
        """AC-5: 用户确认; 该步骤 result=HELD_AT_CONFIRM -> OK,
        后续步骤继续执行."""

Orchestrator.to_audit_record(report: OrchestrationReport) -> dict:
    """AC-7 审计投影; 排除 detail 文本, 保留 trace 步骤 + agent + result."""
```

## 5. AC 映射

| AC | 实现位置 | 失败模式 |
|---|---|---|
| AC-1 登记名称/能力/输入输出 | AgentRegistry.register + AgentSpec 字段 + AgentCapability 闭集 | agent_id 非 safe-id / duplicate 注册 / 未知 capability → ValidationError |
| AC-2 显示可用状态 | AgentRegistry.list_available / by_capability / get | -- |
| AC-3 触发编排流程 | Orchestrator.dispatch_event + OrchestrationEventKind 触发器 | event.kind 不在闭集 / workspace 非 WorkspaceEntry → ValidationError |
| AC-4 显示当前步骤/调用对象/结果 | OrchestrationTrace + OrchestrationReport.trace 列表 | -- |
| AC-5 高影响操作人工确认 | requires_human_confirmation + confirm_human + HELD_AT_CONFIRM | confirmed_by 非 safe-id / now 非 ISO-8601 → ValidationError |
| AC-6 重试/跳过/转人工 | FailurePolicy + on_failure 处理 | -- |
| AC-7 编排过程审计 | to_audit_record + trace 列表 | -- |

## 6. 测试点 (≥ 15)

1. test_agent_capability_closed_set (AC-1)
2. test_agent_registry_register_and_get (AC-1)
3. test_agent_registry_rejects_duplicate (AC-1)
4. test_agent_registry_rejects_unknown_capability (AC-1)
5. test_agent_registry_list_available_filters_by_status (AC-2)
6. test_agent_registry_by_capability (AC-2)
7. test_orchestration_chain_steps_count (AC-3)
8. test_dispatch_event_runs_full_chain (AC-3/AC-4)
9. test_dispatch_event_holds_at_human_confirmation (AC-5)
10. test_confirm_human_resumes_chain (AC-5)
11. test_dispatch_event_uses_retry_policy (AC-6)
12. test_dispatch_event_uses_skip_policy (AC-6)
13. test_dispatch_event_escalates_to_human (AC-6)
14. test_dispatch_event_rejects_unknown_agent (AC-3)
15. test_dispatch_event_rejects_invalid_event (AC-3)
16. test_to_audit_record_excludes_sensitive_detail (AC-7)
17. test_pure_function_determinism_same_input_same_outcome (质量)
18. test_mvp_fixed_chain_definition (MVP 固定链覆盖)

## 7. 风险与缓解

- R1 (MVP 固定链定义与 US-1/2/3/5 现有 facade 的对接): 本切片只定义 chain 步骤元数据 (agent_id / step_kind), 不实际调用 US-1/2/3 facade 业务; 真实调用留待 US-4-AC-2 (后续).
- R2 (人工确认后 chain 继续执行可能再次遇到 HELD_AT_CONFIRM): 当前切片不支持; 第二次 HELD 需要再次 confirm_human (调用者责任).
- R3 (retry 次数无限制): FailurePolicy.RETRY 视为无限重试直到 OK (实际由调用方在外部计时); 这是 MVP 简化.

## 8. 完成定义 (本切片)

- 所有 ≥ 18 项 unit 测试通过
- `python scripts/quality_gate.py --target quality` exit=0, audit chain fully-sealed
- 不修改既有模块 / 既有 wire / 既有密码 / 既有审计配置
- BACKLOG US-4-AC-1 status: ready → done
- STATE bump iteration + status done
- DECISIONS append 一段 finalize 段 (append-only)
- 追踪矩阵 US-4 行追加

## 9. 后续 AC 候选 (本切片不做)

- US-4-AC-2: 真实调用 facade (US-1/2/3 业务接入)
- US-4-AC-3: 重试次数上限 + 退避策略
- US-4-AC-4: 并行编排 (分支 / join)
- US-4-AC-5: 编排 DSL (条件表达式 / 循环)
