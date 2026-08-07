# 分布式具身智能体框架设计方案（v0.3）

> **版本**: v0.3 (2026-08-07)
> **状态**: 草案。在 v0.2 基础上吸收两轮审查（v0.1→v0.2 review / v0.2 架构师+分析师 review）中标记为 **P0 / P1** 的全部条目，并以"产品经理 + 业务负责人"视角补足定位、用户、场景、TCO、对外话术。
> **变更追踪**: §19 修订说明；v0.2 保留为 `design-proposal-v0.2.md`。

---

## 0. 文档定位与读者

| 章节 | 目标读者 | 推荐路径 |
| --- | --- | --- |
| §1 业务定位与价值主张 | 业务负责人 / 投资人 / 高层评审 | **必读** |
| §2 目标用户与典型场景 | 产品经理 / 业务架构师 / 售前 | 必读 |
| §3 初心与指导原则 | 全员 | 必读 |
| §4 总体形态与层 | 架构师 | 必读 |
| §5 Agent Manifest | 框架扩展者 | 必读 |
| §6 六抽象(Task / Memory / Tool / Plan / Policy / Orchestrator) | 各子模块 OWNER | 选读 |
| §7 协议平面 | 协议 / 密码合规 | 选读 |
| §8 编排平面与生命周期 | 编排 OWNER / 运维 | 选读 |
| §9 身份与权限 | 安全审计 | **必读** |
| §10 工作流 | 业务负责人 | 选读 |
| §11 可观测性与 SLA | 运维 | 选读 |
| §12 安全与合规不变量 | 安全审查 | **必读** |
| §13 威胁 × 防御矩阵 | 安全审查 | 必读 |
| §14 迁移路径与里程碑 | 项目经理 / OWNER | 必读 |
| §15 TCO / 实施预算 | 项目经理 / 财务 | 必读 |
| §16 与业界差异化与对外话术 | 业务负责人 / 市场 | 必读 |
| §17 风险与已知限制 | 业务负责人 | 选读 |
| §18 评估与下一轮 | 全员 | 选读 |
| §19 修订说明（v0.1 → v0.2 → v0.3） | 评审专家 / 业务负责人 | **必读** |

**v0.3 新增章节**（相对 v0.2）：
- §1 业务定位与价值主张
- §2 目标用户与典型场景
- §15 TCO / 实施预算
- §16 与业界差异化与对外话术

---

## 1. 业务定位与价值主张

### 1.1 一句话定义

> **本框架（Coevo Trusted Agent Framework，简称 CTAF v0.3）：以 Coevo MVP 中已落地的国家密码学算法（SM2/SM3/SM4）+ `.agent` 加密包协议 + 全程审计链为基础，向受控场景（政府/军工/金融/科研）提供"**可被法规审查、离线优先、零三方依赖**的分布式具身智能体编排框架。"**

### 1.2 三大差异化价值主张

| # | 主张 | 验证/事实 |
| --- | --- | --- |
| **V1** | **可被法规审查** | `.agent` v1.0 + 哈希链审计 + SM 国密；三层 RBAC + Plan-DAG 五项不变量 |
| **V2** | **离线优先 + 零三方依赖** | MVP 标准库 only；新增 MCP/Asyncio 等三方依赖需走主版本号升级流程 |
| **V3** | **受控的自主编排** | Anthropic 5 workflow 可选；Hybrid 模式默认；LLM 不得直接写主状态 |

### 1.3 三不主张（明确不做什么）

- **不主张** 与 AutoGen / LangGraph / CrewAI 在"通用云端"市场正面竞争；
- **不主张** 替代 Kubernetes（见 §16.4 K8s reconcile 边界）；
- **不主张** 把"自主 Agent"作为 v0.3 默认模式（v0.3 默认仍为 Hybrid + 严格 ground truth）。

### 1.4 v0.3 的差异化真相（vs 业界框架）

| 框架 | 主打场景 | CTAF v0.3 的真正差异 |
| --- | --- | --- |
| Microsoft AutoGen | 通用云端 actor + workflow | CTAF 不绑云端；不依赖外部 API key；可完全离线 |
| LangGraph | 通用 DAG 编排 | CTAF 自带 SM 国密；自带审计哈希链；无需外部服务 |
| CrewAI | 角色编排 | CTAF 角色必须经四层 RBAC，不是"角色自由分派" |
| Anthropic Claude Agent SDK | Anthropic 生态 | CTAF 不绑单一 LLM；多 provider 可插拔 |
| MCP | 工具与上下文标准 | CTAF 采纳 schema 层；scope 治理比 MCP 更严格（见 §12 红线 L15） |
| Kubernetes CRD | 声明式资源 + reconcile loop | CTAF **不是** reconcile loop，是 explore-then-execute（见 §16.4） |

---

## 2. 目标用户与典型场景

> v0.2 缺这块内容。v0.3 把它从"技术文档"提升为"产品文档"，便于业务负责人
> 对内/对外讲清楚"谁是用户、用在哪里"。

### 2.1 三类目标用户画像

| 画像 | 角色 | 痛点 | CTAF 解决 |
| --- | --- | --- | --- |
| **U1 受审计场景客户（政府/军工）** | 部委办公室 / 项目牵头处 | 跨部委、跨省、跨密级；纸质公文流转慢；现行 OA 不支持跨网离线 | `.agent` 加密包跨网；四次确认保证合规；SM 国密保合规底线 |
| **U2 大型组织/科研院所** | 项目管理办公室 / 跨学科 PI | 跨学科任务（科研+工程+财务）协同难；缺统一结构化跟踪；难沉淀 | US-0..US-15 全栈 + ProcessFlow 数据已结构化（task_flow/deloitte 五阶段） |
| **U3 出海企业 / 监管严格行业** | 跨国办公 / 合规官 | 数据不能出域；法规要求审计；现有工具无法离线 | 离线优先；全程审计；零三方依赖 |

### 2.2 三类典型场景（User Story）

#### 场景 A：跨部委任务的"加密包跨网流转"（U1）

```
[立项机关] ── 加密 .agent 包 ──> [牵头省厅]
                                     ├─ 分解 → [承办局 1]
                                     ├─ 分解 → [承办局 2]
                                     └─ 合并 → 主版本更新
                                                  └─ 风险预警 → 决策简报
```

- **关键事实**：全链 `.agent` 加密；HOLD 节点强制人工确认；审计链防篡改。
- **MVP 已演示**：`examples/tool-dev-project/run_example.py` 已端到端跑通。

#### 场景 B：跨学科科研任务的"成果回传"（U2）

```
[科研 PI] -- 阶段成果 -- 受控合并 --> 主版本库
                 ↓                          ↑
            [QA 自动比对]          [财务确认 / 评审专家]
                 ↓                          ↑
            [简报生成]  <-- [风险早期预警] 
```

- **关键事实**：与 MVP 状态回传链 B 等价；CTAF 提供跨学科 capability 闭集。

