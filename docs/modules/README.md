# 模块文档索引

`src/coevo` 每个包一份独立文档，统一采用以下模板（2026-08-06 细化）：

1. **定位** — 模块解决什么问题、对应哪个用户故事；
2. **职责边界** — in scope / out of scope；
3. **文件清单** — 逐文件关键类型/函数与职责；
4. **关键入口与数据流** — 调用链与数据流向；
5. **安全与不变量** — 失败关闭、审计、边界；
6. **测试覆盖** — 对应单元/集成/安全/e2e 测试文件；
7. **依赖与下游** — 上游依赖与消费者。

| 包 | 文档 | 故事 |
|---|---|---|
| `app/` | [app.md](app.md) | 应用组合根（演示流水线） |
| `audit_governance/` | [audit_governance.md](audit_governance.md) | US-15 安全审计 |
| `benchmarks/` | [benchmarks.md](benchmarks.md) | 可扩展性探针 |
| `cockpit/` | [cockpit.md](cockpit.md) | US-7 本地驾驶舱 |
| `crypto/` | [crypto.md](crypto.md) | 国密引擎适配 |
| `decision_brief/` | [decision_brief.md](decision_brief.md) | US-13 决策简报 |
| `identity/` | [identity.md](identity.md) | US-0 身份与信任 |
| `knowledge_base/` | [knowledge_base.md](knowledge_base.md) | US-14 知识沉淀 |
| `merge/` | [merge.md](merge.md) | US-10 状态合并 |
| `model/` | [model.md](model.md) | 模型适配层 |
| `orchestrator/` | [orchestrator.md](orchestrator.md) | US-4 运行中枢 |
| `progress_capture/` | [progress_capture.md](progress_capture.md) | US-8 进展采集 |
| `protocol/` | [protocol.md](protocol.md) | US-5 任务包协议 |
| `report/` | [report.md](report.md) | US-9 成果回传 |
| `risk/` | [risk.md](risk.md) | US-11 风险预警 |
| `supervision/` | [supervision.md](supervision.md) | US-12 督办协调 |
| `talent/` | [talent.md](talent.md) | US-3 团队组建 |
| `task_decomposition/` | [task_decomposition.md](task_decomposition.md) | US-2 任务分解 |
| `task_flow/` | [task_flow.md](task_flow.md) | US-1 流程理解 |
| `workspace/` | [workspace.md](workspace.md) | US-6 工作区 |
| 根级模块 | [root_modules.md](root_modules.md) | config/version/logging/records |

总览性质的单文件导览见 [../code-guide.md](../code-guide.md)。
