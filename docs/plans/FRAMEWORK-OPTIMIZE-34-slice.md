# FRAMEWORK-OPTIMIZE-34 切片计划：agent_package.from_mapping 跨字段校验抽取

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-34`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-33]）。
- 目的：`EnvelopeHeader.from_mapping`（103 行）构造后的**跨字段不变量校验块**
  （package_type 枚举 / 协议期望值 / compression 白名单 / expires>created /
  nonce 非空 / 1 TiB 上限）抽为静态方法 `_validate_cross_fields`，`from_mapping`
  收敛为约 78 行；校验顺序、错误消息、失败关闭语义逐字节不变；导入面不变。

## 2. 交付

- `src/coevo/protocol/agent_package.py`：新增 `EnvelopeHeader._validate_cross_fields`
  （原 354-380 行原样搬移，与既有 `_require_*` 静态助手风格一致）；
  `from_mapping` 尾部改为 `EnvelopeHeader._validate_cross_fields(envelope)`。
- 守卫测试 `tests/unit/test_framework_optimize35.py`。

## 3. 测试要点

- 守卫：`from_mapping` 方法体不超过 90 行（原 103）；`_validate_cross_fields`
  存在且被调用；关键错误消息标记存活（连续字面量）；
- 回归：agent_package 相关既有测试（unit + integration envelope 测试）全绿。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-34` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯结构迁移，包校验语义不变）。
- protocol-reviewer：**否**。
