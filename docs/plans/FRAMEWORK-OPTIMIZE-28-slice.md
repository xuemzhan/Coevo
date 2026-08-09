# FRAMEWORK-OPTIMIZE-28 切片计划：重构域注释强化（docstring 补全）

> 状态：已批准（2026-08-09 用户指令"继续加强代码的注释"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-28`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-27]）。
- 目的：为最近重构/迁移涉及的三个域（decision_brief / merge / orchestrator）中 **70 个
  缺少 docstring 的函数**补全契约注释（失败关闭语义、哈希链绑定、返回/异常契约），
  纯文档化、**零行为变化**；同时补齐 OPTIMIZE-20 迁移 `_build.py` 时未带 docstring
  的历史缺口。

## 2. 交付

- 仅修改 docstring/注释（`src/coevo/decision_brief/{_build,_util,models}.py`、
  `src/coevo/merge/{engine,receipt,repository,models}.py`、
  `src/coevo/orchestrator/_real_chain.py`），共 70 处；
- 每个 docstring 说明该函数的判定/不变量/异常语义，不含实现细节噪音；
- 守卫测试：`tests/unit/test_framework_optimize29.py`——断言上述模块中这 70 个
  函数名现在都有 docstring（防回归），且源码除注释外无行为差异（不校验字符串本身）。

## 3. 测试要点

- 守卫：70 个函数均已有非空 docstring；文件可编译；
- 回归：`test_decision_brief` + `test_framework_optimize20/21` + merge 套件 +
  orchestrator 套件全绿（注释不应影响行为）。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-28` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯注释，无逻辑变更；docstring 描述与既有失败关闭语义一致）。
- protocol-reviewer：**否**。
