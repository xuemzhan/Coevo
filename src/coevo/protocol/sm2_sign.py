"""US-5 SM2 signature + SM3 digest layer (US-5-AC-2 / 协议 § 9 + § 12).

Scope
-----
This module implements the wire encoding for the sender's digital
signature over the canonical manifest (协议 § 12). The signature
object is a deterministic JSON structure::

    {
      "algorithm": "SM2-SM3",
      "signer_cert_id": "<cert>",
      "signed_object": "manifest.json",
      "manifest_sm3": "<64-hex>",
      "signature": "<base64>",
      "signed_at": "<ISO-8601 UTC 'Z'>"
    }

The canonical bytes are produced by :func:`canonical_manifest_bytes`,
which applies 协议 § 10 JSON canonicalisation rules (UTF-8, no BOM,
sorted keys, no trailing whitespace, ASCII digits, no duplicate keys,
no NaN/Inf). The SM3 digest is then computed deterministically.

The actual cryptographic operation (SM2 sign / verify) is
**fail-closed** in this slice. Calling :func:`sign_manifest` or
:func:`verify_signature` raises
:class:`AgentPackageCryptoUnavailableError` until an approved SM2
product is wired in.

Non-goals
---------
* No actual SM2 operation (P1 path).
* No IO, no model, no network.
* No mutation of US-5-AC-1 fixed header / envelope wire layout.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-5 SM2 签名 + SM3 摘要层（§9+§12）：规范清单、签名记录与验证。
from __future__ import annotations

import base64
import binascii
import datetime as dt
import json
import re
from dataclasses import dataclass
from typing import Any, Final, Mapping

from .agent_package import AgentPackageError


SM3_DIGEST_SIZE: Final[int] = 32
SM3_HEX_SIZE: Final[int] = SM3_DIGEST_SIZE * 2
SIGNATURE_ALGORITHM: Final[str] = "SM2-SM3"
SIGNED_OBJECT_NAME: Final[str] = "manifest.json"


class AgentPackageCryptoUnavailableError(AgentPackageError):
    """Raised when the SM2 cryptographic operation is requested.

    AGENTS.md §6 forbids assuming an approved SM2 product. This
    error surfaces whenever a caller tries to run sign / verify
    before the approved product has been wired in. Stable code
    AGT-CRY-003 / AGT-CRY-004 per 协议 § 22.
    """

    code: str = "AGT-CRY-003"


class AgentPackageCryptoVerifyError(AgentPackageCryptoUnavailableError):
    code: str = "AGT-CRY-004"


class AgentPackageCanonicalizationError(AgentPackageError):
    """Raised when canonicalisation invariants are violated."""

    code: str = "AGT-PKG-005"


@dataclass(frozen=True)
class SignatureRecord:
    """协议 § 12 ``sender.sig`` signature object."""

    algorithm: str
    signer_cert_id: str
    signed_object: str
    manifest_sm3: str  # 64-char lowercase hex
    signature: str     # base64 (empty string in P1)
    signed_at: str     # ISO-8601 UTC 'Z'

    def to_mapping(self) -> dict[str, str]:
        return {
            "algorithm": self.algorithm,
            "signer_cert_id": self.signer_cert_id,
            "signed_object": self.signed_object,
            "manifest_sm3": self.manifest_sm3,
            "signature": self.signature,
            "signed_at": self.signed_at,
        }


def _now_utc_iso_z() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def _ascii_digit_only(value: Any, *, path: str) -> None:
    """Reject non-ASCII digits / decimal points per 协议 § 10 第 6 条.

    Python ``int`` and ``float`` don't accept non-ASCII digits, but
    strings could come from a JSON loader that accepts them. We
    enforce ASCII-only digits at canonicalisation time.
    """
    if isinstance(value, str):
        if not value.isascii():
            raise AgentPackageCanonicalizationError(
                f"{path} contains non-ASCII characters"
            )


_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def compute_sm3_digest(data: bytes) -> str:
    """Compute the real SM3 digest (GB/T 32905) as 64-char lowercase hex.

    CRYPTO-1 (2026-08-03): the business owner approved replacing the
    previous SHA-256 stand-in with a real SM3 implementation
    (:mod:`coevo.crypto.sm3`), so protocol digests now match the SM3
    algorithm the wire format always claimed (协议 § 12 / cipher suite
    ``CS-SM2-SM4-AEAD-SM3-01``). Signer and verifier use this function
    consistently; historical SHA-256-based digests are not recomputed.
    """
    if not isinstance(data, bytes):
        raise AgentPackageCanonicalizationError("digest input must be bytes")
    from src.coevo.crypto.sm3 import sm3_hexdigest

    return sm3_hexdigest(data)


def compute_real_sm3_digest(data: bytes, *, provider: Any) -> str:
    """Compute SM3 through an explicitly injected approved prototype provider."""
    if not isinstance(data, bytes) or not callable(getattr(provider, "sm3", None)):
        raise AgentPackageCryptoUnavailableError("an SM3 provider is required")
    digest = provider.sm3(data)
    if not isinstance(digest, bytes) or len(digest) != SM3_DIGEST_SIZE:
        raise AgentPackageCryptoUnavailableError("SM3 provider returned an invalid digest")
    return digest.hex()


def _canonicalise_object(value: Any, *, path: str = "$") -> Any:
    """Apply 协议 § 10 canonicalisation recursively.

    Rules implemented:
      * UTF-8 (the bytes are produced by ``json.dumps(..., ensure_ascii=False).encode('utf-8')``)
      * no BOM (utf-8 codec without BOM marker)
      * sorted object keys
      * no trailing whitespace (handled by json.dumps default separators)
      * ASCII digits only (we reject non-ASCII numeric strings)
      * no duplicate keys (handled by Python dict semantics + object_pairs_hook in envelope layer; here we trust the input mapping)

    Returns a *deep-copied* canonical structure. The actual canonical
    bytes are produced by :func:`canonical_manifest_bytes`.
    """
    if isinstance(value, Mapping):
        items = sorted(value.keys(), key=str)
        return {
            str(key): _canonicalise_object(value[key], path=f"{path}.{key}")
            for key in items
        }
    if isinstance(value, list):
        return [
            _canonicalise_object(item, path=f"{path}[{idx}]")
            for idx, item in enumerate(value)
        ]
    if isinstance(value, tuple):
        return [
            _canonicalise_object(item, path=f"{path}[{idx}]")
            for idx, item in enumerate(value)
        ]
    if isinstance(value, str):
        _ascii_digit_only(value, path=path)
        return value
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return value  # json.dumps emits integer literals; Python int never has a leading zero
    if isinstance(value, float):
        # 协议 § 10 第 7 条 forbids non-deterministic floats.
        # We accept only finite floats and emit canonical repr.
        if value != value or value in (float("inf"), float("-inf")):
            raise AgentPackageCanonicalizationError(
                f"{path} is not a finite float"
            )
        return float(repr(value))
    raise AgentPackageCanonicalizationError(
        f"{path} has unsupported type {type(value).__name__}"
    )


def canonical_manifest_bytes(manifest: Mapping[str, Any]) -> bytes:
    """Produce canonical bytes per 协议 § 10 + RFC 8785-style ordering.

    Returns UTF-8 bytes without BOM, with sorted keys and no
    trailing whitespace. The byte sequence is byte-deterministic
    across runs and across Python implementations.
    """
    canonical = _canonicalise_object(manifest)
    text = json.dumps(canonical, ensure_ascii=False, separators=(",", ":"))
    return text.encode("utf-8")


def build_signature_record(
    manifest: Mapping[str, Any],
    *,
    signer_cert_id: str,
    signed_at: str | None = None,
) -> SignatureRecord:
    """Build the canonical signature record with SM3 digest pre-computed.

    The ``signature`` field is intentionally left empty in this
    P1 slice (sign requires an approved SM2 product). The receiver
    contract is fail-closed: empty ``signature`` ⇒ verify raises
    :class:`AgentPackageCryptoVerifyError`.
    """
    if not isinstance(signer_cert_id, str) or not signer_cert_id:
        raise AgentPackageCanonicalizationError(
            "signer_cert_id must be a non-empty string"
        )
    canonical = canonical_manifest_bytes(manifest)
    digest_hex = compute_sm3_digest(canonical)
    if not _HEX_RE.match(digest_hex):
        raise AgentPackageCanonicalizationError(
            "SM3 digest must be 64-char lowercase hex"
        )
    return SignatureRecord(
        algorithm=SIGNATURE_ALGORITHM,
        signer_cert_id=signer_cert_id,
        signed_object=SIGNED_OBJECT_NAME,
        manifest_sm3=digest_hex,
        signature="",
        signed_at=signed_at or _now_utc_iso_z(),
    )


def sign_manifest(
    manifest: Mapping[str, Any],
    *,
    signer_cert_id: str,
    signed_at: str | None = None,
    provider: Any | None = None,
    signer_handle: Any | None = None,
) -> SignatureRecord:
    """Sign the manifest with the sender's SM2 private key.

    **Fail-closed**: raises :class:`AgentPackageCryptoUnavailableError`
    when no SM2 provider is injected. The digest computation (above)
    uses real SM3 (GB/T 32905); the SM2 sign step itself requires an
    injected provider (open-source GmSSL 3.2.0 engine, CRYPTO-1).
    """
    if not isinstance(manifest, Mapping):
        raise AgentPackageCanonicalizationError("manifest must be a mapping")
    if provider is not None and callable(getattr(provider, "sign", None)):
        canonical = canonical_manifest_bytes(manifest)
        digest = compute_real_sm3_digest(canonical, provider=provider)
        signature = provider.sign(signer_handle, canonical)
        if not isinstance(signature, bytes) or not signature:
            raise AgentPackageCryptoUnavailableError("SM2 provider returned an empty signature")
        return SignatureRecord(
            SIGNATURE_ALGORITHM, signer_cert_id, SIGNED_OBJECT_NAME, digest,
            base64.b64encode(signature).decode("ascii"), signed_at or _now_utc_iso_z(),
        )
    record = build_signature_record(manifest, signer_cert_id=signer_cert_id, signed_at=signed_at)
    raise AgentPackageCryptoUnavailableError(
        "SM2 signature requires an approved SM2 product; "
        "AGENTS.md §6 forbids silent fallback. Wire encoding is ready; "
        "approved product path is awaited."
    )


def verify_signature(
    record: SignatureRecord,
    *,
    manifest: Mapping[str, Any],
    expected_signer_cert_id: str | None = None,
    provider: Any | None = None,
    signer_handle: Any | None = None,
) -> None:
    """Verify a SignatureRecord against the canonical manifest.

    **Fail-closed**: raises
    :class:`AgentPackageCryptoVerifyError` when invoked until an
    approved SM2 product is wired in. The digest re-computation is
    deterministic; only the SM2 verify step is awaited.
    """
    if not isinstance(record, SignatureRecord):
        raise AgentPackageCanonicalizationError("record must be SignatureRecord")
    if not isinstance(manifest, Mapping):
        raise AgentPackageCanonicalizationError("manifest must be a mapping")
    if expected_signer_cert_id is not None and (
        not isinstance(expected_signer_cert_id, str) or not expected_signer_cert_id
    ):
        raise AgentPackageCanonicalizationError(
            "expected_signer_cert_id must be a non-empty string when provided"
        )
    canonical = canonical_manifest_bytes(manifest)
    digest_hex = (
        compute_real_sm3_digest(canonical, provider=provider)
        if provider is not None else compute_sm3_digest(canonical)
    )
    if digest_hex != record.manifest_sm3:
        raise AgentPackageCryptoVerifyError(
            "manifest SM3 digest does not match signature record"
        )
    if expected_signer_cert_id is not None and (
        record.signer_cert_id != expected_signer_cert_id
    ):
        raise AgentPackageCryptoVerifyError(
            f"signer_cert_id {record.signer_cert_id!r} does not match expected "
            f"{expected_signer_cert_id!r}"
        )
    if record.signature == "":
        # P1: signatures have not been produced. 协议 § 11 第 2 条
        # requires this state to be loud, not silent.
        raise AgentPackageCryptoVerifyError(
            "signature is empty; approved SM2 product has not signed this manifest"
        )
    if provider is not None and callable(getattr(provider, "verify", None)):
        try:
            signature = base64.b64decode(record.signature, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise AgentPackageCryptoVerifyError("signature is not canonical base64") from exc
        if not provider.verify(signer_handle, canonical, signature):
            raise AgentPackageCryptoVerifyError("SM2 signature verification failed")
        return
    raise AgentPackageCryptoVerifyError(
        "SM2 signature verification requires an approved SM2 product; "
        "AGENTS.md §6 forbids silent fallback."
    )


def decode_signature_record(mapping: Mapping[str, Any]) -> SignatureRecord:
    """Decode a signature record from JSON-shaped data.

    Strict field set + types; rejects unknown fields. This is the
    receiver-side counterpart to :meth:`SignatureRecord.to_mapping`.
    """
    required = {
        "algorithm", "signer_cert_id", "signed_object",
        "manifest_sm3", "signature", "signed_at",
    }
    actual = set(mapping.keys())
    if actual != required:
        missing = required - actual
        extra = actual - required
        raise AgentPackageCanonicalizationError(
            f"signature record field mismatch: missing={sorted(missing)!r} "
            f"extra={sorted(extra)!r}"
        )
    algorithm = mapping["algorithm"]
    if algorithm != SIGNATURE_ALGORITHM:
        # The registry layer refuses unknown algorithms at the
        # envelope level; the signature-record level just enforces
        # the single supported value.
        raise AgentPackageCanonicalizationError(
            f"signature algorithm {algorithm!r} is not supported; "
            f"only {SIGNATURE_ALGORITHM!r} is"
        )
    digest = mapping["manifest_sm3"]
    if not isinstance(digest, str) or not _HEX_RE.match(digest):
        raise AgentPackageCanonicalizationError(
            "manifest_sm3 must be 64-char lowercase hex"
        )
    signed_at = mapping["signed_at"]
    if not isinstance(signed_at, str) or not signed_at:
        raise AgentPackageCanonicalizationError("signed_at must be a non-empty string")
    return SignatureRecord(
        algorithm=algorithm,
        signer_cert_id=str(mapping["signer_cert_id"]),
        signed_object=str(mapping["signed_object"]),
        manifest_sm3=digest,
        signature=str(mapping["signature"]),
        signed_at=signed_at,
    )
