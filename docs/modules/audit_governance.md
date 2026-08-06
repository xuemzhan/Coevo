# `audit_governance/` — 安全审计（US-15）

## 定位

统一审计事件模型、异常包拦截判定、查询/导出，以及 JSONL + SHA-256 哈希链的
持久化审计流。是“全过程留痕”与“审计篡改可检测”需求的实现层。

## 职责边界

- **in scope**：`AuditEvent` 统一事件、五类拦截原因、查询游标分页、JSON/JSONL
  导出、内存发布/订阅与持久化哈希链；
- **out of scope**：签名检查点（`scripts/audit_seal.py`）、循环状态审计
  （`loop/tool-audit.jsonl`，由 `scripts/audit_log.py` 维护）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `AuditEvent`、`InterceptionReason`、`AuditQuery`、`AuditExportPayload` | 统一事件模型、拦截原因五类闭集、查询/导出载荷与全部校验 |
| `facade.py` | `SecurityAuditFacade.evaluate_interception/query_events/export_events` | 集中拦截判定（AC-1）、过滤 + `record_hash` 游标分页（limit 硬上限）、稳定摘要导出 |
| `stream.py` | `AuditStreamHub`、`AuditSubscription` | 内存发布/订阅/历史重放（fail-isolated 投递，单订阅者故障不影响流） |
| `stream_store.py` | `AuditStreamStore.append/iter_events` | JSONL + SHA-256 哈希链持久化，追加独占、尺寸增量维护 |

## 关键入口与数据流

```
业务动作 → to_audit_record() 脱敏投影 → SecurityAuditFacade / AuditStreamHub
  → AuditStreamStore（JSONL 哈希链）→ 查询/导出（安全管理员）
```

- `SecurityAuditFacade.evaluate_interception()` — 损坏/篡改/过期/重复/接收人不匹配
  五类原因集中决策；
- `SecurityAuditFacade.query_events()` — 六字段过滤 + 游标分页，limit ≤ 10000；
- `AuditStreamHub.publish()` / `AuditStreamStore.append()` — 实时 + 持久双通道。

## 安全与不变量

- `AuditEvent` 核心字段（ts/actor/source/action/result）强制有效，缺字段即失败关闭；
- 敏感文本只保留哈希/计数（detail → detail_hash + reasons 列表），不落明文业务数据；
- 哈希链 `prev_hash → record_hash`，篡改即断链；store 尺寸增量与磁盘逐字节一致
  （含 `os.linesep` 补偿）；
- 导出内容哈希稳定（同一数据同一导出 → 同一 SHA-256）。

## 性能与复杂度

- `AuditStreamStore` 追加记录免逐条 `stat()`，尺寸增量维护与磁盘逐字节一致
  （含 `os.linesep` 补偿）；
- 查询游标分页按 `record_hash` 定位，limit 硬上限 10000，防无界扫描。

## 测试覆盖

- `tests/unit/test_audit_governance.py`（29 项：事件/拦截/查询/导出/投影）；
- `tests/unit/test_audit_stream.py`、`test_audit_stream_store.py`；
- `tests/integration/test_audit_stream.py`；`tests/security/test_audit_log.py`、
  `test_audit_seal.py`。

## 依赖与下游

- **上游依赖**：各领域模块的 `to_audit_record` 投影；
- **下游消费者**：驾驶舱审计查询（`tests/e2e/test_cockpit_offline_frontend.py`）、
  `examples/service-api` 审计服务。

## 错误语义

- `AuditEventValidationError` / `AuditQueryValidationError`：事件/查询载荷非法；
- `AuditGovernanceError`：门面级错误；`AuditStreamStoreError`：持久化/断链；
- 哈希链篡改、追加独占冲突、尺寸越界一律失败关闭。
