"""Model access configuration from a versioned config file.

The config file (`config/model-config.json`, tracked in git) holds
non-secret provider settings only. The API key is referenced by
environment-variable *name* (``api_key_env``) and never stored in the
file. Loading is fail-closed: unknown keys, malformed values or
out-of-range numbers are rejected.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 模型访问配置：版本化配置文件加载与校验，失败关闭。
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .contract import ModelError
from .openai_compatible import is_loopback


_SCHEMA_VERSION = "1.0"
_MAX_CONFIG_BYTES = 64 * 1024
_ENV_NAME = re.compile(r"^[A-Z_][A-Z0-9_]{0,63}$")


@dataclass(frozen=True)
class ModelConfig:
    """Validated non-secret model access configuration."""

    provider: str  # "offline" | "deepseek"
    prompts_file: Path
    base_url: str | None = None
    model: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = 30.0
    max_tokens: int = 2000
    external_data_ok: bool = False


def _default_config_path() -> Path:
    return Path(__file__).resolve().parents[3] / "config" / "model-config.json"


def _validate_provider_entry(name: str, raw: object) -> dict[str, object]:
    if not isinstance(raw, dict):
        raise ModelError(f"provider {name!r} must be an object")
    allowed = {
        "base_url",
        "model",
        "api_key_env",
        "timeout_seconds",
        "max_tokens",
        "external_data_ok",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ModelError(
            f"provider {name!r} has unknown fields: {sorted(unknown)}"
        )
    base_url = raw.get("base_url", "https://api.deepseek.com")
    model = raw.get("model", "deepseek-chat")
    api_key_env = raw.get("api_key_env", "COEVO_LLM_API_KEY")
    timeout = raw.get("timeout_seconds", 30.0)
    max_tokens = raw.get("max_tokens", 2000)
    egress = raw.get("external_data_ok", False)
    if not isinstance(base_url, str) or not (
        base_url.startswith("https://")
        or (base_url.startswith("http://") and is_loopback(base_url))
    ):
        raise ModelError(
            f"provider {name!r} base_url must be https or loopback http"
        )
    if (
        not isinstance(model, str)
        or not model.strip()
        or len(model.encode("utf-8")) > 128
    ):
        raise ModelError(f"provider {name!r} model is invalid")
    if api_key_env is None:
        api_key_env = "COEVO_LLM_API_KEY"
    if not isinstance(api_key_env, str) or not _ENV_NAME.fullmatch(api_key_env):
        raise ModelError(f"provider {name!r} api_key_env is invalid")
    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or not 1 <= float(timeout) <= 60
    ):
        raise ModelError(f"provider {name!r} timeout_seconds out of range")
    if (
        not isinstance(max_tokens, int)
        or isinstance(max_tokens, bool)
        or not 0 < max_tokens <= 8000
    ):
        raise ModelError(f"provider {name!r} max_tokens out of range")
    if not isinstance(egress, bool):
        raise ModelError(f"provider {name!r} external_data_ok must be bool")
    return {
        "base_url": base_url,
        "model": model,
        "api_key_env": api_key_env,
        "timeout_seconds": float(timeout),
        "max_tokens": max_tokens,
        "external_data_ok": egress,
    }


def load_model_config(path: Path | str | None = None) -> ModelConfig:
    """Load and validate the model config file (fail-closed)."""
    config_path = Path(path) if path is not None else _default_config_path()
    config_path = config_path.resolve()
    try:
        raw_bytes = config_path.read_bytes()
    except OSError as exc:
        raise ModelError(f"model config file is unreadable: {config_path}") from exc
    if len(raw_bytes) > _MAX_CONFIG_BYTES:
        raise ModelError("model config exceeds the size limit")
    try:
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ModelError("model config is not valid JSON") from exc
    if not isinstance(raw, dict):
        raise ModelError("model config must be a JSON object")
    allowed_top = {
        "schema_version",
        "provider",
        "prompts_file",
        "providers",
    }
    unknown = set(raw) - allowed_top
    if unknown:
        raise ModelError(f"model config has unknown fields: {sorted(unknown)}")
    if raw.get("schema_version") != _SCHEMA_VERSION:
        raise ModelError("model config schema_version mismatch")
    provider = raw.get("provider")
    if provider not in {"offline", "deepseek", "local_openai"}:
        raise ModelError(
            "model config provider must be 'offline', 'deepseek' or 'local_openai'"
        )
    prompts_file = raw.get("prompts_file")
    if (
        not isinstance(prompts_file, str)
        or not prompts_file
        or prompts_file.startswith(("/", "\\"))
        or ".." in Path(prompts_file).parts
    ):
        raise ModelError("model config prompts_file must be a safe relative path")
    providers_raw = raw.get("providers", {})
    if not isinstance(providers_raw, dict):
        raise ModelError("model config providers must be an object")
    extra = set(providers_raw) - {"deepseek", "local_openai"}
    if extra:
        raise ModelError(
            f"model config has unsupported providers: {sorted(extra)}"
        )
    entry = None
    provider_entry = providers_raw.get(provider, {}) if provider != "offline" else {}
    if provider in {"deepseek", "local_openai"}:
        if provider not in providers_raw:
            raise ModelError(
                f"model config provider is {provider!r} but its entry is missing"
            )
        entry = _validate_provider_entry(provider, provider_entry)
    repo_root = config_path.parent.parent
    return ModelConfig(
        provider=provider,
        prompts_file=(repo_root / prompts_file).resolve(),
        base_url=entry["base_url"] if entry else None,
        model=entry["model"] if entry else None,
        api_key_env=entry["api_key_env"] if entry else None,
        timeout_seconds=entry["timeout_seconds"] if entry else 30.0,
        max_tokens=entry["max_tokens"] if entry else 2000,
        external_data_ok=entry["external_data_ok"] if entry else False,
    )


__all__ = ["ModelConfig", "load_model_config"]
