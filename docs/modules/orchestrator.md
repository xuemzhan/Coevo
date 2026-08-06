# `orchestrator/` — 运行中枢（US-4）

## 定位

固定编排链调度：子智能体注册/状态、事件分发、人工确认节点、真实门面链的
SQLite 幂等存储与审计。MVP 只实现两条固定链（任务下发链、成果回传链）。

## 职责边界

- **in scope**：Agent 注册/能力目录/状态、dispatch/confirm 状态机、真实链执行
  （flow→decomp→talent→人工确认→包生成）、审计存储与锚点恢复；
- **out of scope**：动态/条件/循环编排（参考架构扩展项）、子智能体具体领域实现。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `AgentSpec/Registry`、`AgentCapability`（11 类闭集）、`OrchestrationStep`、`FailurePolicy`、`MVP_FIXED_CHAIN` | 注册/状态/失败策略/链/报告模型与校验 |
| `service.py` | `Orchestrator.dispatch_event/confirm_human` | 门面：事件驱动 + 人工确认 + 失败策略（RETRY/SKIP/ESCALATE_HUMAN），trace 构造统一助手 |
| `real_chain_store.py` | `RealChainStore`（begin_dispatch/confirm/begin_resume） | 真实链 SQLite：幂等 + 哈希链审计 + 锚点恢复（事务样板统一助手） |
| `_real_chain.py` | `dispatch_real_chain/confirm_real_chain/resume_real_chain` | 真实门面链：前三步原子执行 → 停在第 4 步人工确认 → 第 5 步生成加密包并回读校验 |

## 关键入口与数据流

```
任务事件 → Orchestrator.dispatch_event（Agent 可用性 + 失败策略）
  → dispatch_real_chain（flow → baseline → talent，原子落盘）
  → 第 4 步人工确认（StaticAuthorizer 权限校验，摘要绑定存储）
  → resume_real_chain（生成加密包 + 回读校验）→ 审计
```

- `Orchestrator.confirm_human()` — 授权校验 + 确认摘要与事件摘要绑定，防跳过确认；
- `RealChainStore.recover()` — 锚点校验失败 → `RealChainStoreRecoveryRequired`。

## 安全与不变量

- 每步原子落盘 + 审计链；恢复必须先通过锚点校验；
- **人工确认节点强制**：确认摘要与事件摘要绑定存储，跳过确认无法生成包；
- 失败策略确定性执行：RETRY 有界重试，其余 ESCALATE_HUMAN，绝不静默降级；
- 模型/规则输出不直接写正式状态。

## 性能与复杂度

- 每步原子落盘 + 审计链（真实链 SQLite 幂等，事务样板统一助手）；
- trace 构造与终局收尾统一助手，避免重复样板；
- 恢复必须先通过锚点校验（失败关闭，不做猜测性修复）。

## 测试覆盖

- `tests/unit/test_orchestrator.py`、`test_real_chain_store.py`；
- `tests/integration/test_orchestrator_real_facade_chain.py`；
- `tests/e2e/test_demo_runner.py`（固定链端到端）。

## 依赖与下游

- **上游依赖**：`task_flow`、`task_decomposition`、`talent`、`protocol`、
  `workspace`、`identity`（授权）；
- **下游消费者**：`app/pipeline`、`examples/service-api` 编排服务。

## 错误语义

- `OrchestratorValidationError`：事件/确认/预览/授权校验失败（可修正）；
- `OrchestratorConflictError`：重复事件/状态冲突（幂等失败关闭）；
- `RealChainStoreRecoveryRequired`：审计锚点校验失败，必须先 `recover()`。
