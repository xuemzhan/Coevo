"""Unit tests for the unified model-adapter layer (DeepSeek provider)."""
from __future__ import annotations

import json
import unittest

from src.coevo.model import (
    DeepSeekProvider,
    ModelError,
    ModelUnavailableError,
    ModelValidationError,
    NullModelProvider,
    parse_json_object,
    select_provider,
)


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


class DeepSeekProviderTests(unittest.TestCase):
    def _capturing_post(self, responses, captured):
        def post(url, body, headers, timeout_seconds):
            captured.append((url, body, headers, timeout_seconds))
            return responses.pop(0)

        return post

    def test_repr_never_exposes_key(self):
        provider = DeepSeekProvider(
            api_key="super-secret-key",
            external_data_ok=True,
        )
        self.assertNotIn("super-secret-key", repr(provider))

    def test_complete_requires_key(self):
        provider = DeepSeekProvider(api_key="", external_data_ok=True)
        with self.assertRaises(ModelUnavailableError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_complete_requires_egress_approval(self):
        provider = DeepSeekProvider(
            api_key="k", external_data_ok=False
        )
        with self.assertRaises(ModelUnavailableError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_complete_sends_expected_request_and_returns_content(self):
        captured = []
        provider = DeepSeekProvider(
            api_key="secret-key",
            external_data_ok=True,
            http_post=self._capturing_post(
                [
                    (
                        200,
                        json.dumps(
                            {
                                "choices": [
                                    {"message": {"content": '{"ok": true}'}}
                                ]
                            }
                        ).encode("utf-8"),
                    )
                ],
                captured,
            ),
        )
        content = provider.complete(
            system="sys",
            user="usr",
            max_tokens=500,
            timeout_seconds=7,
        )
        self.assertEqual('{"ok": true}', content)
        url, body, headers, timeout = captured[0]
        self.assertTrue(url.startswith("https://api.deepseek.com/chat/completions"))
        self.assertEqual(7, timeout)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        parsed = json.loads(body.decode("utf-8"))
        self.assertEqual("deepseek-chat", parsed["model"])
        self.assertEqual(500, parsed["max_tokens"])
        # the key must never appear in the request body
        self.assertNotIn("secret-key", body.decode("utf-8"))

    def test_http_error_is_fail_closed(self):
        provider = DeepSeekProvider(
            api_key="k",
            external_data_ok=True,
            http_post=self._capturing_post([(429, b"rate limited")], []),
        )
        with self.assertRaises(ModelError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_malformed_success_response_is_fail_closed(self):
        provider = DeepSeekProvider(
            api_key="k",
            external_data_ok=True,
            http_post=self._capturing_post([(200, b"not json")], []),
        )
        with self.assertRaises(ModelValidationError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_missing_choices_is_fail_closed(self):
        provider = DeepSeekProvider(
            api_key="k",
            external_data_ok=True,
            http_post=self._capturing_post(
                [(200, b'{"error": "boom"}')], []
            ),
        )
        with self.assertRaises(ModelValidationError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=5
            )

    def test_bounded_arguments_are_enforced(self):
        provider = DeepSeekProvider(api_key="k", external_data_ok=True)
        with self.assertRaises(ModelError):
            provider.complete(
                system="s", user="u", max_tokens=9000, timeout_seconds=5
            )
        with self.assertRaises(ModelError):
            provider.complete(
                system="s", user="u", max_tokens=100, timeout_seconds=0.5
            )


class ProviderSelectionTests(unittest.TestCase):
    def test_default_selection_is_offline(self):
        provider = select_provider()
        self.assertIsInstance(provider, NullModelProvider)

    def test_deepseek_selection_without_key_constructs_but_fails_closed(self):
        import os

        os.environ["COEVO_LLM_PROVIDER"] = "deepseek"
        try:
            os.environ.pop("COEVO_LLM_API_KEY", None)
            provider = select_provider()
            self.assertIsInstance(provider, DeepSeekProvider)
            with self.assertRaises(ModelUnavailableError):
                provider.complete(
                    system="s", user="u", max_tokens=100, timeout_seconds=5
                )
        finally:
            os.environ.pop("COEVO_LLM_PROVIDER", None)

    def test_unsupported_provider_is_rejected(self):
        import os

        os.environ["COEVO_LLM_PROVIDER"] = "claude"
        try:
            with self.assertRaises(ModelError):
                select_provider()
        finally:
            os.environ.pop("COEVO_LLM_PROVIDER", None)


if __name__ == "__main__":
    unittest.main()
