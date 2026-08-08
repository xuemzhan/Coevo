# FRAMEWORK-OPTIMIZE-7 切片计划：真实链失败收尾路径去重

> 状态：已批准（2026-08-08 用户指令"继续"，延续"基于框架，优化原来系统应用的
> 代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-7`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-6]）。
- 目的：`orchestrator/_real_chain.py::dispatch_real_chain` 中 3 处失败收尾路径
  （agent 不可用 / facade 失败 / facade 重试失败）结构完全相同——追加 ESCALATED
  trace 后调用 `_finish_dispatch_terminal(ESCALATED)`。提取
  `_escalate_and_finish` 辅助消除重复代码路径（算法/数据结构维度，行为不变）。

## 2. 交付

- `src/coevo/orchestrator/_real_chain.py`：
  * 新增 `_escalate_and_finish(chain, event, workspace, traces, summaries,
    event_digest, project_digest, package_preview, store, now, step, detail)`
    ——追加 ESCALATED trace + 终态收尾；
  * `dispatch_real_chain` 3 处失败块改为单次调用（detail 各保留原文案）。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize7.py`：
  * `_escalate_and_finish` 行为回归（真实 RealChainStore：先 begin_dispatch，
    调用后 outcome/trace 均为 escalated）；
  * 守卫：3 个失败 detail 各只出现一次（单一调用点）、helper 定义存在。
- 回归：test_orchestrator / test_orchestrator_real_facade_chain / demo e2e +
  全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-7 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（真实链失败路径涉及 ESCALATED 状态与审计存储，
  须确认语义与 fail-closed 不变）；protocol-reviewer：**否**。
