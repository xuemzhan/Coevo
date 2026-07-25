"""Fixed Header + Envelope Header encoding for the offline .agent protocol.

Scope and non-goals
--------------------
This module implements ONLY:

* encoding/decoding of the **Fixed Header** (``docs/protocol/agent-package-protocol.md``
  闂?7.1) in big-endian / network byte order, with strict
  byte-exact layout and fail-closed parsing;
* construction, validation and canonical JSON serialisation of the
  **Envelope Header** (闂?7.2) using the project's canonical-JSON rules
  (闂?10);
* project / sequence / package_id semantics needed to detect replay
  and out-of-order packets (闂?16, 闂?17).

It does NOT implement:

* payload encryption (SM4 AEAD 闂?requires an approved SM4 product,
  AGENTS.md 闂? stop condition, deferred to a future AC);
* SM2 key encapsulation (requires approved SM2 product + the
  US-0-AC-2 stored private key 闂?see ``coevo.identity.private_keys``);
* manifest signing or verification (depends on US-0 signed anchors);
* decryption / atomic-import (US-6 territory).

Re-exports are in ``coevo.protocol``; ``AgentPackageError`` and its
subclasses are the protocol boundary's only failure surface.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
import struct
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntFlag
from typing import Any, Mapping

# Wire constants ------------------------------------------------------------

MAGIC = b"AGENTPKG"  # 8 bytes, ASCII
PROTOCOL_MAJOR = 1
PROTOCOL_MINOR = 0

# Fixed Header layout (big-endian, network byte order):
#   8 bytes  Magic
#   2 bytes  Major Version
#   2 bytes  Minor Version
#   4 bytes  Header Length        (envelope JSON length, big-endian)
#   4 bytes  Key Block Length     (key block length, big-endian; this AC emits 0)
#   8 bytes  Payload Length       (ciphertext length, big-endian; this AC emits 0)
#   4 bytes  Flags                (see AgentPackageFlags)
#   4 bytes  Reserved (must be 0)
FIXED_HEADER_FORMAT = ">8sHHIIQI4s"  # 8s(Magic) + 2H(major) + 2H(minor) + 4I(header_len) + 4I(key_block_len) + 8Q(payload_len) + 4I(flags) + 4s(reserved)
FIXED_HEADER_SIZE = struct.calcsize(FIXED_HEADER_FORMAT)  # = 36 bytes
assert FIXED_HEADER_SIZE == 36, "Fixed Header layout drifted"

# Envelope field constraints ------------------------------------------------

PACKAGE_TYPES: frozenset[str] = frozenset({
    "TASK_ASSIGNMENT", "TASK_PROGRESS", "RESULT_SUBMISSION", "TASK_CHANGE",
    "MEETING_DECISION", "RISK_NOTICE", "SUPERVISION_NOTICE", "CORRECTION_PACKAGE",
    "REVOCATION_PACKAGE", "AUDIT_CHECKPOINT",
})

PROTOCOL_VERSION_RE = re.compile(r"^\d+\.\d+$")
CLIENT_VERSION_RE = re.compile(r"^[A-Za-z0-9_.+-]{1,32}$")
INSTANT_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)

# Tight limits to keep malicious envelopes from forcing work on the
# parser. These are well above any realistic package size but BELOW
# plausible DoS targets.
ENVELOPE_MAX_BYTES = 64 * 1024               # 64 KiB 闂?small relative to typical payloads
PROJECT_ID_MAX = 64                           # characters
CERT_ID_MAX = 64                              # characters
NONCE_BASE64_MAX = 128                        # characters
CIPHER_SUITE_MAX = 64                         # characters
COMPRESSION_MAX = 32                         # characters
KEY_BLOCK_FORMAT_MAX = 32                     # characters
PACKAGE_TYPE_MAX = 32                         # characters
SCHEMA_VERSION = "1.0"
CIPHER_SUITE = "CS-SM2-SM4-AEAD-SM3-01"
COMPRESSION_NONE = "NONE"
COMPRESSION_ZIP_DEFLATE = "ZIP-DEFLATE"
KEY_BLOCK_FORMAT = "SM2-KEY-TRANSPORT-V1"


class AgentPackageError(ValueError):
    """Base class for all protocol-level package errors."""


class AgentPackageMagicError(AgentPackageError):
    """The packet does not start with the AGENTPKG magic."""


class AgentPackageVersionError(AgentPackageError):
    """Major / minor protocol version not supported by this client."""


class AgentPackageLayoutError(AgentPackageError):
    """Fixed Header layout is inconsistent (length fields disagree with reality)."""


class AgentPackageEnvelopeError(AgentPackageError):
    """Envelope Header JSON failed structural or semantic validation."""


class AgentPackageCanonicalizationError(AgentPackageError):
    """JSON cannot be serialised in the protocol's canonical form."""


