# US-16-AC-1 切片计划：框架层 manifest-checker（CTAF §5.3 / M1a）

> 状态：已批准（2026-08-07 业务负责人）。规划包由 loop-engineer 按 mvp-planner
> 方法论产出；实施由 mvp-builder 执行，验证由 mvp-verifier / security-reviewer
> 独立完成。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-1-framework-manifest-checker-v0.1`
- 用户故事：US-16【框架层】受控智能体声明校验与策略抽象——安全管理员/框架扩展者在
  部署点对 Agent Manifest 强制校验，只有声明合规、策略受控的智能体才能进入编排。

## 2. AC 清单与测试映射现状

| AC | 现状 | 目标测试 |
| --- | --- | --- |
| AC-1.1 最小合法通过并注册 | 无 | test_manifest_minimal_valid |
| AC-1.2 capability 闭集拒绝 | 无 | test_manifest_unknown_capability_rejected |
| AC-1.3 人工确认默认 true | 无 | test_manifest_requires_human_confirmation_default |
| AC-1.4 crypto_scope 闭集 | 无 | test_manifest_crypto_scope_enum |
| AC-1.5 redact ⊆ 审计投影 | 无 | test_manifest_redact_in_audit_subset |
| AC-1.6 spec_hash 排除自指字段 | 无 | test_spec_hash_excludes_self_referential_fields |
| AC-1.7 policy_ref 三段绑定 + 证书链公钥 | 无 | test_policy_ref_binding_and_cert_public_key |
| AC-1.8 policy_version 绑定 | 无 | test_policy_version_required_and_registered |
| AC-1.9 失败不注册 / 纯函数 / 离线零依赖 | 无 | test_failure_does_not_register + test_pure_stdlib_only |
| AC-1.10 `.agent` v1.0 wire 字节级回归 | 既有 header 测试，缺钉死回归 | test_agent_wire_v1_unchanged（T6） |

## 3. 本轮最小可交付切片

新增 `src/coevo/framework/` 包与 `manifest_checker.py`：以纯函数实现
Agent Manifest 强制校验（CTAF §5.3 契约），全部为 stdlib、零三方依赖、
可离线运行；提供"校验通过才注册"的薄封装。同步补齐 L17 文档守卫与 T6
wire 字节级回归。

## 4. 需修改/新增文件

- 新增 `src/coevo/framework/__init__.py`（重导出 + `__all__`）
- 新增 `src/coevo/framework/manifest_checker.py`（核心校验纯函数 +
  `ManifestCheckInput` / `ManifestCheckResult` 不可变数据类 +
  `register` 薄封装）
- 新增 `tests/unit/test_framework_manifest_checker.py`（AC-1.1..AC-1.10）
- 新增 `tests/unit/test_agent_wire_regression.py` 或并入既有 wire 测试文件
  （T6 字节级回归，使用固定 fixture 钉住 `.agent` v1.0 envelope 字节）
- 新增 `docs/modules/framework.md`（模块文档，L17 守卫）
- 修改 `docs/modules/README.md`（模块索引登记 framework，防
  `test_module_docs.py` 失败）
- 可能修改 `docs/modules/root_modules.md` / 索引（若守卫要求）

## 5. 需新增测试（含异常/重放/越权/穿越边界）

- 最小合法 Manifest 通过（T1）；
- 闭集外能力、缺失能力、大小写/空白变体能力拒绝（T2）；
- `requires_human_confirmation` 缺省 true 且显式 false 覆盖（T3）；
- `crypto_scope` 闭集外拒绝（T4）；
- `redact_in_audit` 非审计投影子集拒绝（T5）；
- `spec_hash`：与规范化字节（排除 `spec_hash`/`policy_ref.signature`）不一致拒绝；
  把自指字段计入哈希（朴素全字节哈希）时判定失败（F5 负例）；
- `policy_ref`：签名被替换/指纹不匹配/公钥不来自证书链均拒绝（F8 负例）；
- `policy_version`：缺失、与部署点策略注册表不一致拒绝（F7）；
- 校验失败不注册、不产生任何业务副作用；校验函数无 IO（注入 resolver）；
- 源码级断言：仅导入标准库（零三方依赖，L15）；
- T6：`.agent` v1.0 envelope 固定字节 fixture 哈希回归，防止 wire 漂移。

## 6. 安全与兼容性风险（对照强制性约束）

- 身份/信任：policy_ref 验签公钥必须来自证书链，不得取自包内容本身（§7.3.3）；
- 规范化：spec_hash 的规范化规则必须与 `.agent` 协议 JSON 规范化（协议 §10）一致，
  避免双源漂移；自指字段排除规则必须显式化；
- 能力闭集：不得与现有 `AgentCapability` 漂移，需单一事实来源；
- 依赖：禁止新增三方依赖（L15），仅 stdlib；
- 文档守卫：新增包必须满足 `test_module_docs.py`（L17），否则门禁失败；
- 兼容：`.agent` v1.0 wire 不变，T6 钉住。

## 7. 明确不属于本轮

- AC-2（Policy 抽象 / validate_plan，M2，下一轮登记）；
- `.agent` wire 任何改动、A2A 实现、MCP 路径 B、跨组织 PKI 联邦；
- Plan-LSP（M6）、Hybrid Orchestrator（M7）、Memory 接口（M3）；
- 不修改现有编排/状态机代码。

## 8. 可验证完成条件

- `python -m unittest tests.unit.test_framework_manifest_checker` 全绿；
- `python scripts/quality_gate.py --target fmt`、`--target lint`（含
  traceability + audit verify）exit 0；
- `make quality` 由 mvp-verifier 在只读沙箱实际执行，exit 0 且 audit
  fully-sealed；
- 追溯矩阵新增 US-16 | AC-1 行，无悬空条目；
- 独立 mvp-verifier 放行 + security-reviewer 无 Critical/High。

## 9. 给 mvp-builder 的指令包

按第 4/5 节实现；遵守仓库既有模块风格（单文件巨型模块风格、docstring、
类型注解、`to_audit_record` 投影惯例）；仅 stdlib；测试同步提交；只 stage
本轮文件；提交信息 `feat(framework): US-16-AC-1 manifest-checker + tests`；
提交后运行 `python scripts/quality_gate.py --target fmt` 与
`--target lint` 及定向单元测试，全部通过后再交付。

## 10. 审查门

- security-reviewer：**是**（身份/信任/policy_ref/审计脱敏，BACKLOG
  security_review=true）；
- protocol-reviewer：**否**（wire 不变，T6 守护；A2A 协议面改动留待 M5）。
