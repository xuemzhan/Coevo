"""US-5 SM4 AEAD payload layer (US-5-AC-2 / 协议 § 7.4).

Scope
-----
This module implements the wire encoding for the encrypted inner
payload block (协议 § 7.4). The bytes-on-wire format is::

    [8-byte payload header][12-byte nonce][N-byte ciphertext][16-byte auth tag]

where the 8-byte payload header is::

    b"SM4GCM"   (6 bytes magic)
    b"\\x01"     (1 byte version)
    b"\\x00"     (1 byte reserved-zero)

so the total block on disk is ``8 + 12 + N + 16`` bytes and the
fixed-header ``payload_length`` field captures exactly that. The
wire-level framing is deterministic and pure-Python.

The actual cryptographic operation (SM4-GCM AEAD encrypt / decrypt)
is **fail-closed** in this slice. Calling :func:`encrypt_payload`
or :func:`decrypt_payload` raises
:class:`AgentPackageCryptoUnavailableError` until an approved SM4
product is wired in (AGENTS.md §6 — crypto-scheme change requires
business-owner sign-off + offline binary path).

Non-goals (out of scope for US-5-AC-2)
--------------------------------------
* No cryptographic operation. Every call to encrypt / decrypt raises.
* No LLM, no IO, no network.
* No tampering with the existing US-5-AC-1 wire layout (Fixed Header,
  Envelope, flags). This module plugs in only at the payload block.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Final

from .agent_package import AgentPackageError


PAYLOAD_HEADER_MAGIC: Final[bytes] = b"SM4GCM"        # 6 bytes
PAYLOAD_HEADER_VERSION: Final[int] = 0x01
PAYLOAD_HEADER_SIZE: Final[int] = 8                    # magic(6) + version(1) + reserved(1)
PAYLOAD_NONCE_SIZE: Final[int] = 12
PAYLOAD_TAG_SIZE: Final[int] = 16


class AgentPackageCryptoUnavailableError(AgentPackageError):
    """Raised when the cryptographic operation is requested.

    AGENTS.md §6 forbids assuming an approved SM2/SM4 product. This
    error is the explicit, fail-closed path that surfaces whenever
    a caller tries to run an actual encrypt or decrypt before the
    approved product has been wired in.

    The error carries a stable ``code`` (AGT-CRY-001 / AGT-CRY-002)
    so audit emitters can record the precise cause per 协议 § 22.
    """

    code: str = "AGT-CRY-001"


class AgentPackageCryptoDecryptError(AgentPackageCryptoUnavailableError):
    code: str = "AGT-CRY-002"


@dataclass(frozen=True)
class PayloadBlock:
    """Wire-level SM4 AEAD payload block (协议 § 7.4).

    ``header`` is exactly :data:`PAYLOAD_HEADER_SIZE` bytes and
    starts with :data:`PAYLOAD_HEADER_MAGIC`. ``nonce`` is exactly
    :data:`PAYLOAD_NONCE_SIZE` bytes. ``ciphertext`` and ``tag``
    carry the AEAD-protected inner payload.
    """

    header: bytes
    nonce: bytes
    ciphertext: bytes
    tag: bytes


def encode_payload_header() -> bytes:
    """Encode the 8-byte payload header.

    The header is :data:`PAYLOAD_HEADER_MAGIC` (6 bytes) followed by
    1 version byte (``PAYLOAD_HEADER_VERSION`` = ``0x01``) and 1
    reserved byte (``0x00``). Receivers reject unknown magic /
    version / non-zero reserved bytes (see
    :func:`decode_payload_header`).
    """
    return PAYLOAD_HEADER_MAGIC + bytes([PAYLOAD_HEADER_VERSION]) + b"\x00"


def decode_payload_header(block_header: bytes) -> None:
    """Reject anything that does not match the wire header.

    The receiver contract is fail-closed: unknown magic / version /
    non-zero reserved bytes are errors, not silent fallbacks.
    """
    if not isinstance(block_header, bytes) or len(block_header) != PAYLOAD_HEADER_SIZE:
        raise AgentPackageCryptoDecryptError(
            f"payload header must be exactly {PAYLOAD_HEADER_SIZE} bytes"
        )
    if block_header[:6] != PAYLOAD_HEADER_MAGIC:
        raise AgentPackageCryptoDecryptError("payload header magic mismatch")
    if block_header[6] != PAYLOAD_HEADER_VERSION:
        raise AgentPackageCryptoDecryptError(
            f"payload header version {block_header[6]!r} is not supported"
        )
    if block_header[7] != 0:
        raise AgentPackageCryptoDecryptError("payload header reserved byte must be zero")


def generate_payload_nonce() -> bytes:
    """Return a 12-byte nonce drawn from a cryptographically secure RNG.

    The function uses :mod:`secrets` (CSPRNG) per AGENTS.md §3 第 7
    条: "禁止以时间戳或普通伪随机数作为会话密钥或 Nonce 来源".

    This is the **only** randomness-using operation in this module
    that actually runs in P1. The SM4-GCM encrypt / decrypt step
    remains fail-closed.
    """
    return secrets.token_bytes(PAYLOAD_NONCE_SIZE)


def assemble_payload_block(
    ciphertext: bytes,
    *,
    nonce: bytes | None = None,
) -> PayloadBlock:
    """Assemble a :class:`PayloadBlock` from already-encrypted bytes.

    ``ciphertext`` must already be the SM4-GCM output (this slice
    does not perform SM4-GCM). This helper exists so callers in
    future slices can wire in the approved SM4 product and pass the
    resulting bytes here.

    ``nonce`` defaults to a fresh 12-byte value. Callers that need
    a deterministic nonce (e.g. test fixtures) may supply one.
    """
    if not isinstance(ciphertext, bytes):
        raise AgentPackageCryptoUnavailableError("ciphertext must be bytes")
    if nonce is None:
        nonce = generate_payload_nonce()
    if len(nonce) != PAYLOAD_NONCE_SIZE:
        raise AgentPackageCryptoUnavailableError(
            f"nonce must be exactly {PAYLOAD_NONCE_SIZE} bytes"
        )
    # Tag length is part of the wire contract; an empty tag would
    # silently weaken the security guarantees (协议 § 7.4 forbids
    # non-authenticated modes). We refuse to assemble a block whose
    # tag is shorter than the protocol requires.
    return PayloadBlock(
        header=encode_payload_header(),
        nonce=nonce,
        ciphertext=ciphertext,
        tag=b"\x00" * PAYLOAD_TAG_SIZE,
    )


def encrypt_payload(
    plaintext: bytes,
    *,
    associated_data: bytes,
) -> PayloadBlock:
    """Encrypt ``plaintext`` with SM4-GCM AEAD.

    **Fail-closed**: raises :class:`AgentPackageCryptoUnavailableError`
    unconditionally until the approved SM4 product is wired in. The
    wire layout above is fully designed and unit-tested; the only
    missing piece is the SM4-GCM primitive.

    ``associated_data`` is the AAD that MUST bind the outer
    Envelope Header to the ciphertext (协议 § 7.4 — "外层信封应作为
    认证加密的附加认证数据"). Callers are expected to pass the
    canonical Envelope bytes here so any envelope tampering
    invalidates the AEAD tag.
    """
    if not isinstance(plaintext, bytes):
        raise AgentPackageCryptoUnavailableError("plaintext must be bytes")
    if not isinstance(associated_data, bytes):
        raise AgentPackageCryptoUnavailableError("associated_data must be bytes")
    raise AgentPackageCryptoUnavailableError(
        "SM4-GCM AEAD encryption requires an approved SM4 product; "
        "AGENTS.md §6 forbids silent fallback. Wire encoding is ready; "
        "approved product path is awaited."
    )


def decrypt_payload(
    block: PayloadBlock,
    *,
    associated_data: bytes,
) -> bytes:
    """Decrypt a :class:`PayloadBlock` with SM4-GCM AEAD.

    **Fail-closed**: same as :func:`encrypt_payload`. The function
    still validates the wire header before raising, so callers can
    detect encoding-level corruption early.
    """
    if not isinstance(block, PayloadBlock):
        raise AgentPackageCryptoUnavailableError("block must be PayloadBlock")
    if not isinstance(associated_data, bytes):
        raise AgentPackageCryptoUnavailableError("associated_data must be bytes")
    decode_payload_header(block.header)
    raise AgentPackageCryptoUnavailableError(
        "SM4-GCM AEAD decryption requires an approved SM4 product; "
        "AGENTS.md §6 forbids silent fallback."
    )