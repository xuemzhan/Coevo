# RECORDS-ARCHIVE-2 切片计划：记录归档自动化守卫 + control.pyz 门禁同步

> 状态：已批准（2026-08-08 用户指令"继续"）。本轮为增量门禁 + 全量复核口径。

## 1. 目标工作项

- 工作项：`RECORDS-ARCHIVE-2`（ENG-BASE，dependencies=[QUALITY-ROBUST-1]）。
- 目的：
  a. loop 记录容量守卫：`loop/VERIFICATION.md`（当前约 1.5MB）与
     `loop/DECISIONS.md`（约 577KB）已超过归档策略容量（500KB），但没有任何机制
     在门禁中失败关闭提示归档，记录将持续膨胀；
  b. 消除门禁入口行为分裂：`make quality` 经由 `.tools/control/control.pyz`
     内嵌的**旧版** `quality_gate.py` 运行（无 QUALITY-ROBUST-1 的
     CHILD_TIMEOUT_SECS / 阶段重新封缄 / 归档检查），而
     `python scripts/quality_gate.py` 运行仓库脚本，两者行为不一致。

## 2. 交付

- `src/coevo/records_archive.py`：新增纯函数 `over_policy_size(kind, text) -> bool`
  （或等价 `check_policy`），作为容量阈值的单一事实源（fail-closed）；`POLICY`
  从 `scripts/archive_records.py` 收敛到本模块（消除双份）。
- `scripts/archive_records.py`：新增 `--check` 门禁模式——任一记录文件
  `archive_plan(...).archive` 非空（超容量或有待归档段落）即打印原因并以非零
  退出（fail-closed），提示运行 `--apply`；`--dry-run` 仍为默认。
- `scripts/quality_gate.py`：`TARGETS["lint"]` 追加
  `[sys.executable, str(ROOT/"scripts"/"archive_records.py"), "--check"]`
  （lint 命令集变化 → 门禁指纹变化，记录实际指纹）。
- 重建 `.tools/control/control.pyz`（确定性 ZIP_STORED、sorted 固定条目、
  DOS epoch）：`__main__.py` ← `scripts/control_main.py`；8 个模块 ← 仓库
  `scripts/` 同名文件（audit_log / audit_seal / check_loop_stop / loop_state /
  quality_gate / run_validation / traceability_check / validate_opencode）。
- 全链哈希同步：`docs/dependencies/python-script-lock.tsv`（archive_records /
  quality_gate / control_main 等变更行）、`scripts/tool-shims/make.cs`
  （ScriptInventorySha256 + ControlArchiveSha256）、
  `docs/dependencies/toolchain-lock.json`（control_archive + script_inventory +
  source_sha256）。
- 实际执行 `python scripts/archive_records.py --apply`：把 VERIFICATION.md /
  DECISIONS.md 归档至策略容量内（dry-run 已确认 audit 无归档动作，审计链不动）。
- `docs/modules/root_modules.md` 如有新增模块登记。

## 3. 测试要点

- `tests/unit/test_records_archive.py`：新增容量判定纯函数正反用例（超阈值 /
  阈值内 / 边界 / 非预期 kind 拒绝）。
- `tests/unit/test_quality_gate_lock.py`：断言 lint 命令集包含
  `archive_records.py --check`。
- `scripts/archive_records.py --check`：真实仓库上 exit=0（归档后）；在临时
  复制场景断言超阈值时非零（如可行，否则以纯函数覆盖）。
- 回归：`tests/integration/test_dev_environment_entry.py`、
  `tests/security/test_local_toolchain_security.py`（锁链同步后必须全绿）。
- 验证 control.pyz 重建后：内嵌 `quality_gate.py` 含
  `CHILD_TIMEOUT_SECS` / `stage audit seal` / `archive_records --check`；
  `make lint` 与 `python scripts/quality_gate.py --target lint` 行为一致。

## 4. 完成条件

- 定向测试全绿；`python scripts/quality_gate.py --target fmt` 与
  `--target lint` exit=0（记录新指纹）；
- control.pyz 与仓库脚本同步（内嵌 quality_gate 含本轮与 QUALITY-ROBUST-1
  修复）；`make quality` 入口行为一致；
- VERIFICATION.md / DECISIONS.md 收敛到策略容量内；归档文件落
  `loop/archive/YYYYMMDD/`；tool-audit.jsonl 与审计封缄不变；
- 追溯矩阵新增 `ENG-BASE | RECORDS-ARCHIVE-2` 行（无悬空）；
- security-reviewer 放行（涉及审计记录 / 脚本锁链 / 门禁 fail-closed 语义）。

## 5. 审查门

- security-reviewer：**是**（审计记录归档边界、脚本锁链全链同步、门禁 fail-closed）。
- protocol-reviewer：**否**（不涉及 `.agent` 协议字段）。