# ----------------------------------------------------------------------------


class AgentPackageFlags(IntFlag):
    """Reserved flag bits in the Fixed Header. Slice-1 uses only NONE."""

    NONE = 0x00000000
    COMPRESSION_ZIP_DEFLATE = 0x00000001
    EXTENSION_PRESENT = 0x00000002
    KEY_BLOCK_PRESENT = 0x00000004
    PAYLOAD_PRESENT = 0x00000008

    @classmethod
    def parse(cls, value: int) -> "AgentPackageFlags":
        if isinstance(value, bool) or not isinstance(value, int):
            raise AgentPackageLayoutError("flags must be an integer bitmask")
        known_mask = int(
            cls.COMPRESSION_ZIP_DEFLATE
            | cls.EXTENSION_PRESENT
            | cls.KEY_BLOCK_PRESENT
            | cls.PAYLOAD_PRESENT
        )
        unknown_bits = value & ~known_mask
        if unknown_bits:
            raise AgentPackageLayoutError(
                f"flags contain unsupported bits: 0x{unknown_bits:08x}"
            )
        return cls(value)


# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class EnvelopeHeader:
    """The Envelope Header (闂?7.2) 闂?canonical UTF-8 JSON, sorted keys.

    Use :meth:`canonical_bytes` to obtain the exact signed/verified bytes,
    and :meth:`from_mapping` for strict validation on read.
    """

    schema_version: str
    protocol_version: str
    package_id: str
    package_type: str
    sender_cert_id: str
    recipient_cert_id: str
    project_id: str
    created_at: str             # ISO-8601 with timezone
    expires_at: str             # ISO-8601 with timezone
    sequence_no: int
    cipher_suite: str
    compression: str
    nonce: str                  # base64
    key_block_format: str
    payload_length: int
    required_client_version: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "protocol_version": self.protocol_version,
            "package_id": self.package_id,
            "package_type": self.package_type,
            "sender_cert_id": self.sender_cert_id,
            "recipient_cert_id": self.recipient_cert_id,
            "project_id": self.project_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "sequence_no": self.sequence_no,
            "cipher_suite": self.cipher_suite,
            "compression": self.compression,
            "nonce": self.nonce,
            "key_block_format": self.key_block_format,
            "payload_length": self.payload_length,
            "required_client_version": self.required_client_version,
        }

    @staticmethod
    def canonical_bytes(envelope: "EnvelopeHeader") -> bytes:
        """Return the exact UTF-8 bytes used for signing/verification.

        Per 闂?10:
        * UTF-8 encoding;
        * no BOM;
        * object keys sorted lexicographically;
        * no insignificant whitespace / newlines;
        * no duplicate keys.
        """
        text = json.dumps(envelope.to_mapping(), ensure_ascii=False,
                          sort_keys=True, separators=(",", ":"))
        try:
            text.encode("utf-8").decode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise AgentPackageCanonicalizationError(
                "envelope contains characters that cannot be encoded as UTF-8"
            ) from exc
        return text.encode("utf-8")

    @staticmethod
    def _require_text(value: Any, *, name: str, maximum: int, pattern: re.Pattern | None = None) -> str:
        if not isinstance(value, str):
            raise AgentPackageEnvelopeError(f"{name} must be a string")
        if not value:
            raise AgentPackageEnvelopeError(f"{name} must not be empty")
        if len(value) > maximum:
            raise AgentPackageEnvelopeError(f"{name} exceeds the maximum length of {maximum} characters")
        if pattern is not None and not pattern.fullmatch(value):
            raise AgentPackageEnvelopeError(f"{name} has an unsupported format")
        # Disallow control / line-separator characters aggressively.
        for ch in value:
            if ord(ch) < 0x20 or ord(ch) == 0x7F:
                raise AgentPackageEnvelopeError(f"{name} contains a control character")
        return value

    @staticmethod
    def _require_nonce(value: Any, *, name: str, maximum: int) -> str:
        if not isinstance(value, str):
            raise AgentPackageEnvelopeError(f"{name} must be a string")
        if len(value) > maximum:
            raise AgentPackageEnvelopeError(f"{name} exceeds the maximum length of {maximum} characters")
        if value == "":
            return value
        if not value.isascii():
            raise AgentPackageEnvelopeError(f"{name} must be canonical ASCII base64")
        try:
            decoded = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise AgentPackageEnvelopeError(f"{name} must be canonical ASCII base64") from exc
        if base64.b64encode(decoded).decode("ascii") != value:
            raise AgentPackageEnvelopeError(f"{name} must use canonical base64 padding")
        return value

    @staticmethod
    def _require_int(value: Any, *, name: str, minimum: int = 0, maximum: int = (1 << 63) - 1) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise AgentPackageEnvelopeError(f"{name} must be a non-negative integer")
        if value < minimum or value > maximum:
            raise AgentPackageEnvelopeError(f"{name} must be in the range [{minimum}, {maximum}]")
        return value

    @staticmethod
    def from_mapping(payload: Mapping[str, Any]) -> "EnvelopeHeader":
        if not isinstance(payload, Mapping):
            raise AgentPackageEnvelopeError("envelope payload must be an object")
        required = {
            "schema_version", "protocol_version", "package_id", "package_type",
            "sender_cert_id", "recipient_cert_id", "project_id",
            "created_at", "expires_at", "sequence_no", "cipher_suite",
            "compression", "nonce", "key_block_format", "payload_length",
            "required_client_version",
        }
        unknown = set(payload) - required
        if unknown:
            raise AgentPackageEnvelopeError(
                f"envelope has unsupported fields: {', '.join(sorted(map(str, unknown)))}"
            )
        missing = required - set(payload)
        if missing:
            raise AgentPackageEnvelopeError(
                f"envelope is missing required fields: {', '.join(sorted(missing))}"
            )

        envelope = EnvelopeHeader(
            schema_version=EnvelopeHeader._require_text(
                payload["schema_version"], name="schema_version", maximum=16,
            ),
            protocol_version=EnvelopeHeader._require_text(
                payload["protocol_version"], name="protocol_version",
                maximum=16, pattern=PROTOCOL_VERSION_RE,
            ),
            package_id=EnvelopeHeader._require_uuid_string(
                payload["package_id"], name="package_id",
            ),
            package_type=EnvelopeHeader._require_text(
                payload["package_type"], name="package_type",
                maximum=PACKAGE_TYPE_MAX,
            ),
            sender_cert_id=EnvelopeHeader._require_text(
                payload["sender_cert_id"], name="sender_cert_id", maximum=CERT_ID_MAX,
            ),
            recipient_cert_id=EnvelopeHeader._require_text(
                payload["recipient_cert_id"], name="recipient_cert_id", maximum=CERT_ID_MAX,
            ),
            project_id=EnvelopeHeader._require_text(
                payload["project_id"], name="project_id", maximum=PROJECT_ID_MAX,
            ),
            created_at=EnvelopeHeader._require_instant(
                payload["created_at"], name="created_at", must_be_future_safe=True,
            ),
            expires_at=EnvelopeHeader._require_instant(
                payload["expires_at"], name="expires_at", must_be_future_safe=False,
            ),
            sequence_no=EnvelopeHeader._require_int(
                payload["sequence_no"], name="sequence_no", minimum=1, maximum=1 << 31,
            ),
            cipher_suite=EnvelopeHeader._require_text(
                payload["cipher_suite"], name="cipher_suite", maximum=CIPHER_SUITE_MAX,
            ),
            compression=EnvelopeHeader._require_text(
                payload["compression"], name="compression", maximum=COMPRESSION_MAX,
            ),
            nonce=EnvelopeHeader._require_nonce(
                payload["nonce"], name="nonce", maximum=NONCE_BASE64_MAX,
            ),
            key_block_format=EnvelopeHeader._require_text(
                payload["key_block_format"], name="key_block_format",
                maximum=KEY_BLOCK_FORMAT_MAX,
            ),
            payload_length=EnvelopeHeader._require_int(
                payload["payload_length"], name="payload_length",
            ),
            required_client_version=EnvelopeHeader._require_text(
                payload["required_client_version"], name="required_client_version",
                maximum=64, pattern=CLIENT_VERSION_RE,
            ),
        )
        if envelope.package_type not in PACKAGE_TYPES:
            raise AgentPackageEnvelopeError(
                f"package_type {envelope.package_type!r} is not in the protocol enum"
            )
        expected_values = {
            "schema_version": SCHEMA_VERSION,
            "protocol_version": f"{PROTOCOL_MAJOR}.{PROTOCOL_MINOR}",
            "cipher_suite": CIPHER_SUITE,
            "key_block_format": KEY_BLOCK_FORMAT,
        }
        for field_name, expected in expected_values.items():
            if getattr(envelope, field_name) != expected:
                raise AgentPackageEnvelopeError(
                    f"{field_name} must be {expected!r} for protocol 1.0"
                )
        if envelope.compression not in {COMPRESSION_NONE, COMPRESSION_ZIP_DEFLATE}:
            raise AgentPackageEnvelopeError("compression is not supported")
        created = datetime.fromisoformat(envelope.created_at.replace("Z", "+00:00"))
        expires = datetime.fromisoformat(envelope.expires_at.replace("Z", "+00:00"))
        if expires <= created:
            raise AgentPackageEnvelopeError("expires_at must be strictly after created_at")
        if envelope.payload_length > 0 and envelope.nonce == "":
            raise AgentPackageEnvelopeError("nonce must not be empty when payload_length is nonzero")
        if envelope.payload_length > (1 << 40):  # 1 TiB hard cap 闂?even worst case far below
            raise AgentPackageEnvelopeError(
                "payload_length exceeds the protocol's 1 TiB hard limit"
            )
        return envelope

    @staticmethod
    def _require_uuid_string(value: Any, *, name: str) -> str:
        text = EnvelopeHeader._require_text(value, name=name, maximum=64)
        try:
            normalised = str(uuid.UUID(text))
        except (ValueError, AttributeError, TypeError) as exc:
            raise AgentPackageEnvelopeError(f"{name} must be a UUID") from exc
        if normalised != text:
            raise AgentPackageEnvelopeError(f"{name} must be canonical lowercase UUID text")
        return text

    @staticmethod
    def _require_instant(value: Any, *, name: str, must_be_future_safe: bool) -> str:
        text = EnvelopeHeader._require_text(value, name=name, maximum=64)
        if not INSTANT_RE.fullmatch(text):
            raise AgentPackageEnvelopeError(
                f"{name} must use YYYY-MM-DDTHH:MM:SS[.ffffff](Z|+HH:MM)"
            )
        candidate = text.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError as exc:
            raise AgentPackageEnvelopeError(f"{name} must be ISO-8601") from exc
        if parsed.tzinfo is None:
            raise AgentPackageEnvelopeError(f"{name} must include a timezone")
        # Round-trip: ASCII emit; reject any non-ASCII digits.
        if not text.isascii():
            raise AgentPackageEnvelopeError(f"{name} contains non-ASCII characters")
        return text


# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class FixedHeader:
    """Decoded Fixed Header 闂?enough bytes to drive routing decisions."""

    major: int
    minor: int
    header_length: int      # Envelope Header length in bytes
    key_block_length: int
    payload_length: int
    flags: AgentPackageFlags = field(default=AgentPackageFlags.NONE)
    version: tuple[int, int] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "version", (self.major, self.minor))


def _reserved_must_be_zero(chunk: bytes, *, error: type[AgentPackageError]) -> bytes:
    if any(byte != 0 for byte in chunk):
        raise error("reserved field must be zero")
    return chunk


def encode_fixed_header(*, header_length: int, key_block_length: int = 0,
                        payload_length: int = 0, flags: AgentPackageFlags | int = AgentPackageFlags.NONE,
                        major: int = PROTOCOL_MAJOR, minor: int = PROTOCOL_MINOR) -> bytes:
    """Render the 36-byte Fixed Header in network / big-endian byte order."""
    integer_fields = {
        "header_length": (header_length, 0xFFFFFFFF),
        "key_block_length": (key_block_length, 0xFFFFFFFF),
        "payload_length": (payload_length, 0xFFFFFFFFFFFFFFFF),
        "major": (major, 0xFFFF),
        "minor": (minor, 0xFFFF),
    }
    for name, (value, maximum) in integer_fields.items():
        if isinstance(value, bool) or not isinstance(value, int):
            raise AgentPackageLayoutError(f"{name} must be an integer")
        if value < 0 or value > maximum:
            raise AgentPackageLayoutError(f"{name} out of range")
    if isinstance(flags, AgentPackageFlags):
        flags_int = int(flags)
    elif isinstance(flags, int) and not isinstance(flags, bool):
        flags_int = int(AgentPackageFlags.parse(flags))
    else:
        raise AgentPackageLayoutError("flags must be an AgentPackageFlags value")
    reserved = b"\x00" * 4
    return struct.pack(
        FIXED_HEADER_FORMAT,
        MAGIC, major, minor,
        header_length & 0xFFFFFFFF,
        key_block_length & 0xFFFFFFFF,
        payload_length & 0xFFFFFFFFFFFFFFFF,
        int(flags) & 0xFFFFFFFF,
        reserved,
    )


