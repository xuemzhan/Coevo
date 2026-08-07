# `framework/` — 框架层（CTAF US-16）

## 定位

CTAF（Coevo Trusted Agent Framework）v0.4.1 框架层在 `src/coevo` 的落位。
US-16-AC-1 交付部署点 manifest-checker：只有声明合规、策略受控的智能体才能
注册进入编排；US-16-AC-2 交付 Policy 抽象、Plan/L18 白名单、八态生命周期（L19）
与 validate_plan；US-16-AC-3 交付能力闭集收敛（M1b）；US-16-AC-4 交付 Memory
抽象（M3）；US-16-AC-5 交付 Tool 抽象与 MCP schema 路径 A（M4）；US-16-AC-6
交付 A2A wire 0.1 与 policy_ref 三段绑定（M5）；US-16-AC-7 交付 Plan 规范化
序列化（Plan-LSP，M6）；US-16-AC-8 交付 Hybrid Orchestrator 核心（M7）。
US-16-AC-9 交付 K8s CRD 纸面清单生成器（M9）。
FRAMEWORK-INTEGRATION-1 交付框架接入现有编排（GuardedOrchestrator 适配）。
设计基线：`docs/plans/distributed-agent-framework/design-proposal.md` §5。

## 职责边界

- **in scope**：Agent Manifest 强制校验（能力闭集 / 人工确认默认 / crypto_scope
  闭集 / 审计脱敏子集 / spec_hash 排除自指字段 / policy_ref 三段绑定 /
  policy_version 绑定）、"校验通过才注册"的薄封装、T6 wire 回归；Policy 抽象
  （4 个默认 Profile / L16 / EMERGENCY fail-fast）、Plan 模型与 L18 白名单、
  八态生命周期 L19、validate_plan 五项不变量；
- **out of scope**：A2A 实现、
  MCP、Plan-LSP、Hybrid Orchestrator、跨组织 PKI 联邦；不修改 `.agent` v1.0
  wire 与既有编排代码。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `capability.py` | `CAPABILITY_CLOSED_SET`、`CapabilityEntry`、`CapabilityKind`、`resolve_capability`、`check_consistency` | CTAF §5.2 能力闭集收敛：MVP 映射 AgentCapability、框架抽象、CRYPTO_PROXY 限 approved scope |
| `manifest_checker.py` | `check`、`AgentManifest`、`ManifestCheckInput`、`ManifestCheckResult`、`ManifestRegistry`、`PolicyRegistry`/`CertificateResolver`/`SignatureVerifier`（注入协议） | 部署点强制校验（纯函数、fail-closed）+ 校验通过才注册 |
| `policy.py` | `Policy`/`TimeoutProfile`/`RetryProfile`/`ConsentProfile`、`default_profiles`、`validate_policy`、`get_default_profile` | 策略数值边界（L16 / F7 / EMERGENCY fail-fast F1/F9） |
| `plan.py` | `Plan`/`PlanNode`/`PlanEdge`/`PlanNodeKind`、`POLICY_OWNED_NUMERIC_KEYS`（L18 白名单）、`plan_fingerprint`、`validate_plan_structure` | Plan 纯结构模型与规范化哈希、L18 校验 |
| `lifecycle.py` | `LifecycleState`、`can_transition`、`validate_transition_path` | 八态生命周期与 L19 路径规则 |
| `memory.py` | `MemoryRecord`、`MemoryKind`、`write_memory`、`redact_record`、`Redactor`/`EpisodicMemoryStore`/`SemanticApprovalChecker`/`SemanticMemoryStore`（注入协议） | Memory 统一模型：审计投影 + Semantic 审批 + L12 脱敏 |
| `validation.py` | `ValidationResult`、`validate_plan`、`ToolScopeChecker`/`RbacChecker`（注入协议） | dispatch 前置校验：五项不变量 + L18 + L19 |
| `plan.py` | 另含 `plan_to_json` / `json_to_plan` / `parse_plan_json_bytes`（Plan-LSP 序列化） | Plan 规范 JSON 双向转换 + 严格解析 + 上限 |
| `tools.py` | `Tool`、`ToolRegistry`、`ToolSideEffect`、`validate_schema`、`tool_to_mcp`/`mcp_to_tool`、`canonical_schema_bytes` | Tool 统一模型 + MCP 路径 A 双向转换（零三方依赖） |
| `a2a.py` | `A2aMessage`、`PolicyRef`、`verify_policy_ref`、`to_agent_fields`/`from_agent_fields`、`validate_payload_size` | A2A 信封 + policy_ref 五步验证 + `.agent` 字段映射 + 大小边界 |
| `orchestrator.py` | `plan_for`、`dispatch`、`transition`、`chain_plan`、`StaticChainProvider`/`LlmPlanProvider`/`PlanExecutor`（注入协议）、`OrchestrationOutcome` | Hybrid Orchestrator：validate_plan 前置 + 三种模式 + L19 + HOLD 门 |
| `k8s_listing.py` | `generate_listing`、`listing_fingerprint`、`render_yaml`、`validate_listing_bytes`、`ListingInput` | 声明式纸面清单生成（JSON + YAML 子集），确定性可哈希、零 IO |
| `integration.py` | `guard_registration`、`plan_to_chain`、`guarded_dispatch`、`report_to_outcome`、`GuardResult` | 框架门禁接入现有编排：注册过 manifest、派发过 validate_plan、Plan→OrchestrationChain 适配 |

