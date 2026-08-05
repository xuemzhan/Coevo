"""Versioned, model-adjustable prompt registry.

Prompts live in a git-tracked data file (`config/model-prompts.json`)
so every change is version controlled. Each template carries a
monotonic ``version`` and a SHA-256 ``digest`` over its content; the
registry re-verifies the digest on every load (tamper detection,
fail-closed).

Personalization per model: resolve by ``(prompt_id, provider_key)``
where ``provider_key`` is ``"<provider>/<model>"`` (e.g.
``"deepseek/deepseek-chat"``); when no exact variant exists the
``"default"`` variant is used. This lets operators tune prompts for
different models without touching business code.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 版本化、可调模型提示词注册表：load_prompt_registry 校验并冻结。
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .contract import ModelError


_SCHEMA_VERSION = "1.0"
_MAX_REGISTRY_BYTES = 256 * 1024
_MAX_PROMPT_ENTRIES = 64
_MAX_STRING_BYTES = 8 * 1024
_ID = re.compile(r"^[a-zA-Z0-9_.\-]{1,128}$")
_PROVIDER_KEY = re.compile(r"^[a-zA-Z0-9_.\-/]{1,128}$")
_PLACEHOLDER = re.compile(r"\{([a-zA-Z0-9_]+)\}")
_KNOWN_PLACEHOLDERS = frozenset({"project", "flow"})


def _digest(
    *,
    prompt_id: str,
    version: int,
    provider_key: str,
    system: str,
    user_template: str,
) -> str:
    payload = "\0".join(
        (prompt_id, str(version), provider_key, system, user_template)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PromptTemplate:
    """A single versioned prompt variant for one provider/model."""

    prompt_id: str
    version: int
    provider_key: str
    system: str
    user_template: str

    def expand(
        self,
        *,
        values: Mapping[str, str],
        max_bytes: int,
    ) -> str:
        """Expand bounded placeholders; fail-closed on unknown keys."""
        unknown_placeholders = {
            name
            for name in _PLACEHOLDER.findall(self.user_template)
            if name not in _KNOWN_PLACEHOLDERS
        }
        if unknown_placeholders:
            raise ModelError(
                f"prompt {self.prompt_id!r} has unknown placeholders: "
                f"{sorted(unknown_placeholders)}"
            )
        missing = _KNOWN_PLACEHOLDERS - set(values)
        if missing:
            raise ModelError(
                f"prompt {self.prompt_id!r} is missing values for {sorted(missing)}"
            )
        rendered = self.user_template.format(**values)
        if len(rendered.encode("utf-8")) > max_bytes:
            raise ModelError("expanded prompt exceeds the size limit")
        return rendered


class PromptRegistry:
    """Loaded and validated prompt registry from a data file."""

    def __init__(self, templates: tuple[PromptTemplate, ...]) -> None:
        self._templates = templates

    def resolve(
        self,
        prompt_id: str,
        *,
        provider_key: str | None = None,
    ) -> PromptTemplate:
        """Resolve by (id, provider_key) with fallback to 'default'."""
        if provider_key is not None:
            for template in self._templates:
                if (
                    template.prompt_id == prompt_id
                    and template.provider_key == provider_key
                ):
                    return template
        for template in self._templates:
            if (
                template.prompt_id == prompt_id
                and template.provider_key == "default"
            ):
                return template
        raise ModelError(f"no prompt template for {prompt_id!r}")


def load_prompt_registry(path: Path | str) -> PromptRegistry:
    """Load and validate the prompt data file (fail-closed)."""
    registry_path = Path(path).resolve()
    try:
        raw_bytes = registry_path.read_bytes()
    except OSError as exc:
        raise ModelError(f"prompt file is unreadable: {registry_path}") from exc
    if len(raw_bytes) > _MAX_REGISTRY_BYTES:
        raise ModelError("prompt file exceeds the size limit")
    try:
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ModelError("prompt file is not valid JSON") from exc
    if not isinstance(raw, dict) or raw.get("schema_version") != _SCHEMA_VERSION:
        raise ModelError("prompt file schema_version mismatch")
    prompts = raw.get("prompts")
    if (
        not isinstance(prompts, list)
        or not prompts
        or len(prompts) > _MAX_PROMPT_ENTRIES
    ):
        raise ModelError("prompt file prompts must be a bounded list")
    templates: list[PromptTemplate] = []
    seen: set[tuple[str, str]] = set()
    for raw_entry in prompts:
        if not isinstance(raw_entry, dict):
            raise ModelError("prompt entry must be an object")
        try:
            prompt_id = raw_entry["id"]
            version = raw_entry["version"]
            provider_key = raw_entry["provider_key"]
            system = raw_entry["system"]
            user_template = raw_entry["user_template"]
            digest = raw_entry["digest"]
        except KeyError as exc:
            raise ModelError(
                f"prompt entry missing field {exc.args[0]!r}"
            ) from exc
        if not _ID.fullmatch(prompt_id):
            raise ModelError(f"unsafe prompt id {prompt_id!r}")
        if not isinstance(version, int) or version < 1:
            raise ModelError(f"prompt {prompt_id!r} version must be >= 1")
        if not _PROVIDER_KEY.fullmatch(provider_key):
            raise ModelError(f"unsafe provider_key {provider_key!r}")
        for value, name in (
            (system, "system"),
            (user_template, "user_template"),
        ):
            if (
                not isinstance(value, str)
                or not value.strip()
                or len(value.encode("utf-8")) > _MAX_STRING_BYTES
            ):
                raise ModelError(f"prompt {prompt_id!r} {name} is invalid")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest)
        ):
            raise ModelError(f"prompt {prompt_id!r} digest is invalid")
        key = (prompt_id, provider_key)
        if key in seen:
            raise ModelError(f"duplicate prompt entry {key!r}")
        seen.add(key)
        expected = _digest(
            prompt_id=prompt_id,
            version=version,
            provider_key=provider_key,
            system=system,
            user_template=user_template,
        )
        if digest != expected:
            raise ModelError(
                f"prompt {prompt_id!r}/{provider_key!r} digest mismatch "
                "(tampered or not regenerated)"
            )
        templates.append(
            PromptTemplate(
                prompt_id=prompt_id,
                version=version,
                provider_key=provider_key,
                system=system,
                user_template=user_template,
            )
        )
    return PromptRegistry(tuple(templates))


__all__ = ["PromptRegistry", "PromptTemplate", "load_prompt_registry"]
