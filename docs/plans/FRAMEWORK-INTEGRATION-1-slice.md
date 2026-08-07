# FRAMEWORK-INTEGRATION-1 切片计划：框架接入现有编排（GuardedOrchestrator 适配）

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-INTEGRATION-1`（ENG-BASE，dependencies=[US-16-AC-1,
  US-16-AC-8]）
- 目的：把框架门禁接到现有 `src/coevo/orchestrator`——注册必须过 manifest-
  checker、派发必须过 validate_plan 并走真实 `Orchestrator.dispatch_event`。

## 2. 交付

新增 `src/coevo/framework/integration.py`：

- `guard_registration`：manifest-checker 通过才调用注入的 inner_register；
- `plan_to_chain`：框架 Plan → 现有 `OrchestrationChain`（AGENT 节点按能力
  解析注册代理为 AGENT_CALL；HUMAN_GATE → HUMAN_CONFIRM；TOOL 节点 / 框架
  抽象能力 → IntegrationError，当前产品编排器不可执行）；
- `guarded_dispatch`：validate_plan 前置 → plan_to_chain →
  `Orchestrator.dispatch_event` → 报告映射 `OrchestrationOutcome`
  （COMPLETED / HELD / ESCALATED）；
- `GuardResult` / 审计投影；纯函数 stdlib + L17（integration.md）。

## 3. 测试要点（含负例）

- plan_to_chain：AGENT+HUMAN_GATE 混合 → 正确步骤；TOOL 节点拒绝；非 MVP
  能力拒绝；无注册代理拒绝；
- guarded_dispatch：无效 Plan → REJECTED 且内部分派不被调用；有效 Plan →
  内部分派被调用；报告 COMPLETED/HELD/ESCALATED 映射正确；内部分派异常 →
  ESCALATED；
- guard_registration：未通过 manifest → 不注册；通过 → 注册；内部注册异常 →
  fail-closed；
- L15 stdlib / L17 文档守卫。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-INTEGRATION-1 行。

## 5. 审查门

- security-reviewer：**是**（门禁接线 / 异常收敛）；protocol-reviewer：**否**。