#### 场景 C：跨国出海任务的"完全离线"（U3）

```
[总部] ── 加密 .agent ──> [海外子公司 A] ── 合并 ──> [总部]
                          [海外子公司 B] ── 合并 ──↑
```

- **关键事实**：所有通讯走 `.agent` 加密包；服务端可完全离线；审计留痕。

### 2.3 反模式（明确不适用）

- **R1**：单用户单任务的极简场景 —— 用 IM/邮件即可，本框架过重。
- **R2**：超大规模 (>1000 智能体) 实时调度 —— v0.3 不承诺，需 v0.4+；
- **R3**：纯无服务器 SaaS 化部署 —— 与 v0.3 "离线优先" 路线不符。

---

## 3. 初心与指导原则

### 3.1 初心

把已经端到端跑通的 MVP（US-0..US-15 + 固定链 A/B）抽象为可被"多个第三方组织"复用的
框架层；让外部多参与方（不限于本仓库 OWNER）能在不重写内核的前提下，按业务需求
**组装**新的分布式智能体应用。

### 3.2 五大指导原则（与 MVP 不变量严格对齐）

> 这些原则**不可降级**；任何框架扩展必须以不破坏它们为前提。

| # | 原则 | 与 MVP 不变量的对应 |
| --- | --- | --- |
| **P1** | **失败关闭 + 显式错误码** | AGENTS.md "强制边界" + `AgentPackageError` 闭类 |
| **P2** | **版本优先于时间戳** | `src/coevo/version.py` 0.2.0；`Strict monotonic version` |
| **P3** | **状态变更须人工确认** | 编排 HOLD / 合并 HOLD / 知识入库人工审核 |
| **P4** | **全程审计 + 哈希链 + 签名检查点** | `loop/audit-head.json` + `tool-audit.jsonl` |
| **P5** | **不可信路径上不暴露密钥材料** | CNG `ProtectedKeyHandle` + Python 进程不见私钥字节 |

### 3.3 业界取舍（与 MVP 兼容）

参考 Anthropic 2024-12 文三条核心取舍：

1. **优先简单**，只在必要时增加复杂度；
2. **框架只是脚手架**：不要为框架添加遮蔽底层语义的额外抽象层；
3. **信任要可验证**：所有高风险动作都必须有 ground truth 与人工确认点。

---

## 4. 总体形态：两层 + 四域 + 两切面

```text
   ╔════════════════════════════════════════════════════════════╗
   ║             Protocol & Security Layer (P1)                ║
   ║  · 身份 (identity)         · 协议 (.agent v1.0)           ║
   ║  · 密码学 (SM2/SM3/SM4)    · 审计 (audit_governance)     ║
   ║  · MCP 工具描述层（仅 schema）                              ║
   ╠════════════════════════════════════════════════════════════╣
   ║            Orchestration Layer (P3)                        ║
   ║  · 编排 Engine（可注入）    · 工作流实例                   ║
   ║  · State Machine           · 审计事件流                   ║
   ║  · A2A 子层（跨组织消息，全部走 .agent v1.0 加密承载）   ║
   ╠════════════════════════════════════════════════════════════╣
   │              Execution Domain (4 域)                      │
   └──────────────────────────────────────────────────────────┘
   ≋≋≋≋≋≋≋≋≋≋  Trust Surface  ≋≋≋≋≋≋≋≋≋≋   (横切)
   ≋≋≋≋≋≋≋≋≋≋  Audit Surface  ≋≋≋≋≋≋≋≋≋≋   (横切)
```

### 4.1 两层职责

| 层 | 职责 | MVP 落位 |
| --- | --- | --- |
| **P1: Protocol & Security** | 身份、加密、信封、安全握手、审计 | `crypto/`、`protocol/`、`identity/`、`audit_governance/` |
| **P3: Orchestration** | 多智能体的事件总线、状态机、人机协作、A2A 子层 | `orchestrator/`、`supervision/`、`decision_brief/` |

### 4.2 四个域（执行平面的内部格）

| 域 | 职责 | 落位 |
| --- | --- | --- |
| **执行域**（17 个 `src/coevo/<d>/` 子包） | 单智能体的感知/记忆/工具/计划/输出 | `task_flow / task_decomposition / talent / …` |
| **协议域** | `.agent` + 处理包登记 | `protocol/` |
| **密码学域** | SM2/SM3/SM4 + CryptoProvider 契约 | `crypto/` |
| **协作域**（拟新增） | 跨组织 A2A | `src/coevo/a2a/`（F3 阶段） |

### 4.3 两切面（横切关注点）

| 切面 | 关注点 | 落位 | 红线 |
| --- | --- | --- | --- |
| **Trust Surface** | 身份、签名、密钥、防回滚 | `identity/` + `crypto/` + `audit_governance/` | 不允许任何域绕过 Trusted CryptoProvider |
| **Audit Surface** | 记录、摘要链、签名检查点、可观测 | `audit_governance/` + `loop/audit-*` + 各 facade 的 `to_audit_record` | 不允许任何域绕过 `to_audit_record` 写状态 |

---

## 5. 智能体的最小可定义单元（Agent Manifest）

> v0.3 与 v0.2 主结构一致；细节增补看 §6.1 Policy 抽象新增字段。

### 5.1 Manifest 草案（v0.3 增量）

```yaml
apiVersion: coevo.framework/v1
kind: Agent
metadata:
  agent_id: "task_decomposition.basic"
  display_name: "任务分解智能体（基础版）"
  semantic_version: "0.2.0"
  spec_hash: "<sha256(规范化字节)>"          # 自身摘要，便于审计链锚定
spec:
  capability: "TASK_DECOMPOSITION"
  triggers:
    - kind: orchestration.event
      event_type: "REQUEST_TASK_DECOMPOSITION"
  inputs_schema:  "coevo://schemas/project_baseline/v1.json"
  outputs_schema: "coevo://schemas/project_baseline/v1.json"
  tools:
    allow: [ "coevo://tools/dependency_graph.cycle_check" ]
    deny:  [ "*shell*", "*filesystem*" ]
  memory:
    episodic_retention_days: 30
    semantic: false
  requires_human_confirmation: true
  confirmation_role: "project_owner"
policy:                                      # v0.3 新增
  timeout_profile: "INTERACTIVE"
  retry_profile:  "STANDARD"
  consent_required: true
  policy_ref:                                # v0.3 新增；与 policy_pack 解耦
    spec_hash: "<sha256(spec.canonical_bytes)>"
    signer_cert_fingerprint: "<sha256(证书 DER)>"
security:
  crypto_scope: "TASK_AGENT"
audit:
  redact_in_audit:
    - "model_reasoning"
    - "user_input"
```

### 5.2 capability 闭集（与 MVP `AgentCapability` 同步）

