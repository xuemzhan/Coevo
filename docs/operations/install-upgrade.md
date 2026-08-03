# 离线安装 / 升级 / 回滚 / 卸载手册（INSTALL-1）

> 状态：生效（2026-08-03）。对应 P0-1 决策点“打包 / 离线安装器 / 升级回滚”。
> 仅使用 Python 标准库；不引入新依赖、不在运行时下载任何内容。

## 1. 定位

`scripts/install_cockpit.py` 是本地驾驶舱的离线部署工具，提供五个动作：

| 动作 | 说明 |
|---|---|
| `install` | 安装指定版本（默认取 `src/coevo/version.py` 的 `VERSION`） |
| `upgrade` | 安装新版本并切换 `current` 指针；上一版本保留可回滚 |
| `rollback` | 回滚到上一版本（先复验上一版本完整性清单，再切指针） |
| `uninstall` | 移除当前版本（数据与日志保留，其他版本保留） |
| `check` | 校验当前安装完整性（指针/版本目录/清单/数据目录） |

## 2. 目录布局

默认安装根目录为 `%LOCALAPPDATA%\KaiwuAgent`（可用 `--install-root` 覆盖）：

```text
%LOCALAPPDATA%\KaiwuAgent\
├─ app\<version>\         运行时包（src/、scripts/run_cockpit.py、config/、README.md）
├─ manifests\<version>.sha256  每版本 SHA-256 完整性清单
├─ releases.json          安装历史（schema 1.0，追加式）
├─ current                current 指针（原子切换，内容为版本号）
├─ logs\install.log       安装操作日志（尽力而为，不影响结果）
├─ cockpit-state.json     驾驶舱状态（数据，卸载保留）
└─ cockpit-access.jsonl   驾驶舱访问日志（数据，卸载保留）
```

## 3. 使用

```powershell
# 安装（版本取源码 VERSION）
python scripts\install_cockpit.py --action install

# 安装指定版本
python scripts\install_cockpit.py --action install --version 0.2.0

# 升级到新版本（上一版本保留）
python scripts\install_cockpit.py --action upgrade --version 0.3.0

# 回滚到上一版本（先复验完整性清单）
python scripts\install_cockpit.py --action rollback

# 校验当前安装
python scripts\install_cockpit.py --action check

# 卸载当前版本（保留数据/日志/其他版本）
python scripts\install_cockpit.py --action uninstall

# 卸载全部版本与安装历史（仍保留数据/日志）
python scripts\install_cockpit.py --action uninstall --all
```

## 4. 安全与完整性

- 版本号必须匹配 `^\d+\.\d+\.\d+$`（语义化版本，禁止时间戳），并作为唯一安全路径段；
- 每个文件复制时计算 SHA-256，写入清单后**复验通过才切换 `current` 指针**；
- 回滚前必须通过上一版本清单复验，否则拒绝切换；
- 安装失败自动清理目标版本目录，不留下半成品；指针只在完整安装后切换；
- 源目录中的符号链接一律跳过（不跟随），复制范围固定为 `src/`、`scripts/run_cockpit.py`、
  `scripts/run_demo.py`、`config/`、`README.md`；
- 破坏性操作仅限 `app/`、`manifests/`、`releases.json` 与 `current` 指针；数据/日志永不删除；
- 单实例锁（`install.lock`，残留超过 10 分钟自动接管）防止并发安装。

## 5. 启动

安装完成后运行：

```powershell
python "%LOCALAPPDATA%\KaiwuAgent\app\0.2.0\scripts\run_cockpit.py"
```

## 6. 已知限制与后续决策点

- 本工具交付"离线安装 + 完整性清单 + 升级/回滚"；**制品签名**（对完整性清单做数字签名）
  与 **pyproject/setuptools 打包元数据** 需另行审批（构建工具链属新依赖，按仓库规则离线审批）；
- 未包含 Windows 服务/自启注册（任务计划）与 Win7 分支安装验证；这两项属 P0-②/④ 决策点；
- 安装包不包含 `.tools/`（开发工具链）与 `loop/`（开发循环记录），生产运行不需要。
