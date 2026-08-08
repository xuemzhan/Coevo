# RECORDS-HYGIENE-1 切片计划：DECISIONS 时间序整理与守卫

> 状态：已批准（2026-08-08 用户指令"继续优化，不做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`RECORDS-HYGIENE-1`（ENG-BASE，dependencies=[]）。
- 目的：`loop/DECISIONS.md` 的段落存在 9 处日期倒序违规（历史遗留 + 本会话早期
  apply_patch 歧义上下文插入），影响"最新段治理标记"测试与归档 keep-last-N 语义；
  本轮按日期稳定排序整理，并新增时间序守卫防止复发。

## 2. 交付

- `loop/DECISIONS.md`：按段落头 `## YYYY-MM-DD...` 日期**稳定排序**（同日期保持
  原相对顺序；前导 `# Loop 决策记录` 保留在文件头）；内容逐字节保留，仅重排。
- 新增守卫测试（并入 `tests/unit/test_records_archive.py`）：
  `test_decisions_sections_are_chronologically_ordered`——所有段落日期非递减、
  头可解析；防止后续追加再引入倒序。
- 核对：最新段（排序后 = 最新日期段，即 FRAMEWORK-OPTIMIZE-16 收口）仍携带
  治理标记（既有 `test_decisions_records_the_audit_corpus_status` 钉住）。

## 3. 测试要点

- 守卫测试（新）：DECISIONS 全段落日期非递减；
- 既有标记测试：最新段治理标记通过；
- 回归：`tests/unit/test_records_archive.py` 全部（含 archive_plan）、
  `tests/unit/test_traceability_check.py`、`archive_records.py --check`。

## 4. 完成条件

- 定向测试全绿；fmt + lint exit=0；`archive_records.py --check` exit=0；
- DECISIONS 段落数与排序前一致（无丢段），9 处倒序清零；
- 追溯矩阵新增 `ENG-BASE | RECORDS-HYGIENE-1` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**否**（纯记录整理 + 守卫，不涉及代码/密钥/审计链）；
  protocol-reviewer：**否**。
