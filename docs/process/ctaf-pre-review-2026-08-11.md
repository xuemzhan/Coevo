# CTAF 设计提案 v0.4.1 实现方视角预评审（非独立评审）

> 日期：2026-08-11
> 视角：**实现方预评审**——由实现者核对提案与代码/测试/文档的一致性，产出可交接材料。
> **本报告不替代独立架构评审**：CTAF-PROPOSAL-REVIEW 仍为 REVIEW-REQUIRED 外部门禁，
> 独立评审人应以本预审为输入之一，独立复核下述全部结论。

## 1. 结论摘要

- 提案 v0.4.1 与当前实现**高度对齐**：M1a/M1b/M2/M3/M4/M5/M6/M7/M9 的核心切片均已交付
  （`src/coevo/framework/` 13 个模块 + 20+ 个框架测试文件），红线 L9..L19 大部分有
  实现与守卫测试；作为实施基线总体可行。
- 未发现阻断性设计缺陷；发现 **3 处文档一致性缺陷（P1）+ 2 处交付跟踪问题（P2）**，
  均可在定稿前低成本修正。
- 明确边界：四层 RBAC 中的 L2 ProjectRoleBinding 等实体仍为**设计态**；M8（跨组织验证）
  **未实现**（提案自述为 14 周里程碑）。"已交付"仅指框架核心切片，不等于全里程碑完成。

## 2. 审查方法与证据基线

- 通读 `docs/plans/distributed-agent-framework/design-proposal.md` 全文（19 章）；
- 对照 `src/coevo/framework/` 全部 13 个模块与 `tests/unit/test_framework*.py`、
  `tests/unit/test_pipeline_framework_gate.py`、`tests/unit/test_module_docs.py`（L17 守卫）；
- 对照 `docs/framework/` 8 份契约与 `docs/plans/distributed-agent-framework/README.md`；
- 门禁基线：fast `fb8029ba3cf2de07` / quality `b96157dbb895a417`（全量门禁未在本预评审
  中重新运行）。

## 3. 提案 → 实现 → 测试对照表

| 提案条目 | 实现落位 | 测试 | 状态 |
|---|---|---|---|
| §5.1/5.3 Manifest + T1..T6 | `framework/manifest_checker.py` | `test_framework_manifest_checker.py`、`test_framework_optimize24.py` | 已交付 |
| §5.2 capability 闭集（M1b） | `framework/capability.py`、`agent_catalog.py` | `test_framework_capability.py`、`test_arch_review_4_agent_manifest_registry.py` | 已交付，与提案闭集一致（含 CRYPTO_PROXY / PLANNER..HUMAN_GATE） |
| §6.5 Policy 四 Profile + L16（M2） | `framework/policy.py` | `test_framework_policy.py` | 已交付（EMERGENCY fail-fast、max_recover_attempts≤3、事后 30 分钟确认） |
| §6.2 Memory（M3） | `framework/memory.py` | `test_framework_memory.py` | 已交付（L12 脱敏 + 审批投影） |
| §6.3 Tool / MCP 路径 A（M4） | `framework/tools.py` | `test_framework_tools.py` | 已交付 |
| §7.3 A2A + policy_ref 五步验证（M5） | `framework/a2a.py` | `test_framework_a2a.py` | 已交付（trace_id 64-hex、大小边界、fail-closed） |
| §6.4 Plan-LSP + 五不变量（M6） | `framework/plan.py`、`validation.py` | `test_framework_plan_lsp.py`、`test_framework_plan_l18.py`、`test_framework_validate_plan.py` | 已交付（L18 白名单拒收策略数值键） |
| §6.6/8.3/8.4 Hybrid Orchestrator + L19（M7） | `framework/orchestrator.py`、`lifecycle.py`、`integration.py` | `test_framework_orchestrator.py`、`test_framework_lifecycle.py`、`test_framework_integration*.py`、`test_pipeline_framework_gate.py` | 已交付（validate_plan 前置无旁路；ESCALATED 回 ACTIVE 必须经 HELD） |
| §16.4 K8s 纸面清单（M9） | `framework/k8s_listing.py` | `test_framework_k8s_listing.py` | 已交付（仅声明导出，无 reconcile loop） |
| §12.2 L17 文档守卫 | `tests/unit/test_module_docs.py` | — | 已交付 |
| §14.2 M8 跨组织验证 | 未实现 | — | **未来里程碑**（提案自述 14 周） |
| §9 四层 RBAC（L1..L4） | L1/L3/L4 有实现证据；**L2 ProjectRoleBinding 为设计态** | 部分 | 独立评审需确认运行时接线覆盖度 |

