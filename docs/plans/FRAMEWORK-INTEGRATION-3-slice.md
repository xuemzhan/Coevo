# FRAMEWORK-INTEGRATION-3 切片计划：真实产品接线（app/pipeline）

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-INTEGRATION-3`（ENG-BASE，dependencies=[FRAMEWORK-INTEGRATION-2]）
- 目的：把框架 Plan 门接进真实产品组合根——`app/pipeline.py` 在调用
  `Orchestrator.dispatch_event_with_real_facades` 之前，先用
  `validate_product_chain` 校验 `MVP_FIXED_CHAIN`（抬升 → validate_plan
  五项不变量 + L18 + L19），失败即中止；让框架真正治理产品派发。

## 2. 交付

- `app/pipeline.py`：派发前插入框架门（RBAC/L4 使用结构 allow-all，真实
  authorizer 留待产品接线）；门失败抛 RuntimeError 中止。
- L7 ISO 校验兼容小数秒（产品 `now_utc_iso_z()` 为
  `...00.123456Z`），4 个模块（a2a/memory/validation/orchestrator）统一。
- `tests/unit/test_pipeline_framework_gate.py`：MVP_FIXED_CHAIN 抬升校验通过 +
  缺注册代理拒绝；demo 管线 e2e 回归（test_demo_runner 管线测试）。

## 3. 测试要点

- 门前置：MVP_FIXED_CHAIN + pipeline 4 代理注册表 → validate_product_chain
  accepted；移除任一代理 → REJECTED（"not registered"）；
- 小数秒 ISO：`2026-08-08T08:00:00.123456Z` 通过 validate_plan；
- 回归：demo 管线真实包+持久化 e2e 通过。

## 4. 完成条件

- 定向测试 + demo 管线 e2e 全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-INTEGRATION-3 行。

## 5. 审查门

- security-reviewer：**是**（产品接线门前置 / 异常中止）；protocol-reviewer：**否**。
