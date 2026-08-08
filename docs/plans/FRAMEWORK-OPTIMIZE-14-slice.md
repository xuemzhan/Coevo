# FRAMEWORK-OPTIMIZE-14 切片计划：共享 JSON 重复键拒绝守卫（jsonutil.py）

> 状态：已批准（2026-08-08 用户指令"继续下一步"，延续"基于框架，优化原来系统
> 应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-14`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-13]）。
- 目的：JSON 解析的"拒绝重复键"守卫（`object_pairs_hook`）在 5 个模块重复
  （protocol/agent_package、framework/k8s_listing、crypto/cng_handle、
  cockpit/state_store、framework/manifest_checker），实现同构、异常类型各异。
  本轮新增根级叶子 `src/coevo/jsonutil.py` 统一守卫（`reject_duplicate_pairs`，
  可注入 error_factory 保持各模块异常语义），消除重复（单一事实源，fail-closed
  不降）。

## 2. 交付

- 新增 `src/coevo/jsonutil.py`：
  `reject_duplicate_pairs(pairs, *, error_factory=ValueError) -> dict`
  （重复键抛 `error_factory("duplicate key ...")`，正常合并返回）。
- 5 个模块本地守卫删除，改用
  `functools.partial(reject_duplicate_pairs, error_factory=<各自异常>)`。
- `docs/modules/root_modules.md` 登记 `jsonutil.py`。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize14.py`：
  * reject_duplicate_pairs：重复键拒绝（error_factory 注入）、正常合并、空输入；
  * 守卫：5 个模块不再含本地 `def _reject_duplicate_keys/_reject_duplicate_pairs/
    _unique_pairs`。
- 回归：agent_package / k8s_listing / cng_handle / cockpit/state_store /
  manifest_checker 相关测试（含重复键 fail-closed 用例）+ 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-14 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（JSON 解析 fail-closed 为包/清单/存储安全关键，
  须确认异常类型语义保留、消息含 "duplicate key" 兼容既有断言）；
  protocol-reviewer：**否**。
