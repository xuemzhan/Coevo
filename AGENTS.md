# 分布式任务管理具身智能体系统开发规则（Coevo）

本仓库遵循 Loop Engineering 模式：`/loop` 命令只推进一个最小工作项，且必须由独立验证与独立安全审查共同放行。`opencode` 仅是执行工具，所有权威规则都沉淀在文档与状态文件里。

## 1. 权威输入

任何 Agent 在动手前必须阅读：

- `docs/requirements/system-requirements.md`
- `docs/requirements/mvp-user-stories.md`
- `docs/constraints/mandatory-technical-constraints.md`
- `docs/architecture/mvp-reference-architecture.md`
- `docs/protocol/agent-package-protocol.md`
- `loop/GOAL.md`
- `loop/STATE.json`（最近一次循环结果）
- `loop/VERIFICATION.md`（最近一次门禁记录）

文档冲突时优先级：

1. 强制性技术约束
2. `.agent` 任务包协议规范
3. MVP 用户故事及验收标准
4. MVP 参考架构
5. 代码现状

不得自行降低安全要求。优先级越低的文档不得改写优先级越高的文档；如确有冲突须记入 `loop/DECISIONS.md`。

## 2. 开发方式（七个固定阶段）

每个循环只处理一个用户故事或一个可验证切片：

1. **DISCOVER**：阅读需求、既有代码、既有测试、当前 `git diff`。
2. **PLAN**：调用 `mvp-planner` 生成最小可交付切片、影响范围、测试点和风险。
3. **IMPLEMENT**：调用 `mvp-builder` 实现本轮范围，**测试同步提交**。
4. **VERIFY**：调用 `mvp-verifier` 实际执行质量门禁（`make quality`）。
5. **REVIEW**：涉及协议时调 `protocol-reviewer`；涉及身份/密钥/文件解析/权限/审计时调 `security-reviewer`。
6. **RECORD**：更新 `loop/STATE.json`、`loop/VERIFICATION.md`、`docs/traceability/requirements-test-matrix.md`、`loop/DECISIONS.md`、`loop/tool-audit.jsonl`。
7. **DECIDE**：标记 done / 返工 / blocked，进入下一故事或停轮。

## 3. 强制边界

- 不得删除或降低既有安全测试。
- 不得用时间戳代替项目版本。
- 不得明文存储私钥、不得让私钥进入日志或模型上下文。
- 不得自动执行任务包中的程序、脚本、宏、可执行扩展。
- 不得在运行时下载依赖；新依赖必须离线审批后导入并锁版本。
- 不得将模型输出直接写为正式任务状态；状态必须由 Custom Tool 或人工写入。
- 不得覆盖用户原始文档；如需修订须在 `loop/DECISIONS.md` 留痕。
- 不得实现未写入用户故事的扩展功能。
- 不得绕过 .opencode/plugins/loop-guard.ts 的拦截。

## 4. 完成定义

一个用户故事只有同时满足以下条件才可标记完成：

- 所有 AC 都有对应测试（含异常输入与重放测试）。
- 单元测试、集成测试、安全测试、`make quality` 全绿。
- 无未解决的 Critical/High 安全问题。
- `docs/traceability/requirements-test-matrix.md` 已更新且无悬空条目。
- `loop/VERIFICATION.md` 中包含本轮门禁结果与命令指纹。
- 独立 `mvp-verifier` 与（必要时）`security-reviewer` 双方均放行。

## 5. 禁止行为

- 不执行 `git push`、不合并分支、不打 tag、不发 release。
- 不修改 `%ProgramData%\opencode\opencode.jsonc`。
- 不添加未经批准的依赖。
- 不伪造测试结果；不通过删除测试"修复"失败。
- 不在 opencode 命令中使用 `--auto` / 自动批准语义。

## 6. 停止条件

满足其一，立即停轮并请求业务负责人决策：

- 当前工作项完成（status → done）。
- 需求或协议文档冲突。
- 需新增依赖 / 调整密码方案 / 调整 `.agent` 协议主版本。
- 同一错误连续出现 3 次。
- 出现 Critical 或 High 安全问题。
- 本轮达到 `loop-engineer` 的最大步数（40）。

## 7. 跨会话规则

Agent 不应在长会话里持续持有上下文。每轮 `/loop` 启动新 session，从仓库中的状态文件恢复上下文；当状态文件被污染时立即停轮。
