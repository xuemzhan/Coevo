# FRAMEWORK-OPTIMIZE-38 切片计划：_build_content 类型参数/标题/进度阶段拆分

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-38`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-37]）。
- 目的：`decision_brief/_build._build_content`（145 行，cc~19，当前全仓最高复杂度的
  大函数）按三类型分支做**纯迁移式阶段拆分**为 3 个模块级助手，`_build_content`
  收敛为约 70 行组装编排；校验顺序、错误消息、标题/进度文案、风险字段逐字节不变。

## 2. 交付

- `src/coevo/decision_brief/_build.py` 新增 3 个模块级私有函数（代码原样搬移，
  逐函数惰性导入沿用既有风格）：
  1. `_type_parameters(brief_type, period_start, period_end, topic_risk_ids,
     report) -> frozenset[str] | None`——AC-5 类型参数校验（原 143-197 行，
     返回 topic_set）；
  2. `_content_title(brief_type, receipt, period_start, period_end, topic_set)
     -> str`——类型标签与标题（原 198-208 行）；
  3. `_progress_text(brief_type, receipt, period_start, period_end) -> str`
     ——进度文案（原 209-218 行）。
- `_build_content` 保留来源/变更结论 + 组装（RISK_TOPIC 分支与默认分支原样）。
- 守卫测试 `tests/unit/test_framework_optimize38.py`。

## 3. 测试要点

- 守卫：`_build_content` 方法体不超过 100 行（原 145）；3 个阶段助手存在且被调用；
  关键错误消息标记存活（连续字面量）；
- 回归：`tests/unit/test_decision_brief.py` + `test_framework_optimize21.py`。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-38` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯结构迁移，简报内容语义不变；无密钥/权限边界）。
- protocol-reviewer：**否**。
