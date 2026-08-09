# FRAMEWORK-OPTIMIZE-37 切片计划：crypto helper stdin BOM 健壮性修复（同类隐患收口）

> 状态：已批准（2026-08-09 用户指令"继续优化"；OPTIMIZE-36 同类扫描发现）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-37`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-36]）。
- 根因：与 OPTIMIZE-36 同源——CP65001 下 .NET `Process.StandardInput` StreamWriter
  向重定向 stdin 预写 UTF-8 BOM，`invoke-gmssl-crypto.ps1` 的 COEVOCRYPTO/1 帧
  被前导 BOM 破坏 → `GCP-E-MAGIC`（e2e `test_return_chain` 实测失败；
  单元测试 mock 了 subprocess 未覆盖，门禁通过与否取决于控制台 CP，属环境相关 flaky）。
- 修复：`scripts/invoke-gmssl-crypto.ps1` 顶部钉 BOM-free CP936（与 OPTIMIZE-36
  一致，响应经 `OpenStandardOutput().Write` 原始字节不受影响）；
  `toolchain-lock.json` `gmssl_prototype_provider.helper.launcher` 重哈希。

## 2. 交付

- `scripts/invoke-gmssl-crypto.ps1`：+6 行编码钉；
- `docs/dependencies/toolchain-lock.json`：launcher size 8166→8604、sha256 更新。

## 3. 测试要点

- 修复前直调 `invoke-gmssl-crypto.ps1` → GCP-E-MAGIC；修复后魔数通过（帧格式
  由真实 provider 构建）；
- 回归：`tests/e2e/test_return_chain.py`（真实加密回传链）、
  `tests/unit/test_gmssl_provider_retry.py`；
- 全量 quality exit=0。

## 4. 完成条件

- 定向测试全绿；全量 quality exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-37` 行（无悬空）。

## 5. 审查

- security-reviewer：**是**（生产相关 crypto 路径 + 工具链锁变更；仅编码钉，
  协议帧与篡改检测不变）。
- protocol-reviewer：**否**。
