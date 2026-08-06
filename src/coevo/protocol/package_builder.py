"""US-5 end-to-end package builder / parser (US-5-AC-2 / 协议 § 7 + § 13).

Scope
-----
This module ties the wire layers together. The builder produces a
byte-precise on-disk representation:

    [fixed header][envelope header bytes][key block bytes][payload block bytes]

The parser is the inverse: it reads the four byte slices, decodes
each layer, and returns a :class:`BuiltPackage`. The cryptographic
operations (SM4-GCM AEAD encrypt/decrypt, SM2 sign/verify,
SM2 key-transport) remain **fail-closed** in P1; the builder
raises :class:`AgentPackageCryptoUnavailableError` when the caller
asks it to actually encrypt / sign / wrap.

Important: the signature record (协议 § 12) is **out-of-band**
metadata in this slice. It is carried on :class:`BuiltPackage` as
a Python attribute, NOT embedded in the envelope wire. The
receiver contract (协议 § 13 步骤 16) is to verify the manifest
signature before importing the package; in this slice the
verification call surfaces a fail-closed error until an approved
SM2 product is wired in. A future slice will define a wire carrier
for the signature (either by extending the envelope under a
reserved extensions key, or by adding an auxiliary block). For
now, the signature lives next to the package bytes in the
receiver's storage layer.

Non-goals
---------
* No cryptographic operation. The crypto-bearing surfaces raise.
* No IO, no LLM, no model.
* No mutation of US-5-AC-1 fixed header / envelope wire layout.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 本模块是 `.agent` 任务包的“线格式”组合层（US-5 AC-2 / 协议 §7+§13）：
#   * build_unsigned_package：组装 Fixed Header + Envelope + KeyTransport +
#     Payload，产出字节精确的 BuiltPackage（SM2 封钥/SM4-GCM 载荷）；
#   * build_encrypted_package：在未签名包之上附加发送方签名，形成完整包；
#   * parse_package_bytes：严格解析线字节，拒绝长度矛盾/非法 nonce/尾随数据；
#   * open_encrypted_package：解密 → 严格解析内层 JSON（拒绝重复键）→
#     验签 → 回读 content。句柄证书必须与信封 sender/recipient 一致，
#     否则抛 AgentPackageError（错误接收人包被真实拒绝）。
#   关键安全不变量：Python 进程不接触私钥字节，所有密码运算经
#   GmsslPrototypeProvider 一次性助手完成；解封失败一律 fail-closed。
from __future__ import annotations

import dataclasses
import base64
import binascii
import json
import os
from dataclasses import dataclass
from typing import Any, Mapping

from .agent_package import (
    AgentPackageError,
    AgentPackageFlags,
    EnvelopeHeader,
    FixedHeader,
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    decode_envelope,
    decode_fixed_header,
    encode_envelope,
    encode_fixed_header,
)
from .agent_payload import (
    PAYLOAD_HEADER_SIZE,
    AgentPackageCryptoUnavailableError as PayloadCryptoUnavailable,
    PayloadBlock,
    PAYLOAD_NONCE_SIZE,
    PAYLOAD_TAG_SIZE,
    decode_payload_header,
    encode_payload_header,
)
from .sm2_keywrap import (
    KeyTransportBlock,
    decode_key_transport_bytes,
    encode_key_transport_bytes,
)
from .sm2_sign import SignatureRecord


@dataclass(frozen=True)
class OpenedPackage:
    manifest: Mapping[str, Any]
    content: bytes
    signature: SignatureRecord


@dataclass(frozen=True)
class BuiltPackage:
    """A wire-encoded .agent package assembled from all four layers.

    ``signature`` is out-of-band metadata; it is not embedded in
    ``to_bytes()``. The receiver imports the bytes via
    :func:`parse_package_bytes` and pairs the result with the
    signature record supplied by the upper-layer storage / audit
    log (协议 § 13 步骤 16).
    """

    fixed_header: FixedHeader
    envelope: EnvelopeHeader
    key_block: KeyTransportBlock
    payload_block: PayloadBlock
    signature: SignatureRecord

    def to_bytes(self) -> bytes:
        """Encode the package to canonical bytes.

        Order is fixed: fixed header → envelope bytes → key block
        bytes → payload block bytes. The signature is NOT embedded
        in the wire stream (see module docstring for rationale).
        """
        env_bytes = encode_envelope(self.envelope)
        key_bytes = encode_key_transport_bytes(self.key_block)
        payload_bytes = (
            self.payload_block.header
            + self.payload_block.nonce
            + self.payload_block.ciphertext
            + self.payload_block.tag
        )
        fixed = self.fixed_header
        new_fixed = FixedHeader(
            major=fixed.major,
            minor=fixed.minor,
            header_length=len(env_bytes),
            key_block_length=len(key_bytes),
            payload_length=len(payload_bytes),
            flags=fixed.flags,
        )
        fixed_bytes = encode_fixed_header(
            major=new_fixed.major,
            minor=new_fixed.minor,
            header_length=new_fixed.header_length,
            key_block_length=new_fixed.key_block_length,
            payload_length=new_fixed.payload_length,
            flags=new_fixed.flags,
        )
        return fixed_bytes + env_bytes + key_bytes + payload_bytes

    def expected_total_length(self) -> int:
        """Return the wire-precise total length the Fixed Header advertises.

        The value is computed from the actual envelope / key / payload
        byte lengths (which :meth:`to_bytes` will use to render the
        Fixed Header), so ``len(to_bytes()) == expected_total_length()``
        holds without requiring the caller to pre-fill the Fixed
        Header's length fields.
        """
        from .agent_package import encode_envelope
        from .sm2_keywrap import encode_key_transport_bytes
        env_bytes = encode_envelope(self.envelope)
        key_bytes = encode_key_transport_bytes(self.key_block)
        payload_bytes = (
            self.payload_block.header
            + self.payload_block.nonce
            + self.payload_block.ciphertext
            + self.payload_block.tag
        )
        return 36 + len(env_bytes) + len(key_bytes) + len(payload_bytes)


def build_unsigned_package(
    *,
    envelope: EnvelopeHeader,
    key_block: KeyTransportBlock,
    payload_block: PayloadBlock,
) -> BuiltPackage:
    """Assemble a :class:`BuiltPackage` with an *empty* signature.

    The returned package has ``signature.signature == ""``. Any
    attempt to actually verify the signature will raise
    :class:`AgentPackageCryptoVerifyError` (fail-closed).
    """
    from .sm2_sign import build_signature_record

    manifest = {
        "protocol_version": envelope.protocol_version,
        "package_id": envelope.package_id,
        "package_type": envelope.package_type,
        "sender_cert_id": envelope.sender_cert_id,
        "recipient_cert_id": envelope.recipient_cert_id,
        "project_id": envelope.project_id,
    }
    signature = build_signature_record(
        manifest,
        signer_cert_id=envelope.sender_cert_id,
    )
    env_bytes = encode_envelope(envelope)
    key_bytes = encode_key_transport_bytes(key_block)
    payload_bytes = (
        payload_block.header
        + payload_block.nonce
        + payload_block.ciphertext
        + payload_block.tag
    )
    # OPTIMIZE-5: normalize the envelope's payload_length to the full
    # encrypted block size (header+nonce+ciphertext+tag), exactly like
    # build_encrypted_package does. Protocol § 7.1 requires the envelope
    # and Fixed Header payload_length to agree; emitting an inconsistent
    # package would be rejected by parse_package_header.
    if envelope.payload_length != len(payload_bytes):
        envelope = dataclasses.replace(envelope, payload_length=len(payload_bytes))
    fixed = FixedHeader(
        major=PROTOCOL_MAJOR,
        minor=PROTOCOL_MINOR,
        header_length=len(env_bytes),
        key_block_length=len(key_bytes),
        payload_length=len(payload_bytes),
        flags=AgentPackageFlags.KEY_BLOCK_PRESENT | AgentPackageFlags.PAYLOAD_PRESENT,
    )
    return BuiltPackage(
        fixed_header=fixed,
        envelope=envelope,
        key_block=key_block,
        payload_block=payload_block,
        signature=signature,
    )


def parse_package_bytes(data: bytes) -> BuiltPackage:
    """Parse canonical bytes into a :class:`BuiltPackage`.

    Strict length check: the on-disk length must equal the
    advertised total length (协议 § 7.1 — "文件精确总长度必须等于
    36 + Header Length + Key Block Length + Payload Length").
    Trailing bytes are not silently accepted (协议 § 19).

    The returned package has a placeholder ``signature`` record
    whose ``manifest_sm3`` is the digest of the canonical envelope
    bytes (i.e. a stand-in manifest digest) — the actual
    sender-supplied signature record must be paired in by the
    caller via ``package_bytes + storage_layer_signature``.
    """
    if not isinstance(data, bytes):
        raise AgentPackageError("data must be bytes")
    fixed = decode_fixed_header(data[:36])
    expected_total = (
        36
        + fixed.header_length
        + fixed.key_block_length
        + fixed.payload_length
    )
    if len(data) != expected_total:
        raise AgentPackageError(
            f"package length mismatch: expected {expected_total} bytes, "
            f"got {len(data)} bytes (协议 § 7.1 — no trailing data)"
        )
    cursor = 36
    env_bytes = data[cursor : cursor + fixed.header_length]
    cursor += fixed.header_length
    envelope = decode_envelope(env_bytes)
    if envelope.payload_length != fixed.payload_length:
        # OPTIMIZE-5: mirror the strict parse_package_header consistency rule
        # (协议 § 7.1) so both parse surfaces reject the same wire.
        raise AgentPackageError(
            "envelope.payload_length disagrees with fixed header payload_length: "
            f"envelope={envelope.payload_length} fixed={fixed.payload_length}"
        )
    key_bytes = data[cursor : cursor + fixed.key_block_length]
    cursor += fixed.key_block_length
    if fixed.key_block_length > 0:
        key_block = decode_key_transport_bytes(key_bytes)
    else:
        raise AgentPackageError(
            "empty key_block_length is not supported in protocol 1.0"
        )
    payload_bytes = data[cursor : cursor + fixed.payload_length]
    cursor += fixed.payload_length
    if fixed.payload_length > 0:
        if len(payload_bytes) < PAYLOAD_HEADER_SIZE:
            raise PayloadCryptoUnavailable(
                "payload block shorter than wire header"
            )
        decode_payload_header(payload_bytes[:PAYLOAD_HEADER_SIZE])
        nonce = payload_bytes[
            PAYLOAD_HEADER_SIZE : PAYLOAD_HEADER_SIZE + PAYLOAD_NONCE_SIZE
        ]
        tag = payload_bytes[-PAYLOAD_TAG_SIZE:]
        ciphertext = payload_bytes[
            PAYLOAD_HEADER_SIZE + PAYLOAD_NONCE_SIZE : -PAYLOAD_TAG_SIZE
        ]
        payload_block = PayloadBlock(
            header=payload_bytes[:PAYLOAD_HEADER_SIZE],
            nonce=nonce,
            ciphertext=ciphertext,
            tag=tag,
        )
    else:
        payload_block = PayloadBlock(
            header=b"", nonce=b"", ciphertext=b"", tag=b""
        )
    if cursor != len(data):
        raise AgentPackageError(
            f"trailing bytes after expected total length: "
            f"{len(data) - cursor} bytes (协议 § 7.1)"
        )
    # Build a placeholder signature record whose manifest_sm3 is
    # the digest of the canonical envelope bytes. This keeps the
    # BuiltPackage surface self-contained without depending on the
    # out-of-band signature carrier.
    from .sm2_sign import build_signature_record
    manifest = {
        "protocol_version": envelope.protocol_version,
        "package_id": envelope.package_id,
        "package_type": envelope.package_type,
        "sender_cert_id": envelope.sender_cert_id,
        "recipient_cert_id": envelope.recipient_cert_id,
        "project_id": envelope.project_id,
    }
    signature = build_signature_record(
        manifest, signer_cert_id=envelope.sender_cert_id
    )
    return BuiltPackage(
        fixed_header=fixed,
        envelope=envelope,
        key_block=key_block,
        payload_block=payload_block,
        signature=signature,
    )


def assert_sign_blocked(
    manifest: dict,
    *,
    signer_cert_id: str,
    signed_at: str | None = None,
) -> SignatureRecord:
    """Signal that manifest signing is blocked pending an approved SM2 product.

    The wire format is final (Algorithm = "SM2-SM3", signed_object =
    "manifest.json", manifest_sm3 = 64-hex digest, signature field
    reserved for the future SM2 product). Calling this function
    ALWAYS raises :class:`AgentPackageCryptoUnavailableError`
    (fail-closed) so callers never receive a half-signed record;
    the name is deliberately explicit that signing is blocked.
    """
    from .sm2_sign import AgentPackageCryptoUnavailableError
    raise AgentPackageCryptoUnavailableError(
        "sign_manifest is awaiting an approved SM2 product"
    )


def build_encrypted_package(
    *, envelope: EnvelopeHeader, manifest: Mapping[str, Any], content: bytes,
    provider: Any, sender_handle: Any, recipient_handle: Any,
    signed_at: str | None = None,
) -> BuiltPackage:
    """Build a real signed/encrypted package with an explicitly injected provider."""
    from .sm2_keywrap import build_key_transport_block
    from .sm2_sign import sign_manifest
    if not isinstance(content, bytes):
        raise AgentPackageError("content must be bytes")
    if (getattr(sender_handle, "certificate_id", None) != envelope.sender_cert_id
            or getattr(recipient_handle, "certificate_id", None) != envelope.recipient_cert_id):
        raise AgentPackageError("cryptographic handles do not match envelope certificates")
    signature = sign_manifest(
        manifest, signer_cert_id=envelope.sender_cert_id, signed_at=signed_at,
        provider=provider, signer_handle=sender_handle,
    )
    inner = json.dumps(
        {
            "content": base64.b64encode(content).decode("ascii"),
            "manifest.json": manifest,
            "sender.sig": signature.to_mapping(),
        },
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    nonce = os.urandom(PAYLOAD_NONCE_SIZE)
    envelope = dataclasses.replace(
        envelope,
        nonce=base64.b64encode(nonce).decode("ascii"),
        payload_length=PAYLOAD_HEADER_SIZE + PAYLOAD_NONCE_SIZE + len(inner) + PAYLOAD_TAG_SIZE,
    )
    aad = encode_envelope(envelope)
    sealed = provider.seal(recipient_handle, inner, associated_data=aad, nonce=nonce)
    key_block = build_key_transport_block(
        recipient_cert_id=envelope.recipient_cert_id,
        wrapped_key_b64=base64.b64encode(sealed.wrapped_key).decode("ascii"),
        # GmSSL's standard SM2 ciphertext carries C1 (the ephemeral public
        # point) inside wrapped_key, so this compatibility field is empty.
        ephemeral_public_key_b64="",
    )
    payload = PayloadBlock(
        header=encode_payload_header(),
        nonce=sealed.nonce, ciphertext=sealed.ciphertext, tag=sealed.tag,
    )
    env_bytes = encode_envelope(envelope)
    key_bytes = encode_key_transport_bytes(key_block)
    payload_bytes = (
        payload.header
        + payload.nonce
        + payload.ciphertext
        + payload.tag
    )
    return BuiltPackage(
        FixedHeader(
            PROTOCOL_MAJOR,
            PROTOCOL_MINOR,
            len(env_bytes),
            len(key_bytes),
            len(payload_bytes),
                    AgentPackageFlags.KEY_BLOCK_PRESENT | AgentPackageFlags.PAYLOAD_PRESENT),
        envelope, key_block, payload, signature,
    )


def open_encrypted_package(
    package: BuiltPackage, *, provider: Any, recipient_handle: Any,
    sender_handle: Any,
) -> OpenedPackage:
    """Decrypt, strictly parse, digest-check and verify the inner payload."""
    from src.coevo.crypto import SealedPayload
    from .sm2_sign import decode_signature_record, verify_signature
    if not isinstance(package, BuiltPackage):
        raise AgentPackageError("package must be BuiltPackage")
    if package.key_block.recipient_cert_id != package.envelope.recipient_cert_id:
        raise AgentPackageError("key block recipient does not match envelope")
    if (getattr(recipient_handle, "certificate_id", None) != package.envelope.recipient_cert_id
            or getattr(sender_handle, "certificate_id", None) != package.envelope.sender_cert_id):
        raise AgentPackageError("cryptographic handles do not match package certificates")
    try:
        wrapped = base64.b64decode(package.key_block.wrapped_key, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise AgentPackageError("wrapped key is not canonical base64") from exc
    sealed = SealedPayload(
        wrapped, package.payload_block.nonce,
        package.payload_block.ciphertext, package.payload_block.tag,
    )
    plaintext = provider.open(
        recipient_handle, sealed, associated_data=encode_envelope(package.envelope)
    )
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise AgentPackageError("inner payload contains duplicate JSON keys")
            result[key] = value
        return result
    try:
        inner = json.loads(plaintext.decode("utf-8"), object_pairs_hook=unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AgentPackageError("inner payload is not valid canonical JSON") from exc
    if not isinstance(inner, dict) or set(inner) != {"content", "manifest.json", "sender.sig"}:
        raise AgentPackageError("inner payload field set is invalid")
    signature = decode_signature_record(inner["sender.sig"])
    verify_signature(
        signature, manifest=inner["manifest.json"],
        expected_signer_cert_id=package.envelope.sender_cert_id,
        provider=provider, signer_handle=sender_handle,
    )
    try:
        content = base64.b64decode(inner["content"], validate=True)
    except (ValueError, binascii.Error, TypeError) as exc:
        raise AgentPackageError("inner content is not canonical base64") from exc
    return OpenedPackage(inner["manifest.json"], content, signature)
