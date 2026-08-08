# FRAMEWORK-OPTIMIZE-22 切片计划：MergeEngine.merge 阶段化拆分

> 状态：已批准（2026-08-09 用户指令"继续"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-22`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-21]）。
- 目的：`MergeEngine.merge`（394 行，复杂度约 33，全仓最大单体方法）按 docstring
  既定算法 1-7 步做**纯迁移式阶段拆分**——8 个私有阶段助手，`merge` 收敛为线性编排；
  所有校验顺序、rejection_reason 字符串、失败关闭语义逐字节不变；导入面不变。

## 2. 交付

- `src/coevo/merge/engine.py` 新增 8 个 `MergeEngine` 私有方法（代码原样搬移）：
  1. `_validate_merge_inputs`——类型/形状校验（原 119-131 行）；
  2. `_import_binding_rejection`——P1 导入绑定校验（原 133-215 行，返回首个拒绝提案或 None）；
  3. `_duplicate_rejection`——P2 重复/摘要去重（原 217-237 行）；
  4. `_revision_rejection`——AC-3 项目与基线版本匹配（原 239-266 行，含 HOLD 冲突）；
  5. `_decision_maker_rejection`——Round-2 P4 决策者派生与白名单（原 268-295 行）；
  6. `_merge_fields`——AC-4/5/7/P3 逐字段合并（原 302-385 行，返回
     `(tuple[FieldMerge, ...], has_conflict)`）；
  7. `_rejected_proposal`——P3 任一 HOLD 的整体拒绝提案（原 387-412 行）；
  8. `_commit_proposal`——AC-8/P2 新基线 + 原子注册成功提案（原 414-467 行）。
- `merge()` 收敛为校验 → 四个拒绝阶段 → 版本 → 字段合并 → HOLD/成功两条收尾的线性编排。
- 守卫测试 `tests/unit/test_framework_optimize23.py`。

## 3. 测试要点

- 守卫：`merge` 方法体不超过 200 行（原 394）；8 个阶段助手存在且被 `merge` 调用；
- 回归：`tests/unit/test_merge_engine.py` + `test_merge_engine_v3.py` +
  `test_merge_commit_receipt.py` 全量；`tests/integration/test_merge_risk_receipt_chain.py`；
- rejection_reason 断言均为子串匹配，字符串原样保留即可通过。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-22` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**是**（merge 为安全关键路径：失败关闭、白名单、CAS 原子注册；
  纯迁移不改变任何判定顺序或字符串）。
- protocol-reviewer：**否**。
