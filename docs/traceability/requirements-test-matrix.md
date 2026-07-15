# Requirements ↔ Code ↔ Test Matrix

| 故事 | AC | 行为简述 | 代码入口 | 测试文件 | 门禁结果 | 状态 | 最近变更 commit |
|---|---|---|---|---|---|---|---|
| ENG-BASE | AC-1 | 失败关闭、离线工程底座与签名审计链头 | `scripts/validate_opencode.py`; `scripts/quality_gate.py`; `scripts/loop_state.py`; `scripts/audit_log.py`; `scripts/audit_seal.py`; `scripts/audit_signature.ps1`; `.opencode/tools/`; `.opencode/plugins/path-policy.mjs` | `tests/unit/test_engineering_baseline.py`; `tests/unit/test_traceability_check.py`; `tests/integration/test_tool_contracts.py`; `tests/security/test_audit_log.py`; `tests/security/test_audit_seal.py`; `tests/security/test_loop_state_transaction.py`; `tests/security/path_policy_test.mjs`; `tests/e2e/test_offline_baseline.py` | pass `31c1e373bc9aad53`; verifier pass; security pass | done | 未获初始提交授权 |
| US-0 | AC-1 | 建立用户 / 客户端 / 证书数据模型 | `src/coevo/identity/models.py`; `src/coevo/identity/certificates.py`; `src/coevo/identity/validation.py`; `src/coevo/identity/audit_anchor.py`; `src/coevo/identity/repository.py`; `src/coevo/identity/service.py`; `src/coevo/identity/schema.sql`; `scripts/inspect_certificate.ps1`; `scripts/identity_freshness.ps1` | `tests/unit/test_identity_validation.py`; `tests/integration/identity_store_test.py`; `tests/security/test_identity_store_security.py`; `tests/security/test_identity_freshness_security.py`; `tests/security/test_identity_retirement_security.py`; `tests/e2e/test_identity_dev_environment.py` | quality pass `89fc6674ab3f37d9`; verifier pass; security pass (Critical 0, High 0) | done | 未获初始提交授权 |
| US-0 | AC-2 | 实现私钥安全存储接口 | — | `tests/security/private_key_storage_test.py` | pending | ready | — |
| US-5 | AC-1 | `.agent` 固定包头与 Envelope 编码 | — | `tests/integration/package_header_test.py` | pending | blocked | — |

工程底座已完成，但不代表全部产品用户故事已经完成。RSA-3072/SHA-256 签名仅限开发原型；正式环境必须替换为批准的 SM2 产品。
