"""FRAMEWORK-OPTIMIZE-10: audit_anchor canonical unifies onto canon."""

from __future__ import annotations

import unittest
import hashlib
from pathlib import Path

from src.coevo.canon import canonical_digest, canonical_json_bytes, canonical_json_str
from src.coevo.identity.audit_anchor import canonical


ROOT = Path(__file__).resolve().parents[2]


class TrailingNewlineTests(unittest.TestCase):
    def test_default_has_no_trailing_newline(self) -> None:
        self.assertEqual(b'{"a":1}', canonical_json_bytes({"a": 1}))
        self.assertEqual('{"a":1}', canonical_json_str({"a": 1}))

    def test_trailing_newline_appended_to_all_variants(self) -> None:
        sample = {"a": "中文", "b": 2}
        expected = canonical_json_bytes(sample, ensure_ascii=False) + b"\n"
        self.assertEqual(
            expected,
            canonical_json_bytes(
                sample, ensure_ascii=False, trailing_newline=True
            ),
        )
        self.assertEqual(
            expected.decode("utf-8"),
            canonical_json_str(
                sample, ensure_ascii=False, trailing_newline=True
            ),
        )
        self.assertEqual(
            hashlib.sha256(expected).hexdigest(),
            canonical_digest(
                sample, ensure_ascii=False, trailing_newline=True
            ),
        )


class AuditAnchorCanonicalTests(unittest.TestCase):
    def test_audit_anchor_canonical_matches_shared_canon(self) -> None:
        sample = {"schema_version": "3.0", "nested": {"x": 1}, "text": "中文"}
        self.assertEqual(
            canonical_json_bytes(
                sample, ensure_ascii=False, trailing_newline=True
            ),
            canonical(sample),
        )
        self.assertTrue(canonical(sample).endswith(b"\n"))

    def test_audit_anchor_no_longer_serializes_inline(self) -> None:
        source = (
            ROOT / "src" / "coevo" / "identity" / "audit_anchor.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("json.dumps(", source)


if __name__ == "__main__":
    unittest.main()
