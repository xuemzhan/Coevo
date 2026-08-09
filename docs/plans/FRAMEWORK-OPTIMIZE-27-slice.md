# FRAMEWORK-OPTIMIZE-27 切片计划：resume_real_chain 阶段化拆分

> 状态：已批准（2026-08-09 用户指令"继续"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-27`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-26]）。
- 目的：`_real_chain.resume_real_chain`（148 行，cc~19）的验证门序列做**纯迁移式
  阶段拆分**为 4 个模块级助手，`resume_real_chain` 保留局部导入 + 加密包构建路径，
  收敛为约 95 行编排；校验顺序、错误消息、失败关闭语义逐字节不变；导入面不变。

## 2. 交付

- `src/coevo/orchestrator/_real_chain.py` 新增 4 个模块级私有函数（代码原样搬移，
  函数内局部导入保留既有防环风格）：
  1. `_validate_resume_context(...)`——确认结果/存储绑定/固定链/类型/ISO 时间/
     上下文匹配/base_revision（原 491-508 行）；
  2. `_verify_resume_bindings(confirmed, event, store)`——事件摘要重算 + 存储状态
     比对（原 509-523 行）；
  3. `_require_package_agent(registry, chain, confirmed, store, now)`——step-4
     包构建 agent 注册/能力/AVAILABLE 门（原 524-531 行，含 record_attempt）；
  4. `_begin_resume(confirmed, store, now) -> str`——preview 存在 + resume_digest
     计算 + begin_resume 原子开始，返回 resume_digest（原 532-543 行）。
- `resume_real_chain` 保留头部 `from . import (...)` 局部导入与加密包构建/升级
  回退路径（原 545-626 行），仅把 491-543 换成 4 个助手调用。
- 守卫测试 `tests/unit/test_framework_optimize28.py`。

## 3. 测试要点

- 守卫：`resume_real_chain` 方法体不超过 110 行（原 148）；4 个阶段助手存在且被
  调用；关键错误消息标记存活（连续字面量）；
- 回归：`tests/unit/test_orchestrator.py` + `tests/integration/test_orchestrator_real_facade_chain.py`。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-27` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**是**（US-5 包构建为安全关键：确认状态绑定、事件摘要重算、
  存储一致性、包构建 agent 能力门、失败升级人工；纯迁移不改判定顺序与字符串）。
- protocol-reviewer：**否**。
