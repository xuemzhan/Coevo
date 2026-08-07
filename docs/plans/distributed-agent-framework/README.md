# 分布式具身智能体框架（CTAF）— 设计索引

> 本目录汇总"分布式具身智能体框架"的当前版本与历史快照。所有文档遵守
> `docs/constraints/mandatory-technical-constraints.md` 与 AGENTS.md 的
> 强制边界。

## 当前文件

| 文件 | 版本 | 状态 | 摘要 |
| --- | --- | --- | --- |
| `design-proposal.md` | **v0.4.1** | **产品级 + 工程级双一致蓝图（v0.4 + 审查修复，推荐作为实施基线）** | 在 v0.4 基础上以业务负责人 + 产品经理视角吸收审查修复 15 项（P0 5 + P1 5 + P2 5，见 §19.6）；累计 53 条 net new；自评 4.95/5（待独立复核） |
| `design-proposal-v0.3.md` | v0.3 | 历史 | 引入 Policy 抽象 + A2A policy_ref 三段绑定 |
| `design-proposal-v0.2.md` | v0.2 | 历史 | 占位 |

## v0.4 vs v0.3 关键变化（一图速览）

| 维度 | v0.3 | v0.4 |
| --- | --- | --- |
| 内部一致性 | 3.5（v0.3 隐藏） | **5.0**（A 类 12 条全部修） |
| 章节 | 19 章 | **仍 19 章，内容大幅重写** |
| 抽象 | 6 抽象 | **6 抽象 + Plan/Policy 数值字段拆分**（A1） |
| Manifest | §5.1 草案 + §5.2 闭集 | **+ §5.3 manifest-checker 输入输出契约 + T1..T6** |
| Plan 五项不变量 | 单行说明 | **+ 三时机表（构造/注册/dispatch）**（A2） |
| OrchestrationEngine | 4 方法 | **+ validate_plan 前置**（A9） |
| ESCALATED 出口 | 3 种（含直跳 ACTIVE） | **3 种全部经 HELD 中转**（A10 + L19） |
| 红线 | L9..L17 | **L9..L19（11 条，新增 L18/L19）** |
| 威胁矩阵 | 13 行 | **15 行**（+Plan 数值错位 + ESCALATED 直跳） |
| 路线图 | 估时表 | **+ 风险点 + 进度锚 + 延长触发器**（A3） |
| M1 | 4 周（混合项） | **M1a + M1b 各 2 周**（A4） |
| 依赖图 | ASCII | **Mermaid**（B11） |
| ROI | 单边 | **量化区间 + baseline + 付费节点 M2/M5/M7**（A7） |
| 业界对比 | 单边 | **双向比较 + 下游合作**（A5） |
| 术语 | explore-then-execute | **discrete-execute + fail-up**（A12） |
| Hero Statement | 87 字 | **30 字版 + 完整版**（B1） |
| 红线 P4 | 缺文件映射 | **+ manifest-checker 引用**（B4） |
| Policy | 开放字段 | **+ 4 个默认 Profile 模板**（B6） |
| policy_ref 验证 | JSON 示例 | **+ 五步验证时序**（B7） |
| §8.2 表 purpose 列 | 措辞不准 | **重命名为"对应风险"**（B8） |
| §11.1 指标 | 缺业务涵义 | **+ 业务涵义列**（B10） |
| 反方 FAQ | 缺 | **§2.4 新增 6 条**（A6） |
| README 待补充主题表 | 单向 | **含 M1-M9 + T1-T5**（A11） |

完整修订追踪见 `design-proposal.md` §19。

## 评审入口（v0.4 视角）

| 视角 | 必看章节 | 重点 |
| --- | --- | --- |
| **业务负责人** | §1 / §2.4 / §15.3 / §16 全部 / §17 / §18.2 | ROI 区间 + 反方 FAQ + 双向比较 |
| **架构师** | §5.3 / §6.4 / §6.6 / §7.3.3 / §8.3-4 / §14 | 输入输出契约 + 三时机 + 时间盒 |
| **安全审查** | §6.4.1 / §12.2 / §13 表 | 五项不变量 + L9/L18/L19 |
| **产品经理** | §2.4 / §15.3 / §16.5 / §16.6 | FAQ + 量化 ROI + 双向比较 + 业务触点 |
| **协议工程师** | §7.3.2 / §7.3.3 | policy_ref 三段绑定 + 五步验证 |
| **运维** | §8 / §11 / §14.2 / §14.3 | 八态 + SLA + 时间盒 + 依赖图 |
| **财务** | §15.1 / §15.2 / §15.3 | FTE 配置 + 成本项 + ROI |
| **市场** | §1 / §2 / §16 | Hero + 用户画像 + Hero / 电梯 / 术语 |

## v0.4 累计审查吸收情况

