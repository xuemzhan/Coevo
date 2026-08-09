# FRAMEWORK-OPTIMIZE-36 切片计划：sm2-test-pki helper stdin BOM 健壮性修复

> 状态：已批准（2026-08-09 用户指令"继续优化"；全量门禁收口过程中根因定位并修复）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-36`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-35]）。
- 根因：控制台代码页为 65001（UTF-8）时，.NET Framework 的
  `Process.StandardInput` StreamWriter 会向重定向 stdin 管道**预写 UTF-8 BOM**，
  `BaseStream.Write` 再追加 COEVOPKI/2 请求帧 → 管道开头出现**双重 BOM**，
  helper 魔数校验失败（`GMH-E-MAGIC`），`test_sm2_test_pki_generation` 类 7 项
  失败。CP936 下无 BOM 预写，此前偶发/环境相关。
- 修复：`scripts/generate-sm2-test-pki.ps1` 顶部在启动 helper 前把
  `[Console]::OutputEncoding/InputEncoding` 钉为无 BOM 的 CP936（含原因注释）；
  同步更新 `toolchain-lock.json` 中 launcher 的 size/sha256（锁链重哈希）。

## 2. 交付

- `scripts/generate-sm2-test-pki.ps1`：+4 行编码钉（纯环境健壮性，协议不变）；
- `docs/dependencies/toolchain-lock.json`：launcher size 11208→11642、
  sha256 更新（其余字节不动）。

## 3. 测试要点

- 复现→修复验证：chcp 65001 下修复前双重 BOM → GMH-E-MAGIC；修复后 37 字节
  干净请求帧；
- 回归：`tests/integration/test_sm2_test_pki_generation.py` 全量（25 项）；
- 全量 quality exit=0。

## 4. 完成条件

- 定向测试全绿；全量 quality exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-36` 行（无悬空）。

## 5. 审查

- security-reviewer：**是**（锁定脚本 + 工具链锁变更；仅编码钉，不改变篡改检测
  断言与协议帧，helper 源与协议未动）。
- protocol-reviewer：**否**。
