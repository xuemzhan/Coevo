# Plan 规范化序列化（Plan-LSP，CTAF §14.2 / M6）

> 里程碑：M6（2026-08-08 交付）。实现：`src/coevo/framework/plan.py` 的
> `plan_to_json` / `json_to_plan` / `parse_plan_json_bytes` +
> `validation.py` 的 `validate_plan_json`。
> 工作项：`US-16-AC-7-plan-lsp-v0.1`。

## 定位

把 AC-2 的 Plan 模型补齐规范化序列化（Plan-LSP）：Plan ↔ 规范 JSON 双向转换，
序列化 JSON 与 `plan_fingerprint` 共用同一规范化规则（排序键、紧凑分隔、ASCII
安全转义、排除自指 `plan_id`），保证"序列化 → 反序列化 → 指纹"三方一致。

## 入口

- `plan_to_json(plan)`：校验后输出规范 JSON 对象；
- `json_to_plan(mapping)`：严格解析（未知顶层/节点/边字段、类型错误、非法 kind、
  tool_args 形状错误全部拒绝）；
- `parse_plan_json_bytes(data)`：字节级严格解析（BOM、重复键、UTF-8、64 KiB
  上限、非标准 JSON 常量 NaN/Infinity 拒绝、病态嵌套异常收束）；
- `validate_plan_json(...)`：序列化入口 → Plan → `validate_plan`
  （五项不变量 + L18 + L19），失败返回 REJECTED 而非抛异常。

## 上限（防序列化 DoS）

- JSON 字节 ≤ 64 KiB；
- 节点 ≤ 64、边 ≤ 128、tool_args 条目 ≤ 32、单值文本 ≤ 256；
- 以上与 `validate_plan_structure` 共享，序列化路径与内存路径同一守卫。

## 安全边界

- 序列化入口是信任边界：未知字段/重复键显式拒绝，不静默忽略；
- 非标准 JSON 常量（NaN / Infinity / -Infinity）解析时显式拒绝，保持规范化 JSON 可移植；
- 病态嵌套（RecursionError / MemoryError / ValueError）统一收束为校验失败，不向调用者抛异常；
- 与 `plan_fingerprint` 同一规范化规则，防指纹分叉；
- 纯函数、仅标准库、可离线运行（L15）；文档守卫（L17）。

## 测试覆盖

`tests/unit/test_framework_plan_lsp.py`（AC-7.1..7.5，含往返一致、指纹一致、
重复键/未知字段/坏 kind/坏 tool_args/BOM/超限、validate_plan_json 环与坏 JSON、
L18 序列化负例、病态嵌套变异常收束、非标准常量拒绝、stdlib 断言）。
