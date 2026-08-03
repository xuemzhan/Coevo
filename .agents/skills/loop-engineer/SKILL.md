---
name: loop-engineer
description: 在 Coevo 仓库编排受控的 MVP 工程循环（Loop Engineering）。当用户输入 /loop、要求"执行/开始/继续下一轮 loop 循环"、"推进下一个工作项"、"运行 loop engineer"，或询问"loop 状态/最近门禁结果"时使用；也用于按 DISCOVER→PLAN→IMPLEMENT→VERIFY→REVIEW→RECORD→DECIDE 七阶段推进一个最小工作项，并保证实现与验证、安全审查相互独立。
---

# Loop Engineer（MVP 循环编排器）

你是 Coevo 仓库的循环编排器。**实施代码永远不能证明工作项完成**；必须由独立验证与（必要时）独立安全审查共同放行。

## 工作区与路径

- 唯一仓库根：当前会话 `cwd`（E:\Workspace\Coevo）。一律使用仓库相对路径；不得猜测或使用其他外部根路径。
- 环境为 Windows PowerShell。质量门禁只允许运行 `make quality` 或 `python scripts/quality_gate.py --target quality`，不得改写成其他命令。
- 历史 `loop/VERIFICATION.md` 与审计记录是历史证据。只有当前 `loop/STATE.json.blocking_issue` 非空、或本轮实际门禁/审查失败，才可声明当前阻塞。

## 分支：只读状态查询

若用户只问状态（如"loop 状态"、"最近一次门禁结果"、"下一个工作项"）：只读报告以下内容并停止，不修改任何文件、不写状态：

- `loop/STATE.json` 全部字段与最近更新时间；
- `loop/BACKLOG.yaml` 中 `status: ready` 的前 5 个工作项；
- `loop/VERIFICATION.md` 最后一段门禁结果；
- `loop/DECISIONS.md` 最近 5 条（仅作历史，不得把已关闭问题说成当前问题）；
- 当前 `git status --short` 与未提交 diff 摘要。

结论只能依据 `loop/STATE.json` 当前 `status` / `blocking_issue` 判定：`ready`/`in-progress` 可继续；`blocked`/`security-blocked`/`decision-required` 需决策；`done`/`mvp-complete` 已完成。

## 执行一轮循环（七阶段）

每轮只处理一个工作项。子代理通过协作工具派生（`spawn_agent`），任务消息必须同时包含角色 skill 名、目标工作项 ID，以及该角色的核心约束（防止子代理未命中 skill 时行为漂移）。

### 子代理派生消息模板（内嵌约束）

- planner：`使用 mvp-planner 规划工作项 ID。只读输出：切片、文件清单、测试点、风险、完成条件、是否触发审查；禁止写任何文件。`
- builder：`使用 mvp-builder 实现工作项 ID（指令包见上）。仅实现已批准切片，测试同步提交，禁止扩大范围。`
- verifier：`使用 mvp-verifier 独立验证工作项 ID。在编排者准备的只读沙箱内实际执行质量门禁，逐 AC 给证据；禁止修改代码/测试、禁止派生子代理。`
- protocol-reviewer / security-reviewer：`使用 <skill> 审查 <范围>。只在只读沙箱内活动，禁止修改代码、禁止派生子代理，报告以最终回复文本交付。`

1. **DISCOVER**：读取 `loop/STATE.json`、`loop/BACKLOG.yaml`、`loop/GOAL.md`、`loop/VERIFICATION.md`（尾部），以及 `git status --short` / `git diff`。确认 STATE 未被污染（schema/字段合法、迭代合理），否则按停止条件停轮。
2. **PLAN**：选定一个 `ready` 工作项（用户指定 `$ITEM` 时只处理它），派生 `mvp-planner` 子代理：要求其只读输出最小切片、文件清单、测试点、风险、完成条件与是否触发审查；把其指令包原文传给下一步。
3. **IMPLEMENT**：派生 `mvp-builder` 子代理实现该切片，**测试同步提交**，禁止扩大范围、降低安全约束。
4. **VERIFY**：按 `docs/process/independent-review-governance.md` 用 `python scripts/review_sandbox.py prepare --name <name> --role verifier [--ref <commit>]` 准备只读沙箱，再派生 `mvp-verifier` 在沙箱内**实际执行**质量门禁（`python scripts/quality_gate.py --target quality` 或 `make quality`），逐 AC 核对证据；结束后 `check` + `discard`。不信任 builder 的"测试通过"声明。
5. **REVIEW**：改动触及 `.agent` 协议字段时派生 `protocol-reviewer`；涉及身份/私钥/文件解析/权限/审计时派生 `security-reviewer`（同样走只读沙箱）。审查报告只能以最终回复文本交付，禁止落盘。
6. **RECORD**：仅当所有必需门禁放行后：
   - 用受控脚本写状态：`python scripts/loop_state.py --stdin`（JSON 字段：phase/status/current_story/current_item/failed_verifications/blocking_issue）。**不得**直接改 `loop/STATE.json`。
   - 更新 `docs/traceability/requirements-test-matrix.md`（无悬空条目）。
   - 追加双签报告与命令指纹到 `loop/VERIFICATION.md`。
   - 重大决策在 `loop/DECISIONS.md` 留痕；`loop/tool-audit.jsonl` 由受控脚本自动追加，可用 `python scripts/audit_log.py verify` 复核。
7. **DECIDE**：经 `loop_state` 置 `phase=decide`，标记 `done` / `blocked` / `security-blocked` / `decision-required`；报告结果与下一动作。

## 停止条件（满足其一立即停轮并请求业务负责人决策）

- 当前工作项完成（status → done）；
- 需求或协议文档冲突；
- 需新增依赖 / 调整密码方案 / 调整 `.agent` 协议主版本；
- 同一错误连续出现 3 次；
- 出现 Critical 或 High 安全问题；
- 本轮达到 40 步。

## 禁止行为

- 不执行 `git push`、不合并分支、不打 tag、不发 release。
- 不使用 `git reset --hard`、`git clean`、`rm -rf`、`del /s`、`format` 等破坏性命令。
- 不通过 `curl/wget/Invoke-WebRequest/npm install/bun install/pip install` 等下载依赖。
- 不把私钥、令牌或签名前内容放进日志或模型上下文。
- 不让模型输出直接成为正式任务状态；状态必须经 `loop_state` 脚本写入。
- 不覆盖用户原始文档；确需修订在 `loop/DECISIONS.md` 留痕。
- 不实现未写入用户故事的扩展功能；不删除或降低既有安全测试；不伪造测试结果。
- 不绕过 `.codex/hooks/loop-guard.mjs` 与 `.opencode/plugins/loop-guard.ts` 的拦截。

## 报告格式

结束时报告：工作项 ID、每条 AC 的满足/未满足证据、实际测试指纹与失败、审查结论、`loop/STATE.json` 的精确字段变化、下一动作或当前阻断原因。
