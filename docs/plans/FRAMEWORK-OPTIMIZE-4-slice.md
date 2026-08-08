# FRAMEWORK-OPTIMIZE-4 切片计划：框架默认策略 Profile 惰性缓存

> 状态：已批准（2026-08-08 用户指令"基于框架，优化原来系统应用的代码实现，
> 包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-4`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-3]）。
- 目的：`framework/policy.py` 的 `default_profiles()` 每次调用都会重新构造全部
  4 个 `Policy`（含嵌套 Timeout/Retry/Consent Profile），`get_default_profile()`
  每次线性遍历并触发全量构造——被 pipeline 与 validate_plan 等消费点反复调用。
  Policy 及其嵌套 Profile 均为 frozen dataclass（不可变），可安全缓存：
  `default_profiles()` 惰性构造一次，`get_default_profile()` 字典 O(1) 查找
  （fail-closed 保留），消除重复构造（算法/数据结构优化）。

## 2. 交付

- `src/coevo/framework/policy.py`：
  * 模块级 `_DEFAULT_PROFILES_CACHE: tuple[Policy, ...] | None` 与
    `_DEFAULT_PROFILE_BY_NAME: dict[str, Policy] | None`；
  * `default_profiles()` 惰性构造并缓存（frozen 安全，返回同一 tuple）；
  * `get_default_profile(profile)` 从字典 O(1) 查找，未知名仍抛
    `PolicyValidationError`（行为不变）。
- 文档：`docs/modules/framework.md` 的 policy 行补充"默认 Profile 惰性缓存"。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize4.py`：
  * `default_profiles()` 两次调用返回同一对象（is）且内容一致；
  * `get_default_profile` 与 `default_profiles` 按 profile 一一对应；
    未知名仍 fail-closed（PolicyValidationError）；
  * frozen 不可变性：对返回 Policy 赋值抛 FrozenInstanceError；
  * 行为回归：默认 Profile 数值（INTERACTIVE/BATCH/AUDIT_ONLY/EMERGENCY 关键字段）。
- 回归：test_framework_gaps(2)/validate_plan/integration/orchestrator/plan_l18/
  pipeline_framework_gate + 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-4 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（共享 Policy 缓存被 validate_plan/RBAC 前置消费，
  须确认不可变语义与 fail-closed 保留、无共享可变状态）；protocol-reviewer：**否**。
