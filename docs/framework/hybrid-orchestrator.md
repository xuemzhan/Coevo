# Hybrid Orchestrator（CTAF §6.6 / §8 / M7）

> 里程碑：M7（2026-08-08 交付，核心切片）。实现：
> `src/coevo/framework/orchestrator.py`。
> 工作项：`US-16-AC-8-hybrid-orchestrator-v0.1`。

## 定位

编排核心：三种模式（StateMachine / DynamicLLM / Hybrid）共用同一套硬门——
`validate_plan` 前置、L19 八态衔接、HOLD 人工确认门。LLM / 静态链 / 执行器
全部注入，模块纯函数、可离线测试。

## 模式规则

| 模式 | plan 来源 | 失败处理 |
| --- | --- | --- |
| STATE_MACHINE | 注入 `StaticChainProvider` 编译为规范 Plan | 执行失败/异常 → ESCALATED + audit RECOVER |
| DYNAMIC_LLM | 注入 `LlmPlanProvider` 提议，经完整 `validate_plan` | 提议缺失/异常/无效 → 回退链 Plan |
| HYBRID | LLM 提议仅覆盖非 HOLD 节点 | 提议含 HOLD → 回退链 Plan；链含 HOLD → HELD（执行器不调用） |

## 硬门

- **AC-8.1**：`dispatch` 先 `validate_plan`（五项不变量 + L18 + L19），失败返回
  REJECTED，执行器不被调用；
- **AC-8.4**：HELD 人工确认门强制，确认前不执行后续步骤；
- **AC-8.5**：`transition` 复用 `lifecycle.validate_transition_path`，
  ESCALATED→ACTIVE 必须经 HELD，RETIRED 直退；
- 注入执行器/LLM/链异常一律收敛为 ESCALATED 或回退，不泄漏异常。

## 审计投影

`OrchestrationOutcome.to_audit_record()` 固定五键：accepted / mode / status /
plan_hash / failure_reason。

## 安全边界

- validate_plan 前置不可跳过（fail-closed）；
- HOLD 门强制，LLM 不得自行决定人工确认；
- 纯函数、仅标准库、可离线运行（L15）；文档守卫（L17）。

## 测试覆盖

`tests/unit/test_framework_orchestrator.py`（AC-8.1..8.5，含前置拒绝、链执行/
升级、LLM 回退三支、Hybrid HOLD 门、L19 路径、审计投影、stdlib 断言）。
