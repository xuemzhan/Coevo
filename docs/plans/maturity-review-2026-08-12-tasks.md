# 成熟度审查 → 修复与优化计划（2026-08-12）

> 来源：独立第三方成熟度评估报告（2026-08-12，审查对象 HEAD `631d46a`，
> 全量门禁独立复跑通过，指纹 `b5c12e15ae7c559f`）。
> 拆解指令：用户"将审查报告拆分为修复与优化的计划"、"基于上面的计划分步进行优化，
> 先不做全量门禁"。
> 登记方式：按 RECORDS-2 单一在飞不变量以队列注释登记于 `loop/BACKLOG.yaml`；
> 完整清单与进度以本文档为权威；逐轮进入 loop 时再从队列转为正式条目。

## 1. 修复项（R 系列，必须关闭）

| ID | 标题 | 范围 | 完成定义 | 依赖 / 外部 | 状态 |
|---|---|---|---|---|---|
| R-01 | 独立双签执行 | `docs/process/independent-verification-pack.md`、`external-gates.md` | 独立 mvp-verifier + security-reviewer 双签落档；mvp-complete 条件 11 与 REVIEW-REQUIRED 门禁关闭 | 外部：独立角色（对齐 T-03） | **done**（2026-08-12 双签放行：沙箱守卫 violations=[] + 主树全量门禁 exit=0 fingerprint=`b5c12e15ae7c559f` 2017/2013/0/4 + security pass；外部门 条件 11 → PASS） |
| R-02 | 生产密码产品接入 | `crypto/`、`identity/`、`app/production.py` | 生产链默认拒绝原型；GmsslProtectedProvider 启用；US-5-AC-2 关闭 | 外部：密码审批（对齐 T-06） | pending |
| R-03 | STATE 元数据时效修复 + 守卫 | `loop/STATE.json`、`tests/unit/test_state_metadata_guard.py` | STATE 指向最后正式 BACKLOG 项；last_verified_commit 可达 HEAD；updated_at 非未来；守卫测试全绿 | 无 | **done**（1e6c7f8） |
| R-04 | 全量门禁覆盖 HEAD 纪律 | `scripts/release_check.py`、`docs/operations/ops-runbook.md`、loop 记录 | `gate_covers_head` 检查生效（门禁 started_at ≥ HEAD 提交时间）；本次门禁证据落档提交 | 无 | **done**（8a13ac4） |
| R-05 | AI 定位正式裁决 | `loop/DECISIONS.md`、README、capability-status | 业务负责人裁决留痕；对外口径一致 | 业务负责人（对齐 T-01） | pending |
| R-06 | 审计密钥托管执行 + 独立审查 | `audit-key-runbook.md`、`audit_key_health.py` | 三档托管执行；ARCH-REVIEW-5 / REVIEW2-10 独立审查关闭 | 外部：独立安全审查（对齐 T-07） | **done**（T-07 三档托管已落地；ARCH-REVIEW-5 / REVIEW2-10 独立安全审查 2026-08-12 通过；B/C 档介质仍需批准密码产品） |

## 2. 优化项（O 系列，提升成熟度）

| ID | 标题 | 范围 | 完成定义 | 依赖 / 外部 | 状态 |
|---|---|---|---|---|---|
| O-01 | 在线/受控网络协同版本边界决策 | `docs/architecture/`、`external-gates.md` | 版本边界明确或进入设计；声明纪律守卫 | 业务决策（对齐 T-11/T-12 边界） | **proposed**（DECISIONS 2026-08-12T13:00:00Z；推荐 MVP 维持离线闭环、受控网络列入后续版本，沿用 ARCH-REVIEW-13） |
| O-02 | CI 激活 | `.github/workflows/quality.yml`、`ci-artifact.json` | CI 首次全量门禁绿；制品哈希一致 | 外部：owner Release（对齐 T-18） | pending |
| O-03 | Win7 实机验证 | `win7-compat` 分支、`tests/win7/` | 实机专项通过 + 验证记录 | 外部：Win7 环境 | pending |
| O-04 | WPS 真实宿主验收 | `cockpit/wps.py`、文档 | 真实 WPS 打开/生成副本验收通过 | 外部：WPS 环境 | pending |
| O-05 | 目标硬件性能复测 | `benchmarks/` | 目标硬件 13 项探针达标留档 | 目标硬件 | pending |
| O-06 | 督办/会议真实交互链路 | `supervision/`、`cockpit/`、`app/demo_support.py`、回传链 E2E | 回传链 E2E 含督办/会议协调；驾驶舱 SUPERVISION_VIEW 路由；demo 注册 agent.supervision_meeting；US-12 能力级别提升 | 无 | **done** |
| O-07 | 多用户/中心端同步产品化 | `sync/`、`identity/`、`cockpit/` | 离线文件式对账双节点 E2E（本批完成，`tests/e2e/test_sync_reconciliation.py`，同步离线半升为 INTEGRATION_VERIFIED）；受控网络部分待 O-01 裁决 | 依赖 O-01 | **部分完成**（离线半 done；在线半待 O-01） |
| O-08 | 风险模型推断型增强（可选） | `risk/agent.py`、`config/model-prompts.json` | `RiskSuggestionAgent.suggest` 草稿 + 离线回退；`apply` 仅接受 `ConfirmedStateChange`；单元测试全绿（10 项） | R-05 已由 T-01 选项 B 覆盖（确定性 + 可选模型辅助） | **done** |

## 3. 执行纪律（本轮已遵守）

- 按用户指令**不做全量门禁**：本轮仅跑定向测试（完整单元套件 1597 项、
  驾驶舱 HTTP 集成 28 项、回传链 E2E）与记录校验；
- 涉及文件规模预算的增长按契约例外流程登记（facade.py 676 / server.py 1108）；
- 记录写入（STATE/DECISIONS/BACKLOG）后重封缄审计链；
- 未推送、未打 tag、未发 release；提交留痕见 `loop/DECISIONS.md`。
