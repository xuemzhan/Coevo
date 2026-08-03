# 开发环境

Coevo 的 Loop 开发环境是仓库本地、锁版本且默认离线的。当前基线使用：

- CPython 3.14.3 官方签名离线制品（仓库 `.tools/python/3.14.3`，逐文件锁清单）；
- OpenCode CLI 1.18.2（官方 Windows x64 发布包）；
- Coevo Make compatibility shim 1.0（仅允许仓库 Makefile 已定义的固定目标）；
- Windows PowerShell 5.1+ / .NET X.509、CMS 与 CNG API；
- Git 2.53+；
- 当前 Windows 开发用户 `CurrentUser/My` 中固定指纹、不可导出的审计签名私钥。

## 进入环境

新开 PowerShell 后，在仓库根目录点加载一次入口：

```powershell
. .\scripts\enter-dev-environment.ps1
```

入口会在修改当前会话 PATH 前验证 OpenCode、CPython 与 Make 的锁定信息，重新编译仓库自有 Make 兼容入口，并为已验证的可执行文件和源码持续持有拒绝写入/删除句柄。Make 在 Python 子进程退出前逐文件锁定运行时和 `scripts/*.py`，清除继承的 `PYTHON*` 变量并使用隔离启动参数。入口不修改注册表、永久 PATH 或 `%ProgramData%`，也不联网下载；关闭终端后临时环境和句柄自动释放。

每次入口都会在 `.tools\bin-<PID>` 下编译本会话专用的 Make 兼容入口并加入当前 PATH。该临时目录的生命周期受控：

- `.\scripts\dev.ps1` 与 `.\scripts\run-loop.ps1` 在任务结束（含失败与 `exit` 路径）时通过 `finally` 显式关闭句柄并删除本会话的 `bin-<PID>` 目录；
- 入口再次启动时会先清扫历史残留：仅删除目录名匹配 `bin-<数字>`、路径位于 `.tools` 内、不是重解析点、且对应 PID 已不存在的目录（正在运行的其他会话因句柄锁定会安全跳过，由下一次入口继续清理）；
- 交互式点加载（`. .\scripts\enter-dev-environment.ps1`）未显式收尾时，残留目录由下一次入口自动清扫。
The entry point canonicalizes duplicate Windows `Path` / `PATH` variables into one process-scoped key. The strict `env-check` reports locking progress and verifies the final merged OpenCode configuration: auto-update and LSP download remain disabled, while external-directory, web-fetch, and web-search permissions remain denied.


常用命令：

```powershell
make env-check
make quality
.\scripts\dev.ps1 -Task loop-status
```

也可不进入交互环境，直接运行：

```powershell
.\scripts\dev.ps1 -Task quality
```

`make` 兼容入口只接受 `fmt`、`lint`、`test`、`test-security`、`test-e2e`、`quality`、`verify-loop-state` 与 `env-check`；变量赋值、额外参数和未知目标均返回退出码 64。它不是 GNU Make，也不尝试模拟任意 Makefile 语法。

## 测试与静态检查入口

- 质量门禁的唯一权威测试入口是 `make quality`（内部统一使用 `unittest` 发现并运行
  `tests/unit`、`tests/integration`、`tests/security`、`tests/e2e`）。
- 开发环境中存在的 `pytest` / `ruff`（当前版本见 `.venv` 或系统解释器）未进入
  `docs/dependencies/toolchain-lock.json`，不属于已批准的离线工具链，**不得**作为门禁
  判定依据；将其纳入门禁属于新的依赖审批工作项。

## 工具锁与离线边界

权威工具记录位于 `docs/dependencies/toolchain-lock.json`，包含批准人、精确版本、官方发布地址、构件名称、大小、SHA-256、许可证、运行时依赖与解压后入口哈希。下载只发生在仓库所有者明确批准的配置阶段；日常入口和质量门禁不含下载逻辑。

二进制位于 `.tools/` 且不进入 Git。若本地缓存缺失或哈希不符，环境入口失败关闭；不得自动升级或静默改用系统同名程序。重新导入必须从清单中的官方发布地址取得同一构件并复核哈希。升级版本属于新的依赖审批工作项。

项目级 `opencode.jsonc` 继续禁止联网工具、外部目录和依赖安装。组织级 `%ProgramData%\opencode\opencode.jsonc` 需要管理员独立部署，本仓库和入口脚本均不会修改它。

## Loop 使用边界

`/loop-status` 只读取状态；`/loop` 每次只推进一个最小工作项。开发环境的端到端烟雾验证必须在 `.loop-smoke/` 隔离副本中执行，不允许借环境验证推进真实的 `US-0-AC-2`。真实仓库仍以 `loop/STATE.json`、`loop/BACKLOG.yaml` 和门禁记录为准。

一个工作项只有在独立 verifier 实际运行 `make quality`、必要的安全审查放行、追踪矩阵与验证记录更新后才能完成。门禁会验证源码、OpenCode 配置、追踪矩阵、单元/集成/安全/E2E 测试、全局审计签名，以及身份库的严格证书解析、独立签名审计锚点和回滚检测。

## 身份库安全说明

新库必须显式调用 `IdentityRepository.create(...)`，已有库必须显式调用 `IdentityRepository.open(...)`。数据库、正式链头、签名或当前代际标记任一缺失/不匹配时均失败关闭。

每次业务提交都会生成新的不可导出 CNG 标记私钥和 `CurrentUser/My` 标记证书。旧代际严格先按签名绑定的 key ID 与公钥摘要销毁私钥并验证无法重新打开，再移除证书；正式 head 与外部退休记录保留签名 tombstone。崩溃恢复与安全测试覆盖旧快照回放、标记/tombstone/pending 篡改以及 key-first 删除各阶段。

开发期 RSA-3072/SHA-256、本机自签代际标记和固定审计签名者仅用于本机篡改与回滚发现；正式环境仍必须替换为批准的 SM2 产品、组织证书链、受保护的硬件密钥和独立审计节点。

## 代码注释与文档规范

- **注释必须与当前实现一致**：切片落地后必须清除 `deferred to US-x-AC-y` /
  `future slice` 式过时描述（已完成的 AC 不再"待办"）；不得引用不存在的 AC。
- **模块 docstring 自述真实边界**：说明本模块做什么、不做什么，IO/LLM/持久化
  等边界落到具体实现模块（如 `store.py`、`server.py`、`agent.py`），而非抽象地
  说"未来切片"。
- **注释解释 why/constraint，不重复代码**：安全/合规约束用文档编号引用
  （如"约束 §5.1"、"协议 §16.2"）；普通代码逻辑不逐行复述。
- **语言一致性**：同一文件内保持同一种注释语言；公共 API 以英文 docstring 为主，
  业务术语允许中文，但全仓统一（驾驶舱=cockpit、任务包=.agent package、运行中枢=orchestrator）。
- **配置登记纪律**：新增/删除/修改任一 `COEVO_*` 环境变量必须同步
  `docs/operations/configuration-reference.md`（`tests/unit/test_production_docs.py`
  做双向一致性校验）；修改运行行为须同步 `docs/production-readiness.md`。
- **追溯纪律**：行为或文档基线变更须同步 `loop/BACKLOG.yaml` 与
  `docs/traceability/requirements-test-matrix.md`（lint 门禁校验无悬空条目）。
