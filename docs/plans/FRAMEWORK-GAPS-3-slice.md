# FRAMEWORK-GAPS-3 切片计划：semver 尾部换行收口

> 状态：已批准（2026-08-08，GAPS-2 审查观察项，用户指令"继续开发"）。
> 增量门禁口径（fmt + lint + 定向测试），不跑全量 quality。

## 1. 目标

`manifest_checker` 的 semver 正则用 `$`（Python 语义：可在末尾换行前匹配），
导致 `"1.0.0\n"` 被接受。修复为 `\Z`（仅字符串末尾匹配），ISO 路径已由
`strptime` 兜住，无需改动。

## 2. 改动

- `src/coevo/framework/manifest_checker.py`：`_SEMVER` 的 `$` → `\Z`
- 新增 `tests/unit/test_framework_gaps3.py`（尾部换行拒绝 + 干净 semver 通过）

## 3. 完成条件

- 定向测试全绿；fmt / lint exit 0；追溯矩阵新增 ENG-BASE | FRAMEWORK-GAPS-3 行。

## 4. 审查门

- security-reviewer：**是**（正则边界）；protocol-reviewer：**否**。
