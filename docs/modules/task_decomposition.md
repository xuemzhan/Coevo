# `task_decomposition/` — 任务分解（US-2）

## 定位

基线工厂、依赖图、任务编辑（带 Override 审计）与模型辅助建议代理：把流程模型
转化为可执行、可跟踪、可验收的任务基线。

## 职责边界

- **in scope**：任务/工作包/里程碑/依赖建模、基线构建与确认、编辑审计、
  依赖环检测 + 拓扑排序、模型建议（仅草稿）；
- **out of scope**：进度/成果（`progress_capture`/`report`）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `Task`、`WorkPackage`、`Milestone`、`DependencyEdge`、`ProjectBaseline` | 任务/工作包/里程碑/依赖/基线/覆盖模型（frozen、版本单调） |
| `baseline.py` | `build_baseline()`、`confirm_baseline()` | 构造 v1 基线 / 确认升版本（每次全量重校验） |
| `dependency_graph.py` | `DependencyGraph`、`cycle_in_components()`、`topological_order()` | 邻接索引 + heap 拓扑排序 O((V+E) log V) + 显式栈环检测 |
| `editing.py` | `add_task/remove_task/update_task/reorder_tasks` | 增删改排 + Override 审计（经 build_baseline 重校验） |
| `service.py` | `TaskDecompositionService.propose()` | 门面：按标准阶段分组生成工作包/任务/交付物 |
| `agent.py` | `TaskDecompositionAgent.suggest()` | 模型辅助建议代理（流程 JSON 预索引分组，建议仅草稿） |

## 关键入口与数据流

```
FlowUnderstanding（US-1）→ TaskDecompositionService.propose
  → build_baseline（v1）→ 人工编辑（add/remove/update/reorder + Override）
  → confirm_baseline（版本 +1，全量重校验）→ 项目初始基线
```

- `build_baseline/confirm_baseline`；`add_task/remove_task/update_task/reorder_tasks`；
- `TaskDecompositionAgent.suggest()` — 模型建议仅草稿，人工确认后才入基线。

## 安全与不变量

- 任务 ID 全局唯一；依赖无环（cycle fail-closed）；版本严格单调递增；
- 阶段顺序种子边 + 显式边，拓扑排序确定性与输入顺序无关；
- 建议须人工确认后才写正式状态（模型输出不直接改基线）。

## 测试覆盖

- `tests/unit/test_task_decomposition.py`（23 项：输入/图/基线/服务）、
  `test_task_decomposition_agent.py`、`test_task_decomposition_editing.py`；
- `tests/unit/test_engineering_baseline.py` 等基线回归。

## 依赖与下游

- **上游依赖**：`task_flow`（流程模型/阶段图）；
- **下游消费者**：`talent`（需求映射）、`orchestrator`（基线步骤）、`merge`、
  `report`、`risk`、`knowledge_base`。

## 错误语义

- `TaskDecompositionValidationError`：输入不可调和（可用户修正）；
- `TaskDecompositionError`：结构不变量被破坏（依赖环、ID 冲突、版本回退等）；
- 模型建议仅草稿，人工确认后才写正式状态。
