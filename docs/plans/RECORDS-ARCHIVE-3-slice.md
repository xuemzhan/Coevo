# RECORDS-ARCHIVE-3 切片计划：审计链归档安全（audit 种类防裁剪）

> 状态：已批准（2026-08-08 用户指令"继续进行优化，不用做全量门禁"）。本轮增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`RECORDS-ARCHIVE-3`（ENG-BASE，dependencies=[RECORDS-ARCHIVE-2]）。
- 目的：关闭 RECORDS-ARCHIVE-2 独立安全审查的 Medium 1——
  `scripts/archive_records.py --apply` 对 audit 种类（`loop/tool-audit.jsonl`）同样生效，
  未来 audit 超过 POLICY（2000 行 / 5MB）时会被裁剪，而裁剪会破坏审计链封缄
  （`audit_seal verify` → "audit tail deletion detected"），且当前没有重新锚定/重链流程。

## 2. 交付

- `src/coevo/records_archive.py`：
  * 保留 `POLICY`（三种类阈值，作为策略表文档化）；
  * 新增 `ARCHIVABLE_KINDS = ("verification", "decisions")` 单一事实源——
    audit 种类**不属于**通用归档工具可操作范围（无重锚定流程）；
  * `over_policy_size` 保持对三种类通用（纯指标，供监控/审计使用）。
- `scripts/archive_records.py`：
  * `--check` / `--apply` 只处理 `ARCHIVABLE_KINDS`（verification/decisions）；
  * 若 audit 超策略：打印显式提示"audit 归档需专用重锚定流程（未实现），本工具拒绝
    触碰 tool-audit.jsonl"，且 `--apply` 失败关闭（非零退出），绝不裁剪审计链；
  * 防御性守卫：循环内 `assert kind in ARCHIVABLE_KINDS`（防止未来误加 audit 种类）。
- `docs/process/records-archiving-policy.md`：明确 audit 归档不在通用工具范围内，
  审计链只增不改，超容量时以 `audit_key_health` / 封缄验证为准，重锚定流程为后续工作项。
- 全链哈希同步：`docs/dependencies/python-script-lock.tsv`（archive_records.py 行）、
  `scripts/tool-shims/make.cs`（ScriptInventorySha256）、
  `docs/dependencies/toolchain-lock.json`（script_inventory + source_sha256）。
  control.pyz 不涉及（archive_records.py 不在 control 内嵌模块清单）。

## 3. 测试要点

- `tests/unit/test_records_archive.py`：
  * `ARCHIVABLE_KINDS == ("verification", "decisions")`（audit 不在列）；
  * `over_policy_size("audit", ...)` 仍可用（纯指标不删）；
  * CLI 循环仅处理可归档种类（注入临时 FILES 或直接断言常量为单一事实源）；
  * audit 超策略时 `--apply` 拒绝（非零）且不写任何文件（子进程级测试或纯函数级）。
- `tests/security/test_audit_seal.py`：回归——执行归档流程后审计链仍 fully-sealed
  （或等价断言 tool-audit.jsonl 字节不变）。
- 定向回归：`tests/unit/test_quality_gate_lock.py`（lint 含 archive --check 不变）。

## 4. 完成条件

- 定向测试全绿；`python scripts/quality_gate.py --target fmt` 与 `--target lint` exit=0
  （记录新指纹；lint 含 archive_records --check 应 exit=0）；
- `python scripts/archive_records.py --check` exit=0（当前记录均在容量内）；
- 运行 `--apply` 后 tool-audit.jsonl 字节不变、`audit_seal verify` 仍 fully-sealed；
- 追溯矩阵新增 `ENG-BASE | RECORDS-ARCHIVE-3` 行（无悬空）；
- 安全审查结论更新：RECORDS-ARCHIVE-2 遗留 Medium 1 关闭（audit 不再可被通用归档触碰）。

## 5. 审查门

- security-reviewer：**是**（审计链完整性相关）；protocol-reviewer：**否**。
