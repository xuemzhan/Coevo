# docs/

本目录是唯一的需求与工程约束基线。任何 Agent 在引入新需求、修改行为、调整协议、依赖或删除既有约束时，必须修改本目录下的文件并同步更新 `traceability/requirements-test-matrix.md`。

## 目录结构

| 子目录 / 文件 | 内容 | 唯一权威 |
|---|---|---|
| `requirements/` | 系统原始需求、MVP 用户故事及验收标准 | `system-requirements.md`、`mvp-user-stories.md` |
| `constraints/` | 强制性技术约束（含密码方案、私钥保护、审计链等硬约束） | `mandatory-technical-constraints.md` |
| `architecture/` | MVP 参考架构与技术选型 | `mvp-reference-architecture.md` |
| `protocol/` | `.agent` 任务包协议规范 | `agent-package-protocol.md` |
| `traceability/` | 需求—代码—测试追踪矩阵 | `requirements-test-matrix.md` |
| `dependencies/` | 经批准工具的精确版本、来源、哈希与许可证 | `toolchain-lock.json` |
| `development-environment.md` | 本地开发环境入口、使用方法和离线边界 | `development-environment.md` |

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
