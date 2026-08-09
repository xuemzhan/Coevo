# FRAMEWORK-OPTIMIZE-25 切片计划：dispatch_event AGENT_CALL 分支提取

> 状态：已批准（2026-08-09 用户指令"继续"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-25`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-24]）。
- 目的：`Orchestrator.dispatch_event`（170 行，cc~16）的 AGENT_CALL 分支（约 85 行：
  确认 hold / registry 缺失 / AVAILABLE / RETRY 单次重试 / SKIP / ESCALATE）提取为
  模块级纯函数 `_dispatch_agent_step`，配合冻结 dataclass `_AgentStepResult`
  返回 `(outcome, next_id_seed, stop)`；`dispatch_event` 收敛为约 85 行循环编排；
  判定顺序、trace detail 字符串、失败关闭语义逐字节不变；导入面不变。

## 2. 交付

- `src/coevo/orchestrator/service.py`：
  1. 新增 `@dataclass(frozen=True) _AgentStepResult`（outcome/next_id_seed/stop）；
  2. 新增模块级 `_dispatch_agent_step(...)`（原 103-187 行逐行搬移，trace 追加经
     既有 `_append_trace`，RETRY 成功用 retried_id、失败回落 ESCALATE 用原 trace_id）；
  3. `dispatch_event` 循环中 AGENT_CALL 分支改为调用助手并
     `if result.stop: break; continue`。
- 守卫测试 `tests/unit/test_framework_optimize26.py`。

## 3. 测试要点

- 守卫：`dispatch_event` 方法体不超过 100 行（原 170）；`_dispatch_agent_step` 与
  `_AgentStepResult` 存在且被调用；关键 detail 标记存活（连续字面量）；
- 回归：`tests/unit/test_orchestrator.py` 全量 +
  `tests/integration/test_orchestrator_real_facade_chain.py`。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-25` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**是**（编排失败策略为安全相关：人工确认门、白名单缺失失败、
  重试上限一次、升级人工；纯迁移不改判定顺序与字符串）。
- protocol-reviewer：**否**。
