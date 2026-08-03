---
description: 只读输出当前 Loop 状态摘要：当前工作项、最近一次结果、下一个 ready 工作项、最近 5 条决策。
agent: loop-engineer
subtask: true
---

只读报告。不修改任何文件、不调用任何写操作。

读取并展示：

- `loop/STATE.json` 全部字段 + 最近一次迭代时间。
- `loop/BACKLOG.yaml` 中 `ready` 状态的前 5 个工作项。
- `loop/VERIFICATION.md` 最后一段（最近一次门禁结果）。
- `loop/DECISIONS.md` 最近 5 条，仅作为历史记录，不得把已关闭问题说成当前问题。
- `loop/tool-audit.jsonl` 最近 5 行。
- 当前 `git status --short` 与未提交 diff 摘要。

结论只能依据 `loop/STATE.json` 当前的 `status` 与 `blocking_issue`：

- `ready` / `in-progress` → 可继续；
- `blocked` / `security-blocked` → 已阻断，并逐字引用当前 `blocking_issue`；
- `decision-required` → 需决策；
- `done` / `mvp-complete` → 已完成。

不得从历史决策推断当前仍存在 Critical/High，不得声称已完成的故事仍未解决，不得改变任何状态。