def decode_fixed_header(blob: bytes) -> FixedHeader:
    """Parse + validate the Fixed Header. Fails closed on any deviation."""
    if not isinstance(blob, (bytes, bytearray, memoryview)):
        raise AgentPackageMagicError("fixed header must be bytes")
    if len(blob) < FIXED_HEADER_SIZE:
        raise AgentPackageLayoutError(
            f"fixed header must be at least {FIXED_HEADER_SIZE} bytes; got {len(blob)}"
        )
    magic, major, minor, header_length, key_block_length, payload_length, flags_int, reserved = (
        struct.unpack(FIXED_HEADER_FORMAT, bytes(blob[:FIXED_HEADER_SIZE]))
    )
    if magic != MAGIC:
        raise AgentPackageMagicError(f"package magic mismatch; expected {MAGIC!r}, got {magic!r}")
    if major != PROTOCOL_MAJOR or minor != PROTOCOL_MINOR:
        raise AgentPackageVersionError(
            f"unsupported protocol version {major}.{minor}; client supports "
            f"{PROTOCOL_MAJOR}.{PROTOCOL_MINOR}"
        )
    _reserved_must_be_zero(reserved, error=AgentPackageLayoutError)
    flags = AgentPackageFlags.parse(flags_int)
    if not isinstance(flags, AgentPackageFlags):
        raise AgentPackageLayoutError("flags must be a valid IntFlag combination")
    return FixedHeader(major=major, minor=minor,
                       header_length=header_length,
                       key_block_length=key_block_length,
                       payload_length=payload_length,
                       flags=flags)


