# FRAMEWORK-GAPS-6 切片计划：共享 ISO 校验构造器全仓落地

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-GAPS-6`（ENG-BASE，dependencies=[FRAMEWORK-GAPS-5]）
- 目的：把 GAPS-5 的 11 处 ISO 正则收敛为唯一共享构造器，消除全仓重复副本
  （GAPS-4/5 观察项最终收口）。

## 2. 交付

- 新增 `src/coevo/timefmt.py`（stdlib-only 叶模块）：`is_iso_utc_z(value)`——
  `\Z` 锚定、小数秒、日历校验、非字符串 fail-closed。
- `docs/modules/root_modules.md` 登记 timefmt.py（L17）。
- `framework/validation.py` 从 timefmt 导入并再导出 `is_iso_utc_z`（框架调用方
  不变）。
- 10 个产品模块去正则副本、改引 `is_iso_utc_z`：cockpit/models+sessions、
  crypto/cng_handle、knowledge_base/models、audit_governance/models、
  orchestrator/models、progress_capture/models+watcher、talent/models、
  task_decomposition/agent+baseline。
- 更新 cockpit/knowledge_base/orchestrator 的 `__init__` 再导出（移除 `_ISO_UTC_Z`）。
- 锚定测试改测共享 `is_iso_utc_z`（含尾部换行/小数秒/日历/非字符串边界）。

## 3. 测试要点

- `is_iso_utc_z` 共享构造器：合法/小数秒/尾部换行/非法日期/非字符串全边界；
- 受影响产品模块回归（cockpit/knowledge_base/audit_governance/orchestrator/
  progress_capture/talent/task_decomposition/crypto）；
- 框架族回归（a2a/memory/orchestrator/integration/validate_plan）；
- L15 stdlib / L17（root_modules 含 timefmt）。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-GAPS-6 行。

## 5. 审查门

- security-reviewer：**是**（共享校验边界，涉及 crypto/audit 敏感模块）；
  protocol-reviewer：**否**。