| 阶段 | 文档版本 | 来源 | 净新增审查结论 |
| --- | --- | --- | --- |
| v0.1 → v0.2 | v0.2 | 自评 + 第一轮审查 | **+17 条**（M1..M5 + S1..S5 + O1..O12 部分 + ST1..ST3） |
| v0.2 → v0.3 | v0.3 | 架构师 + 分析师第二轮 | **+9 条**（A1..A6 + A11 + IN4 + IN5） |
| v0.3 → v0.4 | v0.4 | 架构师 + 分析师 + 产品经理第三轮 | **+12 A + 7 B = 19 条**（A1..A12 + B1/B4/B6/B7/B8/B10/B11） |
| v0.4 → v0.4.1 | v0.4.1 | 业务负责人 + 产品经理批判性吸收 | **+15 项修复/补强**（P0 5 + P1 5 + P2 5，详见 design-proposal §19.6） |
| **累计** | — | — | **60 条**（含迭代交叉）/ **53 条 net new** |

> 注：详见 v0.4 §19.4 累计口径统一表（解决"26 vs 38 vs 45"分歧）。

## 备份（历史快照已留档）

- `design-proposal-v0.3.md` 完整 v0.3 历史快照（2026-08-07 从 git 历史恢复，内容同时并入 v0.4 §19.1/§19.4 修订追踪）
- `design-proposal-v0.2.md` 占位

## 待补充文档（按 M1..M9 排期）

| 主题 | 负责模块 | 里程碑 | 测试要求 | 估算 |
| --- | --- | --- | --- | --- |
| `manifest-checker.md` | `src/coevo/framework/manifest/` | **M1a (2 周)** | T1..T6 | 2 周 |
| `capability-closedset.md` | `src/coevo/framework/capability.py` | **M1b（已交付 2026-08-08，US-16-AC-3）** | 与 `AgentCapability` 双向一致 + CRYPTO_PROXY approved scope | 2 周 |
| `policy-template.md` | `src/coevo/framework/policy/` | M2 (4 周) | 4 个 Profile 模板 + validate_plan | 4 周 |
| `memory-interface.md` | `src/coevo/framework/memory.py` | **M3（已交付 2026-08-08，US-16-AC-4）** | bridge 与 `progress_capture/` / `knowledge_base/` 兼容 + L12 脱敏 | 6 周 |
| `tool-registry.md` | `src/coevo/framework/tools/` | M4 (8 周) | MCP 路径 A 一致性 ≥ 99% | 8 周 |
| `a2a-protocol.md` | `src/coevo/a2a/` | M5 (6 周) | protocol-reviewer 审批 | 6 周 |
| `plan-lsp.md` | `src/coevo/framework/plan/` | M6 (10 周) | 五项不变量 + L18 字段检查 | 10 周 |
| `hybrid-orchestrator.md` | `src/coevo/framework/orchestrator/` | M7 (12 周) | e2e 闭环 | 12 周 |
| `cross-org-validation.md` | 演练手册 | M8 (14 周) | 跨网 + 跨组织 | 14 周 |
| `k8s-crd-listing.md` | 纸面清单生成器 | M9 (8 周) opt-in 沙箱 | 与 K8s 解耦 | 8 周 |

## 业务负责人审阅清单（建议逐项签字）

- [ ] §1.1 一句话（30 字）适合客户卡片
- [ ] §2.4 反方 FAQ 已被售前覆盖
- [ ] §15.3 ROI 区间符合市场 baseline
- [ ] §16.5 双向比较能站得住（对方反驳有回应）
- [ ] §16.6 业务触点映射能用于文档发布
- [ ] §17 风险表没有遗漏（与 §13 威胁矩阵对应）
- [ ] §18.2 自评 4.95/5 经独立复核（不是 PR 文案）

## 审阅流程建议

1. **业务负责人** 读 §1 / §2.4 / §15 / §16 → 拍板
2. **架构师** 读 §5.3 / §6 / §7.3 / §8 / §14 → 评估可实施性
3. **安全审查** 读 §6.4.1 / §12 / §13 → 评估合规
4. **三方汇合** → DECISIONS.md 留痕
5. **启动 M1a 切片**：manifest-checker + 6 项测试（含 T6 wire 回归）

---

> **结论**：v0.4.1 是"产品级 + 工程级双一致"方案。在 v0.4 基础上由业务负责人 + 产品经理批判性吸收审查结论（P0 5 + P1 5 + P2 5 共 15 项修复/补强，详见 design-proposal §19.6），并明确暂缓/拒绝项。从 v0.1 评审到 v0.4.1，累计 53 条 net new 结论全部落地，自评 4.95/5（待独立复核），可作为 M1..M9 实施基线。
>
> **v0.4.1 之后不再频繁大改**：仅在 v0.5（v0.4.1 BACKLOG 全部完成或新外部约束触发）时聚合演进。
