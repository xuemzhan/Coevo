# 配置参考（Configuration Reference）

> 状态：生效（2026-08-03，DOCS-COMMENT-1）。这是全部 `COEVO_*` 环境变量的权威登记表；
> 新增/删除/修改任一变量必须同步本表，并由
> `tests/unit/test_production_docs.py` 做“代码使用 ⇄ 文档登记”双向一致性校验。

## 变量分类

| 分类 | 用途 | 生产运行是否需要 |
|---|---|---|
| 驾驶舱运行时 | 本地驾驶舱的绑定、状态、日志与会话 | 是（均有默认值，按需覆盖） |
| 模型访问 | 本地/远程模型服务接入 | 按需（默认 offline） |
| 开发/门禁工具链 | 锁版本工具链定位与完整性校验 | 否（仅开发/门禁环境） |
| 仅测试/故障注入 | 测试专用故障钩子 | **禁止**在生产设置 |

所有运行时变量经 `src/coevo/config.py::AppConfig.from_env()` 校验，非法值一律抛
`ConfigError`（fail-closed），绝不静默回退到不安全默认值。

## 1. 驾驶舱运行时（src/coevo/config.py）

| 变量 | 默认值 | 合法范围/规则 | 说明 |
|---|---|---|---|
| `COEVO_COCKPIT_HOST` | `127.0.0.1` | 仅环回字面量 | 绑定地址；禁止 `0.0.0.0`/局域网地址（约束 §5.1） |
| `COEVO_COCKPIT_PORT` | `12701` | 整数 1..65535 | 本地 HTTP 服务端口 |
| `COEVO_COCKPIT_CHECKPOINT_SEC` | `300` | 正数 | 驾驶舱状态周期快照间隔（秒）；停机仍做最终落盘 |
| `COEVO_SESSION_TIMEOUT_SEC` | `28800` | 正整数 | 会话不活动超时（秒） |
| `COEVO_DATA_DIR` | `%LOCALAPPDATA%\KaiwuAgent` | 可解析路径 | 状态与数据根目录 |
| `COEVO_LOG_DIR` | `%LOCALAPPDATA%\KaiwuAgent` | 可解析路径 | 应用日志根目录 |
| `COEVO_LOG_LEVEL` | `INFO` | CRITICAL/ERROR/WARNING/INFO/DEBUG | 应用运行日志级别 |
| `COEVO_STATE_PATH` | 由 data 目录派生 | 可解析路径 | 驾驶舱状态文件显式覆盖 |
| `COEVO_LOG_PATH` | 由 log 目录派生 | 可解析路径 | 驾驶舱访问日志显式覆盖 |
| `COEVO_LOCK_PATH` | `%LOCALAPPDATA%\KaiwuAgent\cockpit.lock` | 可解析路径 | 单实例锁文件显式覆盖（STABILITY-1） |
| `COEVO_REPO_ROOT` | 脚本所在仓库根 | 可解析路径 | 门禁/脚本定位仓库根（开发与运维脚本） |
| `COEVO_WPS_EXE` | `wps.exe` | 非空字符串 | WPS 启动器显式可执行文件（cockpit/wps.py） |

## 2. 模型访问（src/coevo/model/）

模型供应商、端点、超时等**非敏感**配置位于 `config/model-config.json`
（经 `load_model_config` 严格校验 fail-closed）；提示词位于
`config/model-prompts.json`（SHA-256 digest 防篡改）。

| 变量 | 默认值 | 说明 |
|---|---|---|
| `COEVO_LLM_API_KEY` | 无 | 远程模型 API 密钥，仅经环境变量读取，绝不进配置/日志/repr/请求体 |
| `COEVO_LLM_EXTERNAL_DATA_OK` | 未设置（=0） | 兼容性遗留开关：仅在**直接构造** `DeepSeekProvider` 且未显式传 `external_data_ok` 时生效；经 `select_provider` 的标准路径以外发审批由 `config/model-config.json` 的 `external_data_ok` 决定（fail-closed 检查点在 provider 内）。设置时 `run_cockpit --preflight` 返回 degraded 并在启动日志告警（OPS-4 可见性） |

回环地址（`127.0.0.1`/`localhost`/`::1`）自动判定为**本地模式**：免密钥、免外发审批、
数据不出机（约束 §9.1）；非回环必须 https + 密钥 + 外发审批。

## 3. 开发/门禁工具链（锁版本，仅开发环境）

以下变量由 `scripts/enter-dev-environment.ps1` 依据 `docs/dependencies/toolchain-lock.json`
设置，用于锁版本与完整性校验；生产运行不需要，也不得手工绕过：

| 变量 | 指向 |
|---|---|
| `COEVO_POWERSHELL_PATH` / `COEVO_POWERSHELL_SHA256` | Windows PowerShell 5.1 及其哈希 |
| `COEVO_PYTHON_PATH` / `COEVO_PYTHON_SHA256` | 锁定 Python 解释器及其哈希 |
| `COEVO_NODE_PATH` / `COEVO_NODE_SHA256` | 锁定 Node（安全测试用）及其哈希 |
| `COEVO_OPENCODE_PATH` | 锁定 opencode 可执行文件 |
| `COEVO_MAKE_PATH` / `COEVO_MAKE_SHA256` | make 兼容 shim 及其哈希 |
| `COEVO_EXTERNAL_MAKE_PATH` / `COEVO_EXTERNAL_MAKE_SHA256` | 外部 make 探测与哈希 |
| `COEVO_CONTROL_ARCHIVE` / `COEVO_CONTROL_SHA256` | 锁定 `control.pyz` 归档及其哈希 |

## 4. 仅测试/故障注入（禁止生产设置）

以下变量仅用于测试故障注入与门禁探针，**生产环境禁止设置**：

| 变量 | 说明 |
|---|---|
| `COEVO_TEST_DROP_RESPONSE` | 丢弃 GmSSL helper 响应（测试） |
| `COEVO_TEST_KILL_POINT` | 指定杀点（测试） |
| `COEVO_TEST_ONLY_HELPER_HANG` | 使 helper 挂起（测试超时路径） |
| `COEVO_TEST_DIRECTORY_LOCK_ERRORS` / `COEVO_TEST_DIRECTORY_LOCK_ROLE` / `COEVO_TEST_ONLY_DIRECTORY_LOCK_INJECTION` | 目录锁故障注入（测试） |

## 5. 一致性校验

`tests/unit/test_production_docs.py` 断言：

1. `src/coevo/config.py` 中出现的全部 `COEVO_*` 变量均已登记到本表；
2. 本表登记的每个变量都能在 `src/coevo` 或 `scripts/` 代码中找到实际使用；
3. 已完成的切片不得在代码注释中继续以 “deferred to US-x-AC-y” / “future slice”
   描述（防止注释与实现脱节）。
