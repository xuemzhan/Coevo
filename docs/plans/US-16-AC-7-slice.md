# US-16-AC-7 切片计划：Plan 规范化序列化（Plan-LSP，CTAF §14.2 / M6）

> 状态：已批准（2026-08-08 用户指令"继续开发 + 全量门禁检查"）。本轮跑全量
> `make quality`（用户指示），另跑定向测试与增量门禁。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-7-plan-lsp-v0.1`
- 用户故事：US-16【框架层】——把 AC-2 的 Plan 模型补上规范化序列化（Plan-LSP），
  提供 JSON 序列化入口并钉住与 plan_fingerprint 的同一规范化规则。

## 2. AC 清单与目标测试

| AC | 内容 | 目标测试 |
| --- | --- | --- |
| AC-7.1 | Plan ↔ 规范 JSON 往返字节级一致 | test_plan_json_round_trip_identity |
| AC-7.2 | 序列化与 plan_fingerprint 同规则 | test_fingerprint_consistency |
| AC-7.3 | validate_plan_json 序列化入口 | test_validate_plan_json_entry |
| AC-7.4 | 大小/深度/节点/边/tool_args 上限 | test_plan_json_limits |
| AC-7.5 | 纯函数 / 离线 / stdlib / 审计投影 / L17 | test_stdlib_only + test_module_docs |

## 3. 最小可交付切片

在 `src/coevo/framework/plan.py` 增加 `plan_to_json` / `json_to_plan`
（严格解析：重复键、未知字段、类型/结构校验）+ `MAX_PLAN_JSON_BYTES`；
在 `src/coevo/framework/validation.py` 增加 `validate_plan_json`（JSON →
Plan → validate_plan）。新增 `docs/framework/plan-lsp.md`；更新模块文档（L17）。

## 4. 需修改/新增文件

- 修改 `src/coevo/framework/plan.py`、`src/coevo/framework/validation.py`、
  `src/coevo/framework/__init__.py`
- 新增 `tests/unit/test_framework_plan_lsp.py`
- 新增 `docs/framework/plan-lsp.md`；修改 `docs/modules/framework.md`

## 5. 测试要点（含异常/负例）

- 往返：合法 Plan → JSON → Plan 相等，规范字节一致；含 AGENT/TOOL/HUMAN_GATE 混合；
- 指纹一致：json_to_plan(plan_to_json(p)).plan_id == p.plan_id；
- 严格解析：重复键拒绝、未知顶层/节点/边字段拒绝、kind 非法值拒绝、
  tool_args 非键值对数组拒绝、字段类型错误拒绝；
- validate_plan_json：合法 JSON 通过；环/越界能力/L18 键/RBAC 拒绝（复用 AC-2 规则）；
- 上限：JSON > 64 KiB 拒绝；节点 > 64 / 边 > 128 / tool_args > 32 拒绝；
- L15 stdlib / L17 文档守卫。

## 6. 安全与兼容性风险

- 序列化入口是信任边界：严格解析防重复键/未知字段/超大输入；
- 与 plan_fingerprint 同一规范化规则，防指纹分叉；
- 不改 `.agent` wire、不改编排器；零新增三方依赖；文档守卫。

## 7. 明确不属于本轮

- M7（Hybrid Orchestrator）、M8/M9；A2A gossip / MCP-B / K8s CRD（v0.5）；
- `.agent` wire 改动。

## 8. 可验证完成条件

- 定向测试全绿；`make quality`（全量）exit=0，audit fully-sealed；
- 追溯矩阵新增 US-16 | AC-7 行；security-reviewer 无 Critical/High。

## 9. 给实施者的指令包

按第 4/5 节实现；对齐框架层既有风格；只 stage 本轮文件；提交信息
`feat(framework): US-16-AC-7 plan serialization (Plan-LSP, M6)`。

## 10. 审查门

- security-reviewer：**是**（序列化解析边界）；
- protocol-reviewer：**否**（不触碰 wire）。
