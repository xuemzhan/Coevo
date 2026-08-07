# FRAMEWORK-GAPS-4 切片计划：共享 L7 校验构造器

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-GAPS-4`（ENG-BASE，dependencies=[FRAMEWORK-INTEGRATION-3]）
- 目的：把 L7 ISO-8601 UTC 校验收敛为单一公共构造器，消除 4 个模块的私有副本；
  并让 `validate_product_chain` 异常分支的 `validated_at` 也过 L7
  （INTEGRATION-3 Low 收口）。

## 2. 交付

- `validation.py`：`_is_iso_utc_z` 公开为 `is_iso_utc_z`（保持小数秒兼容 +
  日历校验）；`__init__.py` 导出。
- `a2a.py` / `memory.py` / `orchestrator.py`：删除私有 `_is_iso_utc_z` 与
  `_ISO_UTC_Z` 正则、`import datetime`，改引用共享 `is_iso_utc_z`。
- `integration.py`：`validate_product_chain` 顶部先做 L7 校验（异常分支也覆盖）。

## 3. 测试要点

- 共享构造器：`is_iso_utc_z` 对合法/小数秒/畸形输入正确；
- 各模块既有 ISO 负例回归（a2a/memory/validate_plan/transition）；
- validate_product_chain：非 ISO validated_at → REJECTED（L7），含抬升失败分支；
- L15 stdlib / L17 文档守卫。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-GAPS-4 行。

## 5. 审查门

- security-reviewer：**是**（共享校验边界）；protocol-reviewer：**否**。
