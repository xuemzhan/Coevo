# Memory 抽象接口（CTAF §6.2 / M3）

> 里程碑：M3（2026-08-08 交付）。实现：`src/coevo/framework/memory.py`。
> 工作项：`US-16-AC-4-framework-memory-interface-v0.1`。

## 定位

框架层把记忆写入抽象为统一 `MemoryRecord` 模型，在写入边界强制三条不变量：

1. **可哈希**：`record_id` 为排除自指字段后的规范化 JSON SHA-256 指纹；
2. **审计投影**：每条 Episodic 写入必产生 `MemoryWriteResult.to_audit_record()`
   （accepted / record_id / kind / occurred_at / failure_reason）；
3. **L12 脱敏**：敏感字段经注入 `Redactor` 转 `REDACTED:<sha256>` 摘要后才到达
   store，明文不跨写入边界。

## 两类记忆与既有模块适配

| 类别 | 框架模型 | 生产适配（不改既有实现） | 写入约束 |
| --- | --- | --- | --- |
| Episodic | `MemoryKind.EPISODIC` | `EpisodicMemoryStore.append` → `progress_capture/` 捕获事件流 | 审计投影必填；store 异常 fail-closed |
| Semantic | `MemoryKind.SEMANTIC` | `SemanticMemoryStore.ingest` → `knowledge_base/` 知识入库 | 必须经 `SemanticApprovalChecker.is_approved`（映射既有 `ReviewDecisionKind.APPROVE`），未审批拒绝 |

## 注入协议

- `Redactor.redact(value) -> str`：不可恢复摘要（生产可复用 `talent/redaction.py`
  的 RedactedIdentity 摘要约定）；
- `EpisodicMemoryStore.append(record)` / `SemanticMemoryStore.ingest(record)`；
- `SemanticApprovalChecker.is_approved(record) -> bool`。

任何注入异常一律转为 `MemoryWriteResult(accepted=False, failure_reason)`，
绝不静默放行。

## 信任边界与设计说明（security-review 观察项留痕）

- **Semantic 审批检查器接收脱敏前的明文 record**（L12 只约束 store 边界）：
  生产适配器（knowledge_base 侧）不得将审批入参落盘、记日志或外传；
- **拒绝写入的审计投影含 `record_id`（明文内容指纹）**：由 AC-4.1/4.2 共同决定，
  属设计使然；生产 `Redactor` 应采用加盐/密钥化摘要构造，抬高低熵值的字典
  恢复成本，不得使用裸 SHA-256；
- 审计投影对畸形 kind 做防御性取值（不抛异常）。

## 安全边界

- L12 是红线：明文 PII 不得到达 store；未声明为敏感字段却带 `REDACTED:` 值
  的记录拒绝（防脱敏字段语义漂移）；
- Redactor 产出非摘要格式 → 拒绝；
- 纯函数、仅标准库、可离线运行（L15）；模块文档守卫（L17）。

## 测试覆盖

`tests/unit/test_framework_memory.py`（AC-4.1..4.5，含审批拒绝、store/redactor
异常、L12 明文隔离、非敏感字段红值拒绝等负例）。
