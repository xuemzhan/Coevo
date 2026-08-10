# 子智能体 Manifest 注册表契约（Agent Manifest Registry）

> 状态：生效（2026-08-10，ARCH-REVIEW-4）
> 适用范围：`src/coevo/framework/agent_catalog.py`（设计期目录）与运行时注册门。

## 1. 七个专业子智能体目录

| agent_id | capability（闭集） | 服务模块 | model_binding | 人工确认点 | 工具策略 |
|---|---|---|---|---|---|
| agent.flow_understanding | TASK_FLOW_UNDERSTANDING | task_flow | rule | flow_confirm | read-only |
| agent.task_decomposition | TASK_DECOMPOSITION | task_decomposition | hybrid | baseline_confirm | read-only |
| agent.progress_capture | PROGRESS_CAPTURE | progress_capture | rule | progress_accept | guarded-write |
| agent.risk_analysis | RISK_ANALYSIS | risk | hybrid | risk_release | read-only |
| agent.supervision_meeting | SUPERVISION_MEETING | supervision | rule | supervision_confirm | read-only |
| agent.decision_brief | DECISION_BRIEF | decision_brief | hybrid | brief_release | guarded-write |
| agent.knowledge_ingest | KNOWLEDGE_INGEST | knowledge_base | hybrid | knowledge_review | guarded-write |

## 2. 规则/模型切换边界（model_binding）

- `rule`：确定性服务（当前实现），不依赖 ModelProvider；
- `model`：需接入 `src/coevo/model` 适配层（`model-config.json` 选择厂商），
  输出必须经 `DraftSuggestion` 类型边界（REVIEW2-7）；
- `hybrid`：规则为主、模型可选增强；**切换只改配置与提示词版本，不改协议与
  人工确认点**。

## 3. 运行时注册

本目录是**设计期契约**；运行时注册仍必须经
`framework.integration.guard_registration`（manifest-checker + 证书链 + 生产
签名者），任何目录条目不得绕过注册门直接进入编排 registry。

## 4. 守卫测试

`tests/unit/test_arch_review_4_agent_manifest_registry.py`：目录恰为 7 项、
能力闭集覆盖、`validate_catalog()` 无违规、每项有确认点与绑定、文档存在。

## 5. 变更纪律

新增/调整子智能体必须同步目录、能力闭集与 `AgentCapability` 枚举（版本化变更）；
生产采用前需独立安全审查（security_review=true）。
