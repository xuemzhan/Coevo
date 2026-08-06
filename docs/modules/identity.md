# `identity/` — 身份与信任（US-0）

## 定位

离线身份与信任：用户/客户端/组织/证书/角色绑定登记、X.509 受控检查、私钥句柄
接口（私钥字节永不进进程）、SQLite 持久化与签名审计锚点。

## 职责边界

- **in scope**：身份包五要素互锁校验、证书解析、私钥句柄元数据与策略、审计锚；
- **out of scope**：`.agent` 包级加密/签名（`protocol/`）、CNG 底层实现
  （`crypto/cng_handle`）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `Actor`、`UserIdentity`、`ClientIdentity`、`TrustedCertificate`、`ProjectRoleBinding` | 身份/证书/角色绑定不可变模型（证书指纹 SHA-256 唯一） |
| `validation.py` | `validate_bundle()`、`reject_sensitive_input()` | 入库存前严格校验：敏感键拒绝、角色码闭集、证书可用性 |
| `certificates.py` | `inspect_certificate()` | X.509 经受控 PowerShell 助手解析（输入输出 DER 摘要一致，防替包） |
| `private_keys.py` | `PrivateKeyReference`、`PrivateKeyService` | 私钥句柄接口：仅元数据引用；有效期/吊销/销毁策略 + 哈希链审计 |
| `repository.py` | `IdentityRepository` | SQLite 持久化：五表原子注册 + 证书指纹唯一约束 + 审计锚 |
| `service.py` | `IdentityService.register_identity_bundle()` | 鉴权 → 校验 → 注册 → 审计；request_id 幂等（replayed=True） |
| `audit_anchor.py` | `SignedAuditAnchor` | 签名审计头 + 每代不可导出新鲜度（防回滚/防篡改） |

## 关键入口与数据流

```
身份包 → IdentityService.register_identity_bundle（鉴权→validate_bundle→注册→审计）
  → IdentityRepository（五表原子写 + 审计锚）→ 后续 identity:use 校验
```

- `PrivateKeyService.use/verify/store` — 只经受控 CNG 助手完成密码运算；
- `SignedAuditAnchor.prepare/promote/recover` — 数据库绑定摘要链 + 签名检查点。

## 安全与不变量

- **私钥字节、口令永不进入 Python 进程**；句柄载荷拒绝私钥/口令启发式字段；
- 证书指纹唯一约束冲突即回滚并记 `conflict`；重复 request_id 幂等不重复写；
- 审计锚签名链 + 新鲜度单调校验，失败关闭；敏感字段只留哈希/摘要。

## 测试覆盖

- `tests/unit/test_identity_validation.py`、`test_private_key_handles_bindings.py`；
- `tests/integration/identity_store_test.py`、`private_key_windows_store_test.py`；
- `tests/security/test_identity_store_security.py`、`test_identity_freshness_security.py`、
  `test_identity_retirement_security.py`、`test_private_key_storage.py`；
- `tests/e2e/test_identity_dev_environment.py`。

## 依赖与下游

- **上游依赖**：`crypto/cng_handle`、`scripts/inspect_certificate.ps1`、
  `scripts/store_private_key.ps1`；
- **下游消费者**：`protocol/`（接收人绑定、签名权威）、`merge/`（决策者白名单）、
  `decision_brief/`（owner 签名确认）。
