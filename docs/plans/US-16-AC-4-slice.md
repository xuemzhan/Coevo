# US-16-AC-4 切片计划：框架 Memory 抽象（CTAF §6.2 / M3）

> 状态：已批准（2026-08-08 用户指令"继续开发"）。本轮只跑增量门禁（fmt + lint +
> 定向测试），不跑全量 quality（用户指示，豁免留痕）。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-4-framework-memory-interface-v0.1`
- 用户故事：US-16【框架层】——把记忆写入抽象为统一 MemoryRecord 模型，强制
  审计投影（Episodic）、审批（Semantic）与 L12 脱敏（RedactedIdentity 语义）。

## 2. AC 清单与目标测试

| AC | 内容 | 目标测试 |
| --- | --- | --- |
| AC-4.1 | MemoryRecord 统一模型 + 规范化指纹 | test_record_fingerprint_hashability |
| AC-4.2 | Episodic：审计投影必填 + 注入 store fail-closed | test_episodic_write_audit_and_store |
| AC-4.3 | Semantic：审批必过（映射 ReviewDecisionKind.APPROVE） | test_semantic_requires_approval |
| AC-4.4 | L12：敏感字段经 Redactor 转摘要，明文不到 store | test_l12_plaintext_never_reaches_store |
| AC-4.5 | 纯函数 / 离线 / stdlib / L17 | test_stdlib_only + test_module_docs |

## 3. 最小可交付切片

新增 `src/coevo/framework/memory.py`：MemoryKind / MemoryRecord（frozen +
规范化指纹）/ Redactor、EpisodicMemoryStore、SemanticApprovalChecker、
SemanticMemoryStore 注入协议 / `redact_record` / `MemoryService.write`
（校验→脱敏→审批（Semantic）→注入持久化，失败关闭）/ MemoryWriteResult
（审计投影）。新增 `docs/framework/memory-interface.md`（progress_capture /
knowledge_base 适配映射）。

## 4. 需修改/新增文件

- 新增 `src/coevo/framework/memory.py`；修改 `src/coevo/framework/__init__.py`
- 新增 `tests/unit/test_framework_memory.py`
- 新增 `docs/framework/memory-interface.md`；修改 `docs/modules/framework.md`
  （文件清单 + 测试覆盖，L17）

## 5. 测试要点（含异常/负例）

- 指纹：record_id ≠ 规范化指纹拒绝；kind 闭集外拒绝；project_id 非 safe-id 拒绝；
- Episodic：store 收到记录且 to_audit_record 键集固定；store 异常 → 拒绝；
- Semantic：approval=False 拒绝（reason 含 approval）；True 通过；
- L12：敏感字段在 store 中只能是 `REDACTED:<sha256>` 摘要；已摘要值保持；
  Redactor 异常 → 拒绝；未声明 sensitive_fields 的"疑似敏感"字段不做假设；
- 审计投影：MemoryWriteResult.to_audit_record 键集固定（accepted/record_id/
  kind/occurred_at/failure_reason）；
- L15 stdlib / L17 文档守卫。

## 6. 安全与兼容性风险

- L12 是红线：脱敏必须在写入边界强制执行，明文不得进入持久化；
- Semantic 审批委托注入检查器，异常视为拒绝；
- 不改 progress_capture / knowledge_base 现有实现，仅文档化适配映射；
- 零新增三方依赖；文档守卫。

## 7. 明确不属于本轮

- M4（MCP 路径 A）、M5（A2A wire）、M6（Plan-LSP）、M7（Hybrid）、M8/M9；
- progress_capture / knowledge_base 代码改造（仅适配映射文档）；
- `.agent` wire 改动。

## 8. 可验证完成条件

- `python -m unittest tests.unit.test_framework_memory` 全绿；
- `python scripts/quality_gate.py --target fmt` 与 `--target lint` exit 0
  （不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 US-16 | AC-4 行；安全审查无 Critical/High。

## 9. 给实施者的指令包

按第 4/5 节实现；对齐框架层既有风格（frozen dataclass、注入协议、fail-closed、
stdlib-only、审计投影）；只 stage 本轮文件；提交信息
`feat(framework): US-16-AC-4 memory abstraction (M3)`。

## 10. 审查门

- security-reviewer：**是**（L12 脱敏 / 审批边界）；
- protocol-reviewer：**否**（不触碰 wire）。
