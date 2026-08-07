# FRAMEWORK-GAPS-1 切片计划：框架审查观察项收口

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。本轮只跑
> 增量门禁（fmt + lint + 定向测试），豁免留痕。

## 1. 目标工作项

- 工作项：`FRAMEWORK-GAPS-1`（ENG-BASE）
- 目的：把 AC-2/AC-6/AC-8/AC-9 各轮 security-review 留存的 Low/Info 观察项
  一次性收敛，框架层达到"可复核、无悬空观察"状态。

## 2. 收口清单

| 观察项 | 来源 | 处理 |
| --- | --- | --- |
| semantic_version 非 semver 接受 | AC-1 L7 | manifest_checker 加 semver 校验 |
| created_at / occurred_at 非 ISO-8601 UTC Z | AC-6 / AC-4 | a2a / memory 加 ISO 校验 |
| Policy 超时无上界 | AC-2 Info4 | validate_policy 加上界（dispatch≤600s / plan_total≤7200s / consent≤7200s） |
| 链 provider 异常外泄 | AC-8 Low | plan_for 收敛 chain_for 异常为 OrchestrationError |
| 编排审计投影缺 validated_at | AC-8 Low | OrchestrationOutcome 增加 validated_at 并入投影 |
| K8s 清单 spec 项内未知字段未校验 | AC-9 Low | 按项白名单（capability/tool/policy/plan item keys） |
| trusted_anchor 委托语义 | AC-1 L2 | 文档化（manifest_checker docstring + DECISIONS） |
| 审计脱敏接线 | AC-1 L4 | 文档化（DECISIONS，US-15 审计层消费时接线） |
| 宽捕获设计取舍 | AC-2 Info5 | 文档化（validation.py docstring） |

## 3. 需修改/新增文件

- 修改 `src/coevo/framework/manifest_checker.py`、`a2a.py`、`memory.py`、
  `policy.py`、`orchestrator.py`、`k8s_listing.py`
- 新增 `tests/unit/test_framework_gaps.py`（收口项逐条负例）

## 4. 测试要点（含异常/负例）

- semver：`0.2.0` 通过、`0.2` / `v0.2.0` / 空拒绝；
- ISO：`2026-08-08T08:00:00Z` 通过、无 Z / 空格 / 非 UTC 拒绝；
- Policy 上界：超过上界的 Policy 拒绝；默认 4 Profile 全部通过；
- 链异常：chain_for 抛异常 → OrchestrationError（非原始异常外泄）；
- 审计投影：ORCHESTRATION_PROJECTION_KEYS 含 validated_at；
- 清单项：capability/tool/policy/plan 项内未知键拒绝；
- L15 stdlib / L17 文档守卫回归。

## 5. 安全与兼容性风险

- 全部为收紧校验 / 收敛异常 / 补投影，无行为放宽；默认数据（4 Profile、
  既有 fixture）均通过新校验；不触碰 wire。

## 6. 可验证完成条件

- `python -m unittest tests.unit.test_framework_gaps` + 既有框架测试全绿；
- fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-GAPS-1 行。

## 7. 审查门

- security-reviewer：**是**（校验收紧 / 异常收敛边界）；
- protocol-reviewer：**否**。
