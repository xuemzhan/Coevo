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

**audit 种类不在通用归档范围内（RECORDS-ARCHIVE-3）**：`loop/tool-audit.jsonl`
是只增不改的审计链，裁剪会使签名封缄失效（audit tail deletion），而专用
重锚定流程尚未实现；`archive_records.py --check/--apply` 只处理
`verification` 与 `decisions` 两类，audit 超策略时工具打印提示并拒绝触碰
（`--apply` 非零退出）。审计容量以 `audit_key_health` / 封缄验证为准，
重锚定流程留作后续工作项。

**门禁自维护（RECORDS-ARCHIVE-4）**：`quality_gate.py` 每次追加 VERIFICATION
记录后自动调用 `archive_records.py --apply` 就地裁剪 verification/decisions，
使记录始终 ≤ 策略容量，无需人工介入；trim 失败隔离（不使门禁失败），由下一次
lint `--check` 兜底；audit 仍不可被触碰。

归档产物保留在 `loop/archive/YYYYMMDD/`，保留期 2 年；删除归档需业务负责人
单独授权。归档操作只移动旧的记录文本，不触碰 `loop/audit-head.json/.p7s`
签名链与 `loop/STATE.json`；审计封存以 audit 链为准，不受记录归档影响。
