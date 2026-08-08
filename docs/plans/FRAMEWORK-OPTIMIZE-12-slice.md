# FRAMEWORK-OPTIMIZE-12 切片计划：framework 内部 canonical 函数收敛到 canon

> 状态：已批准（2026-08-08 用户指令"继续下一步"，延续"基于框架，优化原来系统
> 应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-12`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-11]）。
- 目的：framework 内部仍有 4 个与 `canon.canonical_json_bytes` 完全等价的
  domain canonical 序列化（tools 的 schema/descriptor、memory 的 record、
  k8s_listing 的 listing），统一到共享 canon（单一事实源，字节逐位不变）。
  `framework/plan.py::canonical_plan_bytes` 因 `default=_json_default`
  （Enum 处理）语义不同，保留独立实现。

## 2. 交付

- `src/coevo/framework/tools.py`：`canonical_schema_bytes` /
  `canonical_descriptor_bytes` 函数体改为 `canonical_json_bytes(x)`。
- `src/coevo/framework/memory.py`：`canonical_record_bytes` 函数体改为
  `canonical_json_bytes(payload)`。
- `src/coevo/framework/k8s_listing.py`：`generate_listing` 函数体改为
  `canonical_json_bytes(generate_listing_json(inp))`。
- 删除上述模块中不再使用的 `json.dumps(` canonical 副本。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize12.py`：
  * 4 个函数输出与 `canon.canonical_json_bytes` 一致（字节回归，含嵌套/中文）；
  * 守卫：tools/memory/k8s_listing 不再含 `json.dumps(`；
  * plan.py 保留 `default=_json_default`（语义差异留痕）。
- 回归：test_framework_tools / test_framework_memory / test_framework_k8s_listing
  / test_framework_plan_lsp + 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-12 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（memory/listing canonical 进入指纹/审计路径，须确认
  字节逐位不变）；protocol-reviewer：**否**。
