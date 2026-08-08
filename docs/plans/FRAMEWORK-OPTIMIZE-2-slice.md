# FRAMEWORK-OPTIMIZE-2 切片计划：共享时间生成器全仓落地（timefmt.now_utc_iso_z）

> 状态：已批准（2026-08-08 用户指令"基于框架，优化原来系统应用的代码实现，
> 包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-2`（ENG-BASE，dependencies=[FRAMEWORK-GAPS-6]）。
- 目的：FRAMEWORK-GAPS-6 已将 ISO-8601 校验统一到框架叶子模块 `src/coevo/timefmt.py`
  （`is_iso_utc_z`），但 **UTC 时间戳生成器**仍以约 13 处私有函数副本 +
  3 处直接内联散落在产品模块（`datetime.now(UTC).isoformat().replace("+00:00","Z")`）。
  本轮把生成器收敛为 `timefmt.now_utc_iso_z()`（依赖无关叶子模块，stdlib only），
  全部产品模块复用，消除重复实现（模块架构/单一事实源），行为与 wire 字节不变。

## 2. 交付

- `src/coevo/timefmt.py`：新增 `now_utc_iso_z() -> str`（输出格式与既有副本完全一致，
  含微秒与尾随 `Z`）。
- 收敛私有副本（删除本地 def，改从 `src.coevo.timefmt` 导入；调用点同名替换）：
  knowledge_base/store、audit_governance/stream_store、task_flow/parser、
  protocol/sm2_sign、protocol/sm2_keywrap、protocol/import_service、
  protocol/package_store_db、progress_capture/watcher、task_decomposition/baseline、
  talent/store、crypto/cng_handle（`_now_utc_iso`）、app/demo_support、
  cockpit/sessions（后两者为公开导出名 `now_utc_iso_z`，保留名称仅改来源）。
- 收敛直接内联（改调用 `now_utc_iso_z()`）：identity/audit_anchor、
  identity/private_keys、identity/repository。
- 清理各模块不再使用的 `datetime`/`UTC` 导入（保留其他用途）。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize2.py`：
  * `timefmt.now_utc_iso_z()` 输出满足 `is_iso_utc_z`、含微秒、UTC；
  * 全仓源码守卫：不允许再出现私有 `*_now_utc_iso*` 定义或
    `datetime.now(UTC).isoformat().replace("+00:00", "Z")` 内联
    （排除 timefmt 自身与测试夹具）；
  * 抽样行为回归：knowledge_base store / task_decomposition baseline /
    progress_capture watcher 时间戳仍合法。
- 回归：受影响模块既有单元/集成测试 + 全量单元套件。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-2 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（时间戳进入审计/签名/包记录路径，须确认行为与格式不变、
  无导入环、无私有键泄漏）；protocol-reviewer：**否**（wire 字节不变，纯重构）。
