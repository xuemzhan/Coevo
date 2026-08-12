# 能力状态矩阵（Capability Status Matrix）

> 状态：生效（2026-08-12，REVIEW2-12 快照已随 08-11/12 驾驶舱产品化轮次刷新；
> 与 ARCH-REVIEW-3 范围治理关联）
> 用途：把 BACKLOG 的 "done" 语义与能力生产成熟度解耦，杜绝
> "全量门禁全绿，因此系统完成"的过度叙事。

## 1. 能力级别

| 级别 | 含义 |
|---|---|
| `DESIGNED` | 方案/契约已定，尚无实现 |
| `MODELED` | 领域模型与类型已落地（含校验） |
| `UNIT_VERIFIED` | 单元测试全绿（含异常/重放/越权） |
| `INTEGRATION_VERIFIED` | 与真实存储/真实链路/相邻模块集成验证通过 |
| `E2E_VERIFIED` | 端到端真实流程跑通（含离线/真实密码原型） |
| `PROTOTYPE` | 依赖原型实现（如 GmSSL 原型、WPS 真实宿主），尚未生产化 |
| `PRODUCTION_READY` | 独立安全审查放行 + 批准密码/密钥生命周期 + 部署验证完成 |
| `BLOCKED` | 依赖外部审批/决策（如 US-5-AC-2 正式密码产品） |

**规则**：BACKLOG 的 `done` 只表示"该切片完成"；能力当前级别必须单独声明。
进入 `PRODUCTION_READY` 前必须满足完成定义（独立验证 + 独立安全审查 + 批准产品）。

## 2. 当前能力状态（2026-08-12 快照）

| 能力 | 当前级别 | 主要证据 / 缺口 |
|---|---|---|
| US-0 身份与密钥 | `INTEGRATION_VERIFIED` / `PROTOTYPE` | 真实 CNG 集成；密钥初始化/轮换/恢复为 PROTOTYPE（REVIEW2-5 前项） |
| US-1 流程理解 | `E2E_VERIFIED` | 下发链 e2e + 单元 27 项 |
| US-2 任务分解 | `INTEGRATION_VERIFIED` | 基线/依赖图/编辑全测试 |
| US-3 人才推荐 | `INTEGRATION_VERIFIED` | 脱敏模型 + 确定性推荐；真实人才库适配待接入 |
| US-4 运行中枢 | `E2E_VERIFIED` | 真实链（real chain）+ 固定编排链 e2e |
| US-5 `.agent` 协议 | `E2E_VERIFIED`（原型密码）/ `BLOCKED`（生产） | wire/导入/回传 e2e 全绿；正式 SM2/SM4 产品待 US-5-AC-2 审批 |
| US-6 工作区 | `INTEGRATION_VERIFIED` | 路径策略/隔离/原子导入 |
| US-7 本地驾驶舱 | `E2E_VERIFIED`（HTTP/离线前端）；WPS 真实进程 `INTEGRATION_VERIFIED` | 黑盒认证矩阵 + 离线断网证明；多项目/网页确认（demo 模式）/会话管理已落地；会话 subject 绑定（T-09）、PolicyAuthorizer（T-08）、PendingActionHandler 契约（T-10）已接线，生产处理器待批准密码产品后注入；WPS 需真实宿主验收 |
| US-8 进展采集 | `INTEGRATION_VERIFIED` | watcher + 证据关联 |
| US-9 成果回传 | `INTEGRATION_VERIFIED` | 报告包 wire 一致性 |
| US-10 状态合并 | `INTEGRATION_VERIFIED` | 合并收敛 property + 收据链 |
| US-11 风险预警 | `INTEGRATION_VERIFIED` | 四类风险 + 传染推断 |
| US-12 督办/会议 | `INTEGRATION_VERIFIED`（回传链 E2E 覆盖协调步骤） | 回传链 e2e 含督办/会议协调（真实加密包闭环）+ 驾驶舱 SUPERVISION_VIEW 路由（unit/integration）+ demo 注册 agent.supervision_meeting；正式会议调度/正式督办发送仍须负责人确认 |
| US-13 决策简报 | `INTEGRATION_VERIFIED` | DOCX 模板受控 + 权威收据绑定 |
| US-14 知识沉淀 | `INTEGRATION_VERIFIED` | SQLite 持久化 + 密级检查 |
| US-15 安全审计 | `E2E_VERIFIED`；归档重锚定 `PROTOTYPE`（REVIEW2-10 后可用、待独立审查） | 哈希链+签名 fully-sealed |
| US-16 框架层（CTAF） | `INTEGRATION_VERIFIED` | manifest/policy/plan/hybrid/k8s 清单全测试 |
| 中心端持久化/跨节点同步 | `DESIGNED` / `MODELED` | 显式事件模型（REVIEW2-8）已建模；真实同步协议待接入 |
| 生产密码能力 | `BLOCKED` | US-5-AC-2 外部审批 |
| 生产部署（安装/升级/回滚） | `PROTOTYPE` | 安装器存在；生产验收待做 |

## 3. 叙事纪律

- 不得使用"全量门禁全绿，因此系统完成"；正确表述为"切片 done + 能力级别 X"；
- 报告/README 的能力声明必须引用本矩阵的级别；
- 外部依赖/待批门与架构级风险以 `architecture-risk-ledger.md` 台账为对照
  （与 `external-gates.md` 一致）；
- BACKLOG 新增字段（如 `capability_level`）的正式采用，并入 ARCH-REVIEW-3 范围治理
  裁决（本矩阵为先行契约）。
- 进入 `PRODUCTION_READY` 前必须先关闭 `docs/architecture/external-gates.md`
  中的对应门禁（外部审批 / 独立安全审查 / 业务决策）。

## 4. 守卫测试

`tests/unit/test_review2_12_capability_status.py`：级别闭集完整、US-0..US-16 全覆盖、
README 无过度叙事短语并引用本矩阵、文档明确"done=切片完成"。
