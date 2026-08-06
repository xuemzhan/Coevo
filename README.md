# Coevo — 分布式任务管理具身智能体系统（MVP）

> 面向跨部门、跨单位、跨专业、长链条复杂任务的全过程管理。以“运行中枢 + 离线任务包 +
> 本地驾驶舱”的方式，实现任务流程理解、结构化分解、团队推荐、安全任务包流转、成果回传
> 与版本合并、风险预警、决策简报和知识沉淀的**离线闭环**。

---

## 1. 项目简介

Coevo 是一个**分布式任务管理具身智能体系统**的 MVP 实现。它把复杂业务任务切成可
离线流转的 `.agent` 加密任务包，由“运行中枢”按固定编排链调度不同角色（负责人、研发、
测试、文档、评审、安全管理员等），并以本地驾驶舱提供可视化与受控操作入口。

设计约束（全部落地并在门禁中强制）：

- **全程离线**：无网络请求、无运行时下载、无隐式依赖；
- **失败关闭**：任何输入不满足契约即抛错，绝不静默降级；
- **版本优先于时间戳**：流程/基线/主版本一律用整数版本号，时间仅作展示；
- **状态变更须人工确认**：编排、合并、风险发布、简报、知识入库都有确认节点；
- **全程审计**：各服务提供 `to_audit_record`，敏感文本只保留哈希/计数；
- **不落明文私钥**：私钥字节不进入 Python 进程，只经受控助手返回密码运算结果。

## 2. 核心能力（US-0 ~ US-15）

| 故事 | 能力 | 主要模块 |
|---|---|---|
| US-0 | 身份与密钥、可信证书、项目角色最小模型 | `identity/`、`crypto/` |
| US-1 | 任务流程理解（canonical/tabular/tree 三 schema） | `task_flow/` |
| US-2 | 任务分解：基线、依赖图、编辑与覆盖审计 | `task_decomposition/` |
| US-3 | 脱敏人才池与确定性推荐 | `talent/` |
| US-4 | 运行中枢：固定编排链 + 真实链 | `orchestrator/` |
| US-5 | `.agent` 任务包：SM2 封钥 + SM4-GCM 载荷 + 原子导入 | `protocol/` |
| US-6 | 工作区初始化与安全路径 | `workspace/` |
| US-7 | 本地驾驶舱（环回绑定 HTTP + 静态资源 + WPS 启动） | `cockpit/` |
| US-8 | 进展采集：文件 watcher + 证据提取 | `progress_capture/` |
| US-9 | 成果回传包构建 | `report/` |
| US-10 | 状态合并（权威回执 + 字段级决策） | `merge/` |
| US-11 | 风险预警（四类基础风险 + 传染推断） | `risk/` |
| US-12 | 督办与会话协调 | `supervision/` |
| US-13 | 决策简报（负责人密钥确认绑定） | `decision_brief/` |
| US-14 | 知识沉淀与可复用模板 | `knowledge_base/` |
| US-15 | 安全审计（统一事件 + 哈希链 + 拦截判定） | `audit_governance/` |

两条**固定编排链**均已端到端验证：

- 任务下发链：`tests/e2e/test_demo_runner.py`（流程理解 → 分解 → 推荐 → 人工确认 → 加密包导出）；
- 成果回传链：`tests/e2e/test_return_chain.py`（真实 SM2/SM4 加密成果包 → 原子导入 → 合并回执 → 风险/简报/知识）。

## 3. 架构总览

```text
examples/                    应用/演示层（可运行示例 + 一致性 API 框架）
src/coevo/                   生产代码
├── app/                     应用组合根（pipeline / demo_support）
├── identity/                身份与信任（US-0）
├── task_flow/               任务流程理解（US-1）
├── task_decomposition/      任务分解（US-2）
├── talent/                  团队组建（US-3）
├── orchestrator/            运行中枢（US-4）
├── protocol/                任务包协议（US-5，.agent）
├── workspace/               工作区初始化（US-6）
├── cockpit/                 本地驾驶舱（US-7）
├── progress_capture/        进展采集（US-8）
├── report/                  成果回传（US-9）
├── merge/                   状态合并（US-10）
├── risk/                    风险预警（US-11）
├── supervision/             督办与会议协调（US-12）
├── decision_brief/          决策简报（US-13）
├── knowledge_base/          知识沉淀（US-14）
├── audit_governance/        安全审计（US-15）
├── crypto/                  国密引擎适配（SM2/SM3/SM4）
├── benchmarks/              可扩展性探针
├── config.py / version.py / logging_setup.py / records_archive.py
scripts/                     工程底座与运维脚本
tests/                       单元/集成/安全/端到端/Win7 测试
examples/                    跨单位小工具开发项目完整演示 + 统一服务框架
```

