# 生产运维手册（OPS-1）

> 状态：生效（2026-08-04）。面向已安装驾驶舱的日常运维：健康检查、自启守护、
> 日志轮转、备份/恢复指引与排障。安装/升级/回滚见 `install-upgrade.md`；
> 环境变量见 `configuration-reference.md`；审计签名密钥见 `audit-key-runbook.md`。

## 1. 健康检查

```powershell
python scripts\health_check.py --install-root "%LOCALAPPDATA%\KaiwuAgent"
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

可接入监控/计划任务定期执行；本脚本只读、不修改任何状态。

## 2. 自启守护（登录启动驾驶舱）

```powershell
# 注册：登录时以普通权限、隐藏窗口启动已安装驾驶舱
.\scripts\register-autostart.ps1 -Action Register -InstallRoot "%LOCALAPPDATA%\KaiwuAgent"

# 先预览（不触碰系统）
.\scripts\register-autostart.ps1 -Action Register -DryRun

# 查询 / 卸载
.\scripts\register-autostart.ps1 -Action Status
.\scripts\register-autostart.ps1 -Action Unregister
```

失败关闭：安装根缺失、current 指针无效、`run_cockpit.py` 缺失或 Python 不可解析时
中止且不修改系统。任务基于 Windows 计划任务（`onlogon`、`LIMITED`），无需管理员。

## 2.1 启动预检与看门狗（AVAIL-1）

```powershell
# fail-fast 启动预检（0=ok / 1=degraded / 2=critical，critical 不启动）
python scripts\run_cockpit.py --preflight

# 看门狗：轮询 /healthz，连续 3 次失败后隐藏窗口重启已安装驾驶舱
.\scripts\cockpit-watchdog.ps1 -InstallRoot "%LOCALAPPDATA%\KaiwuAgent"

# 先探测一轮（不触系统）
.\scripts\cockpit-watchdog.ps1 -DryRun
```

看门狗带重启冷却（默认 60 秒）防止崩溃循环；DryRun 只探测并打印将执行的动作。
预检覆盖：配置、数据/日志目录可写、磁盘余量、审计封存状态、模型配置可加载。

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