## 关键入口与数据流

```
Agent Manifest（canonical JSON）→ ManifestCheckInput
  → check(input, policy_registry, cert_resolver, signature_verifier)
      → 成功: ManifestCheckResult(accepted=True, AgentManifest) → registry.register()
      → 失败: ManifestCheckResult(accepted=False, failure_reason)，不注册
```

- 规范形态为 canonical JSON（与 `.agent` envelope 同规则：无 BOM、键字典序、
  紧凑分隔符、ASCII 安全转义）；YAML 仅为作者格式，离线转 JSON 后校验；
- `spec_hash` = 排除 `metadata.spec_hash` / `policy_ref.signature` 自指字段后的
  规范化字节 SHA-256（F5）；
- `policy_ref` 验签公钥来自证书链 resolver，不取自 manifest 自身（F8）。

## 安全与不变量

- 能力闭集以 `orchestrator.models.AgentCapability` 为单一事实来源（CTAF §5.2
  扩展名经 `capability.py` 注册表在 M1b 收敛，双名解析 + 双向一致性守卫）；
- L16：所有 Profile `max_recover_attempts ≤ 3`；EMERGENCY 必须 fail-fast；
- L18：Plan（含 tool_args）不得携带策略归属数值键，普通工具数值按 schema 允许；
- L19：ESCALATED→ACTIVE 必须经 HELD，RETIRED 直退；
- L12：Memory 写入敏感字段必须经注入 Redactor 转不可恢复摘要，明文不得到达 store；
- MCP 路径 A：schema 白名单子集，未知关键字显式拒绝；x-coevo 扩展块缺失拒绝；
- A2A：policy_ref 验签公钥只来自证书链；>64KiB 业务载荷必须 payload_ref 拆分；
- Plan-LSP：序列化与 plan_fingerprint 同一规范化规则，未知字段/重复键拒绝；
- Hybrid：validate_plan 前置必调；LLM 提议仅覆盖非 HOLD 节点；注入异常收敛；
- K8s 纸面清单：仅声明导出（无 reconcile loop），YAML 安全引号 + 字段白名单；
- 集成适配：TOOL 节点/框架抽象能力暂不可由产品编排器执行（IntegrationError）；
- L4 Scope 与四层 RBAC 经注入协议委托，异常一律视为拒绝（fail-closed）；
- fail-closed：未知能力、闭集外 scope、投影外脱敏、自指哈希、签名/指纹不匹配、
  缺失版本、坏 JSON/BOM/重复键一律拒绝并返回 `failure_reason`；
- 校验为纯函数（证书/验签/策略注册表全部注入）；注册副作用拒绝失败结果；
- L15：仅标准库、可离线运行；L17：本文件为 `test_module_docs.py` 守卫对象。

## 测试覆盖

- `tests/unit/test_framework_manifest_checker.py`（T1..T5 + F5/F7/F8 负例 +
  L15 stdlib 断言，覆盖 US-16 AC-1.1..AC-1.9）；
- `tests/unit/test_agent_wire_regression.py`（T6：Fixed Header /
  Envelope canonical 字节级回归，覆盖 AC-1.10）。
- `tests/unit/test_framework_policy.py`（AC-2.1..2.3、2.8）；
- `tests/unit/test_framework_plan_l18.py`（AC-2.4、2.5）；
- `tests/unit/test_framework_validate_plan.py`（AC-2.6、2.7）。
- `tests/unit/test_framework_capability.py`（AC-3.1..3.5，M1b 能力闭集收敛）。
- `tests/unit/test_framework_memory.py`（AC-4.1..4.5，M3 Memory 抽象）。
- `tests/unit/test_framework_tools.py`（AC-5.1..5.5，M4 Tool/MCP 路径 A）。
- `tests/unit/test_framework_a2a.py`（AC-6.1..6.5，M5 A2A/policy_ref）。
- `tests/unit/test_framework_plan_lsp.py`（AC-7.1..7.5，M6 Plan-LSP）。
- `tests/unit/test_framework_orchestrator.py`（AC-8.1..8.5，M7 Hybrid 核心）。
- `tests/unit/test_framework_k8s_listing.py`（AC-9.1..9.5，M9 纸面清单）。
- `tests/unit/test_framework_integration.py`（FRAMEWORK-INTEGRATION-1）。

## 依赖与下游

- 上游：`orchestrator.models.AgentCapability`、`crypto.contract.ProviderScope`；
- 下游：部署点编排注册入口（后续切片接入）；`docs/plans/US-16-AC-1-slice.md`
  为已批准切片计划。

## 配置与错误语义

- 无环境变量；异常类型 `ManifestValidationError`（注册拒绝）；
- 校验失败不抛异常，以 `ManifestCheckResult.failure_reason` 返回（审计友好）。
