# Go↔Python 一致性契约（Go-Python Parity）

> 状态：生效（2026-08-10，ARCH-REVIEW-10；落实架构审查 P1-1）
> 适用范围：`go/taskflow`（Go 移植）与 `src/coevo/task_flow`（Python 参考实现）

## 1. 单一事实来源

- **Python `src/coevo/task_flow/` 是行为权威参考**：规则表、失败关闭语义、
  版本与溯源模型的裁决以 Python 实现为准；
- Go 包是**行为保持移植**，不得在未同步 Python 侧的情况下单独变更语义；
- GO-MIGRATE 切片全部完成后，由架构评审重新裁决权威语言，本契约随之更新。

## 2. 一致性机制（共享 golden corpus）

- 共享语料：`go/taskflow/testdata/mapping-rules.json`；
- 内容：`rules`（27 条默认映射规则：rule_id / hint / standard_stage /
  priority）与 `cases`（每条规则的正向用例 + 未知 hint / 非字符串 hint /
  重复节点三类负向用例）；
- Go 侧 `go/taskflow/parity_test.go` 与 Python 侧
  `tests/unit/test_arch_review_10_go_python_parity.py` 消费**同一文件**；
- 任一语言规则表或映射行为漂移，对应套件立即红灯。

## 3. 变更纪律

1. 先改共享语料（若规则或用例变化）；
2. Python 参考实现与 Go 移植同步修改；
3. 两侧一致性测试必须全绿；
4. 规则表版本变化（`mapping_rules_version`）必须走既有版本语义并同步更新语料。

## 4. 守卫测试

- `go/taskflow/parity_test.go`（Go 侧：语料加载 / 规则一致 / 用例一致 / 负向 fail-closed）；
- `tests/unit/test_arch_review_10_go_python_parity.py`（Python 侧同构断言）；
- 全量门禁 `quality` 的 Go 阶段运行 Go 套件、单元阶段运行 Python 套件。