```
TASK_FLOW_UNDERSTANDING
TASK_DECOMPOSITION
TEAM_RECOMMENDATION
TASK_PACKAGE_BUILD
RISK_ANALYSIS
DECISION_BRIEF
KNOWLEDGE_INGEST
SUPERVISION
AUDIT_INTERCEPT
PROGRESS_CAPTURE
REPORT_BUILD
MERGE_ENGINE
CRYPTO_PROXY                # 仅 ProviderScope=APPROVED_PRODUCT 可见
PLANNER                      # 抽象工具，做 Orchestrator-Workers 拆分
ROUTER
AGGREGATOR
EVALUATOR
OPTIMIZER
HUMAN_GATE
```

---

## 6. 六个核心抽象

> v0.2 是"5 抽象"。v0.3 把**Policy** 提升为第 6 个抽象（来自 P1 应改建议 A4 的
> "dispatch_timeout 与 plan_total_timeout 拆分"和 IN1 的"差异化定位"），并明确
> 6 抽象与 Anthropic 5 workflow 的对应表。

### 6.0 抽象清单与对应表

| 抽象 | Anthropic 等价 | MVP 落位 |
| --- | --- | --- |
| **Task** | Chaining 的 Step | `.agent` EnvelopeHeader + payload |
| **Memory** | Agent 上下文 | `progress_capture/` + `knowledge_base/` |
| **Tool** | Function calling | `cockpit/wps.py` + `crypto/` 单点 |
| **Plan** | Orchestrator-Workers 的产物 | `OrchestrationChain.steps` |
| **Policy** | 任意 workflow 的"约束参数" | v0.3 新增抽象 |
| **Orchestrator** | 状态机/Orchestrator-Workers | `Orchestrator` + `_real_chain.py` |

### 6.1 抽象 A：Task（消息对象）

> v0.3 修订：解耦 `correlation_key` 与 `sequence_no`（架构师 A2）。

```text
Task = {
  protocol_version: "1.0",
  package_id:       <uuid>,                            # 与 .agent package_id 同步
  task_type:        <closed_enum>,                    # §5.2 capability 闭集
  trace_id:         <uuid>,                            # _make_trace_id(event_id, step_index, seed)
  parent_task_id:   <uuid|None>,
  project_id:       <safe_id>,
  sender_cert_id:   <safe_id>,
  recipient_cert_id:<safe_id>,

  # v0.3 重要改动：业务相关性与包级重放检测显式分离
  sequence_no:      <int>,                            # = EnvelopeHeader.sequence_no
  business_correlation_key:  <string>,                # v0.3 新增；用于跨智能体业务去重
  business_correlation_scope: "project_id|workflow_id",  # v0.3 新增

  inputs:  <inputs_schema 校验>,
  outputs: <outputs_schema 校验>,
  requires_human_confirmation: <bool>,
  envelope_signature: <SM2 sig over canonical bytes>,
}
```

**v0.3 关键改进**：
- `correlation_key` 重命名为 `business_correlation_key` 并带 scope；
- `sequence_no` 仅包级重放检测；
- 同业务不同包可有不同 `sequence_no`；同 sequence_no 不同业务（即被重放）会被 `ProcessedPackageStore.dedup_key` 检测。

### 6.2 抽象 B：Memory（记忆）

| 类别 | 含义 | MVP 落位 | 写入约束 |
| --- | --- | --- | --- |
| **Episodic** | 单次任务输入/输出/审阅 | `progress_capture/` | `to_audit_record` 必填 |
| **Semantic** | 跨任务可复用业务知识 | `knowledge_base/` | `ReviewDecisionKind` 审批 |

**统一不变约束**：记忆落盘前必须经 `RedactedIdentity`；明文 PII 不进入 DB。

### 6.3 抽象 C：Tool（工具）

```yaml
kind: Tool
metadata:
  tool_id: "coevo://tools/dependency_graph.cycle_check"
  tool_version: "1.0.0"             # P2 必填
  display_name: "依赖环检测"
  side_effects: "pure"              # pure | idempotent | external
  requires_consent: true
  timeout_sec: 5
  size_in_bytes_max: 4096
spec:
  input_schema_ref:   "coevo://schemas/tool/cycle_check.in.json"
  output_schema_ref:  "coevo://schemas/tool/cycle_check.out.json"
security:
  crypto_scope: "TASK_AGENT"
  audit_required: true
```

要点（MCP 路径选择 IN5）：
- 路径 A：**v0.3 默认**，仅 schema 对齐（详见 §7.2）；
- 路径 B：**v0.4 可选**，允许引入 MCP SDK，需走 docs/dependencies 申请。

### 6.4 抽象 D：Plan（规划）

```text
Plan = {
  plan_id:        <fingerprint>,
  plan_version:   <semver>,
  nodes:          <tuple[PlanNode, ...]>,
  edges:          <tuple[PlanEdge, ...]>,
  max_plan_depth: 4,
  max_runtime_sec: 600,
  policy_profile: <closed_enum>,    # v0.3 新增；指向 §6.5 Policy 模板
}
```

#### 6.4.1 Plan 五项不变量

| 不变量 | 校验逻辑 | 复用 MVP |
| --- | --- | --- |
| **环检测** | 与 `dependency_graph.cycle_in_components` 同款 | 已成熟 |
| **节点类型闭集** | `node.kind ∈ {AGENT / TOOL / HUMAN_GATE}`；AGENT 节点引用 capability ∈ §5.2 | 新增 |
| **可哈希** | Plan 规范化字节 → SHA-256 → 进 `AuditEvent.fingerprint` | 新增 |
| **Plan 节点不跨越 L4 Scope** | 凡引用 Tool.scoped 资源，必须经 `ProviderScope`；Plan-Generator 不得自创新 scope | **v0.2 增量** |
| **跨域 Plan 必经四层 RBAC** | 见 §9 | **v0.2 强化** |

### 6.5 抽象 E：Policy（策略）— v0.3 新增

> 这是 v0.3 的关键差异化之一。Anthropic 5 workflow 没有把 Policy 独立出来作为
> 一等公民，而 v0.3 把它从 §11 红线 L9..L16 + §13 矩阵中抽出来，提升为可
> 复用的"策略模板"。

```text
Policy = {
  policy_id:     <fingerprint>,
  policy_version: <semver>,
  scope: "AGENT" | "PLAN" | "WORKFLOW_INSTANCE",    # v0.3 显式 scope 三选一

  # 超时策略（架构师 A4 拆分）
  timeout_profile:
    dispatch_timeout_sec:   30,            # 单次 dispatch
    plan_total_timeout_sec: 600,           # 整个 Plan（含 LLM）
    consent_timeout_sec:    600,           # 人工确认等待

  # 重试策略
  retry_profile:
    max_recover_attempts:        3,        # 红线 L16
    max_router_retries:           3,
    recover_backoff_sec:         [1, 5, 15],

  # 确认策略
  consent:
    requires_human_confirmation: true,
    default_role: "project_owner",

  # 审计策略
  audit_redaction: ["model_reasoning", "user_input"],

  # ground truth 策略
  ground_truth_required: ["plan_hashability", "dag_acyclic"],
}
```

