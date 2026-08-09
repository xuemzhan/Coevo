# FRAMEWORK-OPTIMIZE-24 切片计划：merge_and_commit 阶段化拆分

> 状态：已批准（2026-08-09 用户指令"继续"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-24`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-23]）。
- 目的：`MergeEngine.merge_and_commit`（176 行，cc~10）在 `merge` 拆分后做同款
  **纯迁移式阶段拆分**为 4 个私有阶段助手，`merge_and_commit` 收敛为线性编排；
  校验顺序、rejection_reason 字符串、失败关闭语义逐字节不变；导入面不变。

## 2. 交付

- `src/coevo/merge/engine.py` 新增 4 个 `MergeEngine` 私有方法（代码原样搬移）：
  1. `_receipt_context(decided_at)`——回执组成类型门 + 历史回执装载
     （原 668-682 行，返回 `(repository, authority, receipt_store)`）；
  2. `_receipt_binding_rejection(...)`——权威导入事实与报告绑定
     （原 696-715 行，返回拒绝 outcome 或 None）；
  3. `_field_decision_rejection(...)`——全部字段决策须 ACCEPT/MANUAL
     （原 717-732 行）；
  4. `_status_task_rejection(...)`——恰一个已接受的 status 合并且任务在基线内
     （原 734-763 行，status_merges 由编排处计算后传入）。
- `merge_and_commit()` 收敛为：回执上下文 → `merge` 调用 → 绑定/字段/status 三拒绝阶段
  → 签名者校验 → 回执构造+原子提交（内嵌 receipt_builder 闭包保留原样）→ outcome
  （约 100 行）。
- 守卫测试 `tests/unit/test_framework_optimize25.py`。

## 3. 测试要点

- 守卫：`merge_and_commit` 方法体不超过 120 行（原 176）；4 个阶段助手存在且被调用；
  关键拒绝标记存活（连续字面量）；
- 回归：`tests/unit/test_merge_commit_receipt.py` + `test_merge_engine.py` +
  `test_merge_engine_v3.py` + 守卫；`tests/integration/test_merge_risk_receipt_chain.py`。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-24` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**是**（回执链为安全关键路径：签名者绑定、字段决策白名单、
  CAS 原子提交；纯迁移不改判定顺序与字符串）。
- protocol-reviewer：**否**。
