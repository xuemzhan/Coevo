# FRAMEWORK-OPTIMIZE-18 切片计划：OPTIMIZE-11 补漏（knowledge_base SAFE_ID）+ 共享 non-empty 校验

> 状态：已批准（2026-08-08 用户指令"继续优化，不做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-18`（ENG-BASE，dependencies=[]）。
- 目的：
  ① 补漏 FRAMEWORK-OPTIMIZE-11：`knowledge_base/models.py` 仍保留本地
  `_SAFE_ID` 正则副本（与共享 `ids.SAFE_ID` 逐字节相同），统一到共享叶子；
  ② `risk/models.py` 与 `supervision/models.py` 的 `_non_empty` 同构重复
  （消息 "must be a non-empty string" 相同、异常类各异），统一到共享
  `validate.non_empty_string`（error_factory 保留异常类）。

## 2. 交付

- `src/coevo/validate.py`：新增 `non_empty_string(value, *, error_factory, field)`——
  非 str / 空 / 全空白 → error_factory(f"{field} must be a non-empty string")。
- `knowledge_base/models.py`：删除本地 `_SAFE_ID` 正则，改
  `from src.coevo.ids import SAFE_ID as _SAFE_ID`（调用点不变）。
- `risk/models.py` / `supervision/models.py`：`_non_empty` 收敛为薄包装
  （error_factory=ValueError / SupervisionValidationError，消息逐字节保留）。
- `docs/modules/root_modules.md`：登记 `validate.py`；ids.py 条目注明 knowledge_base
  补漏。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize19.py`：
  * non_empty_string：合法非空 / 空串 / 全空白 / 非字符串 / error_factory 异常类
    保留 / 消息逐字节；
  * knowledge_base `_SAFE_ID` 委托共享 ids（源码含 `from src.coevo.ids import
    SAFE_ID as _SAFE_ID`、无本地 `re.compile` 的 safe-id 副本）；
  * risk/supervision `_non_empty` 委托 validate（无本地实现副本）。
- 回归：knowledge_base / risk / supervision 相关测试。

## 4. 完成条件

- 定向测试全绿；fmt + lint exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-18` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**是**（safe-id/非空校验为模型输入安全关键，须确认消息/异常类
  逐字节保留）；protocol-reviewer：**否**。
