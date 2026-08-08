# PERF-SESS-1 切片计划：CockpitSessionManager 会话管理微优化

> 状态：已批准（2026-08-09 用户指令"继续"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`PERF-SESS-1`（ENG-BASE，dependencies=[]）。
- 目的：`cockpit/sessions.py` 的 `validate()` 每次请求把 `now` 解析 2-3 次
  （`_iso_seconds(now)`）；`_evict_if_needed()` 用全量 `sorted()`（O(n log n)）
  淘汰超容量会话（正常路径 excess 恒为 1）。优化为：now 单次解析复用；
  淘汰用 `heapq.nsmallest(excess, ...)`（O(n log excess)，excess=1 时 O(n)），
  淘汰集合与原语义逐位一致。

## 2. 交付

- `src/coevo/cockpit/sessions.py`：
  * `validate()` 顶部解析 `now` 一次，age/timeout 两处检查复用；
  * `_evict_if_needed()` 用 `heapq.nsmallest` 淘汰 `excess` 个最旧会话。

## 3. 测试要点

- `tests/unit/test_cockpit_http.py`（CockpitSessionManagerTests）：
  * 既有 create/revoke/rotate/age/timeout/evict 全量回归；
  * 新增：淘汰后保留最新（second/third 仍有效）、源码守卫
    （heapq.nsmallest 存在、无 `sorted(` 于 _sessions）。

## 4. 完成条件

- 定向测试全绿；fmt + lint exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | PERF-SESS-1` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**否**（纯会话管理微优化，语义不变）；protocol-reviewer：**否**。
