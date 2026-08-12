# 外部依赖与待批门登记（External Gates）

> 状态：生效（2026-08-10，ARCH-REVIEW-3 可落地部分）
> 用途：把"依赖外部审批/独立审查/业务决策"的门禁显式登记，防止隐式消失。

## 登记表

| 门禁 ID | 类型 | 当前状态 | 责任/下一步 |
|---|---|---|---|
| US-5-AC-2 | 外部审批 | `BLOCKED` | 正式 SM2/SM4 密码产品（受保护密钥句柄）审批；批准后接入 GmsslProtectedProvider 生产路径 |
| ARCH-REVIEW-3 | 业务决策 | `DECISION-RECORDED` | 按推荐口径记录"实现完成、待独立验收"（2026-08-10）；若业务负责人另有裁决以新裁决为准 |
| mvp-complete 条件 11 | 独立验收 | `PASS`（2026-08-12 双签放行） | 独立 mvp-verifier（沙箱守卫 violations=[]；主树全量门禁 exit=0 fingerprint=`b5c12e15ae7c559f`，totals 2017/2013/0/4）+ security-reviewer（pass，无阻断项）；审查记录见 loop/DECISIONS.md 2026-08-12T14:00:00Z / T14:30:00Z |
| ARCH-REVIEW-4 | 独立安全审查 | `PASS`（2026-08-12） | 7 个专业子智能体 Manifest 目录（能力闭集/服务模块/人工确认点/工具策略）独立安全审查通过；守卫测试全绿 |
| ARCH-REVIEW-5 | 独立安全审查 | `PASS`（2026-08-12） | 审计签名密钥轮换/恢复手册 + `audit_key_health.py` 全项 ok（含 custody A/B/C）；T-07 三档托管已落地 |
| REVIEW2-10 | 独立安全审查 | `PASS`（2026-08-12） | audit re-anchor 流程独立安全审查通过（fail-closed + 5 项守卫测试全绿） |
| CTAF-PROPOSAL-REVIEW | 独立架构评审 | `PASS`（2026-08-12） | `docs/plans/distributed-agent-framework/design-proposal.md` v0.4.1 独立架构评审通过：内部一致（ARCH-REVIEW-18 守卫）、与已实现框架对齐、边界诚实，可作为 M1..M9 实施基线 |

## 纪律

- 任何进入 `PRODUCTION_READY` 的能力必须先关闭对应门禁（外部审批 / 独立审查 / 业务决策）；
- 门禁状态词汇：`REVIEW-REQUIRED`（待执行）/ `PASS`（已放行，标注日期与证据）/
  `BLOCKED`（外部阻塞）/ `DECISION-RECORDED`（决策已记录）；
- 门禁不得被"全量门禁全绿"掩盖——它们独立于质量门禁存在；
- 门禁全景与架构级风险以 `architecture-risk-ledger.md` 台账为唯一对照表；
- 状态变更必须经 `loop/DECISIONS.md` 留痕。

## 守卫测试

`tests/unit/test_arch_review_3_external_gates.py`：登记表存在、US-5-AC-2 标注
BLOCKED、ARCH-REVIEW-3 标注 DECISION-RECORDED、门状态词汇含 REVIEW-REQUIRED、
四个独立审查门（mvp-complete 条件 11 / ARCH-REVIEW-4 / ARCH-REVIEW-5 /
REVIEW2-10 / CTAF-PROPOSAL-REVIEW）已标注 PASS（2026-08-12）、capability-status
契约引用本表。
