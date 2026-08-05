"""US-5 SM2 key-transport layer (US-5-AC-2 / 协议 § 7.3).

Scope
-----
Each task package carries an SM4 session key that is wrapped under
the recipient's SM2 public key (协议 § 7.3). This module implements
the wire encoding for the wrapped-key block and the deterministic
session-key generator. The actual SM2 key-transport operation is
**fail-closed** in this slice — calling :func:`wrap_session_key`
or :func:`unwrap_session_key` raises
:class:`AgentPackageCryptoUnavailableError` until an approved SM2
product is wired in.

Wire format (协议 § 7.3)::

    {
      "format": "SM2-KEY-TRANSPORT-V1",
      "recipient_cert_id": "<cert>",
      "ephemeral_public_key": "<base64>",
      "wrapped_key": "<base64>",
      "kdf_params": {
        "kdf": "SM3-KDF-V1",
        "salt": "<base64>",
        "iterations": 1
      },
      "wrapped_at": "<ISO-8601 UTC 'Z'>"
    }

The block is stored in the ``key_block`` byte slice between the
Envelope Header and the Encrypted Inner Payload. Length is bounded
by 协议 § 19.3 (capacity limits).

Non-goals
---------
* No actual SM2 operation (P1 path).
* No IO, no model, no network.
* No mutation of US-5-AC-1 fixed header / envelope wire layout.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-5 SM2 密钥传输层（§7.3）：会话密钥封装/解封，规范编码。
from __future__ import annotations

import datetime as dt
import json
import secrets
from dataclasses import dataclass
from typing import Final

from .agent_package import AgentPackageError


KEY_BLOCK_FORMAT: Final[str] = "SM2-KEY-TRANSPORT-V1"
KDF_NAME: Final[str] = "SM3-KDF-V1"
SESSION_KEY_SIZE: Final[int] = 16   # SM4-128
EPHEMERAL_PUBKEY_MAX: Final[int] = 512  # raw EC point, generous cap
WRAPPED_KEY_MAX: Final[int] = 256  # ciphertext, generous cap
KDF_SALT_SIZE: Final[int] = 16
KDF_ITERATIONS_DEFAULT: Final[int] = 1


class AgentPackageCryptoUnavailableError(AgentPackageError):
    """Raised when the SM2 key-transport operation is requested.

    AGENTS.md §6 forbids assuming an approved SM2 product. Stable
    code AGT-CRY-001 per 协议 § 22.
    """

    code: str = "AGT-CRY-001"


@dataclass(frozen=True)
class KeyTransportBlock:
    """协议 § 7.3 wrapped session key block."""

    format: str
    recipient_cert_id: str
    ephemeral_public_key: str    # base64
    wrapped_key: str             # base64
    kdf_params: tuple[tuple[str, object], ...]
    wrapped_at: str              # ISO-8601 UTC 'Z'

    def to_mapping(self) -> dict[str, object]:
        """Serialize a key-transport block to a mapping."""
        return {
            "format": self.format,
            "recipient_cert_id": self.recipient_cert_id,
            "ephemeral_public_key": self.ephemeral_public_key,
            "wrapped_key": self.wrapped_key,
            "kdf_params": dict(self.kdf_params),
            "wrapped_at": self.wrapped_at,
        }


def _now_utc_iso_z() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def generate_session_key() -> bytes:
    """Return a fresh SM4-128 session key from a CSPRNG.

    协议 § 11 第 3 条: "禁止使用时间戳生成密钥". We use
    :mod:`secrets` (CSPRNG).
    """
    return secrets.token_bytes(SESSION_KEY_SIZE)


def build_key_transport_block(
    *,
    recipient_cert_id: str,
    ephemeral_public_key_b64: str = "",
    wrapped_key_b64: str = "",
    wrapped_at: str | None = None,
) -> KeyTransportBlock:
    """Construct a :class:`KeyTransportBlock` with deterministic KDF params.

    ``ephemeral_public_key_b64`` and ``wrapped_key_b64`` default
    to empty strings; they will be filled in by :func:`wrap_session_key`
    once an approved SM2 product is wired in.
    """
    if not isinstance(recipient_cert_id, str) or not recipient_cert_id:
        raise AgentPackageCryptoUnavailableError(
            "recipient_cert_id must be a non-empty string"
        )
    if not isinstance(ephemeral_public_key_b64, str):
        raise AgentPackageCryptoUnavailableError(
            "ephemeral_public_key must be a string (base64)"
        )
    if not isinstance(wrapped_key_b64, str):
        raise AgentPackageCryptoUnavailableError(
            "wrapped_key must be a string (base64)"
        )
    return KeyTransportBlock(
        format=KEY_BLOCK_FORMAT,
        recipient_cert_id=recipient_cert_id,
        ephemeral_public_key=ephemeral_public_key_b64,
        wrapped_key=wrapped_key_b64,
        kdf_params=(
            ("kdf", KDF_NAME),
            ("salt", ""),  # filled in by wrap_session_key once the SM2 product is wired
            ("iterations", KDF_ITERATIONS_DEFAULT),
        ),
        wrapped_at=wrapped_at or _now_utc_iso_z(),
    )


def wrap_session_key(
    session_key: bytes,
    *,
    recipient_cert_id: str,
) -> KeyTransportBlock:
    """Wrap ``session_key`` under the recipient's SM2 public key.

    **Fail-closed**: raises :class:`AgentPackageCryptoUnavailableError`
    unconditionally until an approved SM2 product is wired in. The
    wire layout, KDF parameter set and field-name conventions are
    final; only the SM2 key-transport call awaits.
    """
    if not isinstance(session_key, bytes) or len(session_key) != SESSION_KEY_SIZE:
        raise AgentPackageCryptoUnavailableError(
            f"session_key must be {SESSION_KEY_SIZE} bytes (SM4-128)"
        )
    if not isinstance(recipient_cert_id, str) or not recipient_cert_id:
        raise AgentPackageCryptoUnavailableError(
            "recipient_cert_id must be a non-empty string"
        )
    raise AgentPackageCryptoUnavailableError(
        "SM2 key-transport requires an approved SM2 product; "
        "AGENTS.md §6 forbids silent fallback. Wire encoding is ready; "
        "approved product path is awaited."
    )


def unwrap_session_key(
    block: KeyTransportBlock,
    *,
    recipient_cert_id: str,
) -> bytes:
    """Unwrap a session key from a :class:`KeyTransportBlock`.

    **Fail-closed**: raises :class:`AgentPackageCryptoUnavailableError`
    unconditionally until an approved SM2 product is wired in. The
    function still validates the wire format (format string,
    recipient match) before raising so callers can detect
    encoding-level corruption early.
    """
    if not isinstance(block, KeyTransportBlock):
        raise AgentPackageCryptoUnavailableError(
            "block must be KeyTransportBlock"
        )
    if block.format != KEY_BLOCK_FORMAT:
        raise AgentPackageCryptoUnavailableError(
            f"key block format {block.format!r} is not supported; "
            f"only {KEY_BLOCK_FORMAT!r} is"
        )
    if block.recipient_cert_id != recipient_cert_id:
        raise AgentPackageCryptoUnavailableError(
            "key block recipient does not match caller"
        )
    raise AgentPackageCryptoUnavailableError(
        "SM2 key-unwrapping requires an approved SM2 product; "
        "AGENTS.md §6 forbids silent fallback."
    )


def encode_key_transport_bytes(block: KeyTransportBlock) -> bytes:
    """Encode a :class:`KeyTransportBlock` as canonical UTF-8 JSON bytes.

    Sorted keys, no trailing whitespace, no BOM. The byte sequence
    feeds directly into the ``key_block`` length field of the Fixed
    Header (协议 § 7.1 / § 7.3).
    """
    if not isinstance(block, KeyTransportBlock):
        raise AgentPackageCryptoUnavailableError(
            "block must be KeyTransportBlock"
        )
    text = json.dumps(block.to_mapping(), ensure_ascii=False, separators=(",", ":"))
    return text.encode("utf-8")


def decode_key_transport_bytes(data: bytes) -> KeyTransportBlock:
    """Decode canonical JSON bytes into a :class:`KeyTransportBlock`.

    Strict field set + format check; refuses unknown fields so a
    future receiver can never silently accept a wider wire format.
    """
    if not isinstance(data, bytes):
        raise AgentPackageCryptoUnavailableError("data must be bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AgentPackageCryptoUnavailableError(
            "key block must be valid UTF-8"
        ) from exc
    if text.startswith("\ufeff"):
        raise AgentPackageCryptoUnavailableError("key block must not contain a BOM")
    try:
        mapping = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AgentPackageCryptoUnavailableError(
            "key block must be canonical JSON"
        ) from exc
    if not isinstance(mapping, dict):
        raise AgentPackageCryptoUnavailableError("key block must be a JSON object")
    required = {
        "format", "recipient_cert_id", "ephemeral_public_key",
        "wrapped_key", "kdf_params", "wrapped_at",
    }
    actual = set(mapping.keys())
    if actual != required:
        raise AgentPackageCryptoUnavailableError(
            f"key block field mismatch: missing={sorted(required - actual)!r} "
            f"extra={sorted(actual - required)!r}"
        )
    if mapping["format"] != KEY_BLOCK_FORMAT:
        raise AgentPackageCryptoUnavailableError(
            f"key block format {mapping['format']!r} is not supported"
        )
    kdf = mapping["kdf_params"]
    if not isinstance(kdf, dict):
        raise AgentPackageCryptoUnavailableError("kdf_params must be a JSON object")
    if kdf.get("kdf") != KDF_NAME:
        raise AgentPackageCryptoUnavailableError(
            f"kdf {kdf.get('kdf')!r} is not supported; only {KDF_NAME!r} is"
        )
    if not isinstance(kdf.get("salt"), str):
        raise AgentPackageCryptoUnavailableError("kdf.salt must be a string")
    if not isinstance(kdf.get("iterations"), int) or kdf["iterations"] < 1:
        raise AgentPackageCryptoUnavailableError(
            "kdf.iterations must be a positive integer"
        )
    return KeyTransportBlock(
        format=mapping["format"],
        recipient_cert_id=str(mapping["recipient_cert_id"]),
        ephemeral_public_key=str(mapping["ephemeral_public_key"]),
        wrapped_key=str(mapping["wrapped_key"]),
        kdf_params=tuple(sorted(kdf.items())),
        wrapped_at=str(mapping["wrapped_at"]),
    )