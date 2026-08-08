# PERF-REPLAY-1 切片计划：check_replay 单趟作用域扫描

> 状态：已批准（2026-08-08 用户指令"继续进行优化，不用做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`PERF-REPLAY-1`（ENG-BASE，dependencies=[]）。
- 目的：`src/coevo/protocol/replay_detector.py::check_replay` 对同作用域
  `same_scope` 做了三趟 O(k) 扫描（package_id 命中、package_digest 命中、
  max sequence_no）；合并为**单趟**扫描，同时跟踪三者，决策顺序与结果逐位不变
  （id → digest → sequence 优先级保留），把每作用域扫描降到 1 趟（常数 3×）。

## 2. 交付

- `src/coevo/protocol/replay_detector.py::check_replay`：
  * 单趟遍历 `same_scope`：记录首个 package_id 命中、首个 package_digest 命中、
    最大 sequence_no；
  * 决策顺序不变：先 `DUPLICATE_PACKAGE_ID`，再 `DUPLICATE_DIGEST`，再
    `REPLAY_SEQUENCE`，最后 `ACCEPT`；
  * 关键正确性：id 命中优先级高于 digest——即使 digest 早于 id 命中，也必须返回
    `DUPLICATE_PACKAGE_ID`（不做提前 break，单趟全扫）。

## 3. 测试要点

- 既有 `tests/unit/test_agent_wire_regression.py` / 协议重放相关测试全部不变（行为
  逐位一致）；
- 新增 `tests/unit/test_framework_optimize16.py`（或并入现有重放测试）：
  * 优先级回归：构造 digest 早命中、id 晚命中的作用域，断言返回
    `DUPLICATE_PACKAGE_ID`（钉住合并的正确性）；
  * 单趟结构守卫：check_replay 源码不含三个独立 `for record in same_scope` 循环
    （合并为单循环）。

## 4. 完成条件

- 定向测试全绿（重放全量回归 + 新增优先级/结构用例）；fmt + lint exit=0；
- 追溯矩阵新增 `ENG-BASE | PERF-REPLAY-1` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**是**（重放检测为协议安全关键，须确认决策顺序/结果不变）；
  protocol-reviewer：**否**（不改 wire 布局与协议语义）。
