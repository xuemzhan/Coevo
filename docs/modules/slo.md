# slo/ — 验收指标 SLO 聚合器（ARCH-REVIEW-6）

## 定位

把 system-requirements §20 中可门禁化的验收指标实现为确定性、离线可计算的
比率聚合器；模型/网络/试点类指标显式排除在门禁之外。

## 职责边界

- in scope：`dispatch_success_rate`、`replay_rejection_rate`、
  `interception_rate`、`audit_coverage`、`package_round_trip_rate`、
  `assert_slo_thresholds`（空分母=0.0 fail-closed、未知指标=违规）。
- out of scope：模型准确率、人工采纳率等试点指标；不做持久化/遥测采集。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `metrics.py` | 上述函数 + `SLO_DEFAULTS` + `SloValidationError` | 纯函数比率聚合与阈值断言 |
| `__init__.py` | 再导出 | 公共 API 表面 |

## 关键入口

`assert_slo_thresholds(metrics)` 返回违规列表；配合 e2e demo 管线测量
调度/审计/包闭环三项。

## 安全与不变量

- 无证据（空分母）一律 0.0，禁止"空跑通过"；
- 输入类型/计数越界 fail-closed；
- 未知指标名视为违规，防止阈值被悄悄绕过。

## 测试覆盖

- `tests/unit/test_arch_review_6_slo_metrics.py`；
- `tests/e2e/test_arch_review_6_slo_e2e.py`（真实管线 SLO 断言）。

## 依赖与下游

- 上游：stdlib-only；
- 下游：门禁/发布报告引用；契约见 `docs/architecture/slo-metrics.md`。
