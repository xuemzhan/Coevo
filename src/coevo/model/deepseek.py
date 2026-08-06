"""DeepSeek provider -- a remote OpenAI-compatible variant.

Backward-compatible subclass of :class:`OpenAICompatibleProvider`:
remote https endpoint, API key from ``COEVO_LLM_API_KEY`` (or the
configured ``api_key_env``), external-egress approval required.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# DeepSeek 提供者：OpenAI 兼容远程变体，仅经批准配置可用。
from __future__ import annotations

import os

from .openai_compatible import HttpPost, OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):
    """DeepSeek chat provider (remote, OpenAI-compatible)."""

    def __init__(
        self,
        *,
        api_key_env: str = "COEVO_LLM_API_KEY",
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        external_data_ok: bool | None = None,
        http_post: HttpPost | None = None,
    ) -> None:
        if external_data_ok is None:
            external_data_ok = (
                os.environ.get("COEVO_LLM_EXTERNAL_DATA_OK", "") == "1"
            )
        super().__init__(
            name="deepseek",
            api_key_env=api_key_env,
            base_url=base_url,
            model=model,
            external_data_ok=external_data_ok,
            http_post=http_post,
        )


__all__ = ["DeepSeekProvider"]
