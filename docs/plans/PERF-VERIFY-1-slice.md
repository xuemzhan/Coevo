# PERF-VERIFY-1 切片计划：集成套件回归复测与性能基线

> 状态：已批准（2026-08-08 用户指令"继续进行优化，不用做全量门禁"）。增量验证口径
> （集成套件 = 门禁 test 阶段的一部分，非全量 quality），全量 quality 按用户指示豁免，
> 豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`PERF-VERIFY-1`（ENG-BASE，dependencies=[PERF-HELPER-1]）。
- 目的：PERF-HELPER-1（GmSSL crypto-provider 助手编译缓存）只做了 38 项 crypto
  定向回归；本轮在**完整集成套件（20 个文件 / 261 项）**上复测，量化缓存收益
  （此前约 17 分钟），并记录性能基线；若发现回归（尤其 crypto 路径）就地修复。

## 2. 交付

- 运行 `python -m unittest discover -s tests/integration -p "*test*.py"`（门禁
  test 阶段的集成部分；PYTHONUTF8 环境），记录：
  * 全量 261 项结果（含此前未覆盖的 installer / dev_environment / merge /
    package_store / orchestrator 等）；
  * 总耗时与分布（哪些用例仍占时，作为后续性能工作项依据）。
- 若回归：定位并修复（不扩大范围），重跑失败用例；
- 性能基线写入 VERIFICATION/DECISIONS 与追溯矩阵（PERF-VERIFY-1 行）。

## 3. 测试要点

- 全量集成套件 exit=0（唯一放行标准；失败即修复后重跑）；
- 量化：记录套件总时长（对比 PERF-HELPER-1 前约 17 分钟的基线）；
- 观察 sm2-test-pki 测试助手（仍现场编译）是否成为新的主要耗时点，
  作为 PERF-HELPER-2（测试助手缓存）的依据。

## 4. 完成条件

- 集成套件 261 项全绿（含 crypto 缓存路径）；总时长与基线记录在案；
- 追溯矩阵新增 `ENG-BASE | PERF-VERIFY-1` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**否**（纯验证/测量，无代码改动除非回归修复；若有修复则
  按修复范围评估）；protocol-reviewer：**否**。
