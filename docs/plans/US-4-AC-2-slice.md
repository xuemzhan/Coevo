# US-4-AC-2 第三轮安全修复设计

> 2026-08-01。响应第二次独立安全复审的 4 High / 2 Medium，不修改
> US-1/2/3/5 facade、`.agent` wire 或密码方案，不新增依赖。

## 两阶段边界

1. `dispatch_event_with_real_facades` 真实调用 US-1/2/3，形成冻结的
   `PackagePreview`，停在 `HELD_AT_CONFIRM`。
2. `confirm_real_chain` 接受 identity `Actor` 和可信 `Authorizer`，要求资源权限
   `orchestrator:confirm-package:<project_id>`。确认摘要绑定 actor、held report、
   event digest 及完整预览，结果仅为 `CONFIRMED_PENDING_PACKAGE`。
3. `resume_real_chain` 再校验固定链 step 4 的注册、能力与 `AVAILABLE` 状态。
   当前仓库没有获批 SM2/SM3/SM4 产品能力，因此不调用 unsigned builder 或任何
   placeholder factory，稳定返回 `CRYPTO_CAPABILITY_UNAVAILABLE` 并升级人工，绝不
   标记 `COMPLETED`。

`PackagePreview` 绑定 event、project、task、base revision、project input digest、
sender、recipient、package type 与 payload digest。通用 `confirm_human` 对受保护真实
链保持 fail closed。

## 持久化、重放和恢复

`RealChainStore` 使用 Python 标准库 SQLite：

- `BEGIN IMMEDIATE` 事务原子保存事件状态、规范 JSON outcome snapshot 和 hash-chain
  audit；
- 同 event ID 同摘要重开后返回保存快照，异摘要提交冲突审计后拒绝；
- confirmation 和 resume 保持摘要幂等；
- 启动发现 `DISPATCHING` / `PACKAGE_BUILDING` 时只转为
  `RECOVERY_REQUIRED`，不自动重跑业务或密码操作；
- `recover_real_chain` 要求
  `orchestrator:recover-package:<project_id>`，由有权人员手工终止到
  `ESCALATED`。

审计只保存结构字段、稳定错误码和摘要，不保存自由文本任务内容、人员信息或密码
材料。拒绝冲突审计与状态判断在同一事务内提交。

## 验证范围

- 原 US-4 纯调度兼容回归；
- Authorizer 允许/拒绝和资源化权限；
- 预览篡改、actor/held context 绑定；
- step 4 disabled fail closed；
- 无国密能力稳定失败且无 `COMPLETED`；
- SQLite 重开 replay/conflict、outcome snapshot、hash-chain；
- 中断态启动恢复和有权人工升级。

循环状态、追踪矩阵和治理审计由独立 verifier/reviewer 更新。
