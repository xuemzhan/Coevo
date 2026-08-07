# US-16-AC-8 切片计划：Hybrid Orchestrator（CTAF §6.6 / §8 / M7）

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。本轮只跑
> 增量门禁（fmt + lint + 定向测试），豁免留痕。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-8-hybrid-orchestrator-v0.1`
- 用户故事：US-16【框架层】——实现编排核心 Hybrid Orchestrator：三种模式
  （StateMachine / DynamicLLM / Hybrid）共用 validate_plan 前置与 L19 生命周期，
  任何执行与模型 IO 全部注入，纯函数可离线测试。

## 2. AC 清单与目标测试

| AC | 内容 | 目标测试 |
| --- | --- | --- |
| AC-8.1 | validate_plan 为 dispatch 前置必调 | test_dispatch_requires_valid_plan |
| AC-8.2 | StateMachine 静态链 + fail-closed 转 ESCALATED | test_state_machine_mode |
| AC-8.3 | DynamicLLM 提议 + 失败回退 StateMachine | test_dynamic_llm_fallback |
| AC-8.4 | Hybrid 仅非 HOLD 由 LLM 覆盖 + HELD 门 | test_hybrid_hold_gate |
| AC-8.5 | L19 八态衔接 + 审计投影 + stdlib + L17 | test_lifecycle_integration + test_module_docs |

## 3. 最小可交付切片

新增 `src/coevo/framework/orchestrator.py`：OrchestrationMode /
ChainStep / ExecutionResult / StaticChainProvider / LlmPlanProvider /
PlanExecutor 注入协议 / plan_for / dispatch / confirm / recover /
OrchestrationOutcome（审计投影）。新增 `docs/framework/hybrid-orchestrator.md`；
更新模块文档（L17）。

## 4. 需修改/新增文件

- 新增 `src/coevo/framework/orchestrator.py`；修改 `src/coevo/framework/__init__.py`
- 新增 `tests/unit/test_framework_orchestrator.py`
- 新增 `docs/framework/hybrid-orchestrator.md`；修改 `docs/modules/framework.md`

## 5. 测试要点（含异常/负例）

- 前置：无效 Plan（环 / RBAC 拒绝 / L18 键 / scope 越界）→ dispatch 返回
  REJECTED 且执行器不被调用；
- StateMachine：链构建 Plan 指纹正确；执行成功 COMPLETED；执行失败 /
  执行器异常 ESCALATED（audit RECOVER）；
- DynamicLLM：提议有效 → 执行；提议 None / 提议无效 / 提议异常 → 回退链 Plan；
- Hybrid：提议含 HOLD 节点 → 回退链 Plan；链含 HOLD → HELD（执行器不调用）；
- L19：ESCALATED→ACTIVE 直跳拒绝、经 HELD 通过（复用 lifecycle）；
- 审计投影键集固定；L15 stdlib / L17 文档守卫。

## 6. 安全与兼容性风险

- validate_plan 前置不可跳过（fail-closed）；
- LLM/链/执行器全部注入且异常收敛为 ESCALATED/回退，不泄漏异常；
- HOLD 人工门强制（确认前不得执行后续步骤）；
- 不改 `.agent` wire、不改现有编排器实现；零新增三方依赖；文档守卫。

## 7. 明确不属于本轮

- 接入真实 LLM / 真实 SQLite 存储 / 现有 Orchestrator 门面（M7 后续切片）；
- M8/M9；A2A gossip / MCP-B / K8s CRD（v0.5）；`.agent` wire 改动。

## 8. 可验证完成条件

- `python -m unittest tests.unit.test_framework_orchestrator` 全绿；
- `python scripts/quality_gate.py --target fmt` 与 `--target lint` exit 0
  （不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 US-16 | AC-8 行；security-reviewer 无 Critical/High。

## 9. 给实施者的指令包

按第 4/5 节实现；对齐框架层既有风格（frozen dataclass、注入协议、fail-closed、
stdlib-only、审计投影）；只 stage 本轮文件；提交信息
`feat(framework): US-16-AC-8 hybrid orchestrator core (M7)`。

## 10. 审查门

- security-reviewer：**是**（编排前置校验 / HOLD 门 / L19 / 注入异常收敛）；
- protocol-reviewer：**否**（不触碰 wire）。
