# Tool 注册表与 MCP schema 路径 A（CTAF §6.3 / §7.2 / M4）

> 里程碑：M4（2026-08-08 交付）。实现：`src/coevo/framework/tools.py`。
> 工作项：`US-16-AC-5-framework-tool-registry-v0.1`。

## 定位

把工具声明收敛为统一 `Tool` 模型，并提供 **MCP 路径 A（仅 schema 对齐、
零三方依赖）** 的双向转换：

- 标准 MCP 字段（`name` / `description` / `inputSchema` / `outputSchema`）直接映射；
- 框架专属字段放入 `x-coevo` 扩展块，普通 MCP 消费者可读共享子集，框架侧
  往返保真；
- 一致性守卫：支持子集的往返转换规范字节一致（fixture 语料测试钉住）；
  不支持的关键字/结构显式拒绝，绝不静默丢失（"一致性 ≥ 99%" 的操作化口径）。

## Tool 模型（CTAF §6.3）

| 字段 | 约束 |
| --- | --- |
| `tool_id` | safe-id |
| `tool_version` | semver（P2 必填） |
| `side_effects` | PURE / IDEMPOTENT / EXTERNAL 闭集 |
| `requires_consent` | bool |
| `timeout_sec` | 正整数 |
| `size_in_bytes_max` | 非负整数 |
| `crypto_scope` | ProviderScope 闭集 |
| `audit_required` | bool |
| `input_schema` / `output_schema` | JSON Schema 子集（白名单） |

## JSON Schema 子集（fail-closed）

白名单关键字：`type` / `properties` / `required` / `items` / `enum` /
`description`；`type ∈ {string, number, integer, boolean, object, array}`。

- object 必须有 `properties`，`required ⊆ properties` 键；
- array 必须有 `items`；
- `enum` 非空且 ≤ 64 项；
- 未知关键字（如 `pattern` / `additionalProperties`）显式拒绝；
- 深度 ≤ 16、规范字节 ≤ 16 KiB。

## 注册表

`ToolRegistry.register` 先 `validate_tool` 再登记（校验与注册分离）；重复
`tool_id` 拒绝；容量上限 128。

## 安全边界

- schema 解析是信任边界：未知关键字拒绝而非忽略，防语义漂移；
- `x-coevo` 扩展块缺失或含未知键拒绝（无法保真即失败关闭）；
- 纯函数、仅标准库、可离线运行（L15，不引入 MCP SDK）；文档守卫（L17）。

## 测试覆盖

`tests/unit/test_framework_tools.py`（AC-5.1..5.5，含往返一致、未知键/扩展块缺失、
schema 白名单/超限负例、stdlib 断言）。
