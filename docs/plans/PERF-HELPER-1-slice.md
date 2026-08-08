# PERF-HELPER-1 切片计划：GmSSL 助手编译缓存（哈希锁定 + 失败关闭）

> 状态：已批准（2026-08-08 用户指令"继续进行优化，不用做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`PERF-HELPER-1`（ENG-BASE，dependencies=[]）。
- 目的：集成/单元套件约 17 分钟的主要开销是 `invoke-gmssl-crypto.ps1` 每次调用都
  现场编译 `gmssl-crypto-helper.cs`（helper-<PID>-<GUID>.exe）。本轮为
  crypto-provider 助手增加**编译缓存**（按锁定的源哈希缓存编译产物 + 旁路哈希校验），
  使同一会话内的后续调用直接复用，预计把 crypto 密集套件降到数分钟。
- 边界：只缓存 `invoke-gmssl-crypto.ps1` 的 crypto-provider 助手；sm2-test-pki
  测试助手保持现场编译（其"无残留"行为被测试钉住，不在本轮范围）。

## 2. 交付

- `scripts/invoke-gmssl-crypto.ps1`：
  * 缓存目录 `.tools/runtime/gmssl-crypto-helper/cache/`；
  * 缓存键 = 锁定的 `source_sha256`（`helper-<source_sha256>.exe`）；
  * 旁路文件 `<cache>.sha256`（编译产物哈希，构建时原子写入）；
  * 使用前校验：缓存 exe 存在 + 旁路存在且为 64-hex + 二进制哈希==旁路，否则
    视为缓存未命中；
  * 命中：直接用缓存 exe（`Open-CoevoLockedFile` 按旁路哈希/尺寸锁定）；
  * 未命中：按现有流程现场编译唯一命名助手（当前调用行为不变），成功后尽力
    原子安装到缓存（tmp → 校验 → rename → 写旁路），安装失败不影响当前调用；
  * 缓存损坏/旁路缺失自愈：下次调用按未命中重新编译。
- `docs/dependencies/toolchain-lock.json`：`gmssl_prototype_provider.helper.launcher`
  的 size/sha256 同步（启动器变更）；无 make.cs / control.pyz 波及（launcher 未
  内嵌，Python 侧 gmssl_provider 按 lock 校验启动器）。
- `docs/dependencies/approved-crypto-provider-path.md`（或 DECISIONS）：记录
  "编译缓存"安全取舍——单份持久化可写二进制 + 旁路哈希校验（非认证模块场景可接受；
  本地攻击者可同时替换二进制与旁路，威胁模型与 .tools 本地信任一致，已记录）。

## 3. 测试要点

- `tests/unit/test_gmssl_provider_retry.py` 或新静态用例：启动器脚本含缓存逻辑
  （Test-CachedHelper / source_sha256 键 / 旁路 64-hex 校验 / 未命中现场编译）；
- `tests/integration/test_gmssl_prototype_provider.py`：新增行为用例——
  同一 profile 连续 `_invoke` 两次：均成功；缓存目录出现 `helper-<sha>.exe` +
  `.sha256` 且旁路==二进制哈希；篡改旁路后下一次调用自愈重编译仍成功；
- 回归：`tests/integration/test_cng_handle.py`、`tests/unit/test_cng_handle.py`、
  `tests/integration/test_crypto_sm3.py`、`tests/integration/test_gmssl_prototype_provider.py`
  （crypto 路径全回归，不做全量 quality）。

## 4. 完成条件

- 定向测试全绿；`python scripts/quality_gate.py --target fmt` 与 `--target lint`
  exit=0（记录新指纹；launcher 锁同步后 gmssl_provider 构造校验通过）；
- 行为验证：缓存命中路径、损坏自愈路径、锁链（toolchain-lock launcher sha）一致；
- 追溯矩阵新增 `ENG-BASE | PERF-HELPER-1` 行（无悬空）；
- security-reviewer 放行（crypto 启动链改动；确认算法/密钥语义不变、失败关闭
  保留、旁路校验无绕过）；全量 quality 按用户指示豁免。

## 5. 审查门

- security-reviewer：**是**（crypto 启动链/持久化二进制取舍）；protocol-reviewer：**否**。
