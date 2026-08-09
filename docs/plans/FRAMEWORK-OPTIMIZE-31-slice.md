# FRAMEWORK-OPTIMIZE-31 切片计划：talent/recommender._score_candidate 阶段化拆分

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-31`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-30]）。
- 目的：`talent/recommender._score_candidate`（123 行）按既有评分算法五个阶段做
  **纯迁移式阶段拆分**为 5 个模块级纯函数（skill/credential/window/load/tie-break），
  `_score_candidate` 收敛为约 35 行编排；评分权重、reason/alert 语义、确定性排序
  逐字节不变；导入面不变。

## 2. 交付

- `src/coevo/talent/recommender.py` 新增 5 个模块级私有函数（原阶段代码原样搬移，
  reasons/alerts 沿用既有可变列表风格）：
  1. `_match_skills(requirement, skill_values, reasons) -> float`（原 117-127 行）；
  2. `_match_credentials(requirement, credential_values, reasons) -> float`
     （原 129-139 行）；
  3. `_window_fit(talent, requirement, reasons, alerts) -> float`（原 141-178 行）；
  4. `_load_headroom(talent, reasons, alerts) -> float`（原 180-206 行）；
  5. `_tie_break(talent, reasons) -> None`（原 208-218 行，确定性平局键，分数中性）。
- `_score_candidate` 收敛为 5 步编排 + `return score, tuple(reasons), tuple(alerts)`。
- 守卫测试 `tests/unit/test_framework_optimize32.py`。

## 3. 测试要点

- 守卫：`_score_candidate` 方法体不超过 70 行（原 123）；5 个阶段助手存在且被调用；
  关键 reason kind 标记存活（skill_match/credential_match/availability_fit/
  load_capacity/tie_break）；
- 回归：`tests/unit/test_talent_recommender.py` 全量。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-31` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯结构迁移，评分语义不变；无密钥/权限/文件边界）。
- protocol-reviewer：**否**。
