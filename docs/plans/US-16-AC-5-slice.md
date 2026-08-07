# US-16-AC-5 切片计划：Tool 抽象与 MCP schema 路径 A（CTAF §6.3 / §7.2 / M4）

> 状态：已批准（2026-08-08 用户指令"继续开发"）。本轮只跑增量门禁（fmt + lint +
> 定向测试），不跑全量 quality（用户指示，豁免留痕）。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-5-framework-tool-registry-v0.1`
- 用户故事：US-16【框架层】——把工具声明收敛为统一 Tool 模型，提供 MCP 路径 A
  （仅 schema 对齐、零三方依赖）的双向转换与子集一致性守卫。

## 2. AC 清单与目标测试

| AC | 内容 | 目标测试 |
| --- | --- | --- |
| AC-5.1 | Tool 统一模型 + P2 版本必填 | test_tool_model_and_version_required |
| AC-5.2 | 注册表：重复拒绝、校验注册分离 | test_registry_duplicate_and_fail_closed |
| AC-5.3 | Tool↔MCP 描述双向转换（子集往返字节级一致） | test_mcp_round_trip_identity |
| AC-5.4 | JSON Schema 子集白名单 + 越界/超限拒绝 | test_schema_subset_validation |
| AC-5.5 | 纯函数 / 离线 / stdlib / L17 | test_stdlib_only + test_module_docs |

## 3. 最小可交付切片

新增 `src/coevo/framework/tools.py`：ToolSideEffect / Tool（frozen）/
ToolRegistry / validate_tool / validate_schema（白名单子集 + 深度/大小/枚举上限）/
canonical_schema_bytes / tool_to_mcp / mcp_to_tool（x-coevo 扩展块承载框架字段）。
新增 `docs/framework/tool-registry.md`；更新 `docs/modules/framework.md`（L17）。

## 4. 需修改/新增文件

- 新增 `src/coevo/framework/tools.py`；修改 `src/coevo/framework/__init__.py`
- 新增 `tests/unit/test_framework_tools.py`
- 新增 `docs/framework/tool-registry.md`；修改 `docs/modules/framework.md`

## 5. 测试要点（含异常/负例）

- Tool：tool_version 缺失/非 semver 拒绝；side_effects 闭集外拒绝；timeout≤0、
  size<0 拒绝；crypto_scope 闭集外拒绝；tool_id 非 safe-id 拒绝；
- 注册表：重复 tool_id 拒绝；未校验工具不得注册（校验注册分离）；
- 转换：合法 Tool → MCP 描述 → Tool 往返规范字节一致（fixture 语料）；
  MCP 描述缺 x-coevo 扩展块拒绝（无法保真）；未知顶层键拒绝；
- Schema：type 缺失/未知值拒绝；object 无 properties 或 required 超集拒绝；
  array 无 items 拒绝；enum 为空/超上限拒绝；未知关键字（如 pattern、
  additionalProperties）拒绝；深度/大小上限拒绝；
- L15 stdlib / L17 文档守卫。

## 6. 安全与兼容性风险

- Schema 子集必须 fail-closed：未知关键字拒绝而非忽略（防语义漂移）；
- MCP 描述往返保真依赖 x-coevo 扩展块，缺失即拒绝；
- 不引入 MCP SDK、不改 `.agent` wire；
- 零新增三方依赖；文档守卫。

## 7. 明确不属于本轮

- MCP 路径 B（引入 SDK，v0.5 预约）；远程 MCP 服务调用；
- M5（A2A wire）、M6（Plan-LSP）、M7（Hybrid）、M8/M9；
- `.agent` wire 改动。

## 8. 可验证完成条件

- `python -m unittest tests.unit.test_framework_tools` 全绿；
- `python scripts/quality_gate.py --target fmt` 与 `--target lint` exit 0
  （不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 US-16 | AC-5 行；安全审查无 Critical/High。

## 9. 给实施者的指令包

按第 4/5 节实现；对齐框架层既有风格（frozen dataclass、注入协议、fail-closed、
stdlib-only、审计投影）；只 stage 本轮文件；提交信息
`feat(framework): US-16-AC-5 tool registry + MCP schema path A (M4)`。

## 10. 审查门

- security-reviewer：**是**（工具声明/权限字段/schema 解析边界）；
- protocol-reviewer：**否**（不触碰 wire）。
