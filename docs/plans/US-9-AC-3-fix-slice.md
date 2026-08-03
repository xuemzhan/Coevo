# US-9-AC-3-fix 切片计划：发送端 base_revision 校验 fail-closed

> 2026-08-02。响应 `CODE_REVIEW.md` [BUG-P1] 与
> `loop/DECISIONS.md`（2026-08-01 preamble repair）中记录的
> "US-9 base-revision fail-open" MVP 完成阻塞项。

## 问题

`src/coevo/report/builder.py` 中 AC-3 校验对
`manifest.base_revision != baseline.process_flow_ref[0]` 直接 `pass`：

1. `process_flow_ref[0]` 是 US-1 流程的 `unit_id`，不是项目主版本；
2. 任意 `base_revision` 都会被接受，违反 docstring 声明的
   "baseline and manifest must agree on project_id and base_revision.
   Reject otherwise (fail-closed)"；
3. 接收端 `merge` 引擎（US-10 AC-3 / 协议 §16.3）已按
   `_master_revision(baseline.project_id, baseline.version)` 严格比对，
   发送端缺位造成不对称（fail-open 生成 → 接收端才 HOLD）。

## 范围

- 仅修复发送端校验：`manifest.base_revision` 必须等于基线主版本
  `<project_id>-R<version:04d>`（协议 §16.1，与
  `coevo.merge._master_revision` 格式一致），不匹配抛
  `ReportManifestValidationError`。
- 同步补充 fail-closed 测试与格式一致性测试。
- 不改 wire 布局、不改协议、不改密码方案、不新增依赖、
  不改动审计链签名配置。

## 影响面

| 文件 | 变更 |
|---|---|
| `src/coevo/report/builder.py` | 新增 `_master_revision` 本地 helper；`pass` 替换为严格校验 |
| `tests/unit/test_report_builder.py` | 新增 3 项测试（mismatch 拒绝 / 规范版本接受 / 与 merge 格式锁定） |
| `loop/BACKLOG.yaml` | 新增 `US-9-AC-3-fix` 条目 |
| `docs/traceability/requirements-test-matrix.md` | 新增 US-9/AC-3-fix 行 |
| `loop/DECISIONS.md` / `loop/STATE.json` | 本轮决策与状态记录 |

## 测试点

1. `base_revision="PRJ001-R9999"` vs 基线 version=1 → 必须抛
   `ReportManifestValidationError`（原实现静默通过）。
2. 基线 version=3 → `PRJ001-R0003` 通过、`PRJ001-R0002` 拒绝。
3. 与 `coevo.merge._master_revision` 输出逐版本一致（格式锁定）。
4. 既有 25 项 report 单元测试保持通过（fixture 使用
   `PRJ001-R0001` + version=1，天然匹配）。

## 风险

- 低。发送端更严格不会破坏 wire 兼容性；接收端 HOLD 逻辑不变。
- 唯一行为变化：生成时即拒绝错误基线引用，而不是延迟到合并端。

## 验证与门禁

- `make quality` 全量门禁（fmt + lint + unit + integration +
  security + e2e），要求 exit=0 且 audit seal fully-sealed。
- 安全审查视角：基线身份/解析验证类变更，按 AGENTS.md
  REVIEW 阶段执行安全复核。
