# FRAMEWORK-OPTIMIZE-33 切片计划：64-hex 正则收敛（统一到 ids.HEX_64 并收紧 \Z）

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-33`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-32]）。
- 目的：消除 4 处本地 `[0-9a-f]{64}` 正则副本，统一收敛到共享叶子 `ids.HEX_64`/
  `is_hex_64`，并把共享正则从 `$` 锚定**收紧为 `\Z`**（拒绝尾部换行，与既有
  `fullmatch` 站点语义一致，属失败关闭强化）；行为变化仅限"尾部换行从放行变拒绝"。

## 2. 交付

- `src/coevo/ids.py`：`HEX_64 = re.compile(r"^[0-9a-f]{64}\Z")`（收紧）。
- 收敛 4 处：
  - `identity/private_keys.py`：`PUBLIC_DIGEST_RE = _HEX_64`（ids 导入）；
  - `protocol/sm2_sign.py`：`_HEX_RE = _HEX_64`（ids 导入；删除随之未使用的 `import re`）；
  - `audit_governance/models.py`：`re.fullmatch(r"[0-9a-f]{64}", ...)` →
    `is_hex_64(...)`（ids 导入）；
  - `crypto/cng_handle.py`：两处 `re.fullmatch(r"[0-9a-f]{64}", ...)` →
    `is_hex_64(...)`（ids 导入）。
- 更新 `tests/unit/test_framework_optimize13.py`：pattern 钉 `\Z`、补尾部换行失败关闭
  用例、4 个新收敛模块加入“必须使用共享 HEX_64”守卫。
- 新增守卫 `tests/unit/test_framework_optimize34.py`。

## 3. 测试要点

- 守卫：ids.HEX_64 为 `\Z` 锚定且 `is_hex_64("a"*64 + "\n")` 为 False；4 个模块
  无本地 64-hex 字面量且已导入共享叶子；
- 回归：test_framework_optimize13/22、private_key_handles、sm2_sign 相关、
  audit_governance、cng_handle、framework/report/progress_capture（ids 现有用户）全绿。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-33` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**是**（校验收紧属失败关闭强化：尾部换行不再放行；行为差异需
  在记录中明示）。
- protocol-reviewer：**否**。
