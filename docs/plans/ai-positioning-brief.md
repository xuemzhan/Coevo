# AI 定位决策简报（PRODUCT-REVIEW T-01）

> 状态：**已定稿（选项 B，可修订）**——在业务负责人连续指示"继续完成未完成的"
> 下，由实现方按推荐口径定稿为工作决策；业务负责人可随时修订。登记见
> `loop/DECISIONS.md` 2026-08-12T12:00:00Z 条目（原 07:00 条目为 proposed）。
> 触发：2026-08-12 成熟产品视角审查（关键差距 #1："AI 具身智能体"目前是
> 确定性演示，不是模型驱动）。

## 1. 现状（实现事实）

- 默认配置 `provider: "offline"`（`config/model-config.json`）；演示链使用确定性
  服务（`FlowUnderstandingService` / `TaskDecompositionService` /
  `TalentRecommenderService`）。
- 模型适配层真实存在：`ModelProvider` 契约、`NullModelProvider` 离线兜底、
  OpenAI 兼容本地/远程提供者、版本化提示词注册表；`task_decomposition/agent.py`
  在模型可用时产出**草稿建议**，离线时返回 `None` 走确定性路径，正式基线必须
  经人工确认（US-2-AC-3 边界）。
- 质量门禁从不调用网络（`external_requests=0` 黑盒约束）。

## 2. 选项与权衡

| 选项 | 含义 | 优点 | 代价/风险 |
|---|---|---|---|
| A. 接入本地模型 | 把 local_openai（vLLM/llama.cpp 环回）接入任务分解/流程理解 agent 建议链路 | 兑现"AI 体"叙事；草稿+人工确认边界已具备 | 依赖外部本地推理环境；离线默认仍走确定性；需 E2E 与运维文档 |
| B. 确定性编排 + 可选模型辅助（推荐） | 产品定位为确定性任务编排；模型建议是可选增强，默认离线 | 与当前实现一致；无新外部依赖；门禁不受影响 | 需同步叙事，避免"具身智能体"过度承诺 |

## 3. 推荐：B（确定性编排 + 可选模型辅助）

理由：
1. **事实一致性**：当前 MVP 的全部正式状态流转都是确定性 + 人工确认，模型仅提供
   可选的分解草稿；定位 B 让 README/能力矩阵与实现完全一致。
2. **约束匹配**：离线优先 + 无运行时下载是强制约束；本地模型依赖外部推理服务，
   与当前发布形态冲突。
3. **演进无损**：模型适配层保留为扩展点；未来接入本地模型（选项 A）只需在
   T-02 打通建议链路，不必改产品骨架。

保留建议：README 的"具身智能体"愿景可保留为长期方向，但需在项目简介中明确
"当前 MVP 以确定性任务编排为核心，模型辅助建议为可选增强（草稿经人工确认）"。

## 4. 裁决后动作

- 若选 B：更新 README 澄清句（已落地）、能力矩阵 US-2 注记；T-02 转为
  "模型建议链路契约测试（含离线回退）"而非强制接入。
- 若选 A：T-02 正式实现本地模型建议链路 E2E，并补充运维文档。

## 5. 证据

- `config/model-config.json`（provider=offline，deepseek/local_openai 待审批）
- `src/coevo/task_decomposition/agent.py`（草稿边界 + 离线回退）
- `docs/modules/model.md`（契约 + NullModelProvider 兜底）
- `docs/architecture/capability-status.md`（done=切片完成，能力级别另行声明）
