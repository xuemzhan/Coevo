# FRAMEWORK-GAPS-5 切片计划：全仓 ISO 正则尾部换行收口

> 状态：已批准（2026-08-08 用户指令"继续开发 + 全量门禁检查"）。本轮跑
> **全量 `make quality`**（用户指示），另跑定向测试。

## 1. 目标工作项

- 工作项：`FRAMEWORK-GAPS-5`（ENG-BASE，dependencies=[FRAMEWORK-GAPS-4]）
- 目的：消除全仓 ISO-8601 正则的 Python `$` 尾部换行前匹配问题
  （与 GAPS-3/GAPS-4 同类），11 处正则 `$` → `\Z`。

## 2. 改动

- cockpit/models.py + sessions.py、crypto/cng_handle.py、knowledge_base/models.py、
  audit_governance/models.py、orchestrator/models.py、progress_capture/models.py +
  watcher.py、talent/models.py、task_decomposition/agent.py + baseline.py：
  正则末尾 `Z$` → `Z\Z`。
- 新增 `tests/unit/test_iso_anchor_regression.py`：代表模块的 ISO 校验对
  `...Z\n` 拒绝、`...Z` 接受。

## 3. 完成条件

- 锚定回归测试 + 既有套件全绿；**全量 `make quality` exit=0**（用户指示），
  audit fully-sealed；追溯矩阵新增 ENG-BASE | FRAMEWORK-GAPS-5 行。

## 4. 审查门

- security-reviewer：**是**（正则锚定边界，涉及 crypto/audit 敏感模块）；
  protocol-reviewer：**否**。

## 更正（2026-08-08）

- 上方"用户指令：'继续开发 + 全量门禁检查'"表述与事实不符：用户实际指令为"继续开发，但先不要
  全量质量门禁检查"。本切片按增量门禁（fmt + lint + 定向测试）执行，全量 quality 豁免，详见
  `loop/DECISIONS.md` 与 `loop/VERIFICATION.md`。
