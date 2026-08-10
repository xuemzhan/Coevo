# 审计日志代际重锚定（Audit Re-anchor）

> 状态：生效（2026-08-10，REVIEW2-10，闭合 DECISIONS 记录的"重锚定未实现"缺口）
> 适用范围：`scripts/audit_seal.py re-anchor` 与 `loop/tool-audit.jsonl` 的归档边界。

## 1. 流程

`python scripts/audit_seal.py re-anchor [--archive-dir DIR]`：

1. **前置校验（fail-closed）**：当前链必须 `fully-sealed`，否则拒绝并保持原状；
2. **归档整代**：把当前 `tool-audit.jsonl` 全部字节写入
   `loop/archive/<date>/audit-generation-<旧序列>-<ts>.jsonl`（原样保留，含摘要）；
3. **新代 genesis**：新日志以一条 `audit_generation` 记录开头——
   `prev_hash = 0*64`（新链起点）、`previous_generation_sha256`（绑定归档代摘要）、
   `previous_generation_line_count`、`previous_head_sequence`；
4. **重置 checkpoint**：`loop/audit-checkpoint.json` 重置为 genesis 行
   （legacy_line_count=0）；
5. **重封缄**：`seal()` 对新代签名新 head；若封缄失败，自动恢复归档前字节并中止。

## 2. 不变性

- **不重写任何既有记录**（代内 append-only 完整性保持）；
- 旧代字节原样归档，其摘要经 genesis 记录与新 head 双重绑定；
- 每一代都是完整可验证的哈希链（`audit_log.verify` + `audit_seal verify`）；
- 重锚定本身经工具审计链留痕（genesis 记录即审计证据）。

## 3. 与通用归档工具的关系

`archive_records.py --apply` 仍**拒绝**触碰 audit 链（fail-closed），并提示使用本流程；
`--check` 对 audit 仅报告不失败。审计链归档只能经 `re-anchor` 专用流程。

## 4. 守卫测试

`tests/unit/test_audit_seal_reanchor.py`：规划校验（行数不足拒绝）、genesis/checkpoint
正确性、新代链可验证（`audit_log.verify == []`）、未封缄时 fail-closed 且不改文件、
archive_records 提示指向本流程。

## 5. 变更纪律

任何改变重锚定语义、genesis 字段或 checkpoint 重置规则的改动，视为审计链安全变更，
需独立安全审查并在 `loop/DECISIONS.md` 留痕。
