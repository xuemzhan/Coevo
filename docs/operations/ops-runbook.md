# 生产运维手册（OPS-1）

> 状态：生效（2026-08-04）。面向已安装驾驶舱的日常运维：健康检查、自启守护、
> 日志轮转、备份/恢复指引与排障。安装/升级/回滚见 `install-upgrade.md`；
> 环境变量见 `configuration-reference.md`；审计签名密钥见 `audit-key-runbook.md`。

## 1. 健康检查

```powershell
python scripts\health_check.py --install-root "%LOCALAPPDATA%\KaiwuAgent"
# 异地备份监控（OPS-3）：备份根 + 最大备份年龄（天）
python scripts\health_check.py --backup-root "D:\CoevoBackups" --max-backup-age-days 7
```

输出结构化 JSON（`checks[]` + `status`），退出码：0=ok、1=degraded、2=critical。
检查项：

| 检查 | 含义 | 失败等级 |
|---|---|---|
| dirs | 数据/日志目录存在且可写 | critical |
| disk | 磁盘余量 ≥ `--min-free-bytes`（默认 512MiB） | critical |
| version | current 指针与安装包 `version.py` 一致 | critical |
| lock | 单实例锁未陈旧（<10 分钟） | critical |
| cockpit | `/healthz` 返回 200 | degraded（未运行） |
| audit | `audit_seal.py verify`：fully-sealed ok；未封尾=degraded；失败=critical | 分级 |
| backup | 最新备份 manifest 存在且 ≤ `--max-backup-age-days`（默认 7 天；OPS-3） | degraded（缺失/过期，恢复姿态告警，不阻断服务） |
| pin | `<install-root>\python-path.txt` 存在、绝对路径且指向存在的解释器（OPS-5） | degraded（缺失/无效，看门狗将回退 PATH） |

可接入监控/计划任务定期执行；本脚本只读、不修改任何状态。

`install_cockpit.py --action check`（OPS-5）会**强制**校验解释器 pin：缺失、空、
非绝对路径或目标不存在时 check 失败（exit 1），提示先执行
`register-autostart.ps1 -Action PinPython`（或重跑 `Register`）。

进程内状态端点：`GET /api/health`（需会话令牌，认证只读）返回 service、version、
started_at、uptime_sec、session_count、request_count、probe_count、
audit_records、log_errors，供已登录管理端/运维脚本即时查看运行实例状态。
`request_count` 只统计认证请求；`probe_count`（METRICS-2）单独统计 `/healthz`
存活探测（看门狗/健康检查/基准探针），两者线程安全且互不混淆。

## 2. 自启守护（登录启动驾驶舱）

```powershell
# 注册：登录时以普通权限、隐藏窗口启动已安装驾驶舱
.\scripts\register-autostart.ps1 -Action Register -InstallRoot "%LOCALAPPDATA%\KaiwuAgent"

# 先预览（不触碰系统）
.\scripts\register-autostart.ps1 -Action Register -DryRun

# 固化解释器路径（写 <install_root>\python-path.txt，不碰计划任务）
.\scripts\register-autostart.ps1 -Action PinPython -PythonPath "C:\Python314\python.exe"

# 查询 / 卸载
.\scripts\register-autostart.ps1 -Action Status
.\scripts\register-autostart.ps1 -Action Unregister
```

失败关闭：安装根缺失、current 指针无效、`run_cockpit.py` 缺失或 Python 不可解析时
中止且不修改系统；`Register` 还会先把解析到的解释器写入
`<install_root>\python-path.txt`（写失败则中止，不创建任务）。任务基于 Windows
计划任务（`onlogon`、`LIMITED`），无需管理员。

解释器固化（OPS-2）：`install_cockpit.py` 在安装/升级成功时与 `Register`/`PinPython`
都会把绝对解释器路径写入 `<install_root>\python-path.txt`，看门狗优先读取该
sidecar，不再依赖 PATH。显式 `-PythonPath` 参数优先级最高；sidecar 缺失或指向
不存在的解释器时失败关闭（不静默回退）。

## 2.1 启动预检与看门狗（AVAIL-1）

```powershell
# fail-fast 启动预检（0=ok / 1=degraded / 2=critical，critical 不启动）
python scripts\run_cockpit.py --preflight

# 看门狗：轮询 /healthz，连续 3 次失败后隐藏窗口重启已安装驾驶舱
.\scripts\cockpit-watchdog.ps1 -InstallRoot "%LOCALAPPDATA%\KaiwuAgent"

# 先探测一轮（不触系统）
.\scripts\cockpit-watchdog.ps1 -DryRun

# 显式指定解释器（跳过 sidecar 与 PATH）
.\scripts\cockpit-watchdog.ps1 -PythonPath "C:\Python314\python.exe" -DryRun
```

看门狗带重启冷却（默认 60 秒）防止崩溃循环；DryRun 只探测并打印将执行的动作。
预检覆盖：配置、数据/日志目录可写、磁盘余量、审计封存状态、模型配置可加载。
解释器解析顺序：显式 `-PythonPath` → `<install_root>\python-path.txt`（OPS-2
sidecar）→ PATH；sidecar 内容必须是绝对路径且指向存在的可执行文件，否则失败关闭。

