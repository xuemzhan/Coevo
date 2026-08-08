# FRAMEWORK-OPTIMIZE-19 切片计划：decision_brief/models 纯工具助手提取（_util.py）

> 状态：已批准（2026-08-08 用户指令"继续优化，不做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-19`（ENG-BASE，dependencies=[]）。
- 目的：`decision_brief/models.py`（862 行）是仓库最大单文件；完整拆分受
  dataclass `__post_init__` 与校验/摘要助手循环依赖约束（需谨慎设计）。本切片
  **安全提取 7 个纯工具助手**（无数据类依赖）到 `_util.py`，作为首个拆分步骤，
  建立"纯工具 → 数据类+域校验"的分层模式，后续切片可继续把域助手迁出。

## 2. 交付

- 新增 `src/coevo/decision_brief/_util.py`（依赖无关纯工具）：
  `_ZERO_DIGEST`、`_safe_string`、`_digest`、`_encode_json`、
  `_stat_is_reparse`、`_is_link_or_reparse`、`_parse_utc`（timefmt 薄包装）。
- `src/coevo/decision_brief/models.py`：删除本地副本，`from ._util import ...`
  并**原样再导出**（`from .models import _digest` 等既有导入面不变；
  repositories/service 的 ~7 个私有导入保持可用）。
- 文档：模块 docstring 注明分层（_util 纯工具 / models 数据类+域校验）；
  root_modules.md 登记 `_util.py`。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize20.py`：
  * `_util` 各函数行为回归（safe_string/digest/encode_json/reparse/parse_utc 正反例）；
  * 守卫：models.py 不再含本地 `def _safe_string/_digest/_encode_json/_stat_is_reparse/
    _is_link_or_reparse/_parse_utc/_ZERO_DIGEST` 定义（委托 _util）；
  * `from src.coevo.decision_brief.models import _digest` 仍可用（再导出）。
- 回归：`tests/unit/test_decision_brief.py` 全量。

## 4. 完成条件

- 定向测试全绿；fmt + lint exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-19` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**否**（纯提取、行为逐字节不变、再导出保持导入面）；
  protocol-reviewer：**否**。
