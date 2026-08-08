# FRAMEWORK-OPTIMIZE-17 切片计划：共享 ISO-UTC 解析助手（timefmt.py）

> 状态：已批准（2026-08-08 用户指令"继续优化，不做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-17`（ENG-BASE，dependencies=[]）。
- 目的：`decision_brief/models.py`、`merge/receipt.py`、`risk/models.py`、
  `supervision/models.py` 四处重复实现 `_parse_utc`（ISO-8601 UTC 'Z' 解析，
  结构一致、消息/异常类各异）；统一到 `src/coevo/timefmt.py` 的
  `parse_iso_utc`（error_factory + 消息参数保留各模块异常类与消息，行为逐字节
  不变），延续 ids.py / relpath.py / powershell.py 的收敛模式。

## 2. 交付

- `src/coevo/timefmt.py`：新增
  `parse_iso_utc(value, *, error_factory, not_utc_message, invalid_message) -> datetime`：
  非 str / 无 'Z' 后缀 → error_factory(not_utc_message)；fromisoformat 失败 →
  error_factory(invalid_message)；utcoffset != 0 → error_factory(not_utc_message)
  （该分支实际不可达——替换 'Z' 为 '+00:00' 后偏移恒为 0，保留以保持语义一致）。
- 四模块 `_parse_utc` 收敛为薄包装（调用点与签名不变）：
  * decision_brief：DecisionBriefValidationError + "must be ISO-8601 UTC" /
    "must be valid ISO-8601 UTC"；
  * merge/receipt：MergeCommitReceiptError + "must be UTC ending in Z" /
    "must be ISO-8601 UTC"（原实现无 utcoffset 检查，行为等价，已核对）;
  * risk：RiskValidationError + "must be an ISO-8601 UTC string ending in Z" /
    "must be a valid ISO-8601 UTC string"；
  * supervision：SupervisionValidationError + 同 risk 消息。
- `docs/modules/root_modules.md` 更新 timefmt.py 条目。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize18.py`：
  * parse_iso_utc 正反例：合法 'Z'、无 'Z'、非法格式、非字符串、消息/异常工厂
    注入（各模块消息逐字节）、返回类型；
  * 守卫：四模块 `_parse_utc` 委托 timefmt（源码含 timefmt 导入、不含本地
    fromisoformat 解析副本）。
- 回归：decision_brief / merge / risk / supervision 相关测试。

## 4. 完成条件

- 定向测试全绿；fmt + lint exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-17` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**是**（时间校验为协议/审计安全关键，须确认消息/异常类
  逐字节保留）；protocol-reviewer：**否**。
