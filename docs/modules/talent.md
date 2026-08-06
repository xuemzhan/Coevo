# `talent/` — 团队组建（US-3）

## 定位

脱敏人才池、确定性推荐与 SQLite 持久化：原始 PII 永不进入模型，评分可复现，
人员安排最终由任务/项目负责人确认。

## 职责边界

- **in scope**：脱敏身份、技能/资质/负载/窗口模型、确定性评分、SQLite 持久化
  （导入即脱敏）；
- **out of scope**：组织通讯录接入、人员绩效评价。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `Talent`、`TalentPool`、`RedactedIdentity`、`AvailabilityWindow`、`LoadAlert` | 人才/脱敏身份/窗口/负载告警模型（字段最小契约） |
| `redaction.py` | `redact_identity()`、`stable_pool_code()` | PII 脱敏：稳定池码 + SHA-256 不可逆哈希 + 有界显示提示 |
| `recommender.py` | `recommend()`、`score_candidate()` | 确定性评分：技能 +2.0 / 资质 +1.0 / 窗口全含 +1.5、部分 +0.5 / 负荷余量 +1.0；候选集合预热，O(R·N) 内环 |
| `service.py` | `TalentRecommenderService.recommend_for_requirements()` | 门面：需求 → 推荐 + 理由 + 负载告警 |
| `store.py` | `TalentStore`（create/open/register/iter_talents） | SQLite 持久化：哈希链 + 逐行校验 + 元数据缓存（create 后不可变） |

## 关键入口与数据流

```
本地脱敏人才库 → TalentStore.open（完整性/模式/链校验）
  → TalentRecommenderService.recommend_for_requirements（评分 → 排序 → limit）
  → 候选 + 匹配度 + 理由 → 负责人确认 → 任务责任分工
```

- `recommend(pool, requirements, limit)` — 确定性排序；
- `TalentStore.register/get/iter_talents` — 注册即脱敏；
- `redact_identity()` — 不可逆脱敏。

## 安全与不变量

- **原始 PII 永不进入模型/日志**；脱敏身份只含代号 + 有界提示 + 身份哈希；
- 评分可复现、结果确定（与输入顺序无关）；
- 识别负荷过高（AT_CAPACITY/OVER_CAPACITY）与时间窗口冲突（WINDOW_CONFLICT）；
- 人员调整过程形成操作记录。

## 测试覆盖

- `tests/unit/test_talent_recommender.py`（32 项：模型/脱敏/排序/理由/负载/服务）、
  `test_talent_store.py`；
- `tests/integration/test_talent_store_persistence.py`。

## 依赖与下游

- **下游消费者**：`orchestrator`（固定链第 3 步）、`app/pipeline`、示例闭环。

## 错误语义

- `TalentValidationError`：人才/需求/limit 校验失败；`TalentRecommenderError`：
  评分/门面错误；
- `TalentStoreError` / `TalentStoreIntegrityError` / `TalentStoreDuplicateError`：
  持久化/链校验/重复注册失败关闭。
