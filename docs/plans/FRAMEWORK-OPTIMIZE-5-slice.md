# FRAMEWORK-OPTIMIZE-5 切片计划：real_chain_store 收敛到共享 canonical（canon.py）

> 状态：已批准（2026-08-08 用户指令"基于框架，优化原来系统应用的代码实现，
> 包括数据结构、算法与模块架构，做全量门禁，成功后 push 到 github"）。**全量门禁口径**。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-5`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-3]）。
- 目的：OPTIMIZE-3 新增共享 `src/coevo/canon.py` 后，原编排器真实链存储
  `orchestrator/real_chain_store.py` 仍自带一份 canonical JSON 序列化与摘要
  （`canonical_json_bytes`/`canonical_digest`）。本轮把**序列化与摘要**收敛到
  `canon.py`（单一事实源），同时**保留** real_chain_store 的严格类型校验
  （非有限 float / 非 JSON 类型拒绝，fail-closed 不降约束）。

## 2. 交付

- `src/coevo/canon.py`：`canonical_json_bytes` / `canonical_digest` 新增
  `allow_nan: bool = False` 参数（默认拒绝 NaN/Infinity，fail-closed；
  OPTIMIZE-3 既有调用方输入不含 NaN，字节不变）。
- `src/coevo/orchestrator/real_chain_store.py`：
  * `canonical_json_bytes` 保留 `validate` 严格类型校验，序列化改为
    `canon.canonical_json_bytes(value, ensure_ascii=False, allow_nan=False)`
    （异常转 `RealChainStoreError`，字节与旧实现一致）；
  * `canonical_digest` 改为 `canon.canonical_digest(value, ensure_ascii=False,
    allow_nan=False)`。
- `docs/modules/root_modules.md` 的 canon 行补充 `allow_nan` 语义。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize5.py`：
  * canon 默认拒绝 NaN/Infinity（ValueError），`allow_nan=True` 兼容；
  * real_chain_store canonical 字节与旧实现一致（固定样例，含中文/嵌套）；
  * 非有限 float 仍被 real_chain_store 拒绝（fail-closed 保留）；
  * 全仓守卫：real_chain_store 不再含独立 `json.dumps(` 序列化实现
    （仅保留 validate 校验）。
- 回归：test_real_chain_store / test_orchestrator_real_facade_chain /
  test_framework_optimize3 + 全量单元；**全量门禁**（make quality：
  unit + integration + security + e2e + go）。

## 4. 完成条件

- 定向测试全绿；**全量质量门禁 exit=0**（quality_gate --target quality）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-5 行（无悬空）；
- release_check 全绿、audit fully-sealed；成功后按用户指令 push 到 GitHub。

## 5. 审查门

- security-reviewer：**是**（真实链审计存储为安全关键，须确认字节/摘要逐位不变、
  严格校验保留、fail-closed 不降）；protocol-reviewer：**否**。
