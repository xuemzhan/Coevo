# 密码模式隔离契约（Crypto Mode Isolation）

> 状态：生效（2026-08-10，REVIEW2-6）
> 适用范围：`src/coevo/crypto`（contract / gmssl_provider / protected_provider）的模式边界。

## 1. 模式定义

- **prototype（`ProviderScope.MVP_PROTOTYPE`）**：开源 GmSSL 原型，
  `key_handle_backed=False`。仅限研发验证/演示（demo composition root 显式使用）。
- **production（`ProviderScope.APPROVED_PRODUCT`）**：批准密码产品，
  `key_handle_backed=True`（受保护、不可导出的密钥句柄）。

## 2. 启动守卫（不是调用时才失败）

- `crypto_mode(provider)` 显式报告 `prototype` / `production`，未声明或未知 scope
  一律 fail-closed；
- `require_production_crypto(provider)` 是**生产组合根的启动前置**：mode 非
  production 或 `key_handle_backed != True` 立即抛错——原型提供者在启动即被拒绝，
  而不是等到某次加密调用才失败；
- `ProviderRegistry.require_approved(name)` 同样拒绝原型（resolve 后
  `validate_provider_scope` + key-handle 校验）。

## 3. 接线要求

- 演示/研发路径：`GmsslPrototypeProvider`（`mvp-prototype`）——显式标注，不得冒充批准产品；
- 生产路径：组合根在**任何加密操作之前**调用 `require_production_crypto`，并接入
  `GmsslProtectedProvider`（`approved-product` + `key_handle_backed=True`）；
- US-5-AC-2 正式 SM2 产品接入前，不存在可满足 production 守卫的真实组合根——
  这是已知外部审批依赖，不因"门禁可用"而宣称生产就绪。

## 4. 守卫测试

`tests/unit/test_review2_6_crypto_isolation.py` 强制：模式报告、未声明 fail-closed、
生产守卫拒绝原型/无句柄、注册表拒绝原型、真实 GmSSL 原型恒为 prototype、契约文档存在。

## 5. 变更纪律

任何改变 scope 语义、密钥句柄要求或启动守卫的改动，必须同步本契约并在
`loop/DECISIONS.md` 留痕。
