# `risk/` — 风险预警（US-11）

## 定位

基于最新权威合并回执的确定性风险分析：延期、前置未完成、长期沉默、成果不足四类
基础风险 + AT_RISK/BLOCKED 传染推断 + 严重协调建议。

## 职责边界

- **in scope**：回执链连续性校验、风险规则分析、传染推断、会议建议、审计投影；
- **out of scope**：风险正式发布（必须负责人确认）、督办/会议调度（`supervision/`）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `Risk`、`RiskReport`、`RiskKind`、`SourceKind` | 风险/报告/来源类型与校验（四类闭集） |
| `analyzer.py` | `RiskAnalyzer`、`analyze_after_merge()`、`merge_and_analyze()` | 合并后自动分析：最新回执校验 → 规则分析 → 传染推断 → 建议 + 审计投影 |
| `agent.py` | `RiskSuggestion`、`RiskSuggestionAgent`（MATURITY-O-08） | 可选模型推断风险建议：草稿边界 + 离线回退；仅经 `ConfirmedStateChange` 人工确认后并入候选报告 |

## 关键入口与数据流

```
merge_and_analyze（合并成功且生成回执）→ RiskAnalyzer.analyze_after_merge
  → 最新 verified 回执 + 基线 → 四类风险 + 传染 + 协调建议 → RiskReport（候选）
  → 负责人确认后才正式发布
```

- `RiskAnalyzer`（阈值可配置：延期天数、沉默天数、证据不足等）；
- `merge_and_analyze()` — 合并失败则无风险报告（不产生伪风险）。
- `RiskSuggestionAgent.suggest()` — 可选增强：模型推断 `SourceKind.INFERRED`
  风险草稿；provider 不可用返回 `()`（确定性分析不变）；
- `RiskSuggestionAgent.apply()` — 只接受 `ConfirmedStateChange`（REVIEW2-7），
  未知/重复/越窗/已存在 id 一律拒绝，产出仍为候选报告（未正式发布）。

## 安全与不变量

- **只用最新权威回执**（旧状态拒绝）；回执链版本连续校验失败关闭；
- 风险报告 `requires_owner_confirmation=True`、`formally_released=False` 为默认；
- 判断依据/影响任务显式记录；审计投影只留结构事实。
- 模型推断建议默认 `requires_confirmation=True`、`formally_released=False`；
  审计投影排除 basis/recommendation/rationale。

## 测试覆盖

- `tests/unit/test_risk_analyzer.py`（延期/前置/沉默/证据不足/传染/建议）；
- `tests/integration/test_merge_risk_receipt_chain.py`；
- `tests/security/test_merge_receipt_repository.py`（回执行级门禁）。
- `tests/unit/test_risk_suggestion_agent.py`（模型建议解析/校验/离线回退/
  人工确认并入/审计脱敏）。

## 依赖与下游

- **上游依赖**：`merge`（回执）、`task_decomposition`（基线）；
- **下游消费者**：`supervision`（督办/会议）、`decision_brief`（风险专题）、
  `knowledge_base`（风险知识）；`model`（可选建议 provider）。

## 错误语义

- `RiskValidationError`：输入/回执绑定校验失败（含旧状态、签名/信任失败）；
- `RiskAnalysisError`：分析器/门面使用错误；回执链版本不连续失败关闭。
