# US-16-AC-2 切片计划：框架层 Policy 抽象与 validate_plan（CTAF §6.5 / M2）

> 状态：已批准（2026-08-07 业务负责人"继续"）。规划包由 loop-engineer 按
> mvp-planner 方法论产出；实施由编排者直接完成（子代理消息投递不稳定），
> 验证与安全审查保持独立子代理。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-2-framework-policy-abstractions-v0.1`
- 用户故事：US-16【框架层】受控智能体声明校验与策略抽象——把 Plan 的数值边界
  统一收敛到 Policy，validate_plan 作为 dispatch 前置必调，阻止 LLM 越权。

## 2. AC 清单与目标测试

| AC | 内容 | 目标测试 |
| --- | --- | --- |
| AC-2.1 | Policy 字段完整、policy_version 必填（F7） | test_policy_fields_and_version_required |
| AC-2.2 | 4 个默认 Profile，max_recover_attempts ≤ 3（L16） | test_default_profiles_within_l16 |
| AC-2.3 | EMERGENCY fail-fast：1 次重试 / 60s / 事后 30 分钟确认 / 本地告警 | test_emergency_profile_fail_fast |
| AC-2.4 | L18 白名单：Plan 内禁策略归属数值键 | test_l18_policy_keys_rejected |
| AC-2.5 | tool_args 数值按 schema 允许（非策略键） | test_tool_args_numeric_allowed |
| AC-2.6 | validate_plan 前置校验五项不变量 + L18 + L19（A9/F4） | test_validate_plan_all_invariants |
| AC-2.7 | L19：ESCALATED→ACTIVE 必须经 HELD；RETIRED 直退 | test_lifecycle_l19_paths |
| AC-2.8 | 纯函数 / 离线 / stdlib / L17 文档守卫 | test_stdlib_only + test_module_docs |

## 3. 最小可交付切片

新增 `src/coevo/framework/` 下 `policy.py`（Policy 数据类 + 4 默认 Profile +
`validate_policy`）、`plan.py`（Plan/PlanNode/PlanEdge + L18 白名单 +
规范化哈希）、`lifecycle.py`（八态状态机 + L19 路径校验）、`validation.py`
（`ValidationResult` + `validate_plan` 五项不变量 + L18 + L19）；全部纯函数、
仅标准库；`validate_plan` 的 L4 Scope 与四层 RBAC 经注入协议委托（同
manifest-checker 模式）。

## 4. 需修改/新增文件

- 新增 `src/coevo/framework/policy.py`、`plan.py`、`lifecycle.py`、`validation.py`
- 修改 `src/coevo/framework/__init__.py`（重导出）
- 修改 `docs/modules/framework.md`（文件清单补 4 个新文件，L17）
- 新增 `tests/unit/test_framework_policy.py`、`test_framework_validate_plan.py`、
  `test_framework_lifecycle.py`

## 5. 测试要点（含异常/负例）

- Policy：缺 policy_version、非闭集 profile、max_recover_attempts>3（如 4/5）拒绝；
  EMERGENCY 非 fail-fast（重试≠1、总时限>60s、在线确认）拒绝；backoff 非正数拒绝；
- L18：Plan 顶层/节点出现 max_plan_depth、max_recover_attempts、timeout 等策略键
  拒绝；tool_args 含策略键拒绝；tool_args 普通数值（如 max_nodes=100）通过；
- validate_plan：环（自环/双节点环/多节点环）拒绝；重复 node_id 拒绝；悬空边拒绝；
  未知 kind/AGENT 无能力/TOOL 无 tool_ref/HUMAN_GATE 缺理由或未强制确认拒绝；
  plan_id 与规范化哈希不符拒绝；policy_profile/policy_version 与 Policy 不符拒绝；
  L4 Scope 越界（scope_checker=False）拒绝；RBAC 拒绝；L19 路径违规拒绝；
- lifecycle：ESCALATED→ACTIVE 拒绝、ESCALATED→HELD→ACTIVE 通过、
  ESCALATED→RETIRED 通过、非法转换 fail-closed；
- L17：framework.md 文件清单覆盖全部 .py。

## 6. 安全与兼容性风险

- L4/RBAC 委托注入协议，必须 fail-closed（异常→拒绝）；
- L18 白名单必须精确（误伤 tool_args 会砍产品功能，漏放则红线失效）；
- 不修改 `.agent` wire、不触碰编排器现有实现（仅新增框架层纯函数）；
- 零新增三方依赖（L15）；文档守卫（L17）。

## 7. 明确不属于本轮

- Orchestrator 真实接入 validate_plan（改编排器调用链）——留待 M7/后续切片；
- Memory 接口（M3）、MCP（M4）、A2A（M5）、Plan-LSP（M6）、Hybrid（M7）；
- `.agent` wire 改动、跨组织 PKI 联邦。

## 8. 可验证完成条件

- 三个新测试文件全绿；`python scripts/quality_gate.py --target fmt` 与
  `--target lint` exit 0；
- 主仓库 `make quality` exit=0（mvp-verifier 独立执行）；
- security-reviewer 无 Critical/High；追溯矩阵新增 US-16 | AC-2 行。

## 9. 给实施者的指令包

按第 4/5 节实现；对齐 manifest_checker 的既有风格（frozen dataclass、注入协议、
失败返回 failure_reason、审计投影、stdlib-only）；测试同步提交；只 stage 本轮
文件；提交信息 `feat(framework): US-16-AC-2 policy abstractions + validate_plan`。

## 10. 审查门

- security-reviewer：**是**（策略数值边界/L18/L19/状态机语义）；
- protocol-reviewer：**否**（不触碰 wire）。
