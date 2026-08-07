# FRAMEWORK-INTEGRATION-2 切片计划：存量链抬升与集成收口

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-INTEGRATION-2`（ENG-BASE，dependencies=[FRAMEWORK-INTEGRATION-1]）
- 目的：让现有产品固定链也能被框架校验——`chain_to_plan` 把
  `OrchestrationChain` 抬升为框架 Plan 后走 `validate_plan`；同时收口
  INTEGRATION-1 的 Low（plan_to_chain 闭集外能力抛错类型不一致）。

## 2. 交付

- `chain_to_plan(chain, registry, policy)`：AGENT_CALL 步骤按 `registry.get`
  解析能力 → AGENT 节点；HUMAN_CONFIRM → HUMAN_GATE；CONDITIONAL /
  未注册代理 → IntegrationError；顺序边 + 指纹。
- `validate_product_chain(chain, registry, policy, *, scope_checker,
  rbac_checker, actor, validated_at)`：抬升 + `validate_plan`。
- `plan_to_chain` 收口：`resolve_capability` 闭集外错误统一为
  `IntegrationError`。

## 3. 测试要点（含负例）

- chain_to_plan：AGENT_CALL + HUMAN_CONFIRM 混合链 → 正确 Plan（validate_plan
  通过）；未注册代理拒绝；CONDITIONAL 拒绝；
- validate_product_chain：合法链 accepted；RBAC 拒绝；
- plan_to_chain：闭集外能力 → IntegrationError（非 CapabilityValidationError）；
- L15 stdlib / L17 文档守卫。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-INTEGRATION-2 行。

## 5. 审查门

- security-reviewer：**是**（能力解析 / 异常收敛）；protocol-reviewer：**否**。