def encode_envelope(envelope: EnvelopeHeader) -> bytes:
    """Return canonical UTF-8 JSON bytes for the Envelope Header."""
    return EnvelopeHeader.canonical_bytes(envelope)


def decode_envelope(blob: bytes) -> EnvelopeHeader:
    """Strictly parse an Envelope Header from canonical UTF-8 JSON."""
    if not isinstance(blob, (bytes, bytearray)):
        raise AgentPackageEnvelopeError("envelope must be bytes")
    if not blob:
        raise AgentPackageEnvelopeError("envelope is empty")
    if len(blob) > ENVELOPE_MAX_BYTES:
        raise AgentPackageEnvelopeError(
            f"envelope exceeds maximum size of {ENVELOPE_MAX_BYTES} bytes"
        )
    # Reject BOM aggressively 闂?the protocol forbids BOM (闂?10).
    if blob.startswith(b"\xef\xbb\xbf"):
        raise AgentPackageEnvelopeError("envelope must not start with a UTF-8 BOM")
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AgentPackageEnvelopeError("envelope is not valid UTF-8") from exc
    try:
        parsed = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise AgentPackageEnvelopeError(f"envelope JSON is malformed: {exc.msg}") from exc
    if not isinstance(parsed, dict):
        raise AgentPackageEnvelopeError("envelope JSON top-level must be an object")
    envelope = EnvelopeHeader.from_mapping(parsed)
    if bytes(blob) != EnvelopeHeader.canonical_bytes(envelope):
        raise AgentPackageCanonicalizationError("envelope JSON is not canonical")
    return envelope


