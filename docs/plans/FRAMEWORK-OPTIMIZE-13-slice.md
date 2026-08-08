# FRAMEWORK-OPTIMIZE-13 切片计划：共享 64-hex 正则叶子（ids.py 扩展）

> 状态：已批准（2026-08-08 用户指令"继续下一步"，延续"基于框架，优化原来系统
> 应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-13`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-12]）。
- 目的：64-hex 正则 `^[0-9a-f]{64}$` 在 7 个模块重复（cockpit / progress_capture
  models+watcher / report / framework a2a+plan+memory），存在漂移风险。本轮在
  `src/coevo/ids.py` 扩展 `HEX_64` + `is_hex_64`（fail-closed）作为单一事实源，
  7 处统一引用（与 OPTIMIZE-11 safe-id 同模式）。

## 2. 交付

- `src/coevo/ids.py`：新增 `HEX_64: re.Pattern[str]`（`^[0-9a-f]{64}$`）+
  `is_hex_64(value) -> bool`（非字符串/长度/字符集 fail-closed）。
- 7 个模块本地 `_HEX_64`/`_HEX64 = re.compile(...)` 改为
  `from src.coevo.ids import HEX_64 as _HEX_64`（或 `as _HEX64`，保留原名称）。
- 清理不再使用的 `import re` / `Final[re.Pattern[str]]` 注解。
- `docs/modules/root_modules.md` 的 ids.py 行补充 HEX_64。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize13.py`：
  * `HEX_64`/`is_hex_64` 正负样例（64 小写 hex、大写拒绝、长度边界、空、
    非字符串 fail-closed）；
  * 守卫：7 个模块不再含 `re.compile(r"^[0-9a-f]{64}$")` 本地定义。
- 回归：cockpit / progress_capture / report / framework a2a+plan+memory
  相关测试 + 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-13 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（64-hex 指纹/哈希校验为审计/身份关键，须确认正则
  字节等价与 fail-closed 保留）；protocol-reviewer：**否**。
