# US-8-AC-1 Slice Plan: progress capture service facade

> Loop-engineer PLAN 阶段产物, 2026-07-31.
> 对应 BACKLOG items[US-8-AC-1].test_progress_capture.
> 本切片遵守 AGENTS.md §1 文档优先级与 §2 七阶段; 不修改 .agent wire, 不修改
> 密码方案, 不修改既有模块。

## 1. 用户故事与 AC

US-8: "本地任务状态和成果证据识别"
1. 系统能够识别工作区中的文档和成果变化;
2. 提取已完成工作、未完成工作、下一步计划和存在问题;
3. 每项进展关联相应成果证据;
4. 显示信息来源和置信度;
5. 用户可以修改或驳回识别结果;
6. 正式任务状态必须由用户确认;
7. 不得仅根据文件修改时间判断任务完成;
8. 确认后可生成成果汇报数据。

## 2. 切片范围

### 2.1 新增模块

- `src/coevo/progress_capture/__init__.py` (≤ 1000 行; 与 US-11/12/13 单文件巨型模块风格一致)
- `tests/unit/test_progress_capture.py` (≥ 12 测试)

### 2.2 不修改

- 既有 `src/coevo/workspace/`, `src/coevo/report/`, `src/coevo/task_flow/` 等任何模块
- `.agent` wire, US-5 / US-9 / US-10 wire layout
- `loop/audit-head.json`, `loop/audit-head.p7s`, `loop/audit-signing.json`
- `scripts/store_private_key.ps1` 与 `src/coevo/identity/private_keys.py`
- `toolchain-lock.json` (无新增依赖)
- `.opencode/plugins/loop-guard.ts`

### 2.3 协议/密码边界

- 不修改 .agent wire → 不需要 protocol-reviewer
- 不修改密码/密钥/权限/审计 → 不需要 security-reviewer
- 单元测试覆盖 AC-6 / AC-7 fail-closed 边界 (作为"已覆盖"留痕, 不强制调 security-reviewer)

## 3. 数据模型

```text
EvidenceKind          (Enum, closed set, fail-closed)
  EXPLICIT_USER_TEXT    -- 用户文本反馈 (AC-7)
  DOCUMENT_CONTENT      -- 文档内容变更 (AC-1/AC-7)
  ARTIFACT_FILE         -- 已有成果文件 (AC-1/AC-3)
  TASK_DEPENDENCY_RESOLVED  -- 依赖前置任务完成 (AC-2)

ProgressItemStatus    (Enum)
  PROPOSED              -- 默认, 模型/采集器输出
  ACCEPTED              -- 用户确认
  REVISED               -- 用户修改
  REJECTED              -- 用户驳回

ProgressItem
  item_id                -- "pc.<workspace.project_id>.<task_id>.<index>"
  workspace              -- WorkspaceEntry (US-6)
  task_id                -- 显式给, 服务层不做自动识别
  kind                   -- COMPLETED | PENDING | NEXT_STEP | BLOCKER (AC-2)
  text                   -- 进展描述
  source_kind            -- EvidenceKind (AC-4)
  source_ref             -- str (定位: document path / feedback id / artifact path)
  confidence             -- float ∈ [0.0, 1.0] (AC-4)
  evidence_refs          -- tuple[EvidenceRef, ...] (AC-3, ≥ 1)
  status                 -- ProgressItemStatus (默认 PROPOSED)
  overrides              -- tuple[ItemOverride, ...] (AC-5, 默认空)
  created_at             -- ISO-8601 UTC 'Z'

EvidenceRef
  path                   -- 相对工作区路径
  role                   -- "document" | "feedback" | "artifact" | "dependency"
  media_type             -- 已知 mime / "text/plain"
  digest_hex             -- 64 字符 lowercase hex (与 US-9 ReportArtifact 一致)
  size_bytes             -- int ≥ 0

ItemOverride
  target_path            -- "text" | "kind" | "confidence" | ...
  original_value
  edited_value
  reason
  edited_at              -- ISO-8601 UTC 'Z'

ProgressCapture
  schema_version          -- "1.0"
  capture_id              -- "pc.<workspace.project_id>.<task_id>.<seq>"
  workspace               -- WorkspaceEntry
  progress_items          -- tuple[ProgressItem, ...]
  requires_user_confirmation  -- 恒为 True (AC-6)
  formally_accepted       -- 恒为 False 直到 accept() 被调用
  accepted_at             -- "" 默认, accept() 后填
  accepted_by             -- "" 默认
  created_at              -- ISO-8601 UTC 'Z'

ProgressCaptureError           -- 基类
ProgressCaptureValidationError -- 字段错 (用户可修)
ProgressCaptureConflictError   -- 操作冲突 (例如对 REJECTED 项 accept)
```

## 4. 服务层

