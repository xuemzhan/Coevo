# 显式事件模型契约（Explicit Event Model）

> 状态：生效（2026-08-10，REVIEW2-8）
> 适用范围：`src/coevo/events`（统一领域事件）与后续离线同步演进。

## 1. 字段

| 字段 | 语义 | 排序/因果作用 |
|---|---|---|
| `event_id` | 全局唯一（safe-id） | 标识 |
| `aggregate_id` / `aggregate_type` | 聚合归属 | 聚合内排序域 |
| `base_revision` | 事件基于的项目主版本 | 冲突判断 |
| `actor` / `operation` / `payload` | 行为与变更内容 | — |
| `created_at` | ISO-8601 UTC Z | **仅元数据，绝不参与排序** |
| `client_sequence` | 写入方单调计数（≥0） | 聚合内唯一排序依据 |
| `correlation_id` | 业务单元分组 | 关联 |
| `causation_id` | 前因事件（可选） | 必须指向前序事件（禁止自指/环） |

## 2. 排序规则

- 聚合内顺序 = `(aggregate_id, client_sequence)` 严格递增；`created_at` 与文件系统时间
  不承担任何顺序判定职责；
- `validate_event_chain` 拒绝：重复 event_id、非严格递增序号、未知前因、
  自指/环状因果；
- 因果边只允许指向规范序中的前序事件，链天然无环。

## 3. 与现有事件的关系

- `orchestrator.OrchestrationEvent`（event_id/kind/project/task/payload/triggered_at）
  与 `audit_governance.AuditEvent`（ts/actor/action/result…）保留为各自领域入口；
- `DomainEvent` 是离线多方同步的统一契约（承接 ARCH-REVIEW-2 合并收敛演进）；
  后续工作项将把导入/合并/撤销路径显式映射到本模型（不一次性替换现有事件）。

## 4. 守卫测试

`tests/unit/test_review2_8_event_model.py`：构造校验、按 client_sequence 排序
（时间戳乱序不影响）、重复 id/非严格序号/未知前因/自指/环拒绝、文档存在。

## 5. 变更纪律

任何让时间戳参与顺序判定、放松因果约束或改变序号规则的改动，视为同步语义变更，
需架构评审并在 `loop/DECISIONS.md` 留痕。
