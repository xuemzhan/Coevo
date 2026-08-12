# 成熟产品视角审查报告 —— 任务拆解（2026-08-12）

> 来源：`docs/process/product-review-2026-08-12.md`（2026-08-12 成熟产品视角
> 审查报告，HEAD `e890be8`、全量门禁 `fingerprint=507ff7cb3ed3fd24` 通过后）。
> 登记方式：按 RECORDS-2 单一在飞不变量，任务以队列注释登记于
> `loop/BACKLOG.yaml`，完整清单以本文档为权威；逐轮进入 loop 时再从队列
> 转为正式条目。

## 1. 拆解原则

- 每个任务是可独立验证的最小切片（规划 → 实现 → 验证）；
- 依赖外部审批/角色（密码产品、独立双签、CI Release）的任务标注
  `[外部依赖]`，不阻塞其余任务；
- P0 决定"产品是什么"；P1 把 demo 语义变成产品语义；P2 负责工程健壮性。

## 2. 任务清单

### P0 —— 产品定位与验收

| ID | 标题 | 范围 | 完成定义 | 依赖 |
|---|---|---|---|---|
| T-01 | AI 定位决策简报 | `config/model-config.json`、`docs/architecture/capability-status.md`、`docs/requirements/`、`README.md`；`loop/DECISIONS.md` 留痕 | 决策记录 + 能力矩阵更新 + README 叙事与实现一致；`test_review2_12_capability_status` 通过 | 无 |
| T-02 | 本地模型建议链路打通（若 T-01 选"接入模型"） | `src/coevo/task_decomposition/agent.py`、`src/coevo/model/openai_compatible.py`、示例配置；新增 E2E | 模型可用路径与离线回退路径均有测试；`external_requests=0` 约束不被破坏 | T-01 |
| T-03 | 独立双签执行 `[外部依赖：独立角色]` | `docs/process/independent-verification-pack.md`；`docs/architecture/external-gates.md` | 两份独立审查报告 + 门禁状态从 `REVIEW-REQUIRED` 关闭 | 独立审查角色 |
| T-04 | 独立验证包核对/更新 | `docs/process/independent-verification-pack.md`、`docs/process/independent-review-governance.md` | 执行包中预期计数/指纹/步骤与现状一致 | 无 |

### P1 —— 产品化接线

| ID | 标题 | 范围 | 完成定义 | 依赖 |
|---|---|---|---|---|
| T-05 | 生产链执行入口契约（ports/adapters） | `src/coevo/app/`（生产 composition root 骨架）、`src/coevo/framework/integration.py`、守卫测试 | 生产入口存在且默认拒绝 demo signer；demo 注入点与生产入口隔离有测试 | 无 |
| T-06 | 生产密码产品接入 `[外部依赖：US-5-AC-2 审批]` | `src/coevo/crypto/`、`src/coevo/identity/`、生产入口 | 生产链使用批准产品；`US-5-AC-2` 门禁关闭 | 外部密码产品审批 |
| T-07 | 审计签名密钥托管方案 | `docs/operations/audit-key-runbook.md`、`scripts/audit_key_health.py` | 方案文档 + 健康检查覆盖新形态；`REVIEW2-10` 前置审查准备就绪 | 无 |
| T-08 | 真实 RBAC / Authorizer 接线 | `src/coevo/framework/policy.py`、`src/coevo/identity/service.py`、编排链接线；越权用例测试 | 无授权角色确认被拒；确认按真实权限判定；安全测试覆盖越权 | T-09 |
| T-09 | 驾驶舱会话绑定用户身份 | `src/coevo/cockpit/sessions.py`、`identity` schema、认证流程 | 会话携带身份；视图按身份过滤；未绑定身份无法确认/驳回 | 无 |
| T-10 | 生产 pending-action 处理器契约 | `src/coevo/cockpit/facade.py`、`server.py`、契约文档 + 守卫测试 | 无处理器 fail-closed 保留；处理器注册路径有文档与测试；demo 与生产语义隔离 | T-08/T-09 |
| T-11 | 中心端同步协议设计 | `docs/architecture/event-model.md`、新增 `docs/architecture/sync-protocol.md` | 设计文档 + 契约测试（字段/版本/重放防护） | 无 |
| T-12 | 中心端同步实现 | `src/coevo/merge/`、新增同步模块、E2E | 双节点对账 E2E；重放/乱序/冲突场景全测 | T-11 |

### P2 —— 工程健壮性

