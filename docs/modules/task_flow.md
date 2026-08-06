# `task_flow/` — 任务流程理解（US-1）

## 定位

把 canonical / tabular / tree 三种输入解析为统一流程模型，映射到标准阶段，
生成阶段图与审阅视图；支持人工 Override 编辑并按版本演进。

## 职责边界

- **in scope**：三 schema 确定性解析、来源溯源（Traced）、阶段映射、StageGraph、
  ReviewerView、Override 升版本；
- **out of scope**：LLM 提取（确定性解析器先行，LLM 半环另作切片）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `Traced`、`ProcessFlow`、`Override`、`Stage`、`StandardStage` | 模型：字段值 + 来源路径 + 置信度 + SourceKind；版本严格单调 |
| `parser.py` | `parse_flow()` | 三 schema 确定性解析（重复 ID/非法类型/置信度越界失败关闭） |
| `mapping.py` | `apply_mapping()`、`DEFAULT_MAPPING_RULES`（27 条） | 规则表映射：hint → StandardStage，预构建 O(1) 命中 |
| `service.py` | `FlowUnderstandingService.understand/confirm/to_audit_record`、`StageGraph`、`ReviewerView` | 理解服务：解析 → 映射 → 图 → 审阅视图；confirm 以 Override 升版本 |

## 关键入口与数据流

```
流程资料 → parse_flow（canonical/tabular/tree 归约为规范形）
  → apply_mapping（规则表 → StandardStage）→ StageGraph（阶段索引）
  → FlowUnderstandingService.understand → 负责人确认（Override 升版本）
  → 带版本流程模型（US-2 依赖）
```

- `FlowUnderstandingService.understand()` — 一次返回 flow + mapped + graph +
  reviewer_view；
- `parse_flow()` / `apply_mapping()`；
- `ReviewerView.source_mapping_lookup/confidence_for` — 展示原始资料对应关系。

## 安全与不变量

- 重复 ID、非法类型、置信度越界、非 UTF-8 全部失败关闭；
- 输出确定性与输入顺序无关；版本严格单调递增（int，非时间戳）；
- 每字段携带 source_path + confidence ∈ [0,1] + SourceKind 闭集；
- 审计投影只记结构事实。

## 测试覆盖

- `tests/unit/test_task_flow_models.py`（18 项）、`test_task_flow_service.py`
  （27 项：4 schema 端到端 / graph / reviewer / confirm / audit / 失败路径）；
- `tests/unit/test_task_flow_service.py`（映射）。

## 依赖与下游

- **下游消费者**：`task_decomposition`（阶段分组）、`orchestrator`（固定链第 1 步）、
  `app/pipeline`。

## 错误语义

- `ProcessFlowParseError`：解析失败（重复 ID/非法类型/置信度越界/非 UTF-8）；
- `ProcessFlowError`：模型不变量（如 Traced 置信度越界）；`TaskFlowValidationError`：
  服务层调用方错误。
