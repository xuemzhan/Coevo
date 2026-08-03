"""DeepSeek chat provider (OpenAI-compatible) over the unified adapter.

Constraints honoured (mandatory-technical-constraints 9.1 / 9.2):

* Replaceable: callers only depend on :class:`ModelProvider`; the
  vendor/model are configuration, not code.
* Fail-closed egress: the provider refuses to send anything unless
  ``external_data_ok=True`` (mirrored by env ``COEVO_LLM_EXTERNAL_DATA_OK``).
  Real sensitive/production data additionally requires a business
  decision per §9.1 -- this slice's default contract is demo/synthetic
  data only.
* The API key is read from ``COEVO_LLM_API_KEY`` (or injected), never
  stored, logged, repr'd or placed in the prompt body.
* Stdlib only (``urllib.request``) -- no new dependency, no runtime
  download. Timeouts are bounded and every failure is fail-closed.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Callable

from .contract import ModelError, ModelUnavailableError, ModelValidationError


HttpPost = Callable[[str, bytes, dict[str, str], float], tuple[int, bytes]]


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
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


class DeepSeekProvider:
    """OpenAI-compatible chat provider (DeepSeek by default)."""

    name = "deepseek"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        external_data_ok: bool | None = None,
        http_post: HttpPost | None = None,
    ) -> None:
        if not base_url.startswith("https://"):
            raise ModelError("base_url must use https")
        self._api_key = api_key or os.environ.get("COEVO_LLM_API_KEY", "")
        self._base_url = base_url.rstrip("/")
        self._model = model
        allowed = external_data_ok
        if allowed is None:
            allowed = os.environ.get("COEVO_LLM_EXTERNAL_DATA_OK", "") == "1"
        self._external_data_ok = bool(allowed)
        self._http_post = http_post or _default_post

    def __repr__(self) -> str:
        # Never expose the key or the base URL's credentials.
        return (
            f"DeepSeekProvider(model={self._model!r}, "
            f"configured={bool(self._api_key)}, "
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
        if not self._api_key:
            raise ModelUnavailableError(
                "DeepSeek API key is not configured (COEVO_LLM_API_KEY)"
            )
        if not self._external_data_ok:
            raise ModelUnavailableError(
                "external model egress is not approved "
                "(set COEVO_LLM_EXTERNAL_DATA_OK=1 and record the "
                "data-class approval in loop/DECISIONS.md)"
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
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        url = f"{self._base_url}/chat/completions"
        status, raw = self._http_post(url, body, headers, timeout_seconds)
        if status != 200:
            raise ModelError(
                f"DeepSeek API returned HTTP {status} "
                f"({len(raw)} bytes, body withheld)"
            )
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ModelValidationError(
                "DeepSeek response is not valid JSON"
            ) from exc
        try:
            choices = parsed["choices"]
            content = choices[0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelValidationError(
                "DeepSeek response is missing choices[0].message.content"
            ) from exc
        if not isinstance(content, str) or not content.strip():
            raise ModelValidationError("DeepSeek response content is empty")
        return content


__all__ = ["DeepSeekProvider"]