def _reject_duplicate_keys(pairs: list[tuple[Any, Any]]) -> dict[Any, Any]:
    seen: set[Any] = set()
    for key, _ in pairs:
        if key in seen:
            from json import JSONDecodeError
            raise JSONDecodeError("duplicate key in envelope", "", 0)
        seen.add(key)
    return dict(pairs)


# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class ParsedPackageHeader:
    """Combined Fixed Header + Envelope Header parse result for routing."""

    fixed: FixedHeader
    envelope: EnvelopeHeader
    envelope_bytes: bytes  # canonical bytes for signing/verification
    total_length: int     # fixed (36) + envelope + key_block + payload


def parse_package_header(blob: bytes) -> ParsedPackageHeader:
    """Parse a full .agent package header (Fixed + Envelope) in one shot."""
    if not isinstance(blob, (bytes, bytearray, memoryview)):
        raise AgentPackageMagicError("package must be bytes")
    if len(blob) < FIXED_HEADER_SIZE:
        raise AgentPackageLayoutError(
            f"package too short for the fixed header ({len(blob)} < {FIXED_HEADER_SIZE})"
        )
    fixed = decode_fixed_header(bytes(blob[:FIXED_HEADER_SIZE]))
    envelope_end = FIXED_HEADER_SIZE + fixed.header_length
    if fixed.header_length == 0 or fixed.header_length > ENVELOPE_MAX_BYTES:
        raise AgentPackageLayoutError("header_length is outside the envelope size limit")
    if envelope_end > len(blob):
        raise AgentPackageLayoutError(
            "package declares a header_length that exceeds the available bytes"
        )
    envelope_bytes = bytes(blob[FIXED_HEADER_SIZE:envelope_end])
    envelope = decode_envelope(envelope_bytes)
    if envelope.payload_length != fixed.payload_length:
        raise AgentPackageLayoutError(
            "envelope.payload_length disagrees with fixed header payload_length"
        )
    has_key_block = bool(fixed.flags & AgentPackageFlags.KEY_BLOCK_PRESENT)
    has_payload = bool(fixed.flags & AgentPackageFlags.PAYLOAD_PRESENT)
    if has_key_block != (fixed.key_block_length > 0):
        raise AgentPackageLayoutError("KEY_BLOCK_PRESENT must agree with key_block_length")
    if has_payload != (fixed.payload_length > 0):
        raise AgentPackageLayoutError("PAYLOAD_PRESENT must agree with payload_length")
    compressed = bool(fixed.flags & AgentPackageFlags.COMPRESSION_ZIP_DEFLATE)
    if fixed.payload_length > 0 and fixed.key_block_length == 0:
        raise AgentPackageLayoutError(
            "an encrypted payload requires a non-empty recipient key block"
        )
    if fixed.key_block_length > 0 and fixed.payload_length == 0:
        raise AgentPackageLayoutError(
            "a recipient key block is not allowed without an encrypted payload"
        )
    if compressed != (envelope.compression == COMPRESSION_ZIP_DEFLATE):
        raise AgentPackageLayoutError("compression flag must agree with envelope.compression")
    if fixed.flags & AgentPackageFlags.EXTENSION_PRESENT:
        raise AgentPackageLayoutError("extensions are not implemented by US-5-AC-1")
    total_length = FIXED_HEADER_SIZE + fixed.header_length + fixed.key_block_length + fixed.payload_length
    if total_length != len(blob):
        raise AgentPackageLayoutError(
            "package length must equal the declared header, key block and payload lengths"
        )
    return ParsedPackageHeader(
        fixed=fixed, envelope=envelope,
        envelope_bytes=envelope_bytes,
        total_length=total_length,
    )


