# Coevo — 分布式任务管理具身智能体系统（MVP）

面向跨部门、跨单位、跨专业、长链条复杂任务的全过程管理，以“运行中枢 + 离线任务包 +
本地驾驶舱”的方式实现任务流程理解、结构化分解、团队推荐、安全任务包流转、成果回传与
版本合并、风险预警、决策简报和知识沉淀的离线闭环。

## 当前状态（2026-08）

- 工程循环：迭代与状态以 `loop/STATE.json` 为准（本快照：iteration 30，BACKLOG 全部 `done`）。
- 能力面：US-0..US-15 全部落地（身份与密钥、流程理解、分解、团队推荐、任务包、
  工作区、驾驶舱、进展采集、成果回传、状态合并、风险、督办会议、简报、知识沉淀、审计）。
- 两条固定编排链均已 E2E 验证：任务下发链（`tests/e2e/test_demo_runner.py`）与
  成果回传链（`tests/e2e/test_return_chain.py`，真实 SM2/SM4 加密成果包闭环）。
- 离线自洽：全部门禁、本地服务、工具调用在断网条件下可复现（`make quality`）。
- 性能：参考架构 SLA 与可扩展性探针全部达标（`python scripts/benchmark.py --check`）。

## 快速开始

```powershell
# 进入受控开发环境（锁版本工具链，零联网）
.\scripts\dev.ps1 -Task env-check

# 全量质量门禁（单元/集成/安全/E2E/审计封存）
.\scripts\dev.ps1 -Task quality

# 离线演示闭环（编排链 + 加密任务包 + 驾驶舱 + 知识库 + 审计流）
python scripts\run_demo.py --smoke

# 生产驾驶舱（环回绑定 + 优雅停机）
python scripts\run_cockpit.py --check
python scripts\run_cockpit.py
```

## 生产部署

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

## 文档

| 主题 | 位置 |
|---|---|
| 需求与约束基线 | `docs/requirements/`、`docs/constraints/` |
| 参考架构与选型 | `docs/architecture/` |
| `.agent` 任务包协议 | `docs/protocol/agent-package-protocol.md` |
| 生产可用性说明 | `docs/production-readiness.md` |
| 开发环境与离线规则 | `docs/development-environment.md` |
| 生产运维手册（配置参考/安装升级/审计密钥） | `docs/operations/` |
| 需求—代码—测试追踪 | `docs/traceability/requirements-test-matrix.md` |
| 工程循环状态 | `loop/`（GOAL/STATE/BACKLOG/DECISIONS/VERIFICATION） |

## 交付边界

MVP 已验证"业务智能、分布式离线协同、运行中枢编排"三类最小能力并全部可离线复现。
密码方案已按业务负责人批准落地为开源引擎（GmSSL 3.2.0，Apache-2.0）+ 纯 Python SM3
（GB/T 32905），真实 SM2/SM3/SM4 全链路可用。正式部署仍剩余三项外部条件：受保护密钥
句柄与国密认证模块（长期目标）、独立审计节点与合规双签复核、Win7 存量环境实机验证
（见 `loop/DECISIONS.md` 与 `docs/dependencies/approved-crypto-provider-path.md`）。
