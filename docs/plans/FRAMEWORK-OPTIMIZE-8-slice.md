# FRAMEWORK-OPTIMIZE-8 切片计划：真实链 resume 失败收尾路径收敛

> 状态：已批准（2026-08-08 用户指令"继续"，延续"基于框架，优化原来系统应用的
> 代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-8`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-7]）。
- 目的：OPTIMIZE-7 已收敛 `dispatch_real_chain` 的失败收尾；`resume_real_chain`
  仍有 2 处结构相同的 ESCALATED 失败收尾（包验证失败 except 分支 /
  crypto 能力不可用分支：追加 ESCALATED trace + report + outcome +
  `store.finish_resume_failure`）。提取 `_finish_resume_escalated` 消除重复
  （行为不变，ESCALATED 语义与审计存储一致）。

## 2. 交付

- `src/coevo/orchestrator/_real_chain.py`：
  * 新增 `_finish_resume_escalated(chain, event, workspace, traces, summaries,
    confirmed, resume_digest, store, now, step, code)`——追加 ESCALATED trace +
    report + outcome + finish_resume_failure；
  * `resume_real_chain` 2 处失败块改为单次调用（code 常量各保留原文案）。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize8.py`：
  * `_finish_resume_escalated` 行为回归（真实 RealChainStore：begin_dispatch +
    confirm 前置后调用，outcome/trace 为 escalated、resume 记录失败）；
  * 守卫：`CRYPTO_PACKAGE_VERIFICATION_FAILED` / `CRYPTO_CAPABILITY_UNAVAILABLE`
    各只出现一次（单一调用点）、helper 定义存在。
- 回归：test_orchestrator / test_orchestrator_real_facade_chain / demo e2e +
  全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-8 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（resume 失败路径涉及 ESCALATED 状态与审计存储，
  须确认语义与 fail-closed 不变）；protocol-reviewer：**否**。
