# GOV-REVIEW-1 切片计划：只读沙箱独立双签

## 目标

把“独立 verifier + security-reviewer 双签”固化为可强制、可审计的治理：审查者只能在隔离只读快照上工作，任何对主工作树的写操作都会被守卫捕获并作废报告。

## 影响范围

- 新增 `scripts/review_sandbox.py`：prepare / check / discard 三子命令 + pin 清单 + 保护路径完整性校验；
- 新增 `docs/process/independent-review-governance.md` 策略文档；
- 新增 `tests/unit/test_review_sandbox.py`：隔离夹具 git 仓库上验证 prepare/check/discard、篡改检测、HEAD 漂移、loop 副产物豁免、路径安全；
- 本次切片本身即执行一轮真实双签（verifier + security-reviewer 两个独立子代理，带 25 分钟超时与守卫校验）。

## 风险

- 子代理越权写主工作树：以沙箱路径隔离 + 守卫 manifest 校验 + 违规作废三重防护；
- 超时失控：编排者用有界 wait + interrupt，超时按未放行处理；
- 沙箱无 `.tools/`/`loop/runtime/`：以 junction 挂载（gitignored，不入清单）。

## 测试点

- 单元：沙箱生命周期与守卫逻辑（约 9 项）；
- 门禁：`make quality` exit=0、指纹与基线一致；
- 双签：两份独立报告通过守卫校验后写入 VERIFICATION。