模型外发姿态（OPS-4）：当激活 provider 为非回环（https）且
`config/model-config.json` 的 `external_data_ok=true`，或遗留开关
`COEVO_LLM_EXTERNAL_DATA_OK=1` 被设置时，`--preflight` 返回 degraded 并在
启动日志输出 `model egress posture` 告警——审批机制本身 fail-closed 且合法，
此告警仅为让"数据可能离开本机"可见；回环 provider（数据不出机）不告警。

## 2.2 交互式访问（会话令牌，REVIEW-FIX-2）

驾驶舱 UI/API 需要会话令牌（Bearer）。交互式启动时签发一次并在 stdout 显示：

```powershell
python scripts\run_cockpit.py --print-token
# 输出：coevo cockpit ready: http://127.0.0.1:12701/
#       session token: <token>
# 浏览器打开 http://127.0.0.1:12701/?token=<token>
```

令牌只在 stdout 显示一次（flush 即时可见），不经过日志框架、不落盘；服务端仅保留
SHA-256 摘要，超时自动失效。自启/看门狗等无控制台场景不打印令牌（进程内会话
不可跨进程签发），headless 运维走 `/healthz` + 健康检查 + 访问日志即可；如确需
在 headless 场景使用 UI，需另行决策令牌分发方案（如受控文件握手）。

## 3. 日志轮转

- 应用运行日志：`coevo-app.log`（5MB×5，自动轮转）；
- 驾驶舱访问日志：`cockpit-access.jsonl`（**5MB×5，按大小自动轮转**，OPS-1）；
- 安装日志：`logs/install.log`（追加式，量小）；
- 审计链：`loop/tool-audit.jsonl` + `audit-head.*`（签名封存，禁止手工轮转/删除）。

## 4. 备份与恢复

推荐使用脚本化备份/恢复工具（离线、SHA-256 清单、运行中拒绝恢复）：

```powershell
# 备份（默认到 %LOCALAPPDATA%\KaiwuAgent\backups\<时间戳>\）
python scripts\backup_state.py --action backup

# 异地备份（另一磁盘/网络共享；BACKUP-2：强制异卷 + 安装根外）
python scripts\backup_state.py --action backup --backup-root "D:\CoevoBackups" --require-external

# 校验备份 / 列出备份 / 恢复（恢复前自动校验；运行中锁存在时拒绝）
python scripts\backup_state.py --action verify --label <label>
python scripts\backup_state.py --action list
python scripts\backup_state.py --action restore --label <label>
```

备份内容：驾驶舱状态/访问日志、current 指针、安装历史、封装密钥注册表、
审计链（tool-audit/audit-head/audit-signing*）与 manifests。恢复前会校验清单；
恢复时把将被覆盖的文件先复制到 `.pre-restore-<ts>` 再回拷。审计链恢复后运行
`python scripts/audit_seal.py verify` 确认封存状态。密钥材料（CNG KEK、私钥句柄）
不随文件备份，需按 `audit-key-runbook.md` / 身份库方案另行处置。

默认备份根（`<install_root>\backups`）与数据同卷；manifest 的 `same_volume`
字段可供自动化检查。生产部署建议用 `--backup-root` 指向另一磁盘/共享并加
`--require-external`：备份根位于安装根内、或与安装根同卷时直接失败（失败关闭），
避免磁盘故障同时毁掉数据与备份。`--require-external` 仅作用于 `backup` 动作；
`verify`/`restore` 不设此限制（恢复只看备份自身完整性）。

## 5. 排障速查

| 现象 | 处置 |
|---|---|
| 驾驶舱无法启动 | `health_check.py` 看 dirs/version/lock；`run_cockpit.py --check` 验配置；单实例锁残留 >10 分钟自动接管 |
| `/healthz` 不通 | 进程是否存活；端口被占则换 `COEVO_COCKPIT_PORT` |
| 审计未封尾（degraded） | 本地执行 `make quality` 重新封存（签名私钥在维护机） |
| 审计 critical | `python scripts/audit_key_health.py` 按 runbook 恢复 |
| 磁盘告警 | 轮转日志已自动处理；检查 `loop/archive/` 归档策略 |
| CI 恢复失败 | `ci-artifact.json` 哈希未回填 → 先发布制品并钉扎（见 ci-artifact-hosting.md） |

## 6. 边界

- 健康检查不替代 `make quality`（后者含测试与审计封存）；
- 自启任务不提升权限、不注册服务；需要 Windows 服务形态属后续决策点；
- 备份不含密钥句柄与 CNG 私钥，恢复密钥需按身份库/密钥手册单独进行。

## 7. 发布就绪（RELEASE-1）

发布前运行单命令就绪检查（JSON + 退出码 0=就绪 / 1=警告 / 2=不发布）：

```powershell
python scripts\release_check.py --expect-version <版本>
```

检查项：git 工作区干净、版本语义化且匹配、审计 fully-sealed（未封尾=警告）、
secret_scan 干净、追溯矩阵一致、loop/STATE done 且无阻塞、无 in-progress 工作项
（ready 项=警告，视为显式推迟）。已知限制与外部条件见
`known-limitations.md`，发布前必读。
