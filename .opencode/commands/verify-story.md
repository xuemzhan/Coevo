---
description: 独立验证指定用户故事；运行门禁并复核追踪矩阵，不修改任何代码或测试。
agent: mvp-verifier
subtask: true
---

验证用户故事 `$1`（格式 `US-N`）的全部 AC。

读取：

- 该故事在 `docs/requirements/mvp-user-stories.md` 中的 AC 列表。
- `docs/traceability/requirements-test-matrix.md` 中的对应条目。
- `loop/VERIFICATION.md` 的历史记录。
- 当前 `git diff` 与最近一次 commit 的测试输出。

执行：

- `make quality`
- 对照 AC 与测试输出给出一致性表。

禁止：

- 修改任何源代码或测试。
- 接受"测试已通过"字面声明，必须看输出与退出码。
- 在涉及 `.agent` 协议的工作项上跳过协议字段核查。

输出：pass / fail / blocked + 证据指针 + 是否允许进入下一工作项。