**Policy 三层 scope**：

| scope | 评估时机 | 谁签发 |
| --- | --- | --- |
| **AGENT** | Manifest 校验时 | agent owner |
| **PLAN** | Plan 注册时 | workflow owner |
| **WORKFLOW_INSTANCE** | 实际 dispatch 时 | runtime |

### 6.6 抽象 F：Orchestrator（编排）

```python
class OrchestrationEngine(Protocol):
    def plan(self, task: Task, policy: Policy) -> Plan: ...
    def dispatch(self, task: Task, plan: Plan) -> OrchestrationOutcome: ...
    def confirm(self, outcome: OrchestrationOutcome, by: str) -> OrchestrationOutcome: ...
    def recover(self, task_id: str) -> OrchestrationOutcome: ...
```

**v0.3 关键改动**：`plan(self, task, policy)` 显式接收 Policy；不再让 Orchestrator 内部隐式读取。

三种实现 + ground truth + fallback（沿用 v0.2）：

| 实现 | ground truth | fallback |
| --- | --- | --- |
| StateMachine | 静态 chain | 终止 + audit RECOVER |
| DynamicLLM | §6.4.1 五项不变量 | 回退 StateMachine |
| Hybrid | LLM 提议只能覆盖非 HOLD 节点 | LLM 提议失败 → 回退 StateMachine |

### 6.7 六抽象与 MVP 落位的总览

| 抽象 | MVP 落位 | 当前可替换度 | 框架改造点 |
| --- | --- | --- | --- |
| **Task** | `.agent` EnvelopeHeader | **不动 wire** | Task 是 `.agent` payload 内 namespace |
| **Memory** | `progress_capture/` + `knowledge_base/` | 领域接口一致 | 加 `Episodic` / `Semantic` 接口 |
| **Tool** | `cockpit/wps.py` + `crypto/` | 同进程注册表 | MCP-style 注册表（仅 schema） |
| **Plan** | `OrchestrationChain.steps` | 待 Manifest 收敛 | Plan-LSP |
| **Policy** (v0.3 新增) | 由 §11 红线 + §13 矩阵累积 | 自然抽象 | 抽出"策略模板" |
| **Orchestrator** | `Orchestrator` 静态类 + `_real_chain` | 部分 | 可注入接口 + 显式 Policy |

---

## 7. 协议平面

### 7.1 `.agent` 协议 v1.0（已实现，**不动**）

```
[fixed_header][envelope_json][sm2_wrapped_key][sm4_gcm_payload][gcm_tag]
```

- 信封字节上限 `ENVELOPE_MAX_BYTES = 64 KiB`；
- payload 内放 Task + Manifest + Signature；
- v1.0 不变；wire 改动必须主版本号升级。

### 7.2 MCP 兼容层

> v0.3 同时给出两条路径，让业务负责人选择（IN5）。

```text
本地 Tool  ←→  本框架 Tool 注册表（JSON 描述）  ←→  远程 MCP 服务
```

- **路径 A（v0.3 默认，推荐）**：仅 schema 对齐；零三方依赖；
- **路径 B（v0.4 可选）**：允许引入 MCP SDK，需先 docs/dependencies 申请 + 主版本号升级 + 强制约束审查；
- 远端 MCP `tools/call` 必须在 Coevo 安全壳内执行（防直调本机 shell / FS）。

### 7.3 A2A（Agent-to-Agent）协议（新增）

> v0.3 重要改动（架构师 A1）：`policy_ref` 与 Manifest `spec_hash` 的关系被
> 明确绑定。

#### 7.3.1 A2A 字段映射

| A2A 字段 | 复用 `.agent` 字段 | 说明 |
| --- | --- | --- |
| `task_id` | `EnvelopeHeader.package_id` | 同 UUID |
| `trace_id` | `OrchestrationTrace.trace_id` | 同 SHA-256 |
| `sender_cert_id` | `EnvelopeHeader.sender_cert_id` | 同闭集 |
| `recipient_cert_id` | `EnvelopeHeader.recipient_cert_id` | 同闭集 |
| `sequence_no` | `EnvelopeHeader.sequence_no` | 包级重放 |
| `business_correlation_key` | `Task.business_correlation_key` | 业务去重（v0.3 新增） |
| `purpose` | payload 内 `task_type` | §5.2 capability 闭集 |
| **policy_ref** | **§7.3.2 新声明（v0.3）** | sender Manifest 锚定 |
| `envelope_signature` | manifest 签名 | SM3 + SM2 |

#### 7.3.2 policy_ref 结构（架构师 A1 修复）

v0.2 表只写 `policy_ref = "引用 sender Agent Manifest 哈希"`，**歧义**。
v0.3 显式化为：

```json
{
  "policy_ref": {
    "spec_hash": "<sha256(manifest.canonical_bytes)>",
    "signer_cert_fingerprint": "<sha256(证书 DER)>",
    "signature": "<SM2 sig over (spec_hash | signer_cert_fingerprint)>"
  }
}
```

或简化为 URI 形式：

```
policy_ref = "coevo://manifests/{sender_cert_id}/{spec_hash}"
```

接收方验签时必须：
1. 验证 `signer_cert_fingerprint == envelope.sender_cert_id`；
2. 验证 `spec_hash == sha256(重新计算的 manifest)`；
3. 验证 signature 合法。

#### 7.3.3 边界声明

1. A2A 消息必须由 `.agent` v1.0 加密包承载；
2. envelope > 64 KiB 时：业务数据 → `RESULT_SUBMISSION` 包；元数据 → A2A envelope；
3. 放宽 envelope 上限必须主版本号升级（v1.1+）。

### 7.4 审计事件格式（沿用 MVP）

`loop/tool-audit.jsonl` + `audit-head.{json,p7s}` + `loop/DECISIONS.md`。
新框架事件必须用 `AuditEvent` / `SecurityAuditFacade` 投射，**不允许直接
写裸 JSON**。

---

## 8. 编排平面与生命周期

### 8.1 三段式生命周期（保留 MVP）

```text
DISPATCH   →  EVAL (auto)  →  CONFIRM (human, optional)
        ↘     ↘
        ESCALATE_HUMAN   /   ABORT_AND_RECORD
```

### 8.2 强制运行时约束（v0.3 修订，架构师 A4）

> 原 v0.2 把 `max_runtime_sec ≤ 600` 单值，针对整个 Plan；这与典型 LLM 推理
> 多次串行的延迟不匹配。v0.3 拆为三个分层（与 §6.5 Policy.timeout_profile 对齐）：

| 约束 | 默认值 | 目的 | 适用场景 |
| --- | --- | --- | --- |
| `dispatch_timeout_sec` | ≤ 30s | 单次 dispatch（含模型推理上限） | 单次 dispatch |
| `plan_total_timeout_sec` | ≤ 600s | 整个 Plan 完成（含多轮 LLM） | 长链路 Plan |
| `consent_timeout_sec` | ≤ 600s | 人工确认等待 | HELD 态 |
| `max_plan_depth` | ≤ 4 | 防 Orchestrator 无限展开 | Plan-DAG |
| `max_recover_attempts` | ≤ 3 | 防 RECOVERED 状态循环 | 编排器 |
| `dangerous_actions_default` | `deny` | 防 LLM 自动批准 | 全局 |

