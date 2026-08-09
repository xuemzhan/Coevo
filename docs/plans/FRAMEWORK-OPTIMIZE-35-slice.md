# FRAMEWORK-OPTIMIZE-35 切片计划：门禁稳定性修复（tamper 测试复原硬化）

> 状态：已批准（2026-08-09 用户指令"继续优化"；全量门禁收口过程中发现并修复）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-35`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-34]）。
- 目的：关闭 DECISIONS 记录的**已知门禁 flakiness**——`test_local_toolchain_security`
  的 tamper 测试临时篡改 `scripts/validate_opencode.py`，若复原失败（含"污染基线"
  场景：上次残留的守卫被当作 original 复原回去），`test_engineering_baseline`
  随之失败。修复：复原源改为 `git show HEAD:` 纯净内容，`finally` 无条件写回。

## 2. 交付

- `tests/security/test_local_toolchain_security.py`：
  `test_tampered_locked_python_script_is_rejected_before_execution` 的复原逻辑
  从"测试前字节"改为"git HEAD blob"（subprocess `git show HEAD:...`，check=True），
  `finally` 写回纯净内容——污染基线无法自我延续。
- 无生产代码改动。

## 3. 测试要点

- 污染模拟：先手工写入残留守卫 → 跑 tamper 测试 → 断言文件复原为纯净；
- 回归：`test_local_toolchain_security` 全量 + `test_engineering_baseline` 全量；
- 全量 quality exit=0。

## 4. 完成条件

- 定向测试全绿；全量 quality exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-35` 行（无悬空）。

## 5. 审查

- security-reviewer：**是**（涉及锁定脚本篡改测试；复原硬化不改变篡改检测断言，
  仅保证测试后文件复原到 HEAD 纯净态）。
- protocol-reviewer：**否**。
