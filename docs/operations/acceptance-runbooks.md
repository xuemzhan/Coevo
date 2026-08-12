# 外部环境验收手册（MATURITY O-03 / O-04 / O-05，2026-08-12 就绪）

> 用途：为三项依赖物理环境的验收项提供"开箱即用"执行单——Windows 7 存量实机
> （O-03）、WPS 真实宿主（O-04）、目标硬件性能复测（O-05）。环境就绪后按本文
> 执行并把结果记录回 `loop/DECISIONS.md` 与 `loop/VERIFICATION.md`。

---

## 1. O-03 Windows 7 存量实机验收

### 前置

- 一台 Windows 7 64-bit 存量机（SP1 及以上）；Python 3.8 兼容层或仓库
  `win7-compat` 分支定义的降级工具链（见 `docs/architecture/win7-compat-branch.md`）；
- 离线介质：仓库离线包（`install_cockpit.py --action install` 产物）与测试
  `.agent` 样例包。

### 步骤

1. 安装并启动本地驾驶舱：`python scripts\run_cockpit.py --check` → `--port 12701`；
2. 冒烟：导入一个正常任务包 → 工作区初始化 → 驾驶舱列表可见；
3. 运行 Win7 专项套件：
   `python scripts\test.py --suite win7`（4 项：兼容档案/路径策略/降级清单/范围声明）；
4. 异常包注入：篡改包、错接收人包各 1 个，确认拦截且客户端不崩溃；
5. WPS 打开（若该机有 WPS）：允许列表内文档打开成功、越权路径被拒；
6. 断电恢复：运行中硬杀进程 → 重启 → 驾驶舱状态快照恢复（`COEVO_COCKPIT_CHECKPOINT_SEC`
   周期内变化最多丢失一个周期）。

### 通过标准

- win7 套件 4/4 通过；异常包 100% 拦截；无 Crash；
- 功能降级与 `win7-compat-branch.md` 声明一致（实机核对，不允许"静态声明当实机"）。

### 记录

在 `loop/DECISIONS.md` 追加条目（机型/OS 版本/结果/截图路径），并把
`known-limitations.md` 的 Win7 行更新为"实机已验证（机型清单）"。

---

## 2. O-04 WPS 真实宿主验收

### 前置

- 一台装有 WPS Office（Windows 版）的机器；`COEVO_WPS_EXE` 指向真实
  `wps.exe` 绝对路径；
- 准备 3 个样例文档（`.docx`/`.xlsx`/`.pptx`）放于受控工作区。

### 步骤

1. 配置校验：`python scripts\run_cockpit.py --check` 通过；
2. 启动驾驶舱，用允许列表内文档走 `/api/wps_open`（带 CSRF 双头 + confirm=true），
   观察 `STARTED`（真实进程拉起）；
3. 越权路径（`..`、绝对路径、`.exe`）→ `DENIED`；
4. 未配置启动器 → `NOT_AVAILABLE`（不得误报已打开）；
5. 生成副本：任务元数据写入模板并保存为新版本，确认原始文件未被覆盖。

### 通过标准

- 真实 WPS 进程启动成功且可打开文档；`wps_open` 状态语义与
  `WpsLaunchDecision`（OK/DENIED/NOT_AVAILABLE/ERROR）一致；
- 原始文件不被覆盖；越权路径全部拒绝。

### 记录

`loop/DECISIONS.md` 追加条目（WPS 版本/路径/打开与副本结果），并把
`capability-status.md` 的 US-7 WPS 注记从"待真实宿主验收"更新为已验收。

---

## 3. O-05 目标硬件性能复测

### 前置

- 目标配置（CPU/内存/磁盘/OS）按 `docs/requirements/system-requirements.md` §18
  与参考架构 SLA 声明；记录硬件与负载快照；
- 同一台机器跑基线 1 次（本机参考：`python scripts\benchmark.py --check` 13 项全达标）。

### 步骤

1. `python scripts\benchmark.py --check`（13 项探针：页面/任务查询/包校验/目录发现/
   打包成功率/DAG 3k/邻接查询/人才推荐/注册表/流程分组/审计追加/watcher 重扫/
   healthz p95）；
2. 并发导入：5 个任务包同时导入，观察原子性与计数；
3. 记录每项耗时到结果表（探针名/值/上限/是否达标/机器信息）。

### 通过标准

- 13 项探针全部 `ok`（与参考架构 SLA 对照：页面 ≤3s、任务查询 ≤2s、小包校验
  ≤10s、目录发现 ≤5s、打包成功率 ≥95% 等）；
- 并发导入无重复包、无半态工作区。

### 记录

结果表追加进 `loop/VERIFICATION.md`（或 `loop/archive/YYYYMMDD/`），并在
`loop/DECISIONS.md` 记录目标硬件配置与结论；`known-limitations.md` 的
"性能为本机测量"更新为"目标硬件已复测"。
