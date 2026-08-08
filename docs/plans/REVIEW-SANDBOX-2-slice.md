# REVIEW-SANDBOX-2 切片计划：独立审查沙箱治理修订（junction 漂移 + 验证口径）

> 状态：已批准（2026-08-08 用户指令"继续进行优化，不用做全量门禁"）。增量门禁口径
> （fmt + lint + 定向测试），全量 quality 按用户指示豁免，豁免在 DECISIONS/VERIFICATION 留痕。

## 1. 目标工作项

- 工作项：`REVIEW-SANDBOX-2`（ENG-BASE，dependencies=[RECORDS-ARCHIVE-2]；
  原登记误用 `REVIEW-SANDBOX-1` 与历史 done 项重名，已更名）。
- 目的：修订 `docs/process/independent-review-governance.md` 的独立双签验证口径——
  实测发现 §7"以 junction 挂载 .tools"与当前安全加固冲突，且复制 .tools 无法
  复现 GmSSL 助手/opencode 测试；需把"主树全量门禁 + 沙箱守卫 + 定向复核"
  确立为实际可行口径，消除文档与实现的漂移（RECORDS-ARCHIVE-2 独立复核已实测）。

## 2. 交付

- `docs/process/independent-review-governance.md`：
  * §2 independent verifier 职责改为"在只读沙箱内做守卫校验 + fmt/lint/单元/
    定向复核；完整质量门禁在主工作树钉扎提交上执行（权威证据），复核追溯矩阵与审计链"；
  * §7 环境说明重写：明确 junction 挂载 .tools 会被"拒绝 reparse point"加固拦截
    （Open-CoevoLockedDirectory 抛错）；复制 .tools 无法复现 GmSSL 助手/DLL 交互
    （GMH-E-MAGIC）与 opencode 配置解析；因此沙箱只承担守卫/静态/单元/定向复核，
    crypto 依赖测试以主树全量门禁为准；保留固定环境变量清单；
  * §1/§2 补充"沙箱内 crypto 测试失败不构成缺陷证据（环境差异）"的说明。
- `scripts/review_sandbox.py`：模块 docstring 补充验证口径说明（沙箱=守卫+定向复核；
  权威全量门禁在主树，详见治理文档）。
- `tests/unit/test_review_sandbox.py`：新增 GovernanceDocTests——
  治理文档包含"主工作树全量门禁 + 沙箱守卫 + 定向复核"口径、junction 局限性说明
  （reparse point / GMH-E-MAGIC / opencode 配置），且不再以 junction 作为唯一
  验证方式；review_sandbox.py docstring 含验证口径说明。

## 3. 测试要点

- `tests/unit/test_review_sandbox.py`（新增类）：
  * 文档含主树全量门禁权威证据表述；
  * 文档含沙箱守卫 + 定向复核表述；
  * 文档说明 junction/reparse 冲突与复制环境限制（GMH-E-MAGIC / opencode 配置）；
  * review_sandbox.py 模块 docstring 引用治理文档口径。
- 回归：既有 `test_review_sandbox.py` 全部用例（沙箱工具机制不变）。

## 4. 完成条件

- 定向测试全绿；`python scripts/quality_gate.py --target fmt` 与 `--target lint`
  exit=0（记录新指纹）；`archive_records.py --check` exit=0；
- 治理文档与 review_sandbox.py docstring 同步更新；追溯矩阵新增
  `ENG-BASE | REVIEW-SANDBOX-2` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查门

- security-reviewer：**是**（涉及审查治理/独立双签流程，须确认不降低只读契约）；
  protocol-reviewer：**否**。
