# events/ — 显式领域事件模型（REVIEW2-8）

## 定位

离线多方同步的统一事件契约（承接 ARCH-REVIEW-2 合并收敛演进）：为导入/合并/
撤销等路径提供带因果与客户端序号的显式事件模型，明确"时间戳不承担顺序判定"。

## 职责边界

- in scope：`DomainEvent` 统一事件形状；`validate_event_chain` 规范排序与
  因果校验（fail-closed）；`event_order_key` 规范序键。
- out of scope：不替换 `orchestrator.OrchestrationEvent` 与
  `audit_governance.AuditEvent`（各自领域入口保留）；不做持久化/传输。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `DomainEvent`、`validate_event_chain`、`event_order_key`、`EventValidationError` | 事件模型：聚合内按 client_sequence 严格递增排序（created_at 仅元数据），causation_id 只允许指向前序事件（无自指/环），重复 id/未知前因/非严格序号 fail-closed |
| `__init__.py` | 再导出 | 公共 API 表面 |

## 关键入口与数据流

`validate_event_chain(events) -> tuple[DomainEvent, ...]`：规范排序
（aggregate_id, client_sequence）→ 唯一性 → 聚合内严格递增 → 因果前序校验。

## 安全与不变量

- 顺序判定绝不使用 `created_at` 或文件系统时间；
- 因果边只允许指向规范序前序事件，链天然无环；
- 所有校验 fail-closed（`EventValidationError`）。

## 测试覆盖

- `tests/unit/test_review2_8_event_model.py`（构造校验、按序号排序（时间戳乱序
  不影响）、乱序到达重排、重复 id/同序号/未知前因/自指/环拒绝、文档守卫）。

## 依赖与下游

- 上游：`src/coevo/ids.py`、`src/coevo/timefmt.py`（stdlib-only）；
- 下游：后续导入/合并/撤销路径显式映射（REVIEW2-8 文档 §3）。
