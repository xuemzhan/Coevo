# `app/` — 应用组合根（演示流水线）

## 定位

把 `src/coevo` 各领域门面按“固定编排链”装配成可离线复现的端到端演示闭环，
是 `scripts/run_demo.py` 与 e2e 测试（`tests/e2e/test_demo_runner.py`、
`test_return_chain.py`）的官方入口。只做装配与调度，**不含领域逻辑**。

## 职责边界

- **in scope**：PKI/测试密钥引导、真实链执行编排、加密任务包导出与回读校验、
  驾驶舱快照/服务、知识包聚合、审计流串联；
- **out of scope**：任何领域规则、持久化、密码运算实现（全部委托给下层门面）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `pipeline.py` | `run_demo_pipeline()` | 七阶段演示流水线（PKI 引导 → 真实链 → 加密包 → 驾驶舱 → 知识 → 审计） |
| `demo_support.py` | `DemoSigner`、`DemoFreshnessAuthority`、`DemoRegistrationVerifier`/`DemoRegistrationResolver`/`DemoPolicyRegistry`、`ensure_demo_profile()`、`sample_project_input()` | 演示专用支撑：SM2 测试 PKI 引导、模拟签名/新鲜度权威、注册门演示适配器（**显式非生产**，生产须注入真实 SM2 验签）、业务化样例输入 |

## 关键入口与数据流

```
样例输入 → 流程理解(US-1) → 基线(US-2) → 人才推荐(US-3) → 人工确认
  → 加密包导出(US-5) → 回读校验 → 驾驶舱快照(US-7) → 知识包(US-14) → 审计流(US-15)
```

- `run_demo_pipeline(...)` — 一键跑通完整演示闭环，返回 `DemoResult`；
- `ensure_demo_profile()` — 引导 SM2 测试 PKI（幂等，仅演示）；
- `sample_project_input()` — 生成跨单位小工具开发样例输入。

## 安全与不变量

- 全流程离线：无网络请求、无运行时下载、无第三方在线服务；
- Python 进程不接触私钥字节（密码运算只经 `GmsslPrototypeProvider` 受控路径）；
- 演示替身（HMAC 签名、内存新鲜度权威）**显式标注非生产**；生产签名走
  `identity/private_keys` + `crypto/cng_handle` 受保护句柄；
- 注册门演示适配器（`DemoRegistrationVerifier` 对任意良构签名返回 True 等）
  **仅限演示**：生产注册必须注入真实 SM2 验签器与证书链，否则不提供身份保证；
- 加密包生成后立即回读校验（解密 + 验签），失败即中止，不留半成品。

## 测试覆盖

- `tests/e2e/test_demo_runner.py` — CLI 冒烟、真实包 + 持久化、驾驶舱服务启停；
- `tests/e2e/test_return_chain.py` — 真实加密汇报包驱动 合并→风险→简报→知识 全链。

## 依赖与下游

- **上游依赖**：`orchestrator`（真实链）、`protocol`（包构建）、`cockpit`（驾驶舱）、
  `knowledge_base`、`audit_governance`、`crypto`；
- **下游消费者**：`scripts/run_demo.py`、e2e 测试、`examples/` 演示体系。
