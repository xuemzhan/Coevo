# `progress_capture/` — 进展采集（US-8）

## 定位

本地工作区文件 watcher（轮询 + 摘要复用 + 稳定性门控）与证据→条目→覆盖的
纯函数服务；正式任务状态必须由用户确认（AC-6），不得仅凭文件修改时间判完成
（AC-7）。

## 职责边界

- **in scope**：文件变更事件、证据输入、进展条目提取/修订/拒绝/接受、汇报草稿；
- **out of scope**：文件内容理解（LLM 半环，另作切片）、正式状态落库。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `EvidenceInput/Ref`、`ProgressItem`、`ProgressCapture`、`ProgressDraft` | 证据/条目/覆盖/草稿模型与校验（EvidenceKind 四类闭集，排除 FILE_MTIME_ONLY） |
| `watcher.py` | `WorkspaceWatcher.scan/drain/start/stop` | 文件 watcher：单次 lstat、符号链接跳过、未变化文件摘要复用、稳定性门控防半写 |
| `service.py` | `ProgressCaptureService.extract_progress/revise/reject/accept/to_report_draft` | 纯函数服务：提取/修订/拒绝/接受/草稿（类型门统一助手） |

## 关键入口与数据流

```
工作区扫描 → WorkspaceWatcher.scan（lstat + 摘要，连续稳定才发事件）
  → ProgressCaptureService.extract_progress（证据 → 条目）
  → revise/reject/accept（requires_user_confirmation=True 强制）
  → to_report_draft（仅 formally_accepted 生成，按条目类型分桶 4 段）
```

- `WorkspaceWatcher.scan()` — 只发文件变更事实，**永不判定完成**；
- `ProgressCaptureService.accept()` — 正式接受前必须用户确认；
- `to_report_draft()` — 产出 US-9 汇报包所需的四段草稿。

## 安全与不变量

- 符号链接跳过、根外逃逸拒绝；watcher 只发事实不判完成；
- 变更需连续扫描稳定才发事件（防半写文件误报）；
- 条目必须关联 ≥1 条证据（EvidenceRef），证据摘要可核验；
- 审计投影排除 text/confidence/override reason 敏感字段。

## 性能与复杂度

- watcher：每文件单次 `lstat`（符号链接+元数据一次完成）；未变化文件复用
  摘要（O(条目数) 静默扫描）；字符串路径运算无 IO；
- 稳定性门控：连续 N 次扫描一致才发事件，避免半写误报。

## 测试覆盖

- `tests/unit/test_progress_capture.py`（29 项：模型常量/闭集/提取/门控/修订/
  草稿/审计投影）、`test_progress_watcher.py`；
- `tests/integration/test_progress_watcher.py`。

## 依赖与下游

- **上游依赖**：`workspace`（工作区路径）、文件系统；
- **下游消费者**：`report`（成果回传草稿）、`knowledge_base`（进展知识条目）。

## 错误语义

- 证据/条目/覆盖校验失败统一抛领域校验错误（失败关闭）；
- watcher 扫描失败只计数不中断（`_error_count`），但绝不发完成事件；
- 无证据的条目、仅文件时间证据（FILE_MTIME_ONLY）一律拒绝。
