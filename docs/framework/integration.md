# 框架接入现有编排（GuardedOrchestrator 适配，FRAMEWORK-INTEGRATION-1）

> 交付：2026-08-08。实现：`src/coevo/framework/integration.py`。

## 定位

把框架层门禁接到现有 `src/coevo/orchestrator`：

- `guard_registration`：Agent Manifest 经 manifest-checker 通过后才调用
  inner_register（注册）；
- `plan_to_chain`：框架 Plan → 现有 `OrchestrationChain`（AGENT 节点按能力
  解析注册代理为 AGENT_CALL；HUMAN_GATE → HUMAN_CONFIRM；TOOL 节点与框架
  抽象能力明确拒绝——当前产品编排器不可执行）；
- `guarded_dispatch`：`validate_plan` 前置 → `plan_to_chain` →
  `Orchestrator.dispatch_event` → 报告映射框架 `OrchestrationOutcome`
  （COMPLETED / HELD / ESCALATED，FAILED 视作 ESCALATED fail-closed）。
- `chain_to_plan` / `validate_product_chain`（FRAMEWORK-INTEGRATION-2）：
  现有产品 `OrchestrationChain` 抬升为框架 Plan（AGENT_CALL 按
  `registry.get` 解析能力、HUMAN_CONFIRM → HUMAN_GATE、CONDITIONAL / 未注册
  代理拒绝）后走 `validate_plan`（五项不变量 + L18 + L19），让存量链也能被
  框架校验。

## 安全边界

- 注册与派发双门：未过 manifest / validate_plan 一律不触达内部编排器；
- 注入的 inner_register / dispatch_fn 异常一律 fail-closed（GuardResult
  accepted=False / ESCALATED），不外泄原始异常；
- `GuardResult.to_audit_record()` 固定四键（accepted / manifest_accepted /
  agent_id / reason）；
- 纯函数（仅注入调用为副作用）、仅标准库、可离线运行（L15）；文档守卫（L17）。
- `plan_to_chain` 对闭集外能力统一抛 `IntegrationError`（不泄漏
  `CapabilityValidationError` 类型细节）。

## 测试覆盖

`tests/unit/test_framework_integration.py`（plan_to_chain 混合/TOOL/非 MVP/
无代理、guarded_dispatch 前置拒绝与三态映射与内部异常、guard_registration
通过/拒绝/内部异常、审计投影、stdlib 断言）。

`tests/unit/test_framework_integration2.py`（chain_to_plan 混合/未注册代理/
CONDITIONAL 拒绝、validate_product_chain 通过与 RBAC 拒绝、plan_to_chain
闭集外错误类型收口、stdlib 断言）。