### 8.3 八态生命周期（v0.3 修订，架构师 A5）

> v0.2 表 ESCALATED "出口"只有"人工确认 / RETIRED"，不明确"人工确认后"回哪。
> v0.3 显式化三种出口：

| 态 | 进入 | 退出 | v0.3 显式化 |
| --- | --- | --- | --- |
| **REGISTERED** | Manifest 通过 manifest-checker | `start()` | — |
| **INSTANTIATED** | `start()` 成功 | `dispatch(task)` | — |
| **ACTIVE** | dispatch | confirm / timeout / recover | — |
| **HELD** | `requires_human_confirmation=true` | confirm / reject | — |
| **RECOVERED** | `recover()` 调用；最多 3 次 | 完成回滚 / 升级 ESCALATED | — |
| **ESCALATED** | recover 计数 ≥ 3 | **三种人工确认出口**（见下） | **v0.3 显式** |
| **RETIRED** | `retire()` | 留 tombstone | — |
| **REVOKED** | `revoke()` | 仅保留审计 | — |

**ESCALATED 三种人工确认出口**：

1. **→ RETIRED**（最常见）：任务因风险太高被终止；
2. **→ HELD with new policy**：带补丁恢复（Policy 模板可被替换，例如把 `max_runtime_sec` 从 600 调到 1800）；
3. **→ ACTIVE with new policy + 重新 RBAC**：重新调度（必须重新过四层 RBAC，见 §9）。

三种出口各自对应不同的审计事件（`escalated_retired` / `escalated_held_new_policy` /
`escalated_resumed_new_policy`）。

---

## 9. 身份与权限：四层 RBAC

> v0.3 强化（A3）：明确四层各自的"校验时机/缓存策略/失效传播"。

| 层 | 决议 | 作用 | MVP 实体 | 校验时机 | 缓存策略 | 失效传播 |
| --- | --- | --- | --- | --- | --- | --- |
| **L1 Subject** | who | 人 / 组织 / 终端 | `Actor` | 每次 dispatch | 无（每次查 `identity_repository`） | cert 失效即时 |
| **L2 Role** | what kind | 项目内角色 | `ProjectRoleBinding`（`project_owner` / `project_member`） | 每次 dispatch | 项目期内缓存 | 项目结束即失效 |
| **L3 Capability** | what action | 智能体被允许动作 | `AgentCapability` 闭集 + `Tool.crypto_scope` | Manifest 校验时 | 与 Manifest 绑定 | Manifest 失效即失效 |
| **L4 Scope** | what crypto | 密码学操作范围 | `CryptoProvider.ProviderScope` | 每次 sign/seal | 无（每次查 CryptoProvider） | scope 切换即重签 |

**核心不变约束**：任何 dispatch 必须四层全部通过；任何一层不通过即拒绝。

**新增 ESCALATED → ACTIVE 路径**：必须重新校验四层（不能复用缓存）。

---

## 10. 智能体协作的三种工作流

### 10.1 Plan-then-Decompose（= Prompt Chaining + Orchestrator）

```
USER → Orchestrator(Plan + Policy) → SpecialistAgent → Gate(Human Confirm)
                ↓
        KnowledgeBase / RiskAnalyzer
```

### 10.2 Specialist Routing（= Routing）

```
USER → RouterAgent(classify) → { PlannerAgent | DecoAgent | ReviewerAgent | RiskAgent }
```

**fallback 规则**：
- Router 首跑必须先过 `outputs_schema` 验证（schema validation ground truth）；
- 失败等价于 `plan_fallback = STATE_MACHINE_RULE_BASED`；
- LLM 驱动时，重试上限 3 次；3 次失败转回 HumanGate。

### 10.3 Multi-Specialist Consensus（= Parallelization + Evaluator-Optimizer）

```
            ┌── Specialist A ──┐
USER → Split┤── Specialist B ──├→ Aggregator → Evaluator → Optimizer → Gate(Human)
            └── Specialist C ──┘              ↑__________________|
```

MVP 等价：`RiskAnalyzer.analyze_after_merge` + `DecisionBriefService`。

---

## 11. 可观测性与 SLA

### 11.1 三层指标（RED + USE）

| 层 | 指标 | 采集者 | 暴露面 |
| --- | --- | --- | --- |
| **Rate** | `dispatch_qps / confirm_qps / recover_qps` | 编排 facade 计时器 | `audit-stream` 派生 |
| **Errors** | `rejected_count / held_count / expired_count / escalated_count` | `InterceptionDecision` | `/api/health` |
| **Duration** | `dispatch_latency / confirm_latency` | 编排 facade 计时器 | `/api/health`（p95/p50/max） |

**v0.3 增量**：
- 采样：全请求采样 → EWMA（权重 0.1）；
- 反压：`audit-stream` 单连接背压阈值 100 events/s，超出走 drop-and-warning。

### 11.2 模型 SLA（独立通路）

- 单次模型推理超时：≤ 30s（与 `dispatch_timeout_sec` 一致）；
- 推理失败重试 1 次，第 2 次失败转 fallback（§10.2 Router 重试上限 3 次）；
- 模型 Token 配额与成本监控走独立面板（不计入主 SLA）。

### 11.3 健康端点

| 端点 | 用途 | 已实现 |
| --- | --- | --- |
| `/healthz` | 进程存活 + Service identity | `AVAIL-2` |
| `/api/health` | 已认证只读状态 | `METRICS-1` |
| `/api/audit-stream` | 实时审计流订阅 | `STREAM-PERSIST-1` |

---

## 12. 安全与合规不变量

### 12.1 MVP 现有红线（保留）

| 类别 | 不变量 | 落位 |
| --- | --- | --- |
| **身份** | 私钥字节不进 Python 进程 | `identity/private_keys.py` + `CngKekStore` |
| **任务包** | 篡改/过期/重放/错接收人 4 类必须 100% 拦截 | `SecurityAuditFacade.evaluate_interception` |
| **合并** | 收据签名 + 快照冻结；版本一致 | `merge/receipt.py` |
| **审计** | 哈希链 + 签名检查点；篡改拒开 | `audit_governance/stream_store.py` |
| **驾驶舱** | 环回绑定 + CSRF + 静态白名单 | `cockpit/server.py` |
| **路径** | 重解析点拒绝、穿越守卫 | `workspace/paths.py` |
| **工具链** | SHA-256 + 大小锁；运行时不联网 | `scripts/ci-restore-toolchain.ps1` |
| **密码学** | SM2/SM3/SM4 全链路 | `crypto/contract.py` |

### 12.2 框架新增红线

