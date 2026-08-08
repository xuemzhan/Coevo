"""FRAMEWORK-OPTIMIZE-3: shared canonical JSON serialization and digest."""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from src.coevo.canon import canonical_digest, canonical_json_bytes


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "coevo"


class CanonRegressionTests(unittest.TestCase):
    def test_canonical_json_bytes_matches_reference_form(self) -> None:
        sample = {
            "z": 1,
            "a": {"nested": True, "text": "中文"},
            "list": [3, 1, 2],
        }
        expected = json.dumps(
            sample,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        self.assertEqual(expected, canonical_json_bytes(sample))
        expected_utf8 = json.dumps(
            sample,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        self.assertEqual(
            expected_utf8, canonical_json_bytes(sample, ensure_ascii=False)
        )

    def test_canonical_digest_matches_manual_sha256(self) -> None:
        for ensure_ascii in (True, False):
            sample = {"event_id": "ev.1", "actor": "u.pm", "result": "ok"}
            expected = hashlib.sha256(
                json.dumps(
                    sample,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=ensure_ascii,
                ).encode("utf-8")
            ).hexdigest()
            self.assertEqual(
                expected, canonical_digest(sample, ensure_ascii=ensure_ascii)
            )


class CanonGuardTests(unittest.TestCase):
    def test_framework_uses_shared_canonical_serializer(self) -> None:
        for relative in (
            "framework/integration.py",
            "framework/manifest_checker.py",
        ):
            source = (SRC / relative).read_text(encoding="utf-8")
            self.assertNotRegex(
                source,
                r"def _canonical(_bytes)?\(",
                f"{relative} must use src.coevo.canon",
            )

    def test_identity_modules_use_shared_digest(self) -> None:
        for relative in (
            "identity/repository.py",
            "identity/validation.py",
            "identity/private_keys.py",
        ):
            source = (SRC / relative).read_text(encoding="utf-8")
            self.assertNotIn(
                "hashlib.sha256(json.dumps(",
                source,
                f"{relative} must use canonical_digest",
            )

    def test_canon_is_registered_as_root_module(self) -> None:
        root_doc = (ROOT / "docs" / "modules" / "root_modules.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("canon.py", root_doc)
        self.assertIn("canonical_digest", root_doc)

    def test_repository_event_hash_is_reproducible_via_canonical_digest(self) -> None:
        event = {
            "event_id": "ev.1",
            "occurred_at": "2026-08-08T01:00:00.000000Z",
            "actor_id": "u.pm",
            "action": "register",
            "request_id": "r.1",
            "result": "ok",
            "target_summary": json.dumps(
                {"org": "o.1"}, sort_keys=True, separators=(",", ":")
            ),
            "payload_digest": "0" * 64,
            "prev_hash": "0" * 64,
        }
        expected = hashlib.sha256(
            json.dumps(
                event, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        self.assertEqual(expected, canonical_digest(event))


if __name__ == "__main__":
    unittest.main()
