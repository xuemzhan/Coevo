"""Unit tests for the unified model-adapter layer (config + prompts + provider)."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from src.coevo.model import (
    DeepSeekProvider,
    ModelConfig,
    ModelError,
    ModelUnavailableError,
    ModelValidationError,
    NullModelProvider,
    OpenAICompatibleProvider,
    PromptRegistry,
    load_model_config,
    load_prompt_registry,
    parse_json_object,
    select_provider,
)


KEY_ENV = "COEVO_LLM_TEST_KEY"


def _set_key(value: str) -> None:
    os.environ[KEY_ENV] = value


def _clear_key() -> None:
    os.environ.pop(KEY_ENV, None)


class NullProviderTests(unittest.TestCase):
    def test_null_provider_is_unavailable(self):
        with self.assertRaises(ModelUnavailableError):
            NullModelProvider().complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )


class ParseJsonTests(unittest.TestCase):
    def test_parse_json_object_accepts_bounded_object(self):
        self.assertEqual(
            {"a": 1}, parse_json_object('{"a": 1}', max_bytes=1024)
        )

    def test_parse_json_object_rejects_empty_oversized_and_non_object(self):
        with self.assertRaises(ModelValidationError):
            parse_json_object("", max_bytes=1024)
        with self.assertRaises(ModelValidationError):
            parse_json_object('{"a": ' + "1" * 2048 + "}", max_bytes=1024)
        with self.assertRaises(ModelValidationError):
            parse_json_object("not json", max_bytes=1024)
        with self.assertRaises(ModelValidationError):
            parse_json_object("[1,2]", max_bytes=1024)


class ConfigLoaderTests(unittest.TestCase):
    def test_default_config_loads_offline(self):
        config = load_model_config()
        self.assertEqual("offline", config.provider)
        self.assertTrue(str(config.prompts_file).endswith(
            "config" + os.sep + "model-prompts.json"
        ))

    def _write_config(self, tmp: str, payload: dict[str, object]) -> Path:
        path = Path(tmp) / "model-config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _base(self, **overrides: object) -> dict[str, object]:
        payload = {
            "schema_version": "1.0",
            "provider": "offline",
            "prompts_file": "config/model-prompts.json",
            "providers": {
                "deepseek": {
                    "base_url": "https://api.deepseek.com",
                    "model": "deepseek-chat",
                    "api_key_env": KEY_ENV,
                    "timeout_seconds": 30,
                    "max_tokens": 2000,
                    "external_data_ok": False,
                }
            },
        }
        payload.update(overrides)
        return payload

    def test_deepseek_config_loads_and_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_config(
                tmp, self._base(provider="deepseek")
            )
            config = load_model_config(path)
            self.assertEqual("deepseek", config.provider)
            self.assertEqual("deepseek-chat", config.model)
            self.assertEqual(KEY_ENV, config.api_key_env)

    def test_local_openai_config_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = self._base(provider="local_openai")
            payload["providers"]["local_openai"] = {
                "base_url": "http://127.0.0.1:8000/v1",
                "model": "qwen2.5-7b-instruct",
                "api_key_env": KEY_ENV,
                "timeout_seconds": 60,
                "max_tokens": 2000,
                "external_data_ok": True,
            }
            config = load_model_config(self._write_config(tmp, payload))
            self.assertEqual("local_openai", config.provider)
            self.assertEqual("qwen2.5-7b-instruct", config.model)

    def test_loopback_http_is_allowed_in_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = self._base(provider="local_openai")
            payload["providers"]["local_openai"] = {
                "base_url": "http://localhost:8080/v1",
                "model": "m",
                "api_key_env": KEY_ENV,
                "timeout_seconds": 60,
                "max_tokens": 2000,
                "external_data_ok": True,
            }
            config = load_model_config(self._write_config(tmp, payload))
            self.assertEqual("http://localhost:8080/v1", config.base_url)

    def test_malformed_configs_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            for label, payload in (
                ("schema", self._base(schema_version="9.9")),
                ("unknown-field", {**self._base(), "extra": 1}),
                ("bad-provider", self._base(provider="claude")),
                ("missing-deepseek", self._base(provider="deepseek", providers={})),
                ("bad-env-name", self._base(
                    provider="deepseek",
                    providers={"deepseek": {
                        **self._base()["providers"]["deepseek"],
                        "api_key_env": "not an env name",
                    }},
                )),
                ("bad-timeout", self._base(
                    provider="deepseek",
                    providers={"deepseek": {
                        **self._base()["providers"]["deepseek"],
                        "timeout_seconds": 0.5,
                    }},
                )),
                ("bad-tokens", self._base(
                    provider="deepseek",
                    providers={"deepseek": {
                        **self._base()["providers"]["deepseek"],
                        "max_tokens": 99999,
                    }},
                )),
                ("path-escape", self._base(prompts_file="../evil.json")),
                ("http-url", self._base(
                    provider="deepseek",
                    providers={"deepseek": {
                        **self._base()["providers"]["deepseek"],
                        "base_url": "http://api.deepseek.com",
                    }},
                )),
            ):
                with self.subTest(label=label):
                    path = self._write_config(tmp, payload)
                    with self.assertRaises(ModelError):
                        load_model_config(path)


class PromptRegistryTests(unittest.TestCase):
    def test_default_registry_resolves_default_and_model_variant(self):
        config = load_model_config()
        registry = load_prompt_registry(config.prompts_file)
        self.assertIsInstance(registry, PromptRegistry)
        default = registry.resolve("task_decomposition.suggest")
        deepseek = registry.resolve(
            "task_decomposition.suggest",
            provider_key="deepseek/deepseek-chat",
        )
        self.assertNotEqual(default.system, deepseek.system)
        self.assertEqual("default", default.provider_key)
        self.assertEqual("deepseek/deepseek-chat", deepseek.provider_key)

    def test_resolve_missing_prompt_is_fail_closed(self):
        config = load_model_config()
        registry = load_prompt_registry(config.prompts_file)
        with self.assertRaises(ModelError):
            registry.resolve("does.not.exist")

    def test_expand_renders_bounded_placeholders(self):
        config = load_model_config()
        registry = load_prompt_registry(config.prompts_file)
        template = registry.resolve("task_decomposition.suggest")
        rendered = template.expand(
            values={"project": '{"p":1}', "flow": '{"f":2}'},
            max_bytes=64 * 1024,
        )
        self.assertIn('{"p":1}', rendered)
        self.assertIn('{"f":2}', rendered)

    def test_expand_rejects_unknown_placeholder_and_missing_values(self):
        config = load_model_config()
        registry = load_prompt_registry(config.prompts_file)
        template = registry.resolve("task_decomposition.suggest")
        with self.assertRaises(ModelError):
            template.expand(
                values={"project": "p"},
                max_bytes=1024,
            )

    def test_tampered_digest_is_rejected(self):
        config = load_model_config()
        with tempfile.TemporaryDirectory() as tmp:
            raw = json.loads(config.prompts_file.read_text(encoding="utf-8"))
            raw["prompts"][0]["system"] += " tampered"
            path = Path(tmp) / "prompts.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaises(ModelError):
                load_prompt_registry(path)


class DeepSeekProviderTests(unittest.TestCase):
    def _capturing_post(self, responses, captured):
        def post(url, body, headers, timeout_seconds):
            captured.append((url, body, headers, timeout_seconds))
            return responses.pop(0)

        return post

    def _provider(self, *, responses=None, captured=None, **kwargs):
        _set_key("super-secret-key")
        self.addCleanup(_clear_key)
        return DeepSeekProvider(
            api_key_env=KEY_ENV,
            http_post=self._capturing_post(responses, captured)
            if responses is not None else None,
            **kwargs,
        )

    def test_repr_never_exposes_key(self):
        provider = self._provider(external_data_ok=True)
        self.assertNotIn("super-secret-key", repr(provider))
        self.assertIn("configured=True", repr(provider))

    def test_complete_requires_key(self):
        _clear_key()
        provider = DeepSeekProvider(
            api_key_env=KEY_ENV, external_data_ok=True
        )
        with self.assertRaises(ModelUnavailableError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_complete_requires_egress_approval(self):
        provider = self._provider(external_data_ok=False)
        with self.assertRaises(ModelUnavailableError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_complete_sends_expected_request_and_returns_content(self):
        captured = []
        provider = self._provider(
            responses=[
                (
                    200,
                    json.dumps(
                        {"choices": [{"message": {"content": '{"ok": true}'}}]}
                    ).encode("utf-8"),
                )
            ],
            captured=captured,
            external_data_ok=True,
        )
        content = provider.complete(
            system="sys",
            user="usr",
            max_tokens=500,
            timeout_seconds=7,
        )
        self.assertEqual('{"ok": true}', content)
        url, body, headers, timeout = captured[0]
        self.assertTrue(
            url.startswith("https://api.deepseek.com/v1/chat/completions")
        )
        self.assertEqual(7, timeout)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        parsed = json.loads(body.decode("utf-8"))
        self.assertEqual("deepseek-chat", parsed["model"])
        self.assertEqual(500, parsed["max_tokens"])
        self.assertNotIn("super-secret-key", body.decode("utf-8"))

    def test_http_error_is_fail_closed(self):
        provider = self._provider(
            responses=[(429, b"rate limited")],
            captured=[],
            external_data_ok=True,
        )
        with self.assertRaises(ModelError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_malformed_success_response_is_fail_closed(self):
        provider = self._provider(
            responses=[(200, b"not json")],
            captured=[],
            external_data_ok=True,
        )
        with self.assertRaises(ModelValidationError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_missing_choices_is_fail_closed(self):
        provider = self._provider(
            responses=[(200, b'{"error": "boom"}')],
            captured=[],
            external_data_ok=True,
        )
        with self.assertRaises(ModelValidationError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_bounded_arguments_are_enforced(self):
        provider = self._provider(external_data_ok=True)
        with self.assertRaises(ModelError):
            provider.complete(
                system="s", user="u", max_tokens=9000, timeout_seconds=5
            )
        with self.assertRaises(ModelError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=0.5
            )


class LocalProviderTests(unittest.TestCase):
    def _capturing_post(self, responses, captured):
        def post(url, body, headers, timeout_seconds):
            captured.append((url, body, headers, timeout_seconds))
            return responses.pop(0)

        return post

    def test_local_provider_works_without_key_or_egress_approval(self):
        captured = []
        provider = OpenAICompatibleProvider(
            name="local_openai",
            base_url="http://127.0.0.1:8000/v1",
            model="qwen2.5-7b-instruct",
            external_data_ok=False,
            http_post=self._capturing_post(
                [
                    (
                        200,
                        json.dumps(
                            {"choices": [{"message": {"content": "ok"}}]}
                        ).encode("utf-8"),
                    )
                ],
                captured,
            ),
        )
        self.assertTrue(provider.name == "local_openai")
        content = provider.complete(
            system="s", user="u", max_tokens=100, timeout_seconds=5
        )
        self.assertEqual("ok", content)
        url, body, headers, _ = captured[0]
        self.assertEqual(
            "http://127.0.0.1:8000/v1/chat/completions", url
        )
        self.assertNotIn("Authorization", headers)

    def test_endpoint_normalization_adds_v1_when_missing(self):
        captured = []
        provider = OpenAICompatibleProvider(
            name="local_openai",
            base_url="http://127.0.0.1:8080",
            model="m",
            external_data_ok=True,
            http_post=self._capturing_post(
                [
                    (
                        200,
                        json.dumps(
                            {"choices": [{"message": {"content": "ok"}}]}
                        ).encode("utf-8"),
                    )
                ],
                captured,
            ),
        )
        provider.complete(
            system="s", user="u", max_tokens=100, timeout_seconds=5
        )
        self.assertEqual(
            "http://127.0.0.1:8080/v1/chat/completions", captured[0][0]
        )

    def test_remote_http_url_is_rejected(self):
        with self.assertRaises(ModelError):
            OpenAICompatibleProvider(
                name="local_openai",
                base_url="http://api.deepseek.com",
                model="m",
            )

    def test_remote_provider_still_requires_key_and_egress(self):
        provider = OpenAICompatibleProvider(
            name="remote",
            base_url="https://api.example.com/v1",
            model="m",
            external_data_ok=False,
        )
        with self.assertRaises(ModelUnavailableError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )


class ProviderSelectionTests(unittest.TestCase):
    def test_default_selection_is_offline(self):
        provider = select_provider()
        self.assertIsInstance(provider, NullModelProvider)

    def test_deepseek_selection_from_config(self):
        _set_key("k")
        self.addCleanup(_clear_key)
        config = ModelConfig(
            provider="deepseek",
            prompts_file=Path("config/model-prompts.json"),
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
            api_key_env=KEY_ENV,
            timeout_seconds=30,
            max_tokens=2000,
            external_data_ok=True,
        )
        provider = select_provider(config)
        self.assertIsInstance(provider, DeepSeekProvider)

    def test_unsupported_provider_is_rejected(self):
        config = ModelConfig(
            provider="claude",
            prompts_file=Path("config/model-prompts.json"),
        )
        with self.assertRaises(ModelError):
            select_provider(config)

    def test_local_openai_selection(self):
        config = ModelConfig(
            provider="local_openai",
            prompts_file=Path("config/model-prompts.json"),
            base_url="http://127.0.0.1:8000/v1",
            model="qwen2.5-7b-instruct",
            api_key_env=KEY_ENV,
            timeout_seconds=60,
            max_tokens=2000,
            external_data_ok=True,
        )
        provider = select_provider(config)
        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertEqual("local_openai", provider.name)


if __name__ == "__main__":
    unittest.main()
