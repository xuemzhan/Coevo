# 决策记录治理（Decision Records / ADR 索引）

> 状态：生效（2026-08-10，ARCH-REVIEW-8）
> 适用范围：`loop/DECISIONS.md`、`loop/VERIFICATION.md` 与 `loop/archive/` 的记录格式与容量。

## 1. 决策条目结构（ADR 式摘要）

`DECISIONS.md` 主文件只保留**索引式摘要**，每条以 `## <日期> - <ID> <标题>` 开头，
正文按以下段落组织：

- `- Decision:`（一句话决策）；
- `- Rationale:`（理由与事实核验）；
- `- Verification:`（命令指纹/门禁/独立验证证据）；
- `- Boundary:`（不属于本轮/外部依赖/安全审查责任）；
- `- Governance marker check:`（最新条目必须承认私钥句柄治理策略 a+b——既有约定）。

正文细节（完整 diff、长证据、长论证）超过容量策略时进
`loop/archive/<日期>/decisions-<日期>.txt`，由 `archive_records.py` 自动修剪。

## 2. 门禁记录

`VERIFICATION.md` 由 `quality_gate.py` 追加生成并自修剪（Phase B 写回），
人工不直接编辑；历史证据以 `loop/archive/<日期>/verification-<日期>.txt` 为准。

## 3. 纪律

- 决策必须可检索（ID + 日期）、可追溯（验证证据）、可审计（marker）；
- 不在主文件堆砌长正文；正文进归档区；
- 修改归档策略/记录格式必须同步本契约并在 DECISIONS 留痕。

## 4. 守卫测试

`tests/unit/test_arch_review_8_records_governance.py`：本契约存在且含关键字；
最新 DECISIONS 条目包含 governance marker（防止 marker 被丢弃）。
