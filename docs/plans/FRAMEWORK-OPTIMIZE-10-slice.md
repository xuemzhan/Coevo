# FRAMEWORK-OPTIMIZE-10 切片计划：audit_anchor canonical 统一到 canon（trailing_newline）

> 状态：已批准（2026-08-08 用户指令"继续下一步"，延续"基于框架，优化原来系统
> 应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-10`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-9]）。
- 目的：canonical 序列化已收敛到 `canon.py`（OPTIMIZE-3/5/9），唯 `identity/
  audit_anchor.py::canonical` 仍是独立副本——同紧凑格式但**尾部追加 `\n`**
  （审计锚定记录格式）。本轮在 `canon.py` 增加 `trailing_newline` 参数并统一
  该副本（行为与字节逐位不变，签名保留，审计锚定链语义不变）。

## 2. 交付

- `src/coevo/canon.py`：`canonical_json_bytes` / `canonical_json_str` /
  `canonical_digest` 新增 `trailing_newline: bool = False` 参数（默认 False
  行为不变；True 时字节/文本尾部追加 `\n`）。
- `src/coevo/identity/audit_anchor.py`：`canonical(value)` 改为调用
  `canonical_json_bytes(value, ensure_ascii=False, trailing_newline=True)`
  （删除本地 json.dumps 副本，函数签名与返回值不变）。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize10.py`：
  * canon `trailing_newline=True` 与旧实现字节一致（含中文/嵌套样例）；
  * audit_anchor.canonical 与 canon trailing_newline 输出一致（字节回归）；
  * 守卫：audit_anchor 不再含 `json.dumps(` canonical 副本。
- 回归：test_identity_validation / test_private_key_storage /
  test_identity_freshness_security / test_identity_store_security / demo e2e
  （审计锚定链）+ 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-10 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（审计锚定链为身份安全关键，须确认 canonical 字节
  逐位不变、换行语义保留、fail-closed 不变）；protocol-reviewer：**否**。
