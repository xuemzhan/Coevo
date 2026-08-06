# `report/` — 成果回传（US-9）

## 定位

成果回传清单模型与包构建器：生成携带状态/进度/证据摘要的 `Report.agent` 汇报包，
并复用 US-5 wire 布局保证与任务下发包一致的加密签名机制（AC-5）。

## 职责边界

- **in scope**：ReportManifest（AC-1..AC-4）、ReportArtifact、提交序号、
  包组装、审计投影；
- **out of scope**：加密/签名实现（委托 `protocol/`）、状态合并（`merge/`）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `ReportManifest`、`ReportArtifact`、`ReportStatus`、`ReportOverride` | 清单状态/工件/覆盖模型与全部校验（大小/枚举/时间） |
| `builder.py` | `ReportBuilder.build()`、`ReportSubmissionSequence` | 提交序列（单调）、包组装（复用 build_unsigned_package）、审计投影 |

## 关键入口与数据流

```
ProgressDraft（US-8 已接受草稿）→ ReportBuilder.build
  → ReportManifest + 工件摘要 → build_unsigned_package（US-5 wire）
  → 加密签名 → Report.agent → 导出（原始成果留在本地工作区）
```

- `ReportBuilder.build()` — 生成汇报包并回读校验；
- `ReportSubmissionSequence.next()/expected_filename()` — 单调提交序号。

## 安全与不变量

- 清单字段严格校验（大小/枚举/时间，无效时间戳失败关闭）；
- 携带项目/任务编号 + 原始基线版本 + 包唯一编号 + 提交序号；
- 原始成果文件保留本地工作区；导出操作形成审计记录。

## 测试覆盖

- `tests/unit/test_report_builder.py`（25 项：工件/清单/序号/构建/文件名/覆盖/审计）；
- `tests/e2e/test_return_chain.py`（真实加密汇报包驱动合并链）。

## 依赖与下游

- **上游依赖**：`progress_capture`（草稿）、`task_decomposition`（基线）、
  `protocol`（包构建）；
- **下游消费者**：`merge`（合并输入）、`app/pipeline`、`examples/`。

## 错误语义

- `ReportManifestValidationError`：清单字段非法（大小/枚举/时间）；
- `ReportBuilderError`：构建失败（如无效时间戳计算失效期，失败关闭）。
