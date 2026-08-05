"""OpenAI-compatible chat provider (vLLM / llama.cpp / DeepSeek).

Both vLLM and llama.cpp serve an OpenAI-compatible
``/v1/chat/completions`` endpoint, so a single provider covers local
model serving (production v1) and remote services.

Local vs remote (mandatory constraint 9.1)
------------------------------------------
* ``base_url`` on a loopback host (127.0.0.1 / localhost / ::1) is
  **local mode**: data never leaves the machine, so no external-egress
  approval is required and the API key is optional (vLLM / llama.cpp
  run key-less by default).
* Any other host requires **https** plus an API key and the
  ``external_data_ok`` approval switch (fail-closed egress).
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# OpenAI 兼容聊天提供者（vLLM/llama.cpp/DeepSeek）：环回校验 + 超时。
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Callable, Final
from urllib.parse import urlparse

from .contract import ModelError, ModelUnavailableError, ModelValidationError


HttpPost = Callable[[str, bytes, dict[str, str], float], tuple[int, bytes]]
_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
MAX_RESPONSE_BYTES: Final[int] = 4 * 1024 * 1024
RESPONSE_OVERHEAD_BYTES: Final[int] = 32 * 1024
MAX_POST_ATTEMPTS: Final[int] = 2


def is_loopback(url: str) -> bool:
    """True when ``url`` targets a loopback host."""
    try:
        return urlparse(url).hostname in _LOOPBACK_HOSTS
    except ValueError:
        return False


def _default_post(
    url: str,
    body: bytes,
    headers: dict[str, str],
    timeout_seconds: float,
) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url, data=body, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ModelValidationError(
                    "model response exceeds the hard size limit"
                )
            return response.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ModelValidationError(
                "model error response exceeds the hard size limit"
            )
        return exc.code, raw


class OpenAICompatibleProvider:
    """OpenAI-compatible chat provider with local/remote fail-closed modes."""

    def __init__(
        self,
        *,
        name: str,
        api_key_env: str = "COEVO_LLM_API_KEY",
        base_url: str,
        model: str,
        external_data_ok: bool = False,
        http_post: HttpPost | None = None,
    ) -> None:
        if not isinstance(name, str) or not name:
            raise ModelError("provider name must be a non-empty string")
        parsed = urlparse(base_url)
        if parsed.scheme != "https" and not (
            parsed.scheme == "http" and is_loopback(base_url)
        ):
            raise ModelError(
                "base_url must be https or http on a loopback host"
            )
        self._name = name
        self._api_key_env = api_key_env
        base = base_url.rstrip("/")
        if not base.endswith("/v1"):
            self._endpoint = f"{base}/v1/chat/completions"
        else:
            self._endpoint = f"{base}/chat/completions"
        self._model = model
        self._external_data_ok = bool(external_data_ok)
        self._local = is_loopback(base_url)
        self._http_post = http_post or _default_post

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return (
            f"OpenAICompatibleProvider(name={self._name!r}, "
            f"model={self._model!r}, local={self._local}, "
            f"configured={bool(os.environ.get(self._api_key_env))}, "
            f"external_data_ok={self._external_data_ok})"
        )

    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int,
        timeout_seconds: float,
    ) -> str:
        """Complete a chat request via the compatible endpoint."""
        api_key = os.environ.get(self._api_key_env, "")
        if not self._local:
            if not api_key:
                raise ModelUnavailableError(
                    f"API key is not configured ({self._api_key_env})"
                )
            if not self._external_data_ok:
                raise ModelUnavailableError(
                    "external model egress is not approved "
                    "(set external_data_ok and record the data-class "
                    "approval in loop/DECISIONS.md)"
                )
        if not 0 < max_tokens <= 8000:
            raise ModelError("max_tokens must be in (0, 8000]")
        if not 1 <= timeout_seconds <= 60:
            raise ModelError("timeout_seconds must be in [1, 60]")
        if not isinstance(system, str) or not system:
            raise ModelError("system prompt must be a non-empty string")
        if not isinstance(user, str) or not user:
            raise ModelError("user prompt must be a non-empty string")
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "stream": False,
        }
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        attempt = 0
        while True:
            attempt += 1
            try:
                status, raw = self._http_post(
                    self._endpoint, body, headers, timeout_seconds
                )
                break
            except (urllib.error.URLError, OSError, TimeoutError) as exc:
                if attempt >= MAX_POST_ATTEMPTS:
                    raise ModelUnavailableError(
                        f"model API unreachable after {attempt} attempts ({exc})"
                    ) from exc
                # Connection-class transient failure: retry once. HTTP
                # error statuses (non-200) and validation failures are
                # never retried (fail-closed).
        max_response_bytes = RESPONSE_OVERHEAD_BYTES + max_tokens * 8
        if len(raw) > max_response_bytes:
            raise ModelValidationError(
                "model response exceeds the size limit for "
                f"max_tokens={max_tokens} ({len(raw)} bytes)"
            )
        if status != 200:
            raise ModelError(
                f"model API returned HTTP {status} "
                f"({len(raw)} bytes, body withheld)"
            )
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ModelValidationError(
                "model response is not valid JSON"
            ) from exc
        try:
            choices = parsed["choices"]
            content = choices[0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelValidationError(
                "model response is missing choices[0].message.content"
            ) from exc
        if not isinstance(content, str) or not content.strip():
            raise ModelValidationError("model response content is empty")
        return content


__all__ = ["OpenAICompatibleProvider", "is_loopback"]
