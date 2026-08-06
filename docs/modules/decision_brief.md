# `decision_brief/` — 决策简报（US-13）

## 定位

候选风险经负责人密钥确认并绑定最新权威合并回执后，生成决策简报；受控 DOCX 模板
注册与 CAS 版本仓库保证简报内容的可追溯、可审计。

## 职责边界

- **in scope**：简报四区块结论、来源绑定、三种简报类型、风险确认、模板注册/复验、
  修订 CAS + 事件幂等 + 内容哈希链；
- **out of scope**：简报文档的实际渲染（调用 WPS/“开悟”工具，生成新版本副本并
  强制人工确认）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `DecisionBrief`、`BriefContent`、`BriefType`、`RiskConfirmation`、`WpsDocumentRequest` | 简报/内容/模板/风险确认模型与全部校验（含 DOCX 校验：宏-free、尺寸/条目上限） |
| `repositories.py` | `DecisionBriefRepository`、`ApprovedTemplateRegistry`、`RiskConfirmationRepository` | 修订 CAS + 事件幂等 + 内容哈希链；模板复验；权威风险确认 |
| `service.py` | `DecisionBriefService.generate/revise/to_audit_record` | 简报生成/修订门面：只消费最新 verified 回执 + owner 签名风险确认 |

## 关键入口与数据流

```
最新权威回执(merge) + 负责人签名风险确认 → DecisionBriefService.generate
  → 四区块结论（进展/变化/风险/待决策，逐项绑定来源）
  → DecisionBriefRepository（CAS 保存修订历史）→ 人工审核 → WPS 生成文档
```

- `DecisionBriefService.generate/revise` — STAGE / PERIODIC / RISK_TOPIC 三类；
- `RiskConfirmationRepository.confirm/verified` — owner 四方身份绑定
  （证书/公钥摘要/算法 OID/父证书固定）；
- `ApprovedTemplateRegistry.approve/verify` — 每次实际复验受控 DOCX。

## 安全与不变量

- 简报**只使用已确认状态**（最新 verified 回执），候选/推断数据不得入稿；
- 风险确认必须绑定 receipt_id + snapshot_digest + risk_digest，签名失败关闭；
- 模板只允许宏-free DOCX、受控根路径、硬上限（尺寸/条目/压缩比）；重放失败关闭；
- 审计投影排除简报正文与敏感依据，只保留哈希/计数/来源引用。

## 测试覆盖

- `tests/unit/test_decision_brief.py`（20 项：权威确认绑定、四区块/三类型、来源追踪、
  输入上限、CAS/重放/哈希链、模板篡改/宏/替代、WPS 审核、审计脱敏）。

## 依赖与下游

- **上游依赖**：`merge`（回执）、`risk`（风险报告）、`identity/private_keys`
  （签名权威）、`report`；
- **下游消费者**：`examples/service-api` 决策简报服务、驾驶舱/报告生成链路。

## 错误语义

- `DecisionBriefValidationError`：输入/绑定/模板/确认校验失败（可修正）；
- `DecisionBriefConflictError`：CAS 冲突 / 事件重放意图冲突（失败关闭）；
- `DecisionBriefError`：其他结构不变量；模板篡改/宏/替代 registry 一律拒绝。
