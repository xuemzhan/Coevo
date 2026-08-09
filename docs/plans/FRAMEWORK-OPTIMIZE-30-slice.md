# FRAMEWORK-OPTIMIZE-30 切片计划：注释补全收尾（audit_governance + real_chain_store）

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-30`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-29]）。
- 目的：注释补全**收尾**——audit_governance（5 处）+ orchestrator/real_chain_store
  （27 处，含 9 个嵌套 `operation` 闭包与 `canonical_json_bytes` 内嵌套 `validate`）
  共 **32 个函数**补全 docstring，写明失败关闭语义、哈希链/审计链绑定、事务原子性
  契约；纯注释、零行为变化。

## 2. 交付

- `src/coevo/audit_governance/{stream_store,facade}.py`（3+2 处）；
- `src/coevo/orchestrator/real_chain_store.py`（27 处：快照冻结/恢复、schema 投影、
  检查点/恢复、事务、审计链、`operation` 事务闭包族）；
- 守卫测试 `tests/unit/test_framework_optimize31.py`——按 (文件,函数名) 锁定，
  每个出现均有非空 docstring（一行桩豁免）。

## 3. 测试要点

- 守卫：32 个目标函数每个出现均有非空 docstring；文件可编译；
- 回归：audit_governance 与 real_chain_store 相关既有测试全绿。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-30` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯注释，无逻辑变更）。
- protocol-reviewer：**否**。
