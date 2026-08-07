# A2A wire 0.1 与 policy_ref 三段绑定（CTAF §7.3 / M5）

> 里程碑：M5（2026-08-08 交付）。实现：`src/coevo/framework/a2a.py`。
> 工作项：`US-16-AC-6-a2a-wire-v0.1`。

## 定位

把 A2A 消息抽象为纯数据信封（`A2aMessage`），随 `.agent` v1.0 加密包承载
（wire 字节不变，T6 守护）；正式化 §7.3.2 `policy_ref` 三段绑定与 §7.3.3
五步验证时序。

## 字段映射（§7.3.1）

| A2A 字段 | `.agent` 字段 |
| --- | --- |
| task_id | package_id |
| trace_id | trace_id（64-hex） |
| sender_cert_id / recipient_cert_id | 同名 |
| sequence_no | sequence_no（包级重放） |
| business_correlation_key | 同名（业务去重） |
| purpose | task_type（能力闭集） |
| policy_ref | policy_ref（三段绑定） |
| payload_ref | payload_ref（RESULT_SUBMISSION 拆分引用） |
| created_at | created_at |

## 五步验证（§7.3.3）

1. 按 `signer_cert_fingerprint` 从证书链解析 sender 证书 DER（注入 resolver）；
2. `sha256(证书 DER) == signer_cert_fingerprint`，否则冒名拒绝；
3. `spec_hash == manifest_spec_hash(manifest_bytes)`（排除自指字段的规范哈希，
   复用 manifest-checker）；
4. 用证书公钥验 SM2 签名（数据 = spec_hash | fingerprint），失败拒绝；
5. 通过 → accepted；任何注入异常 → fail-closed 拒绝。

## 大小边界（AC-6.4）

- A2A 信封内联载荷 ≤ 64 KiB；
- 业务载荷 > 64 KiB 必须拆为 `RESULT_SUBMISSION` 包并以合法 `payload_ref`
  引用；无引用或引用非法即拒绝；
- 放宽 envelope 上限须 `.agent` 协议主版本升级。

## 安全边界

- 验签公钥只来自证书链，绝不取自消息自身（防公钥自包）；
- 能力闭集（purpose）复用框架注册表；审计投影键集固定；
- 纯函数、仅标准库、可离线运行（L15）；文档守卫（L17）。

## 测试覆盖

`tests/unit/test_framework_a2a.py`（AC-6.1..6.5，含五步各失败支路、注入异常、
映射往返、大小边界、审计投影、stdlib 断言）。
