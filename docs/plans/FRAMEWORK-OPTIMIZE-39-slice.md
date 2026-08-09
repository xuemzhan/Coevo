# FRAMEWORK-OPTIMIZE-39 切片计划：progress_capture.revise 字段覆盖去重

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-39`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-38]）。
- 目的：`ProgressCaptureService.revise`（109 行）内 text/kind/confidence 三个字段
  覆盖块**重复构造 ItemOverride 并追加**（三处同构），提取共享助手 `_apply_override`
  消除复制；判定顺序、override 字段、错误语义逐字节不变；`revise` 收敛为约 95 行。

## 2. 交付

- `src/coevo/progress_capture/service.py`：
  1. 新增模块级 `_apply_override(overrides, *, target_path, original_value,
     edited_value, reason, now) -> (overrides + (ItemOverride(...),), edited_value)`
     （含 docstring）；
  2. `revise` 三个字段块改用 `_apply_override`（kind 块的 ProgressItemKind 类型
     检查保留在调用处）。
- 守卫测试 `tests/unit/test_framework_optimize39.py`。

## 3. 测试要点

- 守卫：`revise` 方法体不超过 100 行（原 109）；`_apply_override` 存在且被
  `revise` 调用 3 次；关键错误消息标记存活；
- 回归：`tests/unit/test_progress_capture.py` 全量。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-39` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯去重提取，override 语义不变；无密钥/权限边界）。
- protocol-reviewer：**否**。