数据流（回传链核心）：`成果包 → 原子导入（重放门 + 7 步事务）→ 合并（字段级决策 +
签名收据）→ 风险分析 → 决策简报 → 知识入库 → 审计流`，全程可离线复现。

## 4. 快速开始

### 4.1 环境与工具链

```powershell
# 进入受控开发环境（锁定版本工具链，零联网）
.\scripts\dev.ps1 -Task env-check
```

工具链（Python、GmSSL、编译器）以 `docs/dependencies/toolchain-lock.json` 锁定
版本与 SHA-256，运行时不联网下载。

### 4.2 质量门禁

```powershell
# 全量门禁：compileall + lint + 单元 + 集成 + 安全 + E2E + 审计封存
python scripts\quality_gate.py --target quality

# 或经由 dev.ps1 包装
.\scripts\dev.ps1 -Task quality
```

门禁每次运行都会追加 `loop/VERIFICATION.md` 指纹并封存审计链（`loop/audit-head.*`）。

### 4.3 离线演示闭环

```powershell
python scripts\run_demo.py --smoke        # 编排链 + 加密任务包 + 驾驶舱 + 知识库 + 审计流
python scripts\run_demo.py                # 完整演示（可 --interactive / --serve）
```

### 4.4 本地驾驶舱

```powershell
python scripts\run_cockpit.py --check     # 自检（环回绑定、端口、静态资源）
python scripts\run_cockpit.py             # 启动（环回绑定 + 优雅停机）
```

驾驶舱只允许绑定 `127.0.0.1`（AC-1 失败关闭），API 需要 bearer-token 会话。

### 4.5 基准与性能

```powershell
python scripts\benchmark.py --check
```

覆盖 13 项探针：SLA 参考表（页面/任务查询/包解析/目录扫描/包生成）+ 可扩展性探针
（依赖图拓扑排序、邻接查询、人才推荐、注册表查询、watcher 增量重扫、流程 JSON 分组、
审计流追加、驾驶舱 HTTP）。当前全部达标（`all_ok=true`）。

## 5. 端到端示例（examples）

`examples/` 是使用 MVP 已实现能力做的**可运行端到端演示**，全程离线：

| 示例 | 场景 | 覆盖 |
|---|---|---|
| [tool-dev-project](examples/tool-dev-project/) | “内部工时统计小工具”跨单位开发任务，负责人/研发/测试/文档/评审/安全管理员多角色协作 | US-0 ~ US-15 全流程 |
| [service-api](examples/service-api/) | 统一服务框架：16 个领域模块经一致性 API（统一信封/错误码/权限/OpenAPI/客户端/API 浏览器/审计）开放 | 全模块统筹 + API 封装 |

```powershell
# 一键运行全部示例并核验产物
python examples\run_all.py

# 单个示例
python examples\tool-dev-project\scripts\run_example.py
python examples\service-api\run_demo.py
python examples\service-api\run_demo_full.py

# 演示包装脚本（自动识别虚拟环境）
examples\tool-dev-project\scripts\run-demo.ps1 -Open        # 跑完自动打开演示报告
examples\tool-dev-project\scripts\run-demo.ps1 -Interactive # 逐段暂停讲解
examples\tool-dev-project\scripts\run-demo.ps1 -Serve       # 跑完保持驾驶舱服务
```

示例产出：流程模型、任务基线、加密 `.agent` 任务包、合并回执、风险报告、决策简报、
知识包、审计流，以及离线自包含的 `demo-report.html`。产物写入
`output/run-<时间戳>/`（已 gitignore）。

## 6. 安全与合规不变量

- **身份与密钥**：私钥字节不进入 Python 进程；句柄/回滚/吊销由受控助手完成；
  身份库由签名单调新鲜度锚保护（防回滚/防篡改）。
- **任务包协议**：Fixed Header 字节精确、规范 JSON（去重键拒绝）、重放/重复检测
  失败关闭、原子导入 7 步事务、失败回滚不留半态。
- **合并边界**：合并收据签名 + 快照冻结 + 密封 store（每次访问全量重校验历史）；
  状态变更必须人工确认。
- **审计链**：统一 `AuditEvent`（六核心字段），JSONL + SHA-256 哈希链，追加独占、
  失败关闭；`loop/audit-head.*` 每次门禁后封存。
- **驾驶舱**：仅环回绑定、CSRF 校验、静态资源路径白名单、WPS 启动走允许列表。
- **路径安全**：工作区/模板/静态资源一律安全 ID + 防穿越（`..`、反斜杠、重解析点拒绝）。
- **工具链**：编译产物 SHA-256 锁定，运行时不联网下载新依赖。

