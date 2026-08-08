# FRAMEWORK-OPTIMIZE-20 切片计划：decision_brief 域级助手迁出（_build.py）

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-20`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-19]）。
- 目的：`decision_brief/models.py`（约 930 行）在 _util 提取后仍含约 20 个域级助手。
  本切片把**非 __post_init__ 依赖**的 13 个域助手迁到 `_build.py`（用惰性导入规避
  dataclass __post_init__ ↔ 助手循环依赖），models.py 保留数据类 + __post_init__
  闭包助手 + _util 薄包装，并在底部再导出 _build 名称（导入面不变）。

## 2. 交付

- 新增 `src/coevo/decision_brief/_build.py`（13 个函数，每个函数内惰性
  `from .models import ...`，规避模块级循环）：
  `_latest_receipt`、`_validate_bound_risk`、`_clone_risk_report`、
  `_clone_confirmation`、`_build_content`、`_risk_conclusion`、`_make_version`、
  `_validate_stored_brief`、`_validate_content_model`、`_clone_content`、
  `_clone_brief`、`_brief_id`、`_validate_docx`。
- `src/coevo/decision_brief/models.py`：删除上述 13 个定义，文件底部
  `from ._build import (...)` 再导出（导入面不变）。
- `docs/modules/decision_brief.md`：登记 `_build.py`。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize21.py`：
  * 守卫：models.py 无 13 个助手定义（`def _build_content` 等）、含底部 `from ._build import`；
  * _build.py 无模块级 `from .models import`（仅函数内惰性导入）；
  * 导入面：`from src.coevo.decision_brief.models import _build_content` 等仍可用。
- 回归：`tests/unit/test_decision_brief.py` 全量 + repositories/service 导入路径。

## 4. 完成条件

- 定向测试全绿；fmt + lint exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-20` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**是**（域助手为模型校验/构造安全关键，须确认行为逐字节不变）；
  protocol-reviewer：**否**。
