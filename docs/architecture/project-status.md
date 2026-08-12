# 项目现状总览（Project Status）

> 快照：2026-08-12（全部审查项、工程优化、架构级风险修复与驾驶舱产品化轮次后；
> 供业务负责人作为决策入口）

## 1. 一句话状态

Coevo MVP 的**实现与工程治理已完成**：两位架构师审查的 20 项建议 + 6 项工程优化
+ 架构级风险修复轮次（ARCH-REVIEW-10..15、ENG-OPTIMIZE-7）全部落地，BACKLOG 211 项
全部 done（队列注释另登记 PRODUCT-REVIEW T-01..T-18，见
`docs/plans/review-2026-08-12-tasks.md`），全套件当前状态全绿；
**正式宣告完成（mvp-complete）还差独立双签与业务裁决**。

2026-08-11/12 新增的驾驶舱产品化轮次（已并入上句口径）：
多项目演示视图、网页确认（`--serve-gate`，demo 模式）、会话管理、深链导航、
审计动态与编排轨迹面板；这些仍是演示语义，生产接线任务见 PRODUCT-REVIEW 队列
（T-05/T-08/T-09/T-10）。

## 2. 架构与能力

- 分层：Domain / Application / Ports / Adapters（`ports-adapters.md`）；
- 双模式：受控网络 + 物理隔离离线（`.agent` 加密包）；
- 能力级别：DESIGNED..PRODUCTION_READY/BLOCKED（`capability-status.md`）；
- 双模式范围：MVP 验证离线闭环；受控网络协同为设计态/后续版本范围
  （`online-mode-scope.md`）；
- 架构风险台账：`architecture-risk-ledger.md`（风险 → 处置状态 → 证据 → 责任）；
- 关键契约索引：`docs/README.md`（25+ 份架构契约）。

## 3. 质量与验证

- 门禁：fast（迭代）/ quality（发布），两阶段化（Phase A 结果 JSON → Phase B
  记录），每阶段计数与进度（`gate-tiers.md` / `gate-phases.md`）；
- 当前证据：unit 1528（pass 1525）/ integration 272（pass 271）/ go ok /
  security 103 / e2e 25 / win7 4 全绿；totals discovered=1932 passed=1928
  failed=0；audit fully-sealed（sequence 2486）；quality fingerprint
  `507ff7cb3ed3fd24`；
- 发布前置：`release_check.py`（含 delivery_artifacts + recent_gate）。

## 4. 外部依赖与待批门

见 `external-gates.md`：

| 门禁 | 状态 | 责任 |
|---|---|---|
| US-5-AC-2 正式密码产品 | BLOCKED | 外部审批（最长路径） |
| ARCH-REVIEW-3 MVP 完成裁决 | DECISION-REQUIRED | 业务负责人 |
| ARCH-REVIEW-4/5、REVIEW2-10 独立安全审查 | REVIEW-REQUIRED | 独立审查人 |

## 5. 需要业务负责人裁决（唯一阻塞）

1. **宣告口径**：按"实现满足 GOAL.md 条件 1-10、双签未完成"宣告"实现完成、待独立验收"（推荐），
   还是直接安排独立 mvp-verifier + security-reviewer 双签后再宣告；
2. **独立双签**：安排独立验证/安全审查，或明确豁免并留痕；
3. **外部门顺序**：US-5-AC-2 密码产品审批等处理顺序。

裁决后：解除 `loop/STATE.json` blocked，进入独立验收/试点或正式宣告阶段。