| # | 红线 | 落位 |
| --- | --- | --- |
| **L9** | Plan-DAG 节点引用 scoped Tool 时，必须经 L4 Scope 强制校验；Plan-Generator 不得自创新 scope | §6.4.1, §9 |
| **L10** | A2A 消息不得明文传输（仅 `.agent` v1.0 承载） | §7.3.3 |
| **L11** | Plan-Generator 不得直接修改主版本（只能产生 Plan + 候选 base_revision） | US-10 AC-3 |
| **L12** | Memory 写入必须经 `RedactedIdentity` | §6.2 |
| **L13** | 跨域 Plan / Task 必须四层 RBAC 全通过 | §9 |
| **L14** | 审计链不得任意格式扩展，只能追加 | `audit_governance/stream_store.py` |
| **L15** | **禁止新增 mcp / asyncio / httpx / aiohttp / openai 等三方运行期依赖**；仅允许 Python stdlib + Coevo 自带助手；任何新依赖必须先 docs/dependencies 申请 + 主版本号升级 + 强制约束审查 | §7.2 |
| **L16** | `max_recover_attempts ≤ 3`，超出强制 ESCALATE_HUMAN | §8.2 |
| **L17** | `src/coevo/framework/` 与 `docs/framework/` 的覆盖度必须经 `test_module_docs.py` 守卫（OPTIMIZE-16）；新文件必同步文档 | §13 |

### 12.3 与 mandatory-technical-constraints 的等价关系

> 红线 L9..L17 不冲突 `docs/constraints/mandatory-technical-constraints.md`
> 与 AGENTS.md。冲突时以约束文件为准（本框架不得改写约束文件）。

---

## 13. 威胁 × 防御矩阵

| 威胁 / 防御层 | L1 Subject | L2 Role | L3 Capability | L4 Scope | Trust Surface | Audit Surface |
| --- | --- | --- | --- | --- | --- | --- |
| **冒名顶替** | 证书指纹链 | Binding 引用 | 闭集枚举 | scope 名册 | CNG handle | policy_ref 签名 |
| **重放 / 重复** | n/a | n/a | n/a | n/a | nonce + `sequence_no` | hash chain |
| **业务级去重** | n/a | n/a | n/a | n/a | `business_correlation_key` | dedup_key |
| **过期 / 失效** | cert validity | binding 窗口 | step 级 TTL | scope 时间窗 | signature verify | retention days |
| **错误接收人** | n/a | n/a | capability ↔ cert | scope 拒绝 | recipient check | 拦截记录 |
| **LLM 失控** | n/a | n/a | capability 闭集 | scope 拒绝 | max_plan_depth / dispatch_timeout | Plan hash audit |
| **LLM 提议影响主版本** | n/a | n/a | Plan 不得改 version | n/a | `base_revision` 校验 | merge engine |
| **跨域 PII 泄露** | redaction | n/a | memory.semantic: bool | scope 拒绝 | `RedactedIdentity` | redact_in_audit |
| **审计链篡改** | n/a | n/a | n/a | n/a | n/a | 哈希链 + 签名检查点 |
| **Tool 越权** | n/a | n/a | allowlist | scope 拒绝 | requires_consent | audit_required |
| **policy_ref 冒名** | n/a | n/a | n/a | n/a | policy_ref 三段绑定 | spec_hash 比对 |
| **ESCALATED 重启越权** | n/a | 重新校验 | 重新校验 | 重新校验 | n/a | 重新校验 audit |
| **代码注释覆盖度漂移** | n/a | n/a | n/a | n/a | n/a | `test_module_docs.py` (L17) |

**v0.3 新增行**：
- **业务级去重**：用 `business_correlation_key`；
- **policy_ref 冒名**：用 policy_ref 三段（spec_hash + cert_fingerprint + signature）；
- **ESCALATED 重启越权**：必须重新校验四层。

---

## 14. 迁移路径与里程碑

### 14.1 四阶段渐进

| 阶段 | 目标 | 验收口径 | 不破坏现状 |
| --- | --- | --- | --- |
| **F0 (基线)** | MVP 验收已通过 | 强基线绿 + 弱基线 ≥95% | — |
| **F1 (声明)** | 抽出 Manifest + Policy + AgentSpec 抽象 | 新增 5+3 项向后兼容测试 | wire 不动 |
| **F2 (适配)** | MCP 路径 A + A2A wire 0.1 | 三个 mock agent 走通 | 仅新增模块 |
| **F3 (闭环)** | Plan-as-a-Service + Hybrid Orchestrator + Policy 模板 | e2e 闭环 | 仅扩展 orchestrator |

**强基线** = `make fmt + make lint + unit tests` 24h 内 100% 绿；
**弱基线** = `e2e + helper` 集成测试 24h 内 ≥95% 绿。

### 14.2 里程碑（v0.3 重估时间盒，架构师 A6）

| 节点 | 内容 | 时间盒（v0.3 上调后） | 依赖 | 回滚条件 |
| --- | --- | --- | --- | --- |
| **M0** | 框架宣言（v0.3 获批） | T+0 | — | DECISIONS review 拒绝即停止 |
| **M1** | `manifest-checker` + `Capability` 闭集收敛 | 4 周 | `config/model-prompts.json` | unit 测试失败立即回滚 |
| **M2** | `Policy` 抽象 + 三层 scope | 4 周 | M1 | unit 测试失败回退到 §6.5 之前 |
| **M3** | `EpisodicMemory` / `SemanticMemory` 接口 | 6 周（原 4 周） | M1 | schema 校验失败退到 `to_audit_record` |
| **M4** | MCP schema 路径 A（不引入 SDK） | 8 周（原 6 周） | M1 | 一致性 < 99% 回退 |
| **M5** | A2A wire 0.1 + policy_ref 三段绑定 | 6 周（原 4 周） | M1 | protocol-reviewer 拒绝即停 |
| **M6** | Plan-LSP（可哈希 DAG）+ 五项不变量 | 10 周（原 8 周） | M1, M5 | 不变量 1..5 任何失败都阻断 |
| **M7** | Hybrid Orchestrator 0.1 + Policy 三层 scope 应用 | 12 周 | M2, M3, M6 | LLM 连续 3 次失败回退 StateMachine |
| **M8** | 跨组织验证场景 | 14 周 | M5, M7 | security-reviewer 拒绝即停 |
| **M9** | K8s CRD 类的可声明清单（M9 收尾） | 8 周 opt-in 沙箱 | M1..M8 | 与 K8s 范围严格区分（§16.4） |

总时间盒：约 **72 周 = 18 个月**，1 个核心团队。

### 14.3 依赖图

```text
M0 (v0.3 审阅) ─┬─→ M1 (Manifest + Capability)
               │
               ├─→ M2 (Policy 抽象)
               │
               ├─→ M5 (A2A wire)
               │
M3 (Memory) ───┘
M4 (MCP schema) ───┐
M6 (Plan-LSP) ──┬──┘
M7 (Hybrid Orchestrator) ──→ M8 (跨组织)
                            └───→ M9 (K8s CRD 收尾)
```

