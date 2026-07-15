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
- `loop/DECISIONS.md` 最近 5 条。
- `loop/tool-audit.jsonl` 最近 5 行。
- 当前 `git status --short` 与未提交 diff 摘要。

末尾给出一句话结论：当前是否处于可继续 / 已阻断 / 需决策 三态之一。
