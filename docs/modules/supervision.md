# `supervision/` — 督办与会议协调（US-12）

## 定位

基于风险报告与权威输入生成督办建议、分级升级、提醒建议与会议候选提案；
会议结论投影为任务/风险处置/督办事项三类。**不实际召集会议，只产出建议**。

## 职责边界

- **in scope**：督办项生成、逾期升级建议、会议候选议题/背景/待决策问题、结论投影；
- **out of scope**：正式会议调度、正式督办发送（必须负责人确认）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `SupervisionItem`、`EscalationSuggestion`、`ReminderSuggestion`、`MeetingProposal`、`MeetingConclusionProjection` | 升级/提醒/会议提案模型与校验（闭集枚举 + 常量） |
| `service.py` | `SupervisionCoordinator.coordinate()`、`to_audit_record()` | 门面：风险 → 督办项集 + 升级 + 提醒 + 会议候选 + 结论三类投影 |

## 关键入口与数据流

```
RiskReport（负责人已确认候选）→ SupervisionCoordinator.coordinate
  → 督办项（责任主体/完成时间/关闭条件）+ 分级升级建议 + 提醒建议
  → MeetingProposal（议题/背景/待决策问题）→ 负责人确认 → 会议结论三类投影
```

- `SupervisionCoordinator.coordinate()` — 纯函数、无 IO/LLM；
- `COORDINATION_RECOMMENDED_KINDS` / `SUPERVISABLE_RISK_KINDS` — 触发协调的
  风险种类闭集。

## 安全与不变量

- 纯函数无 IO；建议基于权威输入（已验证风险/回执），失败关闭；
- 会议/督办全流程留痕；审计投影排除 basis/recommendation/rationale 敏感字段；
- 正式督办、跨单位催办必须由有权人员确认（强制约束 §8.4）。

## 测试覆盖

- `tests/unit/test_supervision_meeting.py`（10 项：模型校验/协调器/常量）。

## 依赖与下游

- **上游依赖**：`risk`（风险报告）、`merge`（回执）；
- **下游消费者**：`knowledge_base`（会议结论知识）、`app/pipeline`、示例闭环。

## 错误语义

- `SupervisionValidationError`：输入校验失败（可修正）；`SupervisionError`：
  结构不变量；纯函数门面无 IO，失败关闭。
