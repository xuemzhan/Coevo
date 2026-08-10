# 模型建议/正式状态类型边界（State Change Boundary）

> 状态：生效（2026-08-10，REVIEW2-7）
> 适用范围：`src/coevo/model`（contract）与所有正式状态写入入口。

## 1. 两层类型

- **DraftSuggestion**：模型输出进入业务层**唯一**允许的形状。
  字段：`source` / `content` / `evidence`（SuggestionEvidence 列表）/
  `confidence ∈ [0,1]` / `requires_confirmation`（默认 `True`，构造时不可静默关闭）。
  草稿**不是**正式状态。
- **ConfirmedStateChange**：正式状态写入 API **唯一**接受的形状。
  字段：`confirmed_by`（有权限人员）/ `confirmed_at`（ISO-8601 UTC Z）/
  `source_draft_id`（溯源到草稿）/ `changes`（非空字段变更映射）。

## 2. 守卫

`ensure_confirmed_state_change(change)` fail-closed：

- 传入原始 dict、未确认草稿或任意对象 → `ModelValidationError`；
- 传入 ConfirmedStateChange → 重新校验并返回（防篡改/构造错误）。

## 3. 接入纪律

- 现有正式状态 API 已使用各自类型化模型与确认路径（如 merge 的 MergeRecord、
  knowledge 的 ReviewDecision、progress_capture 的 formally_accepted）；
  本契约是统一边界，新写入口必须经 `ensure_confirmed_state_change` 或等价校验；
- 后续将逐个把 merge / risk / decision_brief / knowledge / report /
  progress_capture 的确认路径显式接入本类型（随各工作项推进，避免一次性大重构）。

## 4. 守卫测试

`tests/unit/test_review2_7_state_boundary.py`：草稿默认需确认、置信度越界拒绝、
边界置信度接受、确认变更字段校验、守卫拒绝 dict/草稿、接受确认变更、文档存在。

## 5. 变更纪律

任何放宽该边界（如允许 dict 直写正式状态）的改动，视为架构安全变更，需架构评审并
在 `loop/DECISIONS.md` 留痕。
