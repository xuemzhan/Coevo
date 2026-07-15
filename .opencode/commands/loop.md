---
description: 执行一个受控 MVP 工程循环（DISCOVER→PLAN→IMPLEMENT→VERIFY→REVIEW→RECORD→DECIDE），只推进一个工作项；可接受 $ITEM 作为工作项 ID 覆盖。
agent: loop-engineer
---

执行且只执行一个工程循环。

读取：

- `loop/STATE.json`
- `loop/BACKLOG.yaml`
- `loop/GOAL.md`
- `loop/VERIFICATION.md`
- 当前 `git diff` 与未提交修改

如有 `$ITEM` 参数（例如 `/loop US-0-AC-2`），将该工作项强制设为本次目标；否则按 `BACKLOG.yaml` 中 `ready` 优先级选最小切片。

严格按以下阶段推进：

DISCOVER → PLAN → IMPLEMENT → VERIFY → REVIEW → RECORD → DECIDE

禁止同时处理多个工作项；禁止跳过测试或安全审查。

结束时必须输出：

1. 当前用户故事 / 工作项 ID。
2. 已满足 AC（逐条）。
3. 未满足 AC（逐条 + 缺口原因）。
4. 测试结果摘要（命令指纹 + 失败列表）。
5. 安全审查 / 协议审查结论（如触发）。
6. 状态文件改动摘要（`STATE.json` 字段前后值）。
7. 下一步建议或阻断原因。
