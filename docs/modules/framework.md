# `framework/` — 框架层（CTAF US-16）

## 定位

CTAF（Coevo Trusted Agent Framework）v0.4.1 框架层在 `src/coevo` 的落位。
US-16-AC-1 交付部署点 manifest-checker：只有声明合规、策略受控的智能体才能
注册进入编排；US-16-AC-2（Policy 抽象 + validate_plan）在下一轮落地。
设计基线：`docs/plans/distributed-agent-framework/design-proposal.md` §5。

## 职责边界

- **in scope**：Agent Manifest 强制校验（能力闭集 / 人工确认默认 / crypto_scope
  闭集 / 审计脱敏子集 / spec_hash 排除自指字段 / policy_ref 三段绑定 /
  policy_version 绑定）、"校验通过才注册"的薄封装、T6 wire 回归；
- **out of scope**：Policy 抽象与 validate_plan（US-16-AC-2）、A2A 实现、
  MCP、Plan-LSP、Hybrid Orchestrator、跨组织 PKI 联邦；不修改 `.agent` v1.0
  wire 与既有编排代码。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `manifest_checker.py` | `check`、`AgentManifest`、`ManifestCheckInput`、`ManifestCheckResult`、`ManifestRegistry`、`PolicyRegistry`/`CertificateResolver`/`SignatureVerifier`（注入协议） | 部署点强制校验（纯函数、fail-closed）+ 校验通过才注册 |

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
  扩展名在 M1b 收敛）；
- fail-closed：未知能力、闭集外 scope、投影外脱敏、自指哈希、签名/指纹不匹配、
  缺失版本、坏 JSON/BOM/重复键一律拒绝并返回 `failure_reason`；
- 校验为纯函数（证书/验签/策略注册表全部注入）；注册副作用拒绝失败结果；
- L15：仅标准库、可离线运行；L17：本文件为 `test_module_docs.py` 守卫对象。

## 测试覆盖

- `tests/unit/test_framework_manifest_checker.py`（T1..T5 + F5/F7/F8 负例 +
  L15 stdlib 断言，覆盖 US-16 AC-1.1..AC-1.9）；
- `tests/unit/test_agent_wire_regression.py`（T6：Fixed Header /
  Envelope canonical 字节级回归，覆盖 AC-1.10）。

## 依赖与下游

- 上游：`orchestrator.models.AgentCapability`、`crypto.contract.ProviderScope`；
- 下游：部署点编排注册入口（后续切片接入）；`docs/plans/US-16-AC-1-slice.md`
  为已批准切片计划。

## 配置与错误语义

- 无环境变量；异常类型 `ManifestValidationError`（注册拒绝）；
- 校验失败不抛异常，以 `ManifestCheckResult.failure_reason` 返回（审计友好）。
