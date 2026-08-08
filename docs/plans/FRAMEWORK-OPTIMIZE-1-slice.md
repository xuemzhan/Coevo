# FRAMEWORK-OPTIMIZE-1 切片计划：基于框架优化原应用实现（数据结构 / 算法 / 模块架构）

> 状态：已批准（2026-08-08 用户指令"基于框架，优化原来系统应用的代码实现，
> 包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-1`（ENG-BASE，dependencies=[FRAMEWORK-INTEGRATION-4]）。
- 目的：在不改变 wire 字节与公共 API 语义的前提下，收敛"原应用 ↔ 框架"桥接层与
  demo 组合根的重复实现与低效结构：
  1. 数据结构/算法：`AgentRegistry.by_capability` 增加惰性能力索引（O(V) → 摊销
     O(1)，注册顺序语义不变，与既有 `_id_cache` 同模式）；
  2. 算法：`build_registration_manifest` 去除 `json.loads(json.dumps(...))`
     双重序列化（结构化剥离自指字段后一次性填充，输出字节不变）；
  3. 数据结构：`chain_to_plan` 消除二次 Plan 构造（`dataclasses.replace` 一次成型）；
  4. 模块架构：demo 注册装配从 `app/pipeline.py` 组合根内联循环收敛到
     `app/demo_support.py` 的 `register_demo_agents()`（显式非生产），组合根单次调用；
     组合根内 `_FrameworkGateAll` 提升为模块级复用。

## 2. 交付

- `src/coevo/orchestrator/models.py`：`AgentRegistry` 新增私有 `_capability_cache`
  （`register`/`set_status` 返回新实例时经 `__post_init__` 自动失效）。
- `src/coevo/framework/integration.py`：`build_registration_manifest` 单次序列化；
  `chain_to_plan` 用 `dataclasses.replace` 设 `plan_id`。
- `src/coevo/app/demo_support.py`：新增 `register_demo_agents()`（4 个 demo 代理：
  build_registration_manifest + guard_registration + registry.register，显式非生产）。
- `src/coevo/app/pipeline.py`：组合根调用 `register_demo_agents()`；`_FrameworkGateAll`
  提升为模块级 `_AllowAllScopeRbac`。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize1.py`：
  * by_capability：与 get/注册顺序一致；register 后新实例缓存失效（语义不变）；
  * build_registration_manifest：固定参数字节级回归锁定（与优化前基准一致，
    spec_hash 与 manifest_spec_hash 一致）；
  * chain_to_plan：plan_id == plan_fingerprint，节点/边与链步骤一一对应；
  * register_demo_agents：4 个代理全部 guard accepted 且注册成功；
- 回归：test_framework_integration2 / test_framework_integration4 /
  test_pipeline_framework_gate / test_orchestrator / test_framework_integration /
  test_module_docs。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-1 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（注册表数据结构与注册装配路径改动，须确认无权限/审计
  语义回退）；protocol-reviewer：**否**。