| ID | 标题 | 范围 | 完成定义 | 依赖 |
|---|---|---|---|---|
| T-13 | cockpit-state schema 迁移机制 | `src/coevo/cockpit/state_store.py` + 迁移测试 | schema 版本变更有迁移路径；旧版本状态可升级且不丢数据 | 无 |
| T-14 | identity/merge SQLite 迁移框架 | `src/coevo/identity/schema.sql`、`src/coevo/merge/schema.sql`、迁移工具 + 测试 | 升级路径测试覆盖 schema 增量变更 | 无 |
| T-15 | 门禁指纹环境无关化 | `scripts/quality_gate.py`、`tests/unit/test_arch_review_7_gate_tiers.py`、`test_arch_review_9_win7_gate.py` | 不同工作区路径下指纹稳定；守卫测试不再因环境漂移 | 无 |
| T-16 | 文档快照刷新 | `docs/architecture/project-status.md`、`capability-status.md`、`docs/operations/known-limitations.md` | 文档计数/日期/能力级别与现状一致；文档一致性测试通过 | 无 |
| T-17 | 令牌安全使用指引 | `docs/operations/ops-runbook.md` / `configuration-reference.md` | 文档说明令牌生命周期、复制/分享注意点、会话过期处理 | 无 |
| T-18 | CI 激活 `[外部依赖：owner 建 Release]` | GitHub Release、`docs/operations/ci-artifact-hosting.md` | CI 首次全量门禁绿；制品哈希与 `ci-artifact.json` 一致 | owner 创建 Release |

## 3. 建议执行顺序

```
第一批（无依赖，立即开工）
  T-01 → T-02（若选接入模型）  T-04  T-05  T-09  T-13  T-14  T-15  T-16  T-17

第二批（依赖第一批）
  T-08（依赖 T-09）  T-10（依赖 T-08/T-09）  T-11 → T-12

第三批（外部依赖并行推进）
  T-03（独立角色）  T-06（密码审批）  T-07  T-18（owner）
```

关键路径：T-01（定位）→ T-02（AI 真实化）→ T-05/T-09/T-10（生产接线）→
T-03（独立双签）→ 宣告完成。

## 4. 进度（2026-08-12 第一批）

| 任务 | 状态 | 备注 |
|---|---|---|
| T-01 AI 定位决策简报 | 已定稿（选项 B，可修订） | `docs/plans/ai-positioning-brief.md` + README 澄清句；DECISIONS 12:00 定稿（原 07:00 proposed；业务负责人可修订） |
| T-02 本地模型建议链路 | done（契约测试已具备并复核） | 离线回退/畸形拒绝/草稿边界/不应用边 6 项测试全绿 |
| T-04 独立验证包核对 | done | 刷新基线（指纹/计数/审计 sequence） |
| T-05 生产链执行入口契约 | done | `src/coevo/app/production.py` + 7 项守卫测试（拒绝 demo 组件、校验先于真实链） |
| T-07 审计密钥托管方案 | done | `audit-key-runbook.md` §6：三档托管 + `audit_key_health.py` custody 检查（A/B/C）落地 |
| T-08 真实 RBAC | done | `PolicyAuthorizer`（framework policy 绑定 + fail-closed）+ production 默认授权器 |
| T-09 会话绑定身份 | done | 会话携带 subject（签发绑定、令牌不可反推）+ 健康 subject 计数 + `COEVO_OPERATOR_ID` |
| T-10 生产 pending-action 契约 | done | `PendingActionHandler` Protocol + `docs/architecture/cockpit-confirmation-contract.md` + 注入隔离守卫 |
| T-11 同步协议设计 | done | `docs/architecture/sync-protocol.md` + `src/coevo/sync/contract.py`（信封/版本/顺序/重放防护） |
| T-12 同步实现 | done | `src/coevo/sync/store.py`：SyncOutbox 追加式哈希链 + SyncReconciler 对账 + 文件包导出/导入（离线优先） |
| T-13 cockpit-state 迁移 | done | schema 1.0→1.1 显式迁移注册表 + 4 项新测试 |
| T-15 门禁指纹环境无关 | done | 指纹按仓库相对路径归一（`b5c12e15ae7c559f`），跨工作区稳定 |
| T-16 文档快照刷新 | done | project-status / capability-status / known-limitations |
| T-17 令牌安全指引 | done | ops-runbook §2.2.1 |
| T-14 DB 迁移框架 | done | `src/coevo/db_migration.py` + merge 仓库接入（1.0 空迁移） |
| T-03 独立双签 | pending（执行包就绪） | 独立 mvp-verifier + security-reviewer；基线已修正（实际 507ff7 / 预期 b5c12e） |
| T-06 生产密码接入 | pending（前置就绪） | `GmsslProtectedProvider` 已声明 APPROVED_PRODUCT scope，生产入口兼容；待 US-5-AC-2 审批 |
| T-18 CI 激活 | pending（CI 就绪） | workflow 无指纹钉、恢复脚本按 SHA-256 失败关闭；待 owner 建 Release 上传制品 |
