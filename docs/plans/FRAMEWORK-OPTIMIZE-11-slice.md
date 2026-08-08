# FRAMEWORK-OPTIMIZE-11 切片计划：共享 safe-id 正则叶子（ids.py）

> 状态：已批准（2026-08-08 用户指令"继续下一步"，延续"基于框架，优化原来系统
> 应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-11`（ENG-BASE，dependencies=[FRAMEWORK-GAPS-7]）。
- 目的：safe-id 正则 `^[a-zA-Z0-9_][a-zA-Z0-9_.\-]{0,63}$` 在 7 个模块重复定义
  （workspace / cockpit / report / progress_capture / audit_governance /
  orchestrator / framework.tools），存在漂移风险。本轮新增根级叶子
  `src/coevo/ids.py`（与 timefmt/canon 对称）作为单一事实源，7 处统一引用。
- 语义差异说明：`task_flow/parser.py`（首字符 `[a-zA-Z_]` 不含数字）与
  `talent/store.py::_is_safe_id`（手写 Unicode 字母首字符判断）与共享正则
  不等价，**保留独立实现**（不改变行为）。

## 2. 交付

- 新增 `src/coevo/ids.py`：`SAFE_ID: re.Pattern[str]`（共享正则）+
  `is_safe_id(value) -> bool`（fail-closed：非字符串/空/超长/非法字符拒绝）。
- 7 个模块的本地 `_SAFE_ID = re.compile(...)` 改为
  `from src.coevo.ids import SAFE_ID as _SAFE_ID`（保留模块内名称与导出兼容）。
- `docs/modules/root_modules.md` 登记 `ids.py`。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize11.py`：
  * `SAFE_ID`/`is_safe_id` 正负样例（合法、非法字符、长度 64 边界、空、非字符串
    fail-closed）；
  * 守卫：7 个模块不再含本地 `re.compile(r"^[a-zA-Z0-9_]` safe-id 定义；
  * `task_flow/parser.py` 与 `talent/store.py` 保留独立实现（语义差异留痕）。
- 回归：workspace / cockpit / report / progress_capture / audit_governance /
  orchestrator / framework tools 相关测试 + 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-11 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（safe-id 为身份/权限/路径校验关键，须确认正则字节
  等价、fail-closed 语义保留、语义差异模块未误统一）；protocol-reviewer：**否**。