```text
class ProgressCaptureService:
    def extract_progress(
        workspace: WorkspaceEntry,
        evidence_inputs: tuple[EvidenceInput, ...],
        *,
        now: str,                       # ISO-8601 UTC 'Z' (注入, 便于纯函数)
    ) -> ProgressCapture:
        """AC-1/AC-2/AC-3/AC-4: 一次性解析, 返回 draft.

        Fail-closed on:
        - workspace 不是 WorkspaceEntry
        - 任一 evidence_inputs 的 kind == FILE_MTIME_ONLY (AC-7)
        - 任一 confidence ∉ [0.0, 1.0] (AC-4)
        - 任一 evidence_refs 为空 (AC-3)
        - 任一 EvidenceRef.digest_hex 不是 64-char lowercase hex
        """

    def revise(
        capture: ProgressCapture,
        item_id: str,
        *,
        new_text: str | None = None,
        new_kind: ProgressItemKind | None = None,
        new_confidence: float | None = None,
        reason: str,
        now: str,
    ) -> ProgressCapture:
        """AC-5: 改 ProgressItem 字段, 记录 overrides."""

    def reject(
        capture: ProgressCapture,
        item_id: str,
        *,
        reason: str,
        now: str,
    ) -> ProgressCapture:
        """AC-5: 标记 ProgressItem.status = REJECTED."""

    def accept(
        capture: ProgressCapture,
        *,
        accepted_by: str,
        now: str,
    ) -> ProgressCapture:
        """AC-6: requires_user_confirmation 不变, formally_accepted -> True."""

    def to_report_draft(
        capture: ProgressCapture,
    ) -> ProgressDraft:
        """AC-8: 仅当 capture.formally_accepted == True 才允许;
        否则 raise ProgressCaptureConflictError.

        不直接 import ReportManifest (US-9 职责), 返回 ProgressDraft 给
        US-9 ReportBuilder 消费.
        """

ProgressDraft
  draft_id                 -- "pd.<capture.capture_id>.<seq>"
  workspace_project_id
  workspace_task_id
  completed_work           -- tuple[str, ...] (每项对应一个 ProgressItem.id)
  pending_work             -- tuple[str, ...]
  next_steps               -- tuple[str, ...]
  blockers                 -- tuple[str, ...]
  source_progress_ids      -- tuple[str, ...] (所有引用 ProgressItem.id)

ProgressCaptureService.to_audit_record(capture) -> dict:
  """投影: 包含 capture_id / workspace / item 计数 / accepted 标志,
  不包含 ProgressItem.text / confidence / overrides.reason (敏感).
  """
```

## 5. AC 映射

| AC | 实现位置 | 失败模式 |
|---|---|---|
| AC-1 (识别变化) | `extract_progress` 接受 4 种 evidence kind 输入 | 输入为空 → 空 capture + 仍 requires_user_confirmation |
| AC-2 (四类提取) | ProgressItem.kind 枚举 4 类; to_report_draft 按 kind 分桶 | kind 非法 → ValidationError |
| AC-3 (证据关联) | evidence_refs ≥ 1 在 __post_init__ | 空 → ValidationError |
| AC-4 (来源+置信度) | source_kind + confidence 强制; confidence ∉ [0,1] 拒绝 | 越界 → ValidationError |
| AC-5 (修改/驳回) | revise / reject 返回新 ProgressCapture (frozen + overrides 链) | 重复 reject / 改 REJECTED 项 → ConflictError |
| AC-6 (用户确认) | requires_user_confirmation=True 强制; formally_accepted 默认 False; accept() 唯一路径 | 模型直接置 formally_accepted=True → ValidationError |
| AC-7 (无 mtime 决定) | EvidenceKind 不含 FILE_MTIME_ONLY; extract_progress 拒绝该 kind | 收到 FILE_MTIME_ONLY → ValidationError |
| AC-8 (生成汇报) | to_report_draft; formally_accepted=False 拒绝 | 未 accept → ConflictError |

## 6. 测试点 (≥ 12)

1. test_extract_progress_recognizes_four_evidence_kinds (AC-1)
2. test_extract_progress_categorizes_into_four_kinds (AC-2)
3. test_extract_progress_links_evidence_refs_per_item (AC-3)
4. test_extract_progress_requires_source_kind_and_confidence_in_range (AC-4)
5. test_revise_replaces_text_and_records_overrides (AC-5)
6. test_reject_marks_status_and_removes_from_report_draft (AC-5)
7. test_accept_sets_formally_accepted_and_recorded (AC-6)
8. test_extract_progress_rejects_file_mtime_only_evidence (AC-7)
9. test_to_report_draft_requires_formally_accepted (AC-8)
10. test_to_report_draft_buckets_items_by_kind_into_four_segments (AC-8)
11. test_empty_inputs_produces_empty_capture_with_user_confirmation_required (AC-1 边界)
12. test_pure_function_determinism_same_input_same_capture_id (质量)
13. test_invalid_workspace_raises_validation_error (输入校验)
14. test_to_audit_record_excludes_sensitive_text (审计投影, 与 US-11/12/13 一致)

## 7. 风险与缓解

- R1 (AC-7 fail-closed 易失): 用 1 项测试直接断言 EvidenceKind.FILE_MTIME_ONLY 不存在,
  并断言构造 EvidenceInput 时传入 FILE_MTIME_ONLY → ValidationError。
- R2 (与 task_flow 职责重叠): progress_capture 不做 task_id 自动识别; task_id
  显式来自 EvidenceInput; 与 task_flow.service 的 task extraction 边界清晰。
- R3 (与 US-9 ReportBuilder 重复): progress_capture 不 import ReportManifest;
  to_report_draft 返回 ProgressDraft, 由 US-9 builder 后续消费。

## 8. 完成定义 (本切片)

- 所有 ≥ 12 项 unit 测试通过
- `scripts/dev.ps1 -Task quality` exit=0, audit chain fully-sealed
- 不修改既有模块 / 既有 wire / 既有密码 / 既有审计配置
- BACKLOG US-8-AC-1 status: ready → done
- STATE bump iteration + status done
- DECISIONS append 一段 finalize 段 (append-only)
- 追踪矩阵 US-8 行追加

## 9. 后续 AC 候选 (本切片不做)

- US-8-AC-2: 实时捕获 / 文件 watcher (US-7 本地驾驶舱依赖)
- US-8-AC-3: 跨项目聚合 / 进展仪表盘 (US-13 决策简报依赖, 当前走 owner 手动汇总)
