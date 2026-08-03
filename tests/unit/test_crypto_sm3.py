"""CRYPTO-1: pure-Python SM3 (GB/T 32905) correctness tests."""
from __future__ import annotations

import unittest

from src.coevo.crypto.sm3 import sm3_digest, sm3_hexdigest


# Official GB/T 32905 / GM/T 0004 test vectors (widely published).
_OFFICIAL_VECTORS = {
    b"": "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b",
    b"abc": "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0",
}


class Sm3OfficialVectorsTests(unittest.TestCase):
    def test_official_vectors(self):
        for message, expected in _OFFICIAL_VECTORS.items():
            self.assertEqual(expected, sm3_hexdigest(message), message)
            self.assertEqual(32, len(sm3_digest(message)), message)

    def test_abc_vector_hex_is_64_lowercase(self):
        digest = sm3_hexdigest(b"abc")
        self.assertEqual(64, len(digest))
        self.assertTrue(digest.islower())
        self.assertTrue(all(c in "0123456789abcdef" for c in digest))


class Sm3BoundaryTests(unittest.TestCase):
    def test_padding_boundaries(self):
        # 55/56/63/64-byte messages exercise every padding branch
        # (message length modulo 64 == 55/56/63/0).
        for size in (55, 56, 63, 64, 65, 127, 128):
            message = bytes(range(size % 251 + 1)) * ((size // 251) + 1)
            message = message[:size]
            self.assertEqual(64, len(sm3_hexdigest(message)), size)

    def test_deterministic(self):
        self.assertEqual(sm3_hexdigest(b"x" * 1000), sm3_hexdigest(b"x" * 1000))

    def test_empty_message(self):
        self.assertEqual(
            "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b",
            sm3_hexdigest(b""),
        )

    def test_digest_and_hex_agree(self):
        message = b"coevo"
        self.assertEqual(sm3_digest(message), bytes.fromhex(sm3_hexdigest(message)))


class Sm3InputValidationTests(unittest.TestCase):
    def test_rejects_non_bytes(self):
        for bad in ("abc", bytearray(b"abc"), 42, None):
            with self.assertRaises(TypeError):
                sm3_digest(bad)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
