# US-16 用户故事与验收标准草案（CTAF v0.4.1 框架层）

> 状态：**已批准（2026-08-07 业务负责人）并已并入**
> `docs/requirements/mvp-user-stories.md` 与 `loop/BACKLOG.yaml`（US-16-AC-1）；
> 追溯矩阵行在对应 AC 完成时登记。本文件保留为审批与 AC 映射的原始凭证。
> 来源：CTAF 设计文档 §18.3 / §19.6（`docs/plans/distributed-agent-framework/`）。

---

## US-16：【框架层】受控智能体声明校验与策略抽象（CTAF v0.4.1 落地）

### 用户故事

作为受控场景（政府 / 军工 / 金融 / 科研）的安全管理员和框架扩展者，
我想在部署点对智能体声明（Agent Manifest）进行强制校验，并把 Plan 的数值边界
统一收敛到策略模板（Policy），以便只有声明合规、策略受控的智能体才能进入编排，
且 LLM 生成的 Plan 无法越权、绕过人工确认或擅自修改执行边界。

### 验收标准（AC-1：manifest-checker，对应 CTAF §5.3 / M1a）

1. 最小合法 Agent Manifest 通过校验并注册（T1）；
2. capability 必须属于 CTAF §5.2 能力闭集，闭集外一律拒绝，不得注册（T2）；
3. `requires_human_confirmation` 缺省为 true，与现有编排步骤语义一致（T3）；
4. `crypto_scope` 必须属于 ProviderScope 闭集，否则拒绝（T4）；
5. `redact_in_audit` 必须是审计投影字段的子集，否则拒绝（T5）；
6. `spec_hash` 必须等于"排除 `spec_hash` 与 `policy_ref.signature` 自指字段后的
   规范化字节"的 SHA-256；无法规范化或哈希不一致时拒绝（CTAF §19.6 F5）；
7. `policy_ref` 三段绑定（spec_hash / signer_cert_fingerprint / SM2 签名）任一
   不匹配即拒绝；验签公钥必须来自证书链，不得取自 policy_ref 自身（F8）；
8. `policy_profile` 必须绑定 `policy_version`，无版本引用或与部署点策略注册表
   不一致时拒绝（F7）；
9. 校验失败仅返回 `failure_reason`，不得注册；校验与注册逻辑必须为纯函数、
   可离线运行、零新增三方依赖（L15）；
10. `.agent` v1.0 wire 字节级保持不变，并提供回归测试钉住（T6）。

### 验收标准（AC-2：Policy 抽象与 validate_plan，对应 CTAF §6.5 / M2）

1. Policy 包含 `policy_id` / `policy_version` / `profile` / `timeout_profile` /
   `retry_profile` / `consent` / `audit_redaction` / `ground_truth_required` 字段，
   `policy_version` 为必填（F7）；
2. 提供 4 个默认 Profile（INTERACTIVE / BATCH / AUDIT_ONLY / EMERGENCY），
   所有 Profile 的 `max_recover_attempts` ≤ 3，对齐 L16 与状态机
   "recover 计数 ≥ 3 → ESCALATED"（F1）；
3. EMERGENCY 采用 fail-fast 语义：1 次重试、总时限 60s、不在线等待人工，
   改为强制审计 + 事后 30 分钟内人工确认，且不依赖外部通知 SaaS（F1 / F9）；
4. Plan 内不得出现策略归属数值键（max_plan_depth / max_runtime_sec /
   max_recover_attempts / timeout 等），数值统一从 Policy 取（L18 白名单口径，F6）；
5. `PlanNode.tool_args` 等数据字段按 schema 允许携带数值，不得被 L18 误拒（F6）；
6. `OrchestrationEngine.validate_plan` 为 dispatch 前置必调：校验 §6.4.1 五项
   不变量 + L18 + L19，失败返回 REJECTED，不得进入 dispatch（A9 / F4）；
7. ESCALATED 状态机不得直跳 ACTIVE，任何回到 ACTIVE 的路径必须经 HELD 中转，
   RETIRED 可直接退出（L19 语义，F4）；
8. Policy / Plan 校验逻辑必须为纯函数、可离线运行、零新增三方依赖，
   新增模块受 `test_module_docs.py` 文档守卫约束（L17）。

---

## AC ↔ 落点 ↔ 测试映射（供 mvp-planner / verifier / security-reviewer 使用）

| AC | CTAF v0.4.1 落点 | 建议测试（含异常/失败输入） | 里程碑 | 审查门 |
| --- | --- | --- | --- | --- |
| AC-1 | §5.1 / §5.2 / §5.3 / §7.3.2 | T1..T6；另补：YAML 别名/重复键拒绝、超长字段拒绝、`spec_hash` 自指字段参与哈希时拒绝、`policy_ref` 签名被替换拒绝、能力字符串大小写/空白变体拒绝 | M1a | security-reviewer（必要时 protocol-reviewer 联动 agent-package） |
| AC-2 | §6.5 / §6.4.1 / §6.6 / §8.3 / §8.4 / §12.2 | 4 个 Profile 边界测试；L18 负例（Plan 携带 timeout/attempts 被拒）；tool_args 数值合法通过；L19 状态机测试（ESCALATED→ACTIVE 直跳被拒、经 HELD 通过）；validate_plan 五项不变量逐项负例 | M2 | security-reviewer |

## 明确不属于本轮（防范围蔓延，对应 CTAF §19.6 暂缓/拒绝项）

- `.agent` v1.0 wire 的任何改动（保持字节级不变）；
- A2A gossip、MCP 路径 B、K8s CRD 清单（维持 v0.5 预约）；
- 跨组织 PKI 联邦（明确不做，采用显式信任列表）；
- Plan-LSP（M6）、Hybrid Orchestrator（M7）、Memory 接口（M3）等后续里程碑。

## 完成定义（草案）

- AC-1 全部 10 项、AC-2 全部 8 项各有可重复测试（含异常输入与重放/越权场景）；
- `make quality` 全绿，审计 fully-sealed；
- `docs/traceability/requirements-test-matrix.md` 新增 US-16 两行且无悬空条目；
- 独立 `mvp-verifier` 放行；AC-1/AC-2 均触发 `security-reviewer` 独立审查；
- `loop/STATE.json` / `DECISIONS.md` / `VERIFICATION.md` 同步更新。