## 7. 开发与工程循环（Loop Engineering）

仓库遵循七个固定阶段推进最小工作项：

```text
DISCOVER → PLAN → IMPLEMENT → VERIFY → REVIEW → RECORD → DECIDE
```

- 权威输入：`docs/requirements/`、`docs/constraints/`、`docs/protocol/`、
  `loop/GOAL.md`、`loop/STATE.json`、`loop/VERIFICATION.md`；
- 每个工作项必须有对应测试（含异常与重放）、`make quality` 全绿、追溯矩阵无悬空；
- 独立 `mvp-verifier` 与（必要时）`security-reviewer` 双签放行；
- 完成定义、禁止行为与停止条件见仓库 `AGENTS.md`。

常用工具：

```powershell
python scripts\quality_gate.py --target fmt     # compileall 语法门禁
python scripts\quality_gate.py --target lint    # validate_opencode + traceability + 审计校验
python scripts\benchmark.py --check             # SLA 与可扩展性探针
python scripts\run_validation.py                # 记录一致性校验（GOAL/STATE/BACKLOG/审计）
```

## 8. 代码注释导览

`docs/code-guide.md` 提供逐模块职责/调用链/安全不变量导览，并附“性能与复杂度特征”
章节（记录 OPT-PERF-1 与后续优化轮的复杂度结论）。`src/coevo` 88 个模块均含
模块总览注释；模块级公开函数与实质性公开方法 docstring 覆盖率 ~99%。

## 9. 生产部署

```powershell
# 1) 离线安装/升级/回滚/卸载（版本化目录 + SHA-256 完整性清单）
python scripts\install_cockpit.py --action install        # 安装（版本取 src/coevo/version.py）
python scripts\install_cockpit.py --action upgrade --version <新版本>
python scripts\install_cockpit.py --action rollback       # 回滚上一版本（先验清单）
python scripts\install_cockpit.py --action check          # 校验当前安装完整性

# 2) 从已安装目录启动驾驶舱
python "%LOCALAPPDATA%\KaiwuAgent\app\<version>\scripts\run_cockpit.py"
```

全部环境变量、默认值与校验规则见 `docs/operations/configuration-reference.md`；
安装/升级/回滚手册见 `docs/operations/install-upgrade.md`；审计签名密钥健康诊断与
恢复见 `docs/operations/audit-key-runbook.md`。

## 10. 仓库结构与文档索引

| 主题 | 位置 |
|---|---|
| 需求与约束基线 | `docs/requirements/`、`docs/constraints/` |
| 参考架构与选型 | `docs/architecture/` |
| `.agent` 任务包协议 | `docs/protocol/agent-package-protocol.md` |
| 生产可用性说明 | `docs/production-readiness.md` |
| 开发环境与离线规则 | `docs/development-environment.md` |
| 依赖与批准密码路径 | `docs/dependencies/` |
| 生产运维手册（配置参考/安装升级/审计密钥） | `docs/operations/` |
| 需求—代码—测试追踪 | `docs/traceability/requirements-test-matrix.md` |
| 代码注释导览 | `docs/code-guide.md` |
| 工程循环状态 | `loop/`（GOAL/STATE/BACKLOG/DECISIONS/VERIFICATION） |
| 端到端示例 | `examples/`（含运行/核验脚本） |
| 审计链 | `loop/audit-head.json` / `loop/tool-audit.jsonl` |

## 11. 当前状态（2026-08）

- 工程循环：迭代与状态以 `loop/STATE.json` 为准（本快照：iteration 30，BACKLOG 全部 `done`）。
- 能力面：US-0..US-15 全部落地并通过门禁。
- 两条固定编排链均已 E2E 验证：任务下发链与成果回传链（真实 SM2/SM4 加密成果包闭环）。
- 离线自洽：全部门禁、本地服务、工具调用在断网条件下可复现（`make quality`）。
- 性能：参考架构 SLA 与可扩展性探针全部达标（`python scripts/benchmark.py --check`）。
- 版本：`src/coevo/version.py` 集中定义（显式语义版本，禁用时间戳）。

## 12. 交付边界

MVP 已验证“业务智能、分布式离线协同、运行中枢编排”三类最小能力并全部可离线复现。
密码方案已按业务负责人批准落地为开源引擎（GmSSL 3.2.0，Apache-2.0）+ 纯 Python SM3
（GB/T 32905），真实 SM2/SM3/SM4 全链路可用。正式部署仍剩余三项外部条件：

1. 受保护密钥句柄与国密认证模块（长期目标）；
2. 独立审计节点与合规双签复核；
3. Win7 存量环境实机验证。

详见 `loop/DECISIONS.md` 与 `docs/dependencies/approved-crypto-provider-path.md`。
