# `model/` — 模型适配层（强制约束 9.2）

## 定位

统一模型适配器契约：业务层不绑定单一厂商/推理框架；版本化配置 + 提示词注册表 +
OpenAI 兼容提供者；`NullModelProvider` 提供离线兜底，保证无网环境下门禁全绿。

## 职责边界

- **in scope**：提供者契约、配置/提示词加载、远程/本地调用、响应严格解析；
- **out of scope**：模型输出写正式状态（必须经人工确认边界）；提示词内容。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `contract.py` | `ModelProvider`、`NullModelProvider`、`parse_json_object()` | 契约 + 离线兜底 + 有界严格 JSON 解析 |
| `config.py` | `ModelConfig`、`load_model_config()` | 版本化配置加载（失败关闭，`external_data_ok` 默认 False） |
| `prompts.py` | `PromptRegistry`、`PromptTemplate`、`load_prompt_registry()` | 版本化提示词注册表 |
| `openai_compatible.py` | `OpenAICompatibleProvider` | OpenAI 兼容聊天提供者（环回校验、4 MiB 响应硬上限、连接类瞬态重试 1 次） |
| `deepseek.py` | `DeepSeekProvider` | DeepSeek 远程兼容变体 |

## 关键入口与数据流

```
业务门面 → ModelProvider.complete(system, user, max_tokens, timeout)
  →（本地）回环 provider /（远程）https + external_data_ok 审批
  → 响应体硬上限校验 → 严格 JSON 解析 → 草稿建议 → 人工确认
```

- `load_model_config()` — 只允许 `offline` / `deepseek` / `local_openai`，
  base_url 必须 https 或环回 http；
- `OpenAICompatibleProvider.complete()` — 环回模式免密钥，非环回必须有 API key +
  `external_data_ok` 审批（失败关闭外发）。

## 安全与不变量

- 敏感/涉密数据不得发送至未批准的模型端点；外发姿态由 `scripts/run_cockpit.py`
  preflight 告警（`model egress posture`）；
- 响应体 ≤ 4 MiB 硬上限；连接类瞬时失败有界重试，HTTP 错误/超限不重试；
- 模型输出仅是**草稿建议**，永不经由此层写正式任务状态。

## 测试覆盖

- `tests/unit/test_model_provider.py`（连接重试/超限拒绝/严格解析）；
- `tests/unit/test_production_docs.py`（配置⇄文档一致性）。

## 依赖与下游

- **上游依赖**：`config/model-config.json`、`config/model-prompts.json`（非密钥）；
- **下游消费者**：`task_decomposition/agent.py`、`scripts/run_cockpit.py` 等
  模型消费方。

## 配置与错误语义

- 配置文件 `config/model-config.json`（非密钥，schema_version=1.0）；API 密钥经
  环境变量名引用（`COEVO_LLM_API_KEY`，默认名），密钥本身不落文件；
- 关键开关：`external_data_ok`（外发审批，默认 False）、`timeout_seconds`（1..60）、
  `max_tokens`（1..8000）；`base_url` 必须 https 或环回 http；
- 异常：`ModelUnavailableError`（离线/无 key）、`ModelValidationError`
  （响应畸形/超限/非严格 JSON）、`ModelError`（配置非法，失败关闭）。
