# FRAMEWORK-OPTIMIZE-9 切片计划：剩余 canonical 序列化变体统一（canonical_json_str）

> 状态：已批准（2026-08-08 用户指令"继续下一步"，延续"基于框架，优化原来系统
> 应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-9`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-5]）。
- 目的：OPTIMIZE-3/5 已收敛 canonical JSON（`canon.py`），但产品模块仍残留
  "sort_keys + 紧凑分隔符" 的 canonical 序列化副本（部分为 bytes、部分为 str）。
  本轮在 `canon.py` 增加 `canonical_json_str`（str 变体，字节与旧实现逐位一致），
  并收敛 5 个模块的剩余副本（cng_handle 2 处 bytes / cockpit state_store 1 处
  bytes / knowledge_base 1 处 str / talent 4 处 str / audit stream_store 3 处
  str），消除重复实现（单一事实源，行为不变）。

## 2. 交付

- `src/coevo/canon.py`：新增 `canonical_json_str(value, *, ensure_ascii=True,
  allow_nan=False) -> str`（内部与 canonical_json_bytes 同参，返回 str）；
  `canonical_json_bytes` 复用 `canonical_json_str().encode("utf-8")`。
- 收敛 bytes 等价点：`crypto/cng_handle.py`（_write body + 删除 `_canonical`
  本地 def，调用点 394/439 用 `canonical_json_bytes`）、`cockpit/state_store.py`。
- 收敛 str 等价点：`knowledge_base/store.py`、`talent/store.py`（4 处）、
  `audit_governance/stream_store.py`（append 2 处 + `_chain_hash` 1 处）。
- 守卫：上述模块不再残留 canonical 模式（cng_handle 仅保留非 canonical 的
  请求体 json.dumps，无 sort_keys）。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize9.py`：
  * `canonical_json_str` 与 `canonical_json_bytes().decode()` 一致（含
    ensure_ascii 两分支、allow_nan 拒绝）；
  * 全仓守卫：5 个模块的 `json.dumps(` 计数归零（cng_handle=1 非 canonical）、
    cng_handle 无 `def _canonical`；
  * 行为回归：cng_handle 注册表哈希链、stream_store 哈希链与 knowledge/talent
    DB 存储语义由既有测试守护。
- 回归：test_crypto_contract / test_private_key_storage（cng）、
  test_cockpit_state_store、test_knowledge_store、test_talent_store、
  test_audit_stream_store / test_audit_stream + 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-9 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（cng 注册表哈希链与审计流哈希链为安全关键，须确认
  canonical 字节逐位不变、fail-closed 保留）；protocol-reviewer：**否**。
