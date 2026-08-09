# FRAMEWORK-OPTIMIZE-26 切片计划：task_decomposition/agent._validate 阶段化拆分

> 状态：已批准（2026-08-09 用户指令"继续P2"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-26`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-25]）。
- 目的：`TaskDecompositionAgent._validate`（108 行，cc~21，全仓复杂度密度最高的校验
  方法）做**纯迁移式阶段拆分**：单任务条目校验提取为模块级 `_parse_task`，单边条目
  校验提取为模块级 `_parse_edge`，`_validate` 收敛为集合界限 → known_packages →
  任务解析 → 已知 id → 边解析 → 去重构造的线性编排（约 35 行）；
  错误消息、校验顺序、失败关闭语义逐字节不变；`_validate` 签名不变（含未使用的
  `project_input` 参数，属既有接口，不越界清理）。

## 2. 交付

- `src/coevo/task_decomposition/agent.py`：
  1. 新增模块级 `_parse_task(raw, *, known_packages) -> SuggestionTask`
     （原 279-337 行单任务校验体：dict 检查/字段缺省/SAFE_ID/字符串字节上限/
     ISO-8601 Z 窗口/acceptance_criteria）；
  2. 新增模块级 `_parse_edge(raw, *, tasks, known_ids) -> SuggestionEdge`
     （原 342-361 行单边校验体：dict 检查/字段缺省/SAFE_ID/自环/未知引用）；
  3. `_validate` 收敛为线性编排（tasks 用 tuple 生成器、edges 经 dict.fromkeys
     去重，与原 append + 去重语义一致）。
- 守卫测试 `tests/unit/test_framework_optimize27.py`。

## 3. 测试要点

- 守卫：`_validate` 方法体不超过 60 行（原 108）；`_parse_task`/`_parse_edge` 存在
  且被 `_validate` 调用；关键错误消息标记存活（连续字面量）；
- 回归：`tests/unit/test_task_decomposition_agent.py` 全量。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-26` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**是**（模型输出解析为安全关键：SAFE_ID/字节上限/ISO 窗口/
  未知引用失败关闭；纯迁移不改判定顺序与字符串）。
- protocol-reviewer：**否**。
