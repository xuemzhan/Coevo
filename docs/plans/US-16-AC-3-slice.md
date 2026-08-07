# US-16-AC-3 切片计划：框架能力闭集收敛（CTAF §5.2 / M1b）

> 状态：已批准（2026-08-08 用户指令"继续开发"）。按用户指示：本轮只跑增量门禁
> （fmt + lint + 定向测试），不跑全量质量门禁；验证与安全审查按独立治理口径执行。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-3-framework-capability-closedset-v0.1`
- 用户故事：US-16【框架层】——把 CTAF §5.2 能力闭集与既有 `AgentCapability`
  收敛为单一事实来源，消除 AC-1 遗留的"扩展名未收敛"缺口（M1b）。

## 2. AC 清单与目标测试

| AC | 内容 | 目标测试 |
| --- | --- | --- |
| AC-3.1 | 能力注册表覆盖 §5.2 全部名称，MVP 映射 AgentCapability | test_registry_covers_ctaf_closed_set |
| AC-3.2 | 双名解析：枚举值/CTAF 名同一条目；闭集外与大小写变体拒绝 | test_dual_name_resolution |
| AC-3.3 | manifest-checker 切换注册表：MVP 未映射拒绝、CRYPTO_PROXY 需 approved scope、框架抽象可用 | test_manifest_capability_rules |
| AC-3.4 | 与 AgentCapability 双向一致（无孤儿/无未映射） | test_bidirectional_consistency |
| AC-3.5 | 纯函数 / 离线 / stdlib / L17 文档守卫 | test_stdlib_only + test_module_docs |

## 3. 最小可交付切片

新增 `src/coevo/framework/capability.py`（能力注册表：CapabilityKind /
CapabilityEntry / CAPABILITY_CLOSED_SET / resolve_capability /
consistency_report），manifest-checker 的 capability 校验从直接
`AgentCapability` 枚举切换为注册表（含 CRYPTO_PROXY 的 approved scope 约束）；
新增 `docs/framework/capability-closedset.md`；更新 `docs/modules/framework.md`
文件清单（L17）。

## 4. 需修改/新增文件

- 新增 `src/coevo/framework/capability.py`
- 修改 `src/coevo/framework/manifest_checker.py`（capability 校验切换 +
  `AgentManifest.capability` 改为规范能力名）
- 修改 `src/coevo/framework/__init__.py`（重导出）
- 新增 `tests/unit/test_framework_capability.py`；更新
  `tests/unit/test_framework_manifest_checker.py`（能力断言适配）
- 新增 `docs/framework/capability-closedset.md`；修改 `docs/modules/framework.md`

## 5. 测试要点（含异常/负例）

- 注册表：§5.2 全部 19 个名称存在；MVP 条目 agent_capability 映射正确；
  CRYPTO_PROXY 标记 approved-only；框架抽象 6 个名称登记；
- 双名：`task_decomposition` 与 `TASK_DECOMPOSITION` 解析同一条目；
  `Task_Decomposition`（混大小写）、未知名、空串拒绝；
- manifest：MVP 未映射能力（如 KNOWLEDGE_INGEST，注册表标记 pending）拒绝；
  CRYPTO_PROXY + mvp-prototype 拒绝、+ approved-product 通过；
  PLANNER（框架抽象）通过；规范名/枚举值均通过；
- 一致性：每个 AgentCapability 成员都在注册表中（无孤儿）；CTAF MVP 名
  都有映射或显式 pending 标记；
- L15 stdlib / L17 文档守卫。

## 6. 安全与兼容性风险

- 能力闭集是信任边界：注册表必须 fail-closed（未知/未映射拒绝）；
- CRYPTO_PROXY 与 approved scope 强绑定，防原型 scope 冒用密码代理能力；
- 切换 manifest-checker 校验不改 `.agent` wire、不改编排器注册逻辑；
- 零新增三方依赖；文档守卫。

## 7. 明确不属于本轮

- M2..M9（Policy 已交付 AC-2；Memory/MCP/A2A/Plan-LSP/Hybrid 等后续里程碑）；
- `.agent` wire 改动、编排器 `AgentCapability` 枚举本身不扩展（用注册表收敛）。

## 8. 可验证完成条件

- `python -m unittest tests.unit.test_framework_capability` 全绿 +
  manifest-checker 回归全绿；
- `python scripts/quality_gate.py --target fmt` 与 `--target lint` exit 0
  （按用户指示不跑全量 quality；豁免留痕）；
- 追溯矩阵新增 US-16 | AC-3 行；安全审查无 Critical/High。

## 9. 给实施者的指令包

按第 4/5 节实现；保持框架层既有风格（frozen dataclass、fail-closed、
stdlib-only、审计投影）；只 stage 本轮文件；提交信息
`feat(framework): US-16-AC-3 capability closed-set convergence (M1b)`。

## 10. 审查门

- security-reviewer：**是**（能力闭集/CRYPTO_PROXY 信任边界）；
- protocol-reviewer：**否**（不触碰 wire）。