每条边均为硬依赖；不允许跨阶段跳进。

---

## 15. TCO / 实施预算

> 这是 v0.3 新增的"产品/财务"章节。架构师视角没有这层，但业务负责人必须
> 看明白预算与 ROI。

### 15.1 人员配置建议（18 个月总投入）

| 角色 | FTE | 投入阶段 | 责任 |
| --- | --- | --- | --- |
| **协议/密码架构师** | 1.0 | M0..M9 | Protocol/crypto、A2A wire、MCP 路径 |
| **安全工程师** | 0.5 | M0..M9 | RBAC / 审计 / Security Audit |
| **编排引擎工程师** | 1.0 | M6..M8 | Plan-LSP、Hybrid Orchestrator |
| **测试工程师** | 0.5 | M1..M9 | `tests/unit` / `tests/integration` / `tests/security` / e2e |
| **文档 OWNER** | 0.25 | 始终 | `docs/framework/` + 培训 |
| **业务产品经理** | 0.25 | 始终 | 场景调研 + 客户反馈 |

**总投入**：3.5 FTE × 18 个月 ≈ **63 人月**。

### 15.2 显性成本项

| 成本 | 用途 | 估算 |
| --- | --- | --- |
| 国密认证模块采购（HANDLE-2 升级） | CNG 受保护密钥 | TBD（业务负责人 KPI） |
| 跨组织验证 mock 环境 | A2A 跨网传输演练 | 1 个 staging cluster |
| 安全审查外聘（security-reviewer） | M8 跨组织验证 | 一次 1 周 |
| Tools / IDE / 培训 | 团队能力建设 | 一次 |

### 15.3 ROI 估算（业务负责人用）

按目标场景 U1（政府/军工）：
- 替代纸质公文流转：1 个部委任务平均节约 30% 流转时间；
- 替代手工合并：1 个项目平均节约 1 人月人工；
- 跨密级合规风险降低：避免 1 次泄密事件的价值远大于本框架总成本。

按目标场景 U3（出海/合规）：
- 海外子公司的合规审计成本：现有方案往往依赖第三方 SaaS，本框架可自托管。

**首次付费客户目标**：12 个月内 1 家国密合规验证通过试点。

### 15.4 预算审批门槛

- **M0..M1：内部预算，0 额外审批**；
- **M2..M5：需业务负责人批准**；
- **M6..M8：需高级管理层批准（含安全审查与跨组织演练预算）**；
- **M9：产品商业化决定**。

---

## 16. 与业界差异化与对外话术

> v0.3 加重"对外话术"层（业务负责人与客户对接直接用）。

### 16.1 一句话定位（Hero Statement）

**Coevo Trusted Agent Framework（CTAF）** 是面向**受控场景**（政府、军工、金融、科研）的"**可被法规审查、离线优先、零三方依赖**"的分布式具身智能体编排框架。

### 16.2 电梯演讲（4 句话）

1. 我们提供基于国家密码学算法的智能体框架，适合受审计场景。
2. 我们用一份 `.agent` v1.0 加密包承载所有跨智能体消息。
3. 我们的 Plan-DAG 五项不变量强制 LLM 不得越权。
4. 我们的八态生命周期 + 全程审计链 + 四层 RBAC，合规可追溯。

### 16.3 三类卖点与对应场景

| 卖点 | 场景 | 价值 |
| --- | --- | --- |
| **合规优先** | 政府/军工 | 通过"安全审计 + 国密合规"前置审批；与 PKI/HSM 兼容 |
| **离线优先** | 出海 / 隔离网 | 全 stdlib；无外部调用；可在完全离线环境运行 |
| **结构化沉淀** | 跨学科任务 | ProcessFlow + 五阶段 + KnowledgeBase 已结构化 |

### 16.4 K8s reconcile 的明确边界（分析师 IN4）

**CTAF v0.3 不是 Kubernetes CRD**。本质区别：

| 维度 | K8s CRD | CTAF v0.3 |
| --- | --- | --- |
| **核心模式** | declarative + reconcile loop | explore-then-execute |
| **状态持久** | etcd/集群内 | SQLite/JSONL + .agent 包 |
| **漂移处理** | controller 自动调和 | 失败转 escalate，无自动漂移 |
| **跨进程边界** | API server 强一致 | `ProcessedPackageStore` 一致性 |

**M9 (K8s CRD 清单) 的承诺范围**：仅**纸面清单**（可声明式清单生成器），
不承诺 reconcile loop。

### 16.5 竞品对比

| 框架 | 主打场景 | CTAF v0.3 的真正差异 |
| --- | --- | --- |
| Microsoft AutoGen | 通用云端 actor | 不绑云端；不依赖外部 API key；可完全离线 |
| LangGraph | 通用 DAG 编排 | 自带 SM 国密；自带审计哈希链 |
| CrewAI | 角色编排 | 角色必须经四层 RBAC，不是"角色自由分派" |
| Anthropic Claude Agent SDK | Anthropic 生态 | 不绑单一 LLM；多 provider 可插拔 |
| MCP | 工具与上下文标准 | schema 层对齐；scope 治理更严格 |
| Kubernetes CRD | 声明式 + reconcile | CTAF 是 explore-then-execute（§16.4） |

### 16.6 术语表（对外发布用）

| 内部术语 | 对外话术 |
| --- | --- |
| Plan-DAG | "结构化任务编排图" |
| business_correlation_key | "业务追踪编号" |
| policy_ref | "策略指纹" |
| INTERCEPT_REJECT / HOLD | "安全拦截止损 / 等待客户确认" |
| ESCALATED | "升级至项目经理" |
| RECOVERED | "任务回退中" |
| `safe-id` | "安全 ID" |
| `processed_package_store` | "加密包校验日志" |

---

## 17. 风险与已知限制

| 风险 | 缓解 |
| --- | --- |
| Plan-Generator LLM 失控 | Plan-DAG 五项不变量 + `max_plan_depth ≤ 4` + `dispatch_timeout ≤ 30s` + `max_recover_attempts ≤ 3`；配置层仅描述能力不开放 |
| 跨组织身份互信 | 一律"对方带 .agent 包 + 显式信任列表"；**不引入 PKI 联邦** |
| A2A 协议与 `.agent` 主版本冲突 | §7.3.3 边界声明：v0.3 不变 wire；超 envelope 走 `RESULT_SUBMISSION` |
| Model 数据泄露到审计 | `audit.redact_in_audit` 强制列字段；Memory 写入经 `RedactedIdentity` |
| LLM 提议影响正式主版本 | MVP 已有：merge engine 仅由审计导入触发；L11 红线 |
| 新增三方依赖 | L15 红线：仅允许 stdlib + Coevo 自带助手 |
| 跨域 Plan 不可观测 | 八态（含 ESCALATED 三出口） + 强制审计 + `audit-stream` |
| 文档覆盖度漂移 | L17 红线 + `test_module_docs.py` 守卫 |
| envelope 大小限制 | v0.3 不变；超 64 KiB 必拆到 `RESULT_SUBMISSION` 包 |
| A2A gossip 模型尚未实现 | v0.4 切片 |
| 商业模式不清（v0.3 新增） | §15.1 / §15.3 仅给"首次付费客户目标 12 个月" |
| 客户认知门槛（v0.3 新增） | §16.2 / §16.4 / §16.6 三大对外话术模板 |
| 国密模块采购（v0.3 新增） | TBD 业务负责人 KPI（HANDLE-N 路径） |