## 4. 发现清单

### P1（一致性缺陷，建议定稿前修正）

- **F-1 累计口径自相矛盾**：§19.3 累计为"60 条（含迭代交叉）/ 53 条 net new"，而
  §19.4（"累计口径统一表"，A8 落地）仍写"17 + 9 + 19 = 45 条 / 38 条 net new"。
  §19.4 表格未纳入 v0.4 → v0.4.1 的 +15 项，与 §19.3、README 的 60/53 口径冲突；
  与 §19.6 F14"累计表同步"自述不符。
- **F-2 威胁矩阵行数口径不一致**：提案 §13/§19.6 F3 为 **16 行**（13 + 4），但
  `distributed-agent-framework/README.md` 的 v0.4 对比表写 **15 行**。
- **F-3 trace_id 格式标注冲突**：§6.1 Task.trace_id 标注 `<uuid>`，§7.3.1 A2A 映射标注
  SHA-256；实现（`a2a.py`）强制 64-hex（SHA-256）。实现与 §7.3.1 一致，§6.1 标注需修正。

### P2（交付跟踪 / 文档路径）

- **F-4 README"待补充文档"表过时**：该表将 `manifest-checker.md`（M1a）与
  `policy-template.md`（M2）标为待交付，但 M1a/M2 的实现与测试已交付，契约实际落在
  `design-proposal.md §5.3`、`docs/architecture/agent-manifest-registry.md`；`docs/framework/`
  下无独立 `manifest-checker.md` / `policy-template.md`。表格未随交付路径更新。
- **F-5 交付口径易误读**：README 将 M1b/M3/M4/M5/M6/M7/M9 标为"已交付"，但 M8 与
  L2 RBAC 实体仍为设计/未来项；建议在 README 增加"已交付=核心切片，不等于里程碑整体
  完成"的显式说明，避免对外误读。

### 实现对照说明（非缺陷）

- `policy.py` 的 EMERGENCY 语义、L16 上限、L18 白名单、L19 状态机路径均与提案一致；
- capability 闭集（含 KNOWLEDGE_INGEST、CRYPTO_PROXY approved-product 约束、
  PLANNER..HUMAN_GATE 抽象）与提案 §5.2 一致；
- A2A 五步验证、大小边界、trace_id 64-hex 与 §7.3 一致。

## 5. 独立评审重点交接清单

独立评审人（CTAF-PROPOSAL-REVIEW）应至少独立复核：

1. **policy_ref 五步验证时序**：`framework/a2a.py` + `test_framework_a2a.py`（冒名 / 替换 /
   伪造 / 大小边界）；
2. **validate_plan 前置无旁路**：`framework/integration.py`（guarded_dispatch）+
   `test_pipeline_framework_gate.py` + orchestrator-seam 契约；
3. **L18 / L19 实现**：`framework/validation.py`、`framework/lifecycle.py` +
   `test_framework_plan_l18.py`、`test_framework_lifecycle.py`；
4. **L17 文档守卫**：`tests/unit/test_module_docs.py`；
5. **四层 RBAC 运行时接线覆盖度**（L2 为设计态，需判定是否满足提案 §9 承诺）；
6. 本预审 F-1..F-5 是否已修正。

## 6. 建议

1. 定稿前修正 F-1..F-3（低风险文字修正，不涉及代码）；
2. 更新框架 README 待补充文档表与交付口径（F-4/F-5）；
3. 维持 `CTAF-PROPOSAL-REVIEW` 外部门禁，安排独立架构评审并以本预审为输入；
4. M8 与 L2 RBAC 实体在进入实施前需单独切片计划与安全评审。
