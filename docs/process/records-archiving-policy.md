# 循环记录归档策略

> 2026-08-02。解决 VERIFICATION.md / DECISIONS.md / tool-audit.jsonl
> 线性膨胀问题。

## 阈值

| 文件 | 保留策略 | 触发 |
|---|---|---|
| `loop/VERIFICATION.md` | 最近 30 个门禁条目（或 ≤500KB） | 旧条目按 30 天归档 |
| `loop/DECISIONS.md` | 最近 20 个决策章节（或 ≤500KB） | 旧章节按 90 天归档 |
| `loop/tool-audit.jsonl` | 最近 2000 行（或 ≤5MB） | 旧行按 30 天归档 |

## 执行

```powershell
python scripts/archive_records.py --dry-run   # 先看计划
python scripts/archive_records.py --check     # 门禁：任一记录文件需归档即非零退出（fail-closed）
python scripts/archive_records.py --apply     # 写入 loop/archive/YYYYMMDD/
```

`--check` 已接入质量门禁 `lint` 阶段（`quality_gate.py`），任何记录文件
超出容量阈值或有待归档章节时门禁直接失败，提示先执行 `--apply`。

归档产物保留在 `loop/archive/YYYYMMDD/`，保留期 2 年；删除归档需业务负责人
单独授权。归档操作只移动旧的记录文本，不触碰 `loop/audit-head.json/.p7s`
签名链与 `loop/STATE.json`；审计封存以 audit 链为准，不受记录归档影响。
