# 框架接入现有编排（GuardedOrchestrator 适配，FRAMEWORK-INTEGRATION-1/4）

> 交付：2026-08-08。实现：`src/coevo/framework/integration.py`。

## 定位

把框架层门禁接到现有 `src/coevo/orchestrator`：

- `guard_registration`：Agent Manifest 经 manifest-checker 通过后才调用
  inner_register（注册）；
- `build_registration_manifest`（FRAMEWORK-INTEGRATION-4）：纯函数生成规范
  Agent Manifest，`spec_hash` 排除自指字段（metadata.spec_hash /
  policy_ref.spec_hash / policy_ref.signature），可选注入签名器对
  `spec_hash|signer_cert_fingerprint` 绑定签名；
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

## 注册门演示接线（FRAMEWORK-INTEGRATION-4）

- `app/demo_support.py` 提供演示专用注册适配器：`DemoRegistrationVerifier`
  （对任意良构签名返回 True）、`DemoRegistrationResolver`（固定演示证书）、
  `DemoPolicyRegistry`（仅 INTERACTIVE 1.0）。三者**显式非生产**：生产必须
  注入真实 SM2 验签器、证书链 resolver 与部署点策略注册表，否则注册门无法
  提供真实身份保证。
- `app/pipeline.py` 在注册 4 个 demo 智能体前先 `guard_registration`：Manifest
  结构、capability 闭集、crypto_scope、spec_hash、policy_ref 绑定格式与
  policy_version 全部通过才调用内部注册，任一失败即拒绝且不触达注册。

## 测试覆盖

`tests/unit/test_framework_integration.py`（plan_to_chain 混合/TOOL/非 MVP/
无代理、guarded_dispatch 前置拒绝与三态映射与内部异常、guard_registration
通过/拒绝/内部异常、审计投影、stdlib 断言）。

`tests/unit/test_framework_integration2.py`（chain_to_plan 混合/未注册代理/
CONDITIONAL 拒绝、validate_product_chain 通过与 RBAC 拒绝、plan_to_chain
闭集外错误类型收口、stdlib 断言）。

`tests/unit/test_framework_integration4.py`（FRAMEWORK-INTEGRATION-4：
build_registration_manifest 产物 spec_hash 一致、篡改拒绝、未知能力拒绝、
缺 policy_version 拒绝、4 个 demo 智能体全部 accepted 且各注册一次、demo
适配器 stdlib 断言）。
