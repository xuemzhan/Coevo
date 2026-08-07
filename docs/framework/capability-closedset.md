# 能力闭集收敛（CTAF §5.2 / M1b）

> 里程碑：M1b（2026-08-08 交付）。实现：`src/coevo/framework/capability.py`。
> 工作项：`US-16-AC-3-framework-capability-closedset-v0.1`。

## 目标

把 CTAF §5.2 的框架能力闭集与运行中枢既有 `AgentCapability` 枚举收敛为单一
事实来源，消除 manifest-checker（AC-1）遗留的"扩展名未收敛"缺口，并保证
注册表与 `_real_chain.py` 使用的能力目录双向一致。

## 注册表设计

| 类别 | 名称 | AgentCapability 映射 |
| --- | --- | --- |
| MVP（12） | TASK_FLOW_UNDERSTANDING / TASK_DECOMPOSITION / TEAM_RECOMMENDATION / KNOWLEDGE_INGEST / TASK_PACKAGE_BUILD / PROGRESS_CAPTURE / RISK_ANALYSIS / DECISION_BRIEF / SUPERVISION / AUDIT_INTERCEPT / REPORT_BUILD / MERGE_ENGINE | task_flow_understanding / task_decomposition / team_recommendation / **knowledge_ingest（M1b 新增）** / task_package_build / progress_capture / risk_analysis / decision_brief / supervision_meeting / audit_governance / report_build / state_merge |
| CRYPTO_PROXY（1） | CRYPTO_PROXY | 无；**必须 `crypto_scope=approved-product`** |
| 框架抽象（6） | PLANNER / ROUTER / AGGREGATOR / EVALUATOR / OPTIMIZER / HUMAN_GATE | 无（Plan 层 AGENT 节点可用） |

## 双名解析

`AgentCapability` 枚举值（如 `task_decomposition`）与 CTAF 规范名
（如 `TASK_DECOMPOSITION`）解析到同一注册条目；枚举成员名（如 `STATE_MERGE`）
同样解析。闭集外、混大小写、空串一律拒绝（fail-closed）。

## 一致性守卫（AC-3.4）

- `orphan_agent_capabilities()`：`AgentCapability` 中未登记进注册表的成员
  （必须为空）；
- `unmapped_mvp_capabilities()`：无映射的 MVP 名称（必须为空）；
- `check_consistency()` 任一非空即抛 `CapabilityValidationError`，
  由测试 `test_bidirectional_consistency` 钉住。

## 对 manifest-checker 的影响

`manifest_checker.check()` 的 capability 校验从直接 `AgentCapability(...)`
切换为 `resolve_capability(...)`：MVP 未映射拒绝、CRYPTO_PROXY 无
approved-product scope 拒绝、框架抽象允许；`AgentManifest.capability` 保存
规范能力名（CTAF §5.2 名称）。

## 安全边界

- 能力闭集是信任边界：未知/未映射一律拒绝；
- CRYPTO_PROXY 与 approved scope 强绑定，防止原型 scope 冒用密码代理能力；
- 纯函数、仅标准库、可离线运行（L15）；模块文档守卫（L17）。
