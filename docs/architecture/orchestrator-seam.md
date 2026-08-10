# 编排器 seam 契约（Orchestrator Seam Contract）

> 状态：生效（2026-08-10，ARCH-REVIEW-1）
> 适用范围：`src/coevo/orchestrator`（产品编排器）与 `src/coevo/framework`（CTAF 框架层）之间的边界。
> 背景：2026-08-10 资深架构师审查发现产品编排器与框架 Hybrid Orchestrator 存在双状态机风险，本契约固化所有权划分与无旁路规则。

## 1. 所有权划分

- **框架层 = 校验/策略网关**：`framework/orchestrator.py`（Hybrid Orchestrator 核心）、
  `framework/integration.py`（桥接）、`framework/validation.py`（validate_plan）只负责校验与策略：
  Plan 五项不变量、L18/L19、policy_ref 绑定、能力闭集、人工确认门。框架层**不持有** workflow
  实例的持久化状态，也不执行任何领域步骤。
- **产品层 = 唯一执行器**：`orchestrator/service.py`（Orchestrator facade）与
  `orchestrator/_real_chain.py`、`orchestrator/real_chain_store.py` 是唯一被允许执行链上步骤、
  生成 `OrchestrationReport`/`RealChainOutcome`、写入 real-chain store 状态迁移的代码。
  所有 workflow 实例的持久化、重试、恢复、人工确认后继续，均以产品层状态机为准。
- **integration = 唯一合法桥**：`framework/integration.py` 提供
  `plan_to_chain` / `chain_to_plan` / `validate_product_chain` / `guarded_dispatch` /
  `guard_registration`，负责框架 Plan 与产品 OrchestrationChain 的双向转换与门禁前置。

## 2. 无旁路规则（No Bypass）

1. 组合根（composition root）中，任何产品编排入口（`Orchestrator.dispatch_event`、
   `dispatch_event_with_real_facades`、`confirm_*`、`resume_real_chain`）**不得**先于
   `validate_product_chain` / `guarded_dispatch` 被调用；必须先过框架门禁，再调用产品入口。
2. `guarded_dispatch` 在校验失败时**不得**调用内层 dispatch（fail-closed）。
3. 框架抽象的 TOOL 节点与非 MVP 能力不得进入产品执行器（`plan_to_chain` 拒绝）。
4. 产品状态迁移（real-chain store 写入）只能经产品层入口发生，框架层不得直接写产品状态。

## 3. 两条固定链的 seam

- **任务下发链**：任务输入 → 流程理解 → 分解 → 团队推荐 → 负责人确认 → 生成任务包。
  组合根 = `src/coevo/app/pipeline.py::run_demo_pipeline`：先 `validate_product_chain`，
  后 `Orchestrator.dispatch_event_with_real_facades`。
- **成果回传链**：成果包导入 → 版本差异审核（merge + signed receipt）→ 项目主版本更新 →
  风险预警 → 决策简报生成 → 知识沉淀入库。每一跳均走生产 facade
  （PackageImportService / MergeEngine / risk / decision_brief / knowledge_base），
  链级语义以各 facade 的仓库与审计记录为准；该链当前不经过产品 Orchestrator，
  未来若接入编排器，必须同样先过框架门禁。

## 4. 守卫测试

`tests/unit/test_arch_review_1_orchestrator_seam.py` 强制：

- Plan ↔ Chain 往返结构稳定（节点 kind / 顺序 / 人工门 / 能力不变）；
- `report_to_outcome` 对全部产品 outcome fail-closed（未知 outcome → ESCALATED）；
- 组合根 `run_demo_pipeline` 中 `validate_product_chain` 必须先于任何产品 dispatch 入口；
- 本契约存在且包含所有权与无旁路声明。

## 5. 变更纪律

任何修改产品编排入口、框架门禁或组合根接线的改动，必须同步更新本契约并在
`loop/DECISIONS.md` 留痕；删除或放松上述任何一条规则，视为架构边界变更，需要架构评审。
