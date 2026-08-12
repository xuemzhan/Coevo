# `sync/` — 跨节点同步（信封契约 / 出站队列 / 对账）

## 定位

跨节点同步协议的可执行契约与离线优先实现：把各节点事件按顺序、可防重放地
汇聚到中心端。设计见 `docs/architecture/sync-protocol.md`
（PRODUCT-REVIEW T-11 契约、T-12 离线文件式实现）。

## 职责边界

- **in scope**：信封字段/版本/顺序/防重放校验、单节点追加式出站链、只读对账、
  文件包导出/导入（与 `.agent` 同思路）；
- **out of scope**：负载内容签名（依赖批准密码产品，见 sync-protocol.md §6）、
  受控网络传输与中心端聚合（DESIGNED）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `contract.py` | `SyncEnvelope`、`validate_envelope`、`envelope_digest`、`validate_chain`、`SYNC_SCHEMA_VERSION` | 信封契约：字段/版本/ISO 时间/64 位 hex 摘要、哈希链、单调序号、event_id 防重放 |
| `store.py` | `SyncOutbox`、`SyncRecord`、`SyncReconciler`、`ReconcileResult`、`export_bundle`、`load_bundle` | 单节点追加式出站链（JSONL 持久化）、只读对账（新事件/重放/缺口）、文件包传输（篡改失败关闭） |

## 关键入口与数据流

```
事件 → SyncOutbox.append（序号+哈希链+防重放）→ export_bundle（文件包）
  → 接收方 load_bundle（整链校验）→ SyncReconciler.reconcile（对账/缺口/重放）
```

## 安全与不变量

- 失败关闭：字段非法、版本未知、序号跳变、哈希链断裂、event_id 重复一律拒绝；
- 离线优先：无网络调用，文件包传输不违反全程离线约束；
- 负载完整性签名与在线传输为后续项（sync-protocol.md §6）。

## 测试覆盖

- `tests/unit/test_sync_protocol_contract.py`：字段/版本/顺序/重放防护/哈希链；
- `tests/unit/test_sync_store.py`：顺序/链路/重放/单源约束/持久化/对账/
  导出导入/篡改拒绝。

## 依赖与下游

- **上游**：`src.coevo.timefmt`（ISO 校验）、标准库 json/hashlib；
- **下游**：未来受控网络传输与中心端聚合（DESIGNED）。
