"""FRAMEWORK-OPTIMIZE-5: real_chain_store converges onto shared canon."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.canon import canonical_digest, canonical_json_bytes
from src.coevo.orchestrator.real_chain_store import (
    RealChainStoreError,
    canonical_digest as store_digest,
    canonical_json_bytes as store_bytes,
)


ROOT = Path(__file__).resolve().parents[2]


class CanonAllowNanTests(unittest.TestCase):
    def test_canon_rejects_nan_by_default(self) -> None:
        with self.assertRaises(ValueError):
            canonical_json_bytes({"x": float("nan")})
        with self.assertRaises(ValueError):
            canonical_digest({"x": float("inf")})

    def test_canon_allows_nan_when_explicit(self) -> None:
        self.assertEqual(
            b'{"x":NaN}',
            canonical_json_bytes({"x": float("nan")}, allow_nan=True),
        )


class RealChainStoreCanonTests(unittest.TestCase):
    def test_store_bytes_match_shared_canon(self) -> None:
        sample = {
            "z": 1,
            "a": {"nested": True, "text": "中文"},
            "list": [3, 1, 2],
        }
        self.assertEqual(
            canonical_json_bytes(sample, ensure_ascii=False, allow_nan=False),
            store_bytes(sample),
        )
        self.assertEqual(
            canonical_digest(sample, ensure_ascii=False, allow_nan=False),
            store_digest(sample),
        )

    def test_store_rejects_non_finite_float_fail_closed(self) -> None:
        with self.assertRaises(RealChainStoreError):
            store_bytes({"v": float("nan")})
        with self.assertRaises(RealChainStoreError):
            store_digest({"v": float("inf")})

    def test_store_rejects_non_json_value_fail_closed(self) -> None:
        with self.assertRaises(RealChainStoreError):
            store_bytes({"v": object()})

    def test_store_no_longer_serializes_inline(self) -> None:
        source = (ROOT / "src" / "coevo" / "orchestrator" / "real_chain_store.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("json.dumps(", source)


if __name__ == "__main__":
    unittest.main()
