# FRAMEWORK-OPTIMIZE-15 切片计划：共享 safe-relative-path 校验叶子（relpath.py）

> 状态：已批准（2026-08-08 用户指令"继续进行优化，不用做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-15`（ENG-BASE，dependencies=[]）。
- 目的：`progress_capture/watcher.py`、`cockpit/static.py`、`cockpit/wps.py`
  三处实现同构的"安全相对路径"检查（非空字符串、无前导 `/`、无 `\`、无
  空/`.`/`..` 段）；统一到单一事实源叶子 `src/coevo/relpath.py`
  （`is_safe_relative_path`，fail-closed），延续 ids.py / jsonutil.py 的收敛模式。

## 2. 交付

- 新增 `src/coevo/relpath.py`：
  `is_safe_relative_path(value: object) -> bool`——非空 str、无前导 `/`、
  无 `\`、无 NUL、无空/`.`/`..` 段才为 True（fail-closed）。
- 三处调用点收敛：
  * `progress_capture/watcher.py::_check_relative_path` → 用共享谓词（保留本地
    异常类与消息）；
  * `cockpit/static.py::resolve_static_path` → 共享谓词（保留扩展名/大小/解析
    检查）；
  * `cockpit/wps.py::WpsLauncher.launch` → 共享谓词（保留 DENIED 语义）。
- 说明：共享谓词包含 NUL 拒绝（static 原有）；watcher/wps 属**严格化统一**——
  NUL 在 Windows 上绝不可能是合法路径，不拒绝任何合法输入。
- 语义差异保留：`workspace/paths.py::_has_parent_traversal`（双方言、允许
  backslash，用于组合路径）与 `model/config.py::prompts_file` 校验（单文件相对
  路径、`..` in parts）语义不同，不统一。
- `docs/modules/root_modules.md` 登记 `relpath.py`。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize15.py`：
  * `is_safe_relative_path` 正反例：合法相对路径、前导 `/`、`\`、NUL、
    `a/../b`、`.`、`..`、空串、非字符串（None/int）边界；
  * 守卫：watcher/static/wps 三模块不再含本地
    `any(part in ("", ".", "..") ...)` 副本（统一引用 relpath）；
  * static/wps 行为回归：原有拒绝路径仍拒绝（走共享谓词）。

## 4. 完成条件

- 定向测试全绿；`python scripts/quality_gate.py --target fmt` 与 `--target lint`
  exit=0（记录新指纹）；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-15` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**是**（路径安全校验收敛，须确认 fail-closed 与拒绝语义
  不降）；protocol-reviewer：**否**。
