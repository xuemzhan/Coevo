# `crypto/` — 国密引擎适配（SM2/SM3/SM4）

## 定位

密码提供者契约、作用域治理与受保护密钥句柄路径；MVP 原型用锁定 GmSSL 3.2.0 +
纯 Python SM3。正式系统必须替换为批准的密码产品/模块（见
`docs/dependencies/approved-crypto-provider-path.md`）。

## 职责边界

- **in scope**：提供者注册与作用域校验、一次性助手进程调用、CNG 句柄背书的
  密钥操作、纯 Python SM3 实现；
- **out of scope**：业务密钥生命周期策略（`identity/private_keys`）、包级
  密码信封（`protocol/`）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `contract.py` | `ProviderScope`、`CryptoProvider`、`ProviderRegistry` | 提供者契约与作用域治理（未知作用域失败关闭） |
| `gmssl_provider.py` | `GmsslPrototypeProvider`（seal/open/sign/verify/sign_wrapped） | 锁定 GmSSL 3.2.0 一次性助手进程客户端；启动级瞬时失败有界重试，密码级错误绝不重试 |
| `protected_provider.py` | `GmsslProtectedProvider` | CNG 句柄背书的提供者（HANDLE-1/2 路径） |
| `cng_handle.py` | `CngProtectedKeyHandle`、`CngKekStore` | CNG 保护的 SM2 密钥句柄：KEK 包装、注册/吊销/销毁 |
| `key_handle.py` | `ProtectedKeyHandle`、`KeyHandleBacked` | 受保护密钥句柄抽象 |
| `sm3.py` | `sm3_digest()`、`sm3_hexdigest()` | 纯 Python SM3（GB/T 32905-2016），确定性 |

## 关键入口与数据流

```
调用方 → ProviderRegistry.resolve(provider_id, scope)
  → GmsslPrototypeProvider._invoke（帧协议，PowerShell 受控启动）
  → 助手进程完成密码运算 → 仅返回结果
```

- `GmsslPrototypeProvider.seal/open/sign/verify` — SM4-GCM/SM2 运算（一次性助手）；
- `sign_wrapped/open_wrapped` — CNG KEK 包装密钥的签名/解密（密钥字节只存助手侧）；
- `protect_key` — 用 CNG KEK 包装 SM2 私钥（仅返回包装结果）。

## 安全与不变量

- **私钥字节、私钥口令、解封后的会话密钥永不进入 Python 进程**；
- 助手启动器路径经 `toolchain-lock.json` 大小 + SHA-256 锁定，篡改即拒绝；
- 会话密钥/Nonce 来自密码学安全随机源；请求帧有界（16 MiB），响应帧严格校验；
- 助手诊断符合 `GCP-E-*` 才视为权威错误，否则按启动级瞬态有界重试。

## 测试覆盖

- `tests/unit/test_crypto_contract.py`、`test_crypto_provider_registry.py`、
  `test_crypto_sm3.py`、`test_gmssl_provider_retry.py`；
- `tests/integration/test_gmssl_prototype_provider.py`、`test_crypto_sm3.py`、
  `test_cng_handle.py`、`test_sm2_test_pki_generation.py`。

## 依赖与下游

- **上游依赖**：`docs/dependencies/toolchain-lock.json`（助手锁定）、PowerShell；
- **下游消费者**：`identity/private_keys`、`protocol/`（包加密签名）、`app/pipeline`。
