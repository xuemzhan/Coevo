# 门禁两阶段化契约（Gate Two-Phase Contract）

> 状态：生效（2026-08-10，REVIEW2-2）
> 适用范围：`scripts/quality_gate.py` 的执行与治理写回边界。

## 1. 两阶段定义

- **Phase A（不可变执行）**：只运行各阶段命令，**不执行任何治理写回**
  （不 append tool-audit、不写 VERIFICATION、不做最终 seal）。每阶段前置
  re-seal 保持不变（幂等、不追加记录，用于满足 e2e 阶段 fully-sealed 前置）。
  执行结果写入机器可读产物：
  `loop/runtime/gate-results/<target>-<ts>.json`（gitignored），
  含 target / fingerprint / exit_code / ok / started_at / duration_ms /
  每阶段 argv / exit_code / duration_ms / output_tail。
- **Phase B（治理写回）**：仅在全部阶段结束后执行——
  append tool-audit 记录 → 最终 seal → 按结果写 VERIFICATION → 记录自修剪。
  阶段失败同样透明记录（exit_code 非 0 也写回），但**顺序上**与测试执行完全解耦。

## 2. 分阶段独立超时

`STAGE_TIMEOUTS`（秒）：

| target | 超时 |
|---|---|
| fmt | 600 |
| lint | 600 |
| test | 2400 |
| test-security | 1800 |
| test-e2e | 2400 |
| test-win7 | 600 |
| fast | 1800 |
| quality | 2400 |

任一阶段超时即失败关闭（exit=13），并在进度行与结果 JSON 中标注。

## 3. 进度输出

每阶段结束后输出：`[gate] stage <i>/<n>: exit=<code> duration_ms=<ms>`，
避免"运行很久不知道卡在哪"。

## 4. 纪律

1. Phase A 内禁止 `append_record` / VERIFICATION 写入 / 最终 seal。
2. 结果 JSON 是权威产物；VERIFICATION 由其输出派生。
3. 修改门禁执行或记录逻辑必须同步本契约与守卫测试。

## 5. 守卫测试

`tests/unit/test_review2_2_gate_phases.py` 强制：两阶段函数存在、Phase A 先于
Phase B、分阶段超时表完整、单阶段成功/失败/超时语义、契约文档存在。
