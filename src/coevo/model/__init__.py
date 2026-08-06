"""Unified model-adapter layer (mandatory constraint 9.2).

Business slices depend on :class:`ModelProvider`; vendors are selected
by a tracked config file (``config/model-config.json``) and prompts
come from a versioned data file (``config/model-prompts.json``).
The default is offline (``NullModelProvider``), so gates never need a
network.
"""
from __future__ import annotations

from .contract import (
    ModelError,
    ModelProvider,
    ModelUnavailableError,
    ModelValidationError,
    NullModelProvider,
    parse_json_object,
)
from .deepseek import DeepSeekProvider
from .openai_compatible import OpenAICompatibleProvider, is_loopback
from .config import ModelConfig, load_model_config
from .prompts import (
    PromptRegistry,
    PromptTemplate,
    load_prompt_registry,
)


def select_provider(config: ModelConfig | None = None) -> ModelProvider:
    """Select a provider from the model config (default offline)."""
    cfg = config or load_model_config()
    if cfg.provider == "offline":
        return NullModelProvider()
    if cfg.provider == "deepseek":
        # OPTIMIZE-2: explicit fail-closed checks (asserts are stripped under -O).
        if cfg.api_key_env is None or cfg.base_url is None or cfg.model is None:
            raise ModelError(
                "deepseek provider configuration is incomplete "
                "(api_key_env/base_url/model are required)"
            )
        return DeepSeekProvider(
            api_key_env=cfg.api_key_env,
            base_url=cfg.base_url,
            model=cfg.model,
            external_data_ok=cfg.external_data_ok,
        )
    if cfg.provider == "local_openai":
        if cfg.base_url is None or cfg.model is None:
            raise ModelError(
                "local_openai provider configuration is incomplete "
                "(base_url/model are required)"
            )
        return OpenAICompatibleProvider(
            name="local_openai",
            api_key_env=cfg.api_key_env or "COEVO_LLM_API_KEY",
            base_url=cfg.base_url,
            model=cfg.model,
            external_data_ok=cfg.external_data_ok,
        )
    raise ModelError(f"unsupported model provider {cfg.provider!r}")


__all__ = [
    "DeepSeekProvider",
    "ModelConfig",
    "ModelError",
    "ModelProvider",
    "ModelUnavailableError",
    "ModelValidationError",
    "NullModelProvider",
    "OpenAICompatibleProvider",
    "PromptRegistry",
    "PromptTemplate",
    "load_model_config",
    "load_prompt_registry",
    "is_loopback",
    "parse_json_object",
    "select_provider",
]