def build_envelope_template(
    *,
    sender_cert_id: str,
    recipient_cert_id: str,
    project_id: str,
    package_type: str,
    sequence_no: int,
    payload_length: int,
    cipher_suite: str = CIPHER_SUITE,
    compression: str = COMPRESSION_NONE,
    nonce_b64: str = "",
    key_block_format: str = KEY_BLOCK_FORMAT,
    required_client_version: str = "1.0.0",
    created_at: str | None = None,
    expires_at: str | None = None,
) -> EnvelopeHeader:
    """Build an EnvelopeHeader suitable for the round-1 implementation.

    Defaults produce a syntactically-valid, future-timestamped envelope
    that tests and tooling can use directly. ``nonce_b64`` is provided by
    the caller to bind the package to the encrypted session key; empty
    string is permitted in the template 闂?it surfaces as the literal
    string ``""`` in canonical JSON, and the receiver MUST treat an
    empty nonce as a failed integrity claim (encoded payload length 0).
    """
    now = datetime.now(UTC).replace(microsecond=0)
    if created_at is None:
        created_at = now.isoformat().replace("+00:00", "Z")
    if expires_at is None:
        one_year = now.replace(year=now.year + 1)
        expires_at = one_year.isoformat().replace("+00:00", "Z")
    mapping = {
        "schema_version": "1.0",
        "protocol_version": f"{PROTOCOL_MAJOR}.{PROTOCOL_MINOR}",
        "package_id": str(uuid.uuid4()),
        "package_type": package_type,
        "sender_cert_id": sender_cert_id,
        "recipient_cert_id": recipient_cert_id,
        "project_id": project_id,
        "created_at": created_at,
        "expires_at": expires_at,
        "sequence_no": sequence_no,
        "cipher_suite": cipher_suite,
        "compression": compression,
        "nonce": nonce_b64,
        "key_block_format": key_block_format,
        "payload_length": payload_length,
        "required_client_version": required_client_version,
    }
    return EnvelopeHeader.from_mapping(mapping)


__all__ = [
    "MAGIC",
    "PROTOCOL_MAJOR",
    "PROTOCOL_MINOR",
    "FIXED_HEADER_SIZE",
    "ENVELOPE_MAX_BYTES",
    "PACKAGE_TYPES",
    "AgentPackageError",
    "AgentPackageMagicError",
    "AgentPackageVersionError",
    "AgentPackageLayoutError",
    "AgentPackageEnvelopeError",
    "AgentPackageCanonicalizationError",
    "AgentPackageFlags",
    "EnvelopeHeader",
    "FixedHeader",
    "ParsedPackageHeader",
    "encode_fixed_header",
    "decode_fixed_header",
    "encode_envelope",
    "decode_envelope",
    "parse_package_header",
    "build_envelope_template",
]
