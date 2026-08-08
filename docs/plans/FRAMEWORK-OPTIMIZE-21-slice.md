# FRAMEWORK-OPTIMIZE-21 切片计划：死导入清理 + BACKLOG 卫生 + 静态守卫

> 状态：已批准（2026-08-09 用户指令"继续优化"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-21`（ENG-BASE，dependencies=[]）。
- 目的：
  1. **BACKLOG 卫生**：`FRAMEWORK-OPTIMIZE-20` 已 done（STATE/矩阵一致）但 BACKLOG 仍为
     `ready`，按 RECORDS-2 惯例补正为 `done`（消除治理漂移）。
  2. **死导入清理**：AST 全仓扫描确认 10 个生产文件共 11 处顶层导入从未被使用
     （含上轮 `_build.py` 引入的 `RiskKind`/`SourceKind`），全部为纯删除、零行为变化。
  3. **静态守卫**：新增 `tests/unit/test_framework_optimize22.py`——扫描 `src/coevo`
     全部生产模块，断言除显式允许清单（再导出语义）外无未使用导入，防复发。

## 2. 交付

- 清理清单（文件:行）：
  - `app/demo_support.py:19` 删除 `from src.coevo.timefmt import now_utc_iso_z`
  - `cockpit/sessions.py:15` 删除 `import re`
  - `decision_brief/_build.py:16` 收敛为 `from src.coevo.risk import Risk, RiskReport`
  - `framework/integration.py:23` 删除 `import json`
  - `framework/memory.py:23` 收敛为 `from typing import Protocol, runtime_checkable`
  - `framework/validation.py:13` 收敛为 `from typing import Protocol, runtime_checkable`
  - `identity/certificates.py:13` 删除 `import os`
  - `identity/private_keys.py:43` 删除 `import os`
  - `identity/validation.py:10` 删除 `import json`
  - `knowledge_base/models.py:10` 删除 `import re`
  - `progress_capture/watcher.py:40` 删除 `from typing import Final`
- 守卫测试 `tests/unit/test_framework_optimize22.py`。

## 3. 测试要点

- 守卫测试对 `src/coevo/**/*.py` 做 AST 未使用导入扫描：排除 `__init__.py`；
  显式允许清单覆盖再导出场景（如 `decision_brief/models.py` 的 `_build` 再导出与
  `_stat_is_reparse` 导入面）；断言其余无未使用导入。
- 回归：清理文件所属模块既有测试（framework/knowledge_base/identity/progress_capture/
  cockpit/merge 等抽样）全绿。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-21` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯死导入删除，无逻辑变更，`private_keys.py` 的 `os`
  经 AST + 词法双重确认从未使用）。
- protocol-reviewer：**否**。
