---
name: acceptance-testing
description: 验收测试方法学——把用户故事 AC 落到可重复、可独立运行的测试用例（含安全与异常输入），供 mvp-verifier 与人工审计使用。当需要设计/检查验收测试、安全测试用例或追溯矩阵条目时使用。
---

## 权威文件

- `docs/requirements/mvp-user-stories.md`
- `docs/constraints/mandatory-technical-constraints.md`
- `docs/protocol/agent-package-protocol.md`（若涉及 `.agent`）
- `docs/traceability/requirements-test-matrix.md`

## 测试层级

| 层级 | 工具 / 路径 | 范围 | 何时运行 |
|---|---|---|---|
| 单元 | `tests/unit/...` | 函数与类的正确性 | 每次 `make test` |
| 集成 | `tests/integration/...` | 模块协作与外部依赖 | 每次 `make test` |
| 安全 | `tests/security/...` | 强制约束的硬性边界 | `make test-security` |
| 端到端 | `tests/e2e/...` | 真实用户故事闭环 | `make test-e2e` |

## 编写规则

1. 每个 AC 至少 1 个正向用例 + 1 个异常输入用例（异常必须含具体证据）。
2. 安全 AC 必须覆盖：注入、穿越、越权、签名错误、过期包、重复包、未授权接收人、压缩炸弹。
3. 测试用例不得跳过（`skip`/`xfail` 须在矩阵中显式登记）。
4. 测试输出必须稳定、可指纹化（命令、退出码、关键输出片段）。
5. 测试不得依赖远程服务、随机时间戳、未固定随机种子。

## 验收门禁

`make quality` 必须全绿；否则视为 `fail`，触发返工或 `blocked`。
