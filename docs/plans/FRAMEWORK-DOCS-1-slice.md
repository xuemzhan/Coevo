# FRAMEWORK-DOCS-1 切片计划：框架层文档治理收口

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-DOCS-1`（ENG-BASE，dependencies=[FRAMEWORK-GAPS-6]）
- 目的：把 CTAF 框架层（US-16 AC-1..AC-9、M1..M9、GAPS/INTEGRATION 工程项、
  `src/coevo/framework/` + `timefmt.py`）纳入仓库顶层文档，使 README /
  code-guide / docs 索引与代码现状一致（文档是本仓库一等治理项）。

## 2. 交付

- README.md：§2 核心能力表加 US-16 行与框架层说明；§3 架构树加
  `framework/`、`timefmt.py`；§10 文档索引加 `docs/framework/` 与
  `docs/plans/distributed-agent-framework/`；§11 当前状态加框架层 bullet。
- docs/code-guide.md：新增 `src/coevo/framework/` 与 `src/coevo/timefmt.py`
  引导节（模块职责 + 关键入口）。
- docs/README.md：索引登记 `docs/framework/`。
- 新增 `tests/unit/test_framework_docs.py`：断言 README 含 US-16 / framework /
  timefmt、docs/framework 文件被 README/docs 索引覆盖、code-guide 含 framework
  引导节（文档治理守卫）。

## 3. 测试要点

- README：US-16、`src/coevo/framework/`、`timefmt.py`、`docs/framework/` 出现；
- code-guide：`framework/` 引导节出现；
- docs/README：`framework` 索引出现；
- 既有 lint / module-docs 回归。

## 4. 完成条件

- 定向测试 + lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-DOCS-1 行。

## 5. 审查门

- security-reviewer：**是**（文档一致性，无行为改动）；protocol-reviewer：**否**。
