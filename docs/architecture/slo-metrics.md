# 验收指标 SLO 化（SLO Metrics）

> 状态：生效（2026-08-10，ARCH-REVIEW-6）
> 对应：system-requirements §20 验收指标。

## 1. 可门禁化指标（CI 内确定性断言）

| §20 指标 | 计算 | 阈值 |
|---|---|---|
| 常规调度成功率 | `dispatch_success_rate`（completed/total） | ≥0.95 |
| 重复包识别率 | `replay_rejection_rate`（拒绝/总数） | 1.0 |
| 非法/损坏/验签失败包拦截率 | `interception_rate`（拦截/总数） | 1.0 |
| 关键操作审计覆盖率 | `audit_coverage`（必需动作集 ∩ 观测动作集） | 1.0 |
| 任务包闭环成功率 | `package_round_trip_rate`（生成/解析/解密/验签闭环） | 1.0 |

约定：**空分母 = 0.0（无证据即失败关闭）**；未知指标名 = 违规。

## 2. 试点测量指标（不在 CI 断言）

- 流程要素提取准确率 / 结构化建模准确率 / 责任主体识别准确率（模型依赖）；
- 智能体建议人工采纳率 / 在线状态识别准确率（生产遥测）；
- 人工填报工作量下降、报告编制定时减少（业务试点前后对比）。

这些指标在受控试点中以真实模型与真实用户采集，方法见
`docs/operations/`（试点时补充），不纳入离线门禁。

## 3. 使用

- 单元：`src/coevo/slo/metrics.py` 纯函数 + `assert_slo_thresholds`；
- e2e：`tests/e2e/test_arch_review_6_slo_e2e.py` 跑真实 demo 管线并把
  调度/审计覆盖/包闭环三项送入断言。

## 4. 变更纪律

任何调整阈值或新增指标，必须同步本契约与 `SLO_DEFAULTS`；不得为"通过门禁"
而把失败样本从分母中剔除。
