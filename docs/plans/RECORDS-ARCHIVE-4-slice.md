# RECORDS-ARCHIVE-4 切片计划：门禁自维护 VERIFICATION 归档（自愈容量）

> 状态：已批准（2026-08-08 用户指令"继续进行优化，不用做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`RECORDS-ARCHIVE-4`（ENG-BASE，dependencies=[RECORDS-ARCHIVE-3]）。
- 目的：VERIFICATION.md 由门禁每次追加而增长（当前 498KB，已逼近 500KB 策略阈值），
  超阈后 lint 的 `archive_records --check` 会失败并强制人工 `--apply`。本轮让门禁在
  追加记录后**自维护**：复用 RECORDS-ARCHIVE-2/3 的归档工具对 verification/decisions
  就地裁剪（audit 仍被 RECORDS-ARCHIVE-3 排除），使记录始终有界且无需人工介入；
  decisions/audit 的失败关闭强制语义不变。

## 2. 交付

- `scripts/quality_gate.py`：
  * 新增 `_trim_records_to_policy(verification=VERIFICATION) -> str`：在 VERIFICATION
    追加后调用 `python scripts/archive_records.py --apply`（复用既有工具，audit 排除），
    返回裁剪摘要（无动作返回空串）；失败隔离（trim 失败不使门禁失败，由下一次
    lint --check 兜底）；
  * VERIFICATION 追加后执行自维护，并把 trim 摘要追加一行到 VERIFICATION；
- 重建 `.tools/control/control.pyz`（quality_gate 内嵌变化：ZIP_STORED + sorted +
  DOS epoch）；全链哈希同步（python-script-lock.tsv / make.cs
  ScriptInventorySha256+ControlArchiveSha256 / toolchain-lock
  control_archive+script_inventory+source_sha256）。
- `docs/process/records-archiving-policy.md`：补充"门禁自维护 verification 容量"说明。

## 3. 测试要点

- `tests/unit/test_quality_gate_lock.py`（或新用例）：
  * `_trim_records_to_policy` 调用 `archive_records.py --apply`（mock subprocess.run，
    断言 argv 与成功路径返回空串）；
  * 有裁剪动作时返回摘要（mock 输出含 "-> wrote"）；
  * trim 失败（非零退出/异常）不抛错、返回提示串；
  * control.pyz 内嵌 quality_gate 含 `_trim_records_to_policy`。
- 实测：真实仓库上运行一次 `_trim_records_to_policy()`（当前记录在容量内）返回空串，
  tool-audit.jsonl 字节不变、audit fully-sealed。

## 4. 完成条件

- 定向测试全绿；`python scripts/quality_gate.py --target fmt` 与 `--target lint`
  exit=0（记录新指纹）；`archive_records.py --check` exit=0；
- VERIFICATION 追加+自维护后仍 ≤ 策略容量；audit 链不动；
- 追溯矩阵新增 `ENG-BASE | RECORDS-ARCHIVE-4` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**是**（门禁/记录/审计链交互，须确认 audit 仍不可被触碰、
  trim 失败隔离不绕过 --check）；protocol-reviewer：**否**。