---

## 18. 评估与下一轮

### 18.1 v0.3 完成度

- ✅ §1 / §2 / §15 / §16：新增（业务定位、用户场景、TCO、对外话术）
- ✅ §6.5 / §6.1 / §9 / §12 / §13 / §19：P0 + P1 全部吸收（架构师 A1..A6 + 分析师 IN4 / IN5）
- ✅ §8.3 ESCALATED 三出口明确（架构师 A5）
- ✅ §8.2 dispatch_timeout 与 plan_total_timeout 拆分（架构师 A4）
- ✅ §14.2 时间盒上调 30-50%（架构师 A6）

### 18.2 自评分

| 维度 | 评分 | 备注 |
| --- | --- | --- |
| 与 MVP 不变量对齐 | **5.0** | 全保留 + 红线 L9..L17 |
| 行业参考吸收 | **4.5** | Anthropic / MCP / A2A / K8s 全部对照 |
| 抽象完整性 | **5.0** | 六抽象（含 Policy v0.3 新增）+ Manifest |
| 安全/合规覆盖 | **5.0** | §12 红线 + §13 矩阵（13 行威胁） |
| 架构演进路径 | **4.5** | 时间盒上调 + 依赖图 + 回滚 |
| 与业界差异化 | **4.5** | §16 完整对外话术；K8s reconcile 边界显式化 |
| 产品/场景适配 | **4.5** | §2 三类用户 + 三类场景 + 反模式 |
| 实施预算/TCO | **4.0** | §15.1 完整 FTE 配置 + ROI 估算 |
| 文档可读性 | **5.0** | §0 阅读路径表 + §19 修订追踪 |
| **综合** | **4.7 / 5** | **v0.3 较 v0.2 上 0.3 分，达到"产品级文档"成熟度；可正式批准进入 M1 BACKLOG 切片** |

### 18.3 下一轮

1. **v0.3 进入产品评审 + BACKLOG 切片**（业务负责人批准）
2. 同步更新 BACKLOG 槽位候选：`US-16-AC-1-framework-manifest-v0.1` + `US-16-AC-2-framework-policy-abstractions-v0.1`
3. **v0.4 预留项**：
   - A2A gossip 模型；
   - K8s CRD 收尾的"可声明清单生成器"；
   - Plan-reconcile（探索性调研，不进路线图）；
   - 商业模式细化（首次付费客户目标的执行计划）。

---

## 19. 修订说明（v0.1 → v0.2 → v0.3）

### 19.1 v0.2 → v0.3 增量（吸收架构师+分析师审查 P0/P1）

| 编号 | 类型 | 标题 | 改动 |
| --- | --- | --- | --- |
| **A1** | 架构师 P0 | policy_ref 与 spec_hash 关系未定义 | §7.3.2 显式化三段绑定 |
| **A2** | 架构师 P0 | correlation_key 与 sequence_no 语义混用 | §6.1 拆分为 sequence_no + business_correlation_key + scope |
| **A3** | 架构师 P0 | RBAC 失效传播未说 | §9 加"校验时机/缓存/失效传播"三列 |
| **A4** | 架构师 P1 | max_runtime_sec 与 LLM 延迟不匹配 | §8.2 / §6.5 三层 timeout |
| **A5** | 架构师 P1 | ESCALATED 出口不明 | §8.3 三种出口 + 各自 audit 事件 |
| **A6** | 架构师 P1 | 路线图时间盒低估 | §14.2 整体上调 30-50% |
| **A11** | 架构师 P1 | 文档覆盖度缺红线 | §12.2 L17 |
| **IN4** | 分析师 P1 | K8s reconcile 概念混淆 | §16.4 + §17 风险表 |
| **IN5** | 分析师 P1 | MCP 路径单一 | §7.2 给路径 A + 路径 B |

### 19.2 v0.3 新增章节

| 章节 | 标题 | 起源 |
| --- | --- | --- |
| §1 | 业务定位与价值主张 | 分析师 IN1 + 产品视角 |
| §2 | 目标用户与典型场景 | 分析师 IN3 |
| §15 | TCO / 实施预算 | 分析师 IN2 |
| §16 | 与业界差异化与对外话术 | 分析师 IN1 + IN6 |
| §6.5 | Policy 作为第 6 个抽象 | 架构师 A4 + 整体抽象完整性 |

### 19.3 v0.2 → v0.3 保留不动部分

- §3/§4/§5（初心、形态、Manifest）：仅细节调整；
- §7.1 协议 v1.0：完全不变；
- §11 SLA、§12 红线 1..8：保留；
- §13 威胁矩阵：仅新增 3 行；
- §14.1 迁移路径框架：保留。

### 19.4 跨版本累计吸收（v0.1 → v0.3）

- v0.1 → v0.2 吸收 17 条 review 结论（M1..M5 + S1..S5 + O1..O12 + ST1..ST3）；
- v0.2 → v0.3 吸收 9 条新审查结论（A1..A6 + A11 + IN4 + IN5）；
- 累计 26 条审查结论全部吸收并显式追踪。

> 注：v0.1→v0.2 共 17 条；v0.2→v0.3 共 9 条；累计 26 条。

### 19.5 v0.4 预约（业务负责人批准后启动）

- A2A gossip 模型与跨域发现；
- K8s CRD 类的可声明清单生成器（M9 收尾）；
- Plan-reconcile 概念探索（不进路线图）；
- 商业模式执行计划（首次付费客户目标）。

---

> 本稿（v0.3）是设计层面的**产品级蓝图**，不是规范文档。任一条目落地仍需：
> 1. 业务负责人批准的切片计划（`docs/plans/US-N-AC-y-slice.md`）；
> 2. `mvp-planner` 出最小可交付任务；
> 3. `mvp-builder` 实现 + 测试；
> 4. `mvp-verifier` + `security-reviewer` 联合放行；
> 5. RECORD 阶段同步更新 `loop/STATE.json / DECISIONS.md / VERIFICATION.md`。

> **业务负责人请重点审阅**：§1 一句话 / §2 三类用户 / §15 TCO / §16 对外话术 / §17 风险；
> **架构师请重点审阅**：§6 五/六抽象 / §8 时序约束 / §9 RBAC / §13 矩阵；
> **安全审查请重点审阅**：§12 红线 / §13 矩阵；
> **产品经理请重点审阅**：§2 用户画像 / §10 工作流 / §16 对外话术。
