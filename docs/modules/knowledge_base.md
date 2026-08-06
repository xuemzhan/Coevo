# `knowledge_base/` — 知识沉淀（US-14）

## 定位

把基线/合并/风险/会议结论/简报/进展/模型总结聚合为知识包、复盘草稿与可复用模板；
入库前必须经人工审核与密级检查（AC-5/6/7）。

## 职责边界

- **in scope**：知识条目聚合、密级取最高值、复盘草稿生成、模板提取、审批入库、
  SQLite 持久化；
- **out of scope**：模型总结生成（外部输入，必须显式审批）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `KnowledgeEntry`、`KnowledgeBundle`、`ReusableTemplate`、`RetrospectiveDraft`、`ReviewDecision` | 知识/分类/模板/复盘模型与校验 |
| `facade.py` | `KnowledgeBaseFacade.aggregate/review/to_audit_record` | 聚合门面：汇总各来源 → 知识包 + 复盘草稿 + 可复用模板；审批入库 |
| `store.py` | `KnowledgeStore`（save/list_by_project） | SQLite 持久化：JSON 载荷编解码 + 原子提交 + 审计哈希链 |

## 关键入口与数据流

```
合并回执 + 风险 + 会议结论 + 简报 + 进展 + 模型总结
  → KnowledgeBaseFacade.aggregate → KnowledgeBundle + RetrospectiveDraft + Templates
  → review（批准/修改后入库/不入库）→ KnowledgeStore.save → 审计
```

- `KnowledgeBaseFacade.aggregate()` — 汇总来源索引 + 去重 + 密级上界；
- `KnowledgeBaseFacade.review()` — 审批入库（模型总结必须显式批准）；
- `KnowledgeStore.save/list_by_project` — 持久化与查询。

## 安全与不变量

- **未经审核的模型总结不得进入正式知识库**（AC-7）；
- 每条知识记录来源项目与适用范围；密级取全部条目最高值；
- 门面纯函数无 IO，持久化由 store 承担；审计投影脱敏。

## 测试覆盖

- `tests/unit/test_knowledge_base.py`、`test_knowledge_store.py`；
- `tests/integration/test_knowledge_store.py`。

## 依赖与下游

- **上游依赖**：`merge`（回执）、`risk`、`supervision`、`decision_brief`、
  `progress_capture`、`task_decomposition`；
- **下游消费者**：`app/pipeline`、`examples/` 演示闭环。
