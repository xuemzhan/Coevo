# loop/

Loop 工程循环的状态机目录。**不要手改** `STATE.json` 与 `tool-audit.jsonl`（除专门审计场景），所有写操作必须经过 `.opencode/tools/loop_state.ts`（背后的 Python 实现位于 `scripts/loop_state.py`）。

| 文件 | 类型 | 写者 | 读者 |
|---|---|---|---|
| `STATE.json` | 状态机当前态 | `loop_state` Tool | `loop-engineer`、`mvp-verifier` |
| `BACKLOG.yaml` | 待办工作项 | `mvp-planner` 或人工 | `loop-engineer` |
| `GOAL.md` | MVP 终态与不可妥协边界 | 仅人工编辑 | 所有 Agent 启动时加载 |
| `VERIFICATION.md` | 最近一次门禁结果 | `quality_gate` Tool | `mvp-verifier`、`security-reviewer` |
| `DECISIONS.md` | 决策留痕 | 人工或 `loop-engineer`（重大变更） | 所有 Agent / 审计 |
| `tool-audit.jsonl` | 所有 Tool 调用指纹 | 各 Tool | 审计 / `security-reviewer` |
| `archive/YYYYMMDD/` | 按容量/期限归档的旧记录（VERIFICATION/DECISIONS/tool-audit） | `python scripts/archive_records.py --apply` | 审计 / 历史追溯 |

## 归档约定

- `VERIFICATION.md` 保留最近 60 个门禁条目（或 ≤1MB）；`DECISIONS.md` 保留最近
  20 个章节（或 ≤500KB）；`tool-audit.jsonl` 保留最近 2000 行（或 ≤5MB）。
- 超限的旧记录由 `scripts/archive_records.py` 移入 `loop/archive/YYYYMMDD/`
  （保留期 2 年），不触碰审计签名链与 `STATE.json`。
- Agent 读取记录时只读最新一段即可；历史证据以 `loop/archive/` 为准。

## 状态字段（`STATE.json`）

```json
{
  "schema_version": "1.0",
  "iteration": 0,
  "current_story": "US-0",
  "current_item": null,
  "phase": "ready",
  "status": "ready",
  "failed_verifications": 0,
  "last_failure_fingerprint": null,
  "last_verified_commit": null,
  "blocking_issue": null,
  "updated_at": null
}
```

| 字段 | 取值范围 | 说明 |
|---|---|---|
| `phase` | discover / plan / implement / verify / review / record / decide | 当前循环阶段 |
| `status` | ready / in-progress / blocked / security-blocked / decision-required / done / mvp-complete | 整体状态 |
| `failed_verifications` | 整数 | 连续失败计数，达 3 触发阻断 |

## 写规则

- 每次 `loop_state` 写入前必须先写 `.bak`，失败即恢复。
- 每次写入产生一条 `command_fingerprint`（命令 + 文件 + 时间）。
- 失败计数 ≥ 3 时强制 `status = blocked` 并停轮。
- `security-reviewer` 命中阻断项时强制 `status = security-blocked`。
