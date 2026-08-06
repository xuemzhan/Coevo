# `merge/` — 状态合并（US-10）

## 定位

以已验证导入 + 权威签名收据为信任边界，做字段级合并决策、项目主版本更新、
签名收据与密封收据 store。禁止仅凭时间戳覆盖（AC-7）。

## 职责边界

- **in scope**：P1 导入绑定校验、P2 去重、AC-3 基线版本核对、P4 决策者白名单、
  字段级 ACCEPT/REJECT/HOLD、签名回执链、SQLite 收据历史；
- **out of scope**：风险分析（`risk/`）、简报（`decision_brief/`）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `FieldMerge`、`MergeDecision`、`MergeProposal`、`MergeRecord`、`MISSING` | 字段合并/提案/记录/哨兵与错误类型 |
| `engine.py` | `MergeEngine.merge/merge_and_commit` | P1→P4 校验 → 逐字段合并 → 提交（HOLD 即拒，回滚拒绝统一助手） |
| `receipt.py` | `build_signed_merge_commit_receipt`、`verify_signed_receipt`、`MergeCommitReceiptStore` | 签名收据 + 密封 store（访问期全量重校验）+ 基线快照冻结 |
| `repository.py` | `MergeReceiptRepository` | SQLite 收据历史 + 签名单调新鲜度锚 + 流式逐行校验（行级门禁） |

## 关键入口与数据流

```
已验证 ImportOutcome + ReportManifest + 当前基线 → MergeEngine.merge
  → 字段级决策（HOLD 即整体拒）→ merge_and_commit
  → 签名收据（冻结基线快照）→ MergeReceiptRepository（连续版本链）→ 风险分析
```

- `MergeEngine.merge()` — 决策者由 `recipient_cert_id` 派生，白名单外拒绝；
- `merge_and_commit()` — 收据链版本连续（跳号即拒绝），失败回滚不留半态；
- `MergeCommitReceiptStore.get/by_project` — 密封语义，每次访问重校验历史。

## 安全与不变量

- **决策者必须来自已验证导入的接收人身份**，且（可选）在项目授权白名单内；
- base_revision 与当前主版本不一致 → HOLD 三方冲突，绝不自动覆盖；
- 收据快照冻结防篡改；收据历史逐行流式校验防超大/畸形行；
- 审计投影排除字段明细，只保留计数与决策者等结构事实。

## 测试覆盖

- `tests/unit/test_merge_engine.py`、`test_merge_engine_v3.py`、
  `test_merge_commit_receipt.py`；
- `tests/security/test_merge_receipt_repository.py`；
- `tests/integration/test_merge_risk_receipt_chain.py`；
- `tests/e2e/test_return_chain.py`。

## 依赖与下游

- **上游依赖**：`protocol`（ImportOutcome）、`report`（ReportManifest）、
  `task_decomposition`（ProjectBaseline）、`identity`（签名权威）；
- **下游消费者**：`risk/`、`decision_brief/`、`knowledge_base/`。

## 错误语义

- `MergeValidationError`：输入契约非法（可用户修正）；`MergeError`：结构不变量
  被破坏（工程缺陷）；两者均失败关闭；
- `MergeCommitReceiptError`：收据构建/校验失败（版本跳号、快照不绑定、签名主体
  不一致等）；
- `MergeReceiptRepositoryError` / `AuditAnchorError`：持久化/锚点失败。
