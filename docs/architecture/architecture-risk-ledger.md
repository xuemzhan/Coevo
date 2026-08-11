# 架构风险台账（Architecture Risk Ledger）

> 状态：生效（2026-08-10，ARCH-REVIEW-15）
> 用途：把历次架构审查识别出的架构级风险统一登记，标注处置状态与证据位置，
> 防止风险"隐式消失"或重复遗漏；作为业务负责人关闭外部项时的唯一对照表。

## 1. 风险清单

| 风险 ID | 风险描述 | 级别 | 处置状态 | 处置证据 | 责任 / 下一步 |
|---|---|---|---|---|---|
| P0-1 | MVP 完成缺独立双签（GOAL.md mvp-complete 条件 11） | P0 | 已登记，待独立验收 | `external-gates.md`（mvp-complete 条件 11 = REVIEW-REQUIRED）；`docs/process/independent-verification-pack.md` | 业务负责人安排独立 mvp-verifier + security-reviewer |
| P0-2 | 正式国密密码产品未接入（受保护密钥句柄为软件 KSP/CNG KEK 实现） | P0 | 已登记，外部审批 | `external-gates.md`（US-5-AC-2 = BLOCKED）；`crypto-mode-isolation.md`；`approved-crypto-provider-path.md` | 外部采购/审批后接入 GmsslProtectedProvider 生产路径 |
| P1-1 | Go/Python 双实现漂移（27 条映射规则双写） | P1 | **已修复** | `go-python-parity.md`；`go/taskflow/testdata/mapping-rules.json`；`go/taskflow/parity_test.go`；`tests/unit/test_arch_review_10_go_python_parity.py` | 规则变更先改 golden corpus，两侧同步 |
| P1-2 | 受控网络协同模式为设计态，易被误报为"已建成分布式系统" | P1 | **已收口（范围声明）** | `online-mode-scope.md`；`capability-status.md`（中心端持久化/跨节点同步 = DESIGNED/MODELED） | 后续版本实现；对外汇报遵守声明纪律 |
| P1-3 | CTAF 设计提案（v0.4.1）未经独立架构评审 | P1 | 已登记，待独立评审（自动独立评审机制尝试失败，见 DECISIONS 2026-08-11） | `external-gates.md`（CTAF-PROPOSAL-REVIEW = REVIEW-REQUIRED）；`design-proposal.md`（产品级草案 / 待独立复核后定稿）；实现方预评审 `docs/process/ctaf-pre-review-2026-08-11.md` | 独立架构师评审后定稿（外部指派 / 豁免留痕 / 可用外部会话执行） |
| P2-1 | 大文件 / 高复杂度单文件风险 | P2 | **已修复** | `file-size-budget.md`；`tests/unit/test_eng_optimize_7_file_size_budget.py`（MAX_FILE_LINES=1133、9 个大文件只降不增） | 维护时遵守预算；超阈值先拆分 |
| P2-2 | 内存态 / 持久态边界不透明 | P2 | **已修复** | `state-persistence.md`；`tests/unit/test_arch_review_11_persistence_matrix.py`（23 个有状态组件） | 新增有状态组件同步更新矩阵 |
| P2-3 | 发布门禁子进程编码健壮性（GBK 控制台下 traceability 打印 U+2194 崩溃致 release_check critical） | P2 | **已修复** | `scripts/release_check.py`（PYTHONIOENCODING=utf-8）；`tests/unit/test_eng_optimize_8_release_encoding.py` | 子进程 stdout 编码保持 UTF-8；规范路径已健壮 |
| EXT-1 | Win7 存量环境实机验证未落地 | P2 | 已登记，外部执行 | `known-limitations.md`；`win7-compat-branch.md`（静态专项） | 存量 Win7 环境实机验收 |
| EXT-2 | CI 未激活（toolchain Release 未上传） | P2 | 已登记，外部执行 | `known-limitations.md`；`ci-artifact.json`；`.github/workflows/quality.yml` | 所有者创建 `toolchain-1.0.0` Release 并上传制品 |
| EXT-3 | 审计签名密钥托管 / 独立审计节点未落地 | P2 | 已登记，外部执行 | `known-limitations.md`；`audit-key-ceremony.md` | 批准密码产品 / 受控密钥介质后落地 |

## 2. 台账纪律

1. 任何架构审查新发现的风险必须登记本台账；
2. "已修复"必须指向守卫测试 / 门禁证据，禁止仅凭声明关闭；
3. 外部项（P0-1 / P0-2 / P1-3 / EXT-1..3）不得被"全量门禁全绿"掩盖，关闭前必须
   同步更新 `external-gates.md` 或 `known-limitations.md` 并留痕；
4. 本台账与 `capability-status.md`、`external-gates.md` 一致：进入 PRODUCTION_READY
   前必须关闭对应风险项。

## 3. 守卫测试

`tests/unit/test_arch_review_15_risk_ledger.py`：台账存在、全部风险 ID 登记、
已修复项指向守卫证据、外部项指向登记表、文档索引登记。
