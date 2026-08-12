# 跨节点同步协议设计（Sync Protocol）

> 状态：设计 + 离线优先实现（2026-08-12；PRODUCT-REVIEW T-11 契约、T-12
> 离线文件式传输与对账已落地；受控网络传输仍为 DESIGNED）。
> 可执行契约：`src/coevo/sync/contract.py`（信封校验、哈希链、防重放）。

## 1. 定位与范围

中心端/跨节点同步把各节点的事件（编排、确认、合并、审计）按顺序安全地汇聚到
中心端，并支持对账。当前 MVP 用 `.agent` 加密任务包做**人工离线搬运**；本协议
为未来自动同步（受控网络形态）定义信封与秩序，不改变离线包协议。

## 2. 信封契约

```text
SyncEnvelope {
  schema_version: "0.1"
  source_node:    safe-id（节点标识）
  event_id:       safe-id（事件标识）
  sequence:       int > 0（每节点单调递增）
  created_at:     ISO-8601 UTC Z
  payload_digest: sha256-64hex（事件负载摘要）
  previous_hash:  sha256-64hex（前一信封摘要；首封为 64 个 0）
}
```

校验规则（`validate_envelope` / `validate_chain`）：

- 字段类型、safe-id、ISO 时间、64 位小写 hex 摘要一律失败关闭；
- **顺序**：每节点 `sequence` 严格 +1，缺失即拒绝；
- **哈希链**：`previous_hash` 必须等于前一信封摘要，防篡改/丢包；
- **版本**：`schema_version` 闭集，未知版本拒绝；
- **重放防护**：每节点 `event_id` 唯一，重复即拒绝。

## 3. 冲突处理

冲突指同一事件在不同节点产生不同结果：

1. 以**权威回执**（merge receipt，US-10）为准，字段级决策；
2. 乱序到达由 `sequence` 排序 + 缺失检测触发重拉；
3. 冲突记录进审计链（`to_audit_record` 投影），不静默覆盖。

## 4. 与离线模型的关系

- 离线：`.agent` 包（US-5）+ 工作区（US-6）人工搬运，本协议不参与；
- 在线（后续）：节点经本协议向中心端推送事件信封，中心端对账后广播；
- 双模式范围见 `online-mode-scope.md`（在线为设计态）。

## 5. 实现状态与守卫

- `src/coevo/sync/contract.py`：信封契约（T-11 已落地，可执行）；
- `tests/unit/test_sync_protocol_contract.py`：字段/版本/顺序/重放防护/哈希链
  全测；
- `src/coevo/sync/store.py`（T-12 已落地）：
  - `SyncOutbox`：单节点追加式出站链（哈希链 + 单调序号 + event_id 防重放），
   持久化为规范 JSONL；
  - `SyncReconciler`：只读对账（校验入站链、识别新事件/重放/缺口）；
  - `export_bundle` / `load_bundle`：文件式传输（与 `.agent` 同思路），
    篡改链字段失败关闭；
- `tests/unit/test_sync_store.py`：顺序/链路/重放/单源约束/持久化/对账/
  导出导入/篡改拒绝全测。

## 6. 后续项

- **负载完整性签名**：当前链校验保护信封链接与顺序，不校验负载内容本身；
  正式负载完整性依赖信封签名（经批准密码产品，US-5-AC-2 后接入）；
- **受控网络传输**：文件包已验证同一信封格式；在线推送/拉取、中心端聚合与
  重拉协议仍为 DESIGNED（见 `online-mode-scope.md`）。
