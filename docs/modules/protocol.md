# `protocol/` — 任务包协议（US-5，`.agent`）

## 定位

`.agent` 任务包线格式：Fixed/Envelope 头、SM2 封钥、SM4 AEAD 载荷、SM3/SM2 签名、
重放检测与原子导入。严格遵循 `docs/protocol/agent-package-protocol.md`。

## 职责边界

- **in scope**：36 字节 Fixed Header + 规范 Envelope、密钥传输块、认证加密载荷、
  签名、已处理包登记、重放/重复检测、7 步原子导入事务；
- **out of scope**：批准密码产品接入（预留，未批准算法显式拒绝）、工作区初始化
  （`workspace/`）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `agent_package.py` | `EnvelopeHeader`、`FixedHeader`、`parse_package_header()` | Fixed/Envelope 头编解码（字节精确、规范 JSON、长度双向一致、拒绝未知标志/尾随数据） |
| `agent_payload.py` | `PayloadBlock` | SM4 AEAD 载荷层（nonce/ciphertext/tag 校验） |
| `sm2_keywrap.py` | `encode_key_transport_bytes()` | SM2 密钥传输块 |
| `sm2_sign.py` | `compute_sm3_digest()`、签名/验签 | SM2 签名 + SM3 摘要层 |
| `sm2_extension.py` | — | 未来批准算法标识占位（fail-closed） |
| `package_builder.py` | `build_encrypted_package/open_encrypted_package` | 端到端构建/解析（签名阻断、回读校验、句柄证书一致性） |
| `replay_detector.py` | `check_replay()`、`check_reference_target()` | 重放/重复/撤销/非法引用检测（§17 全情况） |
| `import_transaction.py` | `AtomicImporter`、`ImportTransaction` | 原子导入 7 步事务状态机（失败回滚不留半态） |
| `import_service.py` | `PackageImportService.import_package()` | 导入门面：重放门 + 固定头一致性 + 显式版本要求 |
| `processed_package_store.py` | `ProcessedPackageStore` | 已处理包内存登记（package_id/摘要去重 + 索引） |
| `package_store_db.py` | SQLite 持久化注册 | 已处理包 SQLite：哈希链 + 逐行校验 + 唯一约束 |

## 关键入口与数据流

```
构建：状态/清单 → build_unsigned_package → SM2 封钥 + SM4-GCM 加密 → 发送方签名
  → Fixed/Envelope 头 → .agent 文件
导入：隔离区 → parse_package_header → 接收人/版本/重放检查 → 解密验签
  → 文件校验 → PackageImportService（7 步事务）→ 工作区初始化
```

- `build_encrypted_package/open_encrypted_package`；
- `PackageImportService.import_package`（无显式 base/current revision 拒绝导入，
  防伪造主版本）；
- `AtomicImporter.begin/advance/fail/check_replay`。

## 安全与不变量

- 规范 JSON（拒绝重复键、非规范空白、BOM）；固定头三长度与真实块一致性校验；
- 重放/重复/撤销/非法引用检测失败关闭；同一包重复导入不得重复生效；
- 原子导入失败回滚不留半态；异常包留在隔离区；
- 未批准算法显式拒绝；私钥/口令不进入协议层（经受控句柄）。

## 测试覆盖

- `tests/integration/package_header_test.py`（56 项）、`package_header_extended_test.py`、
  `test_agent_package_aead.py`（35 项）、`test_agent_package_atomic_import.py`（23 项）、
  `test_package_store_persistence.py`；
- `tests/unit/test_protocol_sign_blocked.py`、`test_package_store_persistence.py`；
- `tests/e2e/test_demo_runner.py`、`test_return_chain.py`。

## 依赖与下游

- **上游依赖**：`crypto`（密码运算）、`identity`（证书/句柄）、
  `docs/protocol/agent-package-protocol.md`；
- **下游消费者**：`workspace`、`merge`、`report`、`orchestrator`、`cockpit`。
