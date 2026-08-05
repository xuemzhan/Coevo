"""Pure-Python SM3 cryptographic hash (GB/T 32905-2016).

CRYPTO-1 (2026-08-03): the business owner approved replacing the
SHA-256 stand-in used for the protocol's SM3 digest with a real SM3
implementation. This module is a small, deterministic, dependency-free
SM3 written against the published standard, validated against the
official test vectors and cross-checked against the locked GmSSL 3.2.0
engine (see ``tests/integration/test_crypto_sm3.py``).

The implementation follows GB/T 32905-2016 (SM3):

* message padding: ``0x80`` + zeros until length ≡ 56 (mod 64),
  then the 64-bit big-endian message bit length;
* eight 32-bit state words initialised to the standard IV;
* 64-round compression with message expansion ``W`` / ``W'``;
* boolean functions ``FF`` / ``GG`` and permutations ``P0`` / ``P1``.

Only bytes are accepted; no str/bytearray aliasing is performed, so
callers cannot accidentally pass a text message. The output is the
32-byte SM3 digest (``digest()``) or its lowercase hex form
(``hexdigest()``) — the same 64-char wire format the protocol uses.

Security note: pure-Python SM3 is not constant-time in the way a
hardware or C implementation would be, and it is not a nationally
certified module. It is approved for this project's functional path
as an offline, verifiable digest; national-certification remains the
long-term requirement (see ``docs/dependencies/approved-crypto-provider-path.md``).
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 纯 Python SM3 哈希（GB/T 32905-2016），零依赖离线实现。
from __future__ import annotations

from typing import Final


_MASK32: Final[int] = 0xFFFFFFFF
_IV: Final[tuple[int, ...]] = (
    0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
    0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E,
)
_T_LEFT: Final[int] = 0x79CC4519
_T_RIGHT: Final[int] = 0x7A879D8A


def _rotl(value: int, bits: int) -> int:
    bits %= 32  # GB/T 32905 rotates by j (0..63); a 32-bit word wraps mod 32
    return ((value << bits) | (value >> (32 - bits))) & _MASK32


def _p0(value: int) -> int:
    return value ^ _rotl(value, 9) ^ _rotl(value, 17)


def _p1(value: int) -> int:
    return value ^ _rotl(value, 15) ^ _rotl(value, 23)


def _ff(round_index: int, x: int, y: int, z: int) -> int:
    if round_index < 16:
        return x ^ y ^ z
    return (x & y) | (x & z) | (y & z)


def _gg(round_index: int, x: int, y: int, z: int) -> int:
    if round_index < 16:
        return x ^ y ^ z
    return (x & y) | ((~x) & z)


def _compress(state: list[int], block: bytes) -> None:
    words = [
        int.from_bytes(block[offset : offset + 4], "big")
        for offset in range(0, 64, 4)
    ]
    w: list[int] = [0] * 68
    w_prime: list[int] = [0] * 64
    w[:16] = words
    for j in range(16, 68):
        w[j] = (
            _p1(w[j - 16] ^ w[j - 9] ^ _rotl(w[j - 3], 15))
            ^ _rotl(w[j - 13], 7)
            ^ w[j - 6]
        ) & _MASK32
    for j in range(64):
        w_prime[j] = w[j] ^ w[j + 4]

    a, b, c, d, e, f, g, h = state
    for j in range(64):
        t = _T_LEFT if j < 16 else _T_RIGHT
        ss1 = _rotl((_rotl(a, 12) + e + _rotl(t, j)) & _MASK32, 7)
        ss2 = ss1 ^ _rotl(a, 12)
        tt1 = (_ff(j, a, b, c) + d + ss2 + w_prime[j]) & _MASK32
        tt2 = (_gg(j, e, f, g) + h + ss1 + w[j]) & _MASK32
        d = c
        c = _rotl(b, 9)
        b = a
        a = tt1
        h = g
        g = _rotl(f, 19)
        f = e
        e = _p0(tt2)
    state[0] = (state[0] ^ a) & _MASK32
    state[1] = (state[1] ^ b) & _MASK32
    state[2] = (state[2] ^ c) & _MASK32
    state[3] = (state[3] ^ d) & _MASK32
    state[4] = (state[4] ^ e) & _MASK32
    state[5] = (state[5] ^ f) & _MASK32
    state[6] = (state[6] ^ g) & _MASK32
    state[7] = (state[7] ^ h) & _MASK32


def sm3_digest(data: bytes) -> bytes:
    """Return the 32-byte SM3 digest of ``data`` (bytes only)."""
    if not isinstance(data, bytes):
        raise TypeError("sm3 digest input must be bytes")
    length_bits = len(data) * 8
    padded = bytearray(data)
    padded.append(0x80)
    while len(padded) % 64 != 56:
        padded.append(0x00)
    padded.extend(length_bits.to_bytes(8, "big"))

    state = list(_IV)
    for offset in range(0, len(padded), 64):
        _compress(state, bytes(padded[offset : offset + 64]))
    return b"".join(word.to_bytes(4, "big") for word in state)


def sm3_hexdigest(data: bytes) -> str:
    """Return the 64-char lowercase hex SM3 digest of ``data``."""
    return sm3_digest(data).hex()


__all__ = ["sm3_digest", "sm3_hexdigest"]
