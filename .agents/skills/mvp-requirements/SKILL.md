---
name: mvp-requirements
description: Coevo 分布式任务管理具身智能体 MVP 的需求、用户故事、验收标准与完成定义；按需加载，不长期占满上下文。当需要定位工作项 ID 对应的用户故事与 AC、检查完成定义、或把需求映射到测试时使用。
---

## 权威文件

- `docs/requirements/system-requirements.md`
- `docs/requirements/mvp-user-stories.md`
- `docs/constraints/mandatory-technical-constraints.md`
- `docs/traceability/requirements-test-matrix.md`

## 使用规则

1. 先用工作项 ID 定位用户故事与 AC；不得跨故事合并范围。
2. 把每条 AC 转换为可执行测试（含失败/异常输入）。
3. 需求不清时输出 `blocked`，不允许自行假定；必须写到 `loop/DECISIONS.md`。
4. 每轮必须输出 AC ↔ 代码 ↔ 测试映射关系，供 verifier 与 security-reviewer 使用。
5. 当 AC 同时涉及协议字段时，提示 `loop-engineer` 同步加载 `agent-package` skill。
