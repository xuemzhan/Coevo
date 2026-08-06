# `model/` — Model Adapter Layer (mandatory constraint 9.2)

## Scope

Unified model-adapter contract so the business layer never binds to a single
vendor: versioned config + prompt registry + OpenAI-compatible provider;
`NullModelProvider` provides the offline fallback so gates stay green without a
network or API key.

## Files

| File | Key functions | Responsibility |
|---|---|---|
| `contract.py` | `ModelProvider`, `NullModelProvider`, `parse_json_object()` | Contract + offline fallback + bounded strict JSON parsing |
| `config.py` | `ModelConfig`, `load_model_config()` | Versioned config loading (fail-closed, `external_data_ok` defaults False) |
| `prompts.py` | `PromptRegistry`, `load_prompt_registry()` | Versioned prompt registry with digest verification |
| `openai_compatible.py` | `OpenAICompatibleProvider` | OpenAI-compatible chat client (loopback check, 4 MiB response cap, bounded retry) |
| `deepseek.py` | `DeepSeekProvider` | Remote compatible variant |

## Security invariants

- Sensitive data must not be sent to unapproved endpoints; egress posture is
  warned at cockpit startup;
- Responses capped at 4 MiB; connection-class transient failures retry once,
  HTTP errors/overruns never retry;
- Model output is always a draft suggestion; never written as formal state.

## Config / errors

- `config/model-config.json` (non-secret; API key referenced by env var name);
  `base_url` must be https or loopback http;
- `ModelUnavailableError` (offline/no key), `ModelValidationError`
  (malformed/oversized/not strict JSON), `ModelError` (bad config).

## Testing

- `tests/unit/test_model_provider.py`; `tests/unit/test_production_docs.py`
  (config↔docs consistency).
