"""FRAMEWORK-OPTIMIZE-9: remaining canonical serialization consolidation."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.canon import canonical_json_bytes, canonical_json_str


ROOT = Path(__file__).resolve().parents[2]


class CanonicalJsonStrTests(unittest.TestCase):
    def test_str_variant_matches_bytes_variant(self) -> None:
        sample = {"z": 1, "a": {"nested": True, "text": "中文"}, "list": [3, 1]}
        for ensure_ascii in (True, False):
            self.assertEqual(
                canonical_json_bytes(sample, ensure_ascii=ensure_ascii),
                canonical_json_str(sample, ensure_ascii=ensure_ascii).encode(
                    "utf-8"
                ),
            )

    def test_str_variant_rejects_nan_by_default(self) -> None:
        with self.assertRaises(ValueError):
            canonical_json_str({"x": float("nan")})


class CanonicalConsolidationGuardTests(unittest.TestCase):
    def test_modules_no_longer_serialize_canonical_json_inline(self) -> None:
        expectations = {
            "src/coevo/cockpit/state_store.py": 0,
            "src/coevo/knowledge_base/store.py": 0,
            "src/coevo/audit_governance/stream_store.py": 0,
            "src/coevo/talent/store.py": 0,
        }
        for relative, expected in expectations.items():
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertEqual(
                expected,
                source.count("json.dumps("),
                f"{relative} must not serialize canonical JSON inline",
            )

    def test_cng_handle_keeps_only_non_canonical_request_body(self) -> None:
        source = (ROOT / "src" / "coevo" / "crypto" / "cng_handle.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("def _canonical", source)
        self.assertEqual(1, source.count("json.dumps("))
        self.assertNotIn("sort_keys=True", source)
        self.assertIn("canonical_json_bytes", source)


if __name__ == "__main__":
    unittest.main()
