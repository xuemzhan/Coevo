# FRAMEWORK-OPTIMIZE-16 切片计划：共享 PowerShell 可执行文件解析（powershell.py）

> 状态：已批准（2026-08-08 用户指令"继续优化，不做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-16`（ENG-BASE，dependencies=[]）。
- 目的：`identity/certificates.py`、`identity/audit_anchor.py`（简单变体）与
  `identity/private_keys.py`、`crypto/cng_handle.py`（锁哈希校验变体）四处重复实现
  "解析 Windows PowerShell 可执行文件"；统一到单一事实源叶子
  `src/coevo/powershell.py`（jsonutil 式 `error_factory` 保留各模块异常语义，
  行为逐位不变）。

## 2. 交付

- 新增 `src/coevo/powershell.py`：
  * `powershell_executable(*, error_factory)`——简单变体：COEVO_POWERSHELL_PATH
    绝对路径优先，否则 SystemRoot 下 powershell.exe（存在即返回，否则抛
    error_factory）；
  * `locked_powershell_executable(lock_path, *, error_factory)`——锁校验变体：
    读 toolchain-lock `make_compatibility_shim.windows_powershell`，解析
    COEVO_POWERSHELL_PATH 或 SystemRoot/<relative>，校验绝对路径 + size + sha256，
    fail-closed。
- 四模块收敛为薄包装（调用点不变，异常类不变）：
  * certificates.py / audit_anchor.py → `powershell_executable(error_factory=...)`；
  * private_keys.py / cng_handle.py → `locked_powershell_executable(lock_path, error_factory=...)`。
- `docs/modules/root_modules.md` 登记 `powershell.py`。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize17.py`：
  * 简单变体：COEVO_POWERSHELL_PATH 绝对路径命中；SystemRoot fallback 存在；
    fallback 缺失 → error_factory 抛错；
  * 锁校验变体：临时 lock（真实 powershell size/sha）命中；篡改 sha → 抛错；
    坏 lock json → 抛错；非绝对 COEVO_POWERSHELL_PATH → 抛错；
  * 守卫：四模块本地解析函数委托共享叶子（源码含 powershell 导入、不含重复的
    SystemRoot/powershell.exe 解析逻辑副本）。
- 回归：identity/crypto 相关测试（certificates / audit_anchor / private_keys /
  cng_handle）。

## 4. 完成条件

- 定向测试全绿；fmt + lint exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-16` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**是**（PowerShell 路径解析为身份/密钥/证书安全关键，须确认
  锁校验与失败关闭语义逐位保留）；protocol-reviewer：**否**。
