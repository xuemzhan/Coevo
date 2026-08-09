# FRAMEWORK-OPTIMIZE-32 切片计划：risk/analyzer._analyze 风险规则阶段化拆分

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-32`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-31]）。
- 目的：`RiskAnalyzer._analyze`（120 行，cc~11，P2 挂起项）的六条风险规则抽为
  **模块级纯函数 `-> Risk | None`**，`_analyze` 收敛为约 65 行编排；
  规则判定顺序、风险字段（severity/due/affected/文案）逐字节不变；
  `coordination` 保持原计算顺序（追加协调风险之前）；导入面不变。

## 2. 交付

- `src/coevo/risk/analyzer.py` 新增 6 个模块级私有函数（append→return 机械改写）：
  1. `_deadline_overrun_risk(...)`——DEADLINE_OVERRUN（原 117-124 行）；
  2. `_evidence_shortfall_risk(...)`——INSUFFICIENT_EVIDENCE（原 126-132 行）；
  3. `_long_silence_risk(...)`——LONG_SILENCE（原 134-140 行）；
  4. `_predecessor_unfinished_risk(...)`——PREDECESSOR_UNFINISHED（原 146-153 行）；
  5. `_status_bloom_risk(...)`——AT_RISK_BLOOM / BLOCKED_BLOOM（原 158-171 行）；
  6. `_coordination_risk(...)`——SEVERE_COORDINATION_NEEDED（原 176-186 行，
     coordination 由编排处先算后传入）。
- `_analyze` 收敛为：时间边界 → 图/回执校验 → 六个规则收集 → 排序 → RiskReport
  （新增 docstring）。
- 守卫测试 `tests/unit/test_framework_optimize33.py`。

## 3. 测试要点

- 守卫：`_analyze` 方法体不超过 80 行（原 120）；6 个规则助手存在且被调用；
  关键风险文案标记存活（连续字面量）；
- 回归：`tests/unit/test_risk_analyzer.py` 全量 + `test_merge_risk_receipt_chain`
  （集成）。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-32` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯结构迁移，风险判定语义不变；无密钥/权限边界）。
- protocol-reviewer：**否**。
