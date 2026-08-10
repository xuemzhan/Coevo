# docs/

本目录是唯一的需求与工程约束基线。任何 Agent 在引入新需求、修改行为、调整协议、依赖或删除既有约束时，必须修改本目录下的文件并同步更新 `traceability/requirements-test-matrix.md`。

## 目录结构

| 子目录 / 文件 | 内容 | 唯一权威 |
|---|---|---|
| `requirements/` | 系统原始需求、MVP 用户故事及验收标准 | `system-requirements.md`、`mvp-user-stories.md` |
| `constraints/` | 强制性技术约束（含密码方案、私钥保护、审计链等硬约束） | `mandatory-technical-constraints.md` |
| `architecture/` | MVP 参考架构、技术选型、编排器 seam 契约、离线合并收敛语义、门禁分层与两阶段化策略、.agent 签名承载契约、WPS 启动链路契约、HTTP 认证黑盒矩阵、密码模式隔离契约、状态变更边界契约、显式事件模型契约、断网黑盒证明、审计日志代际重锚定契约、交付门禁契约、能力状态矩阵、验收指标 SLO 契约、决策记录治理契约、子智能体 Manifest 注册表契约、审计签名密钥仪式契约、外部依赖与待批门登记、MVP 完成度就绪评估、Ports & Adapters 分层契约 | `mvp-reference-architecture.md`、`orchestrator-seam.md`、`merge-convergence.md`、`gate-tiers.md`、`gate-phases.md`、`agent-signature-carrier.md`、`wps-launch-contract.md`、`http-auth-matrix.md`、`crypto-mode-isolation.md`、`state-change-boundary.md`、`event-model.md`、`offline-proof.md`、`audit-reanchor.md`、`delivery-gate.md`、`capability-status.md`、`slo-metrics.md`、`decision-records.md`、`agent-manifest-registry.md`、`audit-key-ceremony.md`、`external-gates.md`、`mvp-complete-readiness.md`、`ports-adapters.md` |
| `protocol/` | `.agent` 任务包协议规范 | `agent-package-protocol.md` |
| `traceability/` | 需求—代码—测试追踪矩阵 | `requirements-test-matrix.md` |
| `dependencies/` | 经批准工具的精确版本、来源、哈希与许可证 | `toolchain-lock.json` |
| `process/` | 独立双签、只读沙箱、记录归档等治理流程 | `independent-review-governance.md` |
| `operations/` | 生产运维手册（配置参考、安装/升级/回滚、审计密钥恢复、健康检查/自启/排障） | `configuration-reference.md`、`install-upgrade.md`、`audit-key-runbook.md`、`ops-runbook.md` |
| `plans/` | 各工作项的切片规划（历史） | `*.md` |
| `framework/` | CTAF 框架层设计与适配映射（manifest / capability / policy / plan / memory / tools / a2a / k8s / hybrid / integration / plan-lsp） | `*.md` |
| `development-environment.md` | 本地开发环境入口、使用方法和离线边界 | `development-environment.md` |
| `production-readiness.md` | MVP 生产可用性说明（配置/停机/日志/版本/性能） | `production-readiness.md` |
| `audit-signing.md` | 审计签名原型与正式密码方案边界 | `audit-signing.md` |

## 生产运维文档

面向部署与运维的权威入口：

| 文档 | 用途 |
|---|---|
| `operations/configuration-reference.md` | 全部 `COEVO_*` 环境变量登记表（代码 ⇄ 文档一致性由测试校验） |
| `operations/install-upgrade.md` | 离线安装 / 升级 / 回滚 / 卸载 |
| `operations/audit-key-runbook.md` | 审计签名密钥健康诊断与恢复 |
| `production-readiness.md` | 生产可用性基线（配置/优雅停机/日志/版本/性能） |

## 冲突优先级

发生冲突时，按以下顺序裁决：

1. `constraints/mandatory-technical-constraints.md`
2. `protocol/agent-package-protocol.md`
3. `requirements/mvp-user-stories.md`
4. `architecture/mvp-reference-architecture.md`
5. 代码现状

任何优先级更低的文档都不得改写优先级更高的文档；如确有冲突须在 `loop/DECISIONS.md` 留痕。

## 同步约定

- 修改需求 → 同步更新追踪矩阵并新增测试用例占位。
- 修改协议 → 同步更新 Schema、版本判断、兼容测试与异常输入测试。
- 修改约束 → 必须在 PR 中显式列出受影响的用户故事。
- 引入或升级工具 → 先审批，再锁定官方来源、精确版本、构件大小、SHA-256、许可证和运行时依赖；运行时不得自动下载。
