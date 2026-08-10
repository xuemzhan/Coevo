# 外部依赖与待批门登记（External Gates）

> 状态：生效（2026-08-10，ARCH-REVIEW-3 可落地部分）
> 用途：把"依赖外部审批/独立审查/业务决策"的门禁显式登记，防止隐式消失。

## 登记表

| 门禁 ID | 类型 | 当前状态 | 责任/下一步 |
|---|---|---|---|
| US-5-AC-2 | 外部审批 | `BLOCKED` | 正式 SM2/SM4 密码产品（受保护密钥句柄）审批；批准后接入 GmsslProtectedProvider 生产路径 |
| ARCH-REVIEW-3 | 业务决策 | `DECISION-RECORDED` | 按推荐口径记录"实现完成、待独立验收"（2026-08-10）；若业务负责人另有裁决以新裁决为准 |
| mvp-complete 条件 11 | 独立验收 | `REVIEW-REQUIRED` | 独立 mvp-verifier + security-reviewer 双签（执行包见 docs/process/independent-verification-pack.md） |
| ARCH-REVIEW-4 | 独立安全审查 | `REVIEW-REQUIRED` | 子智能体 Manifest 目录生产采用前独立安全审查 |
| ARCH-REVIEW-5 | 独立安全审查 | `REVIEW-REQUIRED` | 审计签名密钥轮换/恢复生产执行前独立安全审查 |
| REVIEW2-10 | 独立安全审查 | `REVIEW-REQUIRED` | audit re-anchor 生产使用前独立安全审查 |

## 纪律

- 任何进入 `PRODUCTION_READY` 的能力必须先关闭对应门禁（外部审批 / 独立审查 / 业务决策）；
- 门禁不得被"全量门禁全绿"掩盖——它们独立于质量门禁存在；
- 状态变更必须经 `loop/DECISIONS.md` 留痕。

## 守卫测试

`tests/unit/test_arch_review_3_external_gates.py`：登记表存在、US-5-AC-2 标注
BLOCKED、ARCH-REVIEW-3 标注 DECISION-RECORDED、mvp-complete 条件 11 标注
REVIEW-REQUIRED、capability-status 契约引用本表。
