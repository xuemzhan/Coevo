"""Protocol integration tests for US-5-AC-1: Fixed Header and Envelope.

Scope and non-goals
--------------------
This test module exercises ONLY the parts of the .agent protocol
implemented in Round-1 (US-5-AC-1):

* Fixed Header byte-exact layout (big-endian / network byte order, magic,
  version, length fields, reserved zero, flag bits);
* Envelope Header canonical-JSON serialisation, strict validation,
  reject-path coverage for every disallowed field shape;
* Combined parse_package_header routing logic that the receive-side
  uses BEFORE doing any cryptographic operation.

It does NOT exercise:

* manifest signing/verification (US-5 AC-3);
* SM4 inner-payload decryption (requires approved SM4 product;
  AGENTS.md § 6 stop condition);
* SM2 key-wrap over the session key (depends on US-0-AC-2 store +
  approved SM2 product).

Each test asserts behaviour, never implementation. Anything the
protocol says you MUST or MUST NOT do is asserted directly.
"""

from __future__ import annotations

import json
import struct
import sys
import unittest
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from coevo.protocol.agent_package import (
    ENVELOPE_MAX_BYTES,
    FIXED_HEADER_SIZE,
    MAGIC,
    PACKAGE_TYPES,
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    AgentPackageCanonicalizationError,
    AgentPackageEnvelopeError,
    AgentPackageFlags,
    AgentPackageLayoutError,
    AgentPackageMagicError,
    AgentPackageVersionError,
    EnvelopeHeader,
    build_envelope_template,
    decode_envelope,
    decode_fixed_header,
    encode_envelope,
    encode_fixed_header,
    parse_package_header,
)


def _envelope_dict(**overrides) -> dict:
    base = {
        "schema_version": "1.0",
        "protocol_version": f"{PROTOCOL_MAJOR}.{PROTOCOL_MINOR}",
        "package_id": str(uuid.uuid4()),
        "package_type": "TASK_ASSIGNMENT",
        "sender_cert_id": "CERT-SENDER-001",
        "recipient_cert_id": "CERT-RECIPIENT-021",
        "project_id": "PRJ001",
        "created_at": "2026-07-15T10:20:30Z",
        "expires_at": "2026-08-15T23:59:59Z",
        "sequence_no": 12,
        "cipher_suite": "CS-SM2-SM4-AEAD-SM3-01",
        "compression": "ZIP-DEFLATE",
        "nonce": "AAAAAAAAAAAAAAAAAAAAAA==",
        "key_block_format": "SM2-KEY-TRANSPORT-V1",
        "payload_length": 123456,
        "required_client_version": "1.0.0",
    }
    base.update(overrides)
    return base


class FixedHeaderTests(unittest.TestCase):
    """Fixed Header: byte-exact layout and fail-closed decoders (Section 7.1)."""

    def test_encode_produces_exactly_36_bytes(self) -> None:
        blob = encode_fixed_header(header_length=2000, key_block_length=192,
                                  payload_length=65537,
                                  flags=AgentPackageFlags.COMPRESSION_ZIP_DEFLATE)
        self.assertEqual(len(blob), FIXED_HEADER_SIZE)
        self.assertEqual(len(blob), 36)

    def test_decode_matches_encode_round_trip(self) -> None:
        blob = encode_fixed_header(header_length=2000, key_block_length=192,
                                  payload_length=123456,
                                  flags=AgentPackageFlags.COMPRESSION_ZIP_DEFLATE)
        parsed = decode_fixed_header(blob)
        self.assertEqual(parsed.major, PROTOCOL_MAJOR)
        self.assertEqual(parsed.minor, PROTOCOL_MINOR)
        self.assertEqual(parsed.header_length, 2000)
        self.assertEqual(parsed.key_block_length, 192)
        self.assertEqual(parsed.payload_length, 123456)
        self.assertEqual(parsed.flags, AgentPackageFlags.COMPRESSION_ZIP_DEFLATE)

    def test_first_eight_bytes_are_AGENTPKG(self) -> None:
        blob = encode_fixed_header(header_length=0)
        self.assertEqual(blob[:8], MAGIC)
        self.assertEqual(blob[:8], b"AGENTPKG")

    def test_layout_is_big_endian_network_order(self) -> None:
        blob = encode_fixed_header(header_length=0x01020304,
                                  key_block_length=0xDEADBEEF,
                                  payload_length=0xAABBCCDDEEFF0011,
                                  flags=0x0000000F)
        magic, major, minor, header_len, key_len, payload_len, flags, reserved = (
            struct.unpack(">8sHHIIQI4s", blob)
        )
        self.assertEqual(magic, b"AGENTPKG")
        self.assertEqual(major, PROTOCOL_MAJOR)
        self.assertEqual(minor, PROTOCOL_MINOR)
        self.assertEqual(header_len, 0x01020304)
        self.assertEqual(key_len, 0xDEADBEEF)
        self.assertEqual(payload_len, 0xAABBCCDDEEFF0011)
        self.assertEqual(flags, 0x0000000F)
        self.assertEqual(reserved, b"\x00\x00\x00\x00")

    def test_decode_rejects_wrong_magic(self) -> None:
        blob = encode_fixed_header(header_length=0)
        bad = b"NOTPKG\x00\x00" + blob[8:]
        with self.assertRaises(AgentPackageMagicError):
            decode_fixed_header(bad)

    def test_decode_rejects_truncated_input(self) -> None:
        blob = encode_fixed_header(header_length=10)
        with self.assertRaises(AgentPackageLayoutError):
            decode_fixed_header(blob[:10])
        with self.assertRaises(AgentPackageLayoutError):
            decode_fixed_header(blob[: FIXED_HEADER_SIZE - 1])

    def test_decode_rejects_nonzero_reserved(self) -> None:
        blob = encode_fixed_header(header_length=0)
        tampered = blob[:32] + b"\x00\x00\x00\x01"
        with self.assertRaises(AgentPackageLayoutError):
            decode_fixed_header(tampered)

    def test_decode_rejects_unknown_protocol_version(self) -> None:
        bad = MAGIC + struct.pack(">HH", 2, 0) + struct.pack(">IIQ", 0, 0, 0) + struct.pack(">I", 0) + b"\x00\x00\x00\x00"
        with self.assertRaises(AgentPackageVersionError):
            decode_fixed_header(bad)

    def test_decode_rejects_non_bytes_input(self) -> None:
        with self.assertRaises(AgentPackageMagicError):
            decode_fixed_header("not bytes")  # type: ignore[arg-type]

    def test_decode_rejects_unknown_flag_bits(self) -> None:
        blob = bytearray(encode_fixed_header(header_length=0))
        blob[28:32] = struct.pack(">I", 0x80000000)
        with self.assertRaises(AgentPackageLayoutError):
            decode_fixed_header(bytes(blob))

    def test_encode_accepts_each_declared_flag_bit(self) -> None:
        combined = (
            AgentPackageFlags.COMPRESSION_ZIP_DEFLATE
            | AgentPackageFlags.EXTENSION_PRESENT
            | AgentPackageFlags.KEY_BLOCK_PRESENT
            | AgentPackageFlags.PAYLOAD_PRESENT
        )
        parsed = decode_fixed_header(
            encode_fixed_header(header_length=0, flags=int(combined))
        )
        self.assertEqual(parsed.flags, combined)

    def test_encode_rejects_unknown_flag_bits(self) -> None:
        with self.assertRaises(AgentPackageLayoutError):
            encode_fixed_header(header_length=0, flags=0x80000000)


class EnvelopeCanonicalizationTests(unittest.TestCase):
    """Envelope canonical-JSON (Section 7.2 + 10)."""

    def test_canonical_bytes_round_trip_through_sorted_json(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        text = encode_envelope(env).decode("utf-8")
        parsed = json.loads(text)
        self.assertEqual(set(parsed), {
            "schema_version", "protocol_version", "package_id", "package_type",
            "sender_cert_id", "recipient_cert_id", "project_id",
            "created_at", "expires_at", "sequence_no", "cipher_suite",
            "compression", "nonce", "key_block_format", "payload_length",
            "required_client_version",
        })
        # Lexicographic ordering: payload_length must come after package_id.
        self.assertLess(text.find('"package_id"'), text.find('"payload_length"'))
        self.assertLess(text.find('"created_at"'), text.find('"expires_at"'))

    def test_canonical_bytes_have_no_trailing_whitespace(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        text = encode_envelope(env)
        self.assertFalse(text.endswith((b"\n", b"\r")))

    def test_canonical_is_ascii_only(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        text = encode_envelope(env)
        try:
            text.decode("ascii")
        except UnicodeDecodeError:
            self.fail("envelope canonical bytes contain non-ASCII")

    def test_no_bom_in_canonical_bytes(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        text = encode_envelope(env)
        self.assertFalse(text.startswith(b"\xef\xbb\xbf"))


class EnvelopeStrictValidationTests(unittest.TestCase):
    """Fail-closed validation per Section 7.2 and 10."""

    def test_unknown_field_rejected(self) -> None:
        bad = _envelope_dict(unknown_field="x")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_missing_field_rejected(self) -> None:
        bad = _envelope_dict()
        bad.pop("package_id")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_invalid_uuid_rejected(self) -> None:
        bad = _envelope_dict(package_id="not-a-uuid")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_uuid_must_be_lowercase_canonical(self) -> None:
        bad = _envelope_dict(package_id=str(uuid.uuid4()).upper())
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_unknown_package_type_rejected(self) -> None:
        bad = _envelope_dict(package_type="MYSTERY_TYPE")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_each_supported_package_type_round_trips(self) -> None:
        for package_type in PACKAGE_TYPES:
            env = EnvelopeHeader.from_mapping(_envelope_dict(package_type=package_type))
            self.assertEqual(env.package_type, package_type)

    def test_naive_timestamp_rejected(self) -> None:
        bad = _envelope_dict(created_at="2026-07-15T10:20:30")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_expires_before_created_rejected(self) -> None:
        bad = _envelope_dict(created_at="2026-08-15T23:59:59Z", expires_at="2026-07-15T10:20:30Z")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_control_characters_in_strings_rejected(self) -> None:
        bad = _envelope_dict(project_id="PRJ\x01\x02")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_overlong_string_rejected(self) -> None:
        bad = _envelope_dict(project_id="X" * 1024)
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_negative_sequence_no_rejected(self) -> None:
        bad = _envelope_dict(sequence_no=-1)
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_huge_sequence_no_rejected(self) -> None:
        bad = _envelope_dict(sequence_no=1 << 40)
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_oversize_payload_length_rejected(self) -> None:
        bad = _envelope_dict(payload_length=1 << 50)
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_empty_string_field_rejected(self) -> None:
        bad = _envelope_dict(sender_cert_id="")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)

    def test_malformed_protocol_version_rejected(self) -> None:
        bad = _envelope_dict(protocol_version="1")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad)
        bad2 = _envelope_dict(protocol_version="1.x")
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(bad2)


class EnvelopeDecodeTests(unittest.TestCase):
    """Parsing the canonical JSON back into an EnvelopeHeader."""

    def test_decode_round_trip(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        text = encode_envelope(env)
        again = decode_envelope(text)
        self.assertEqual(again, env)

    def test_decode_rejects_bom(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        with_bom = b"\xef\xbb\xbf" + encode_envelope(env)
        with self.assertRaises(AgentPackageEnvelopeError):
            decode_envelope(with_bom)

    def test_decode_rejects_oversize(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        text = encode_envelope(env)
        too_big = text + b"\x00" * (ENVELOPE_MAX_BYTES + 1)
        with self.assertRaises(AgentPackageEnvelopeError):
            decode_envelope(too_big)

    def test_decode_rejects_duplicate_keys(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        text = encode_envelope(env).decode("utf-8")
        tampered = text.replace('"sequence_no":12', '"sequence_no":12,"sequence_no":12', 1)
        with self.assertRaises(AgentPackageEnvelopeError):
            decode_envelope(tampered.encode("utf-8"))

    def test_decode_rejects_non_object_top_level(self) -> None:
        with self.assertRaises(AgentPackageEnvelopeError):
            decode_envelope(b'"just a string"\n')

    def test_decode_rejects_non_utf8(self) -> None:
        with self.assertRaises(AgentPackageEnvelopeError):
            decode_envelope(b"\xff\xfe\x00\x01not utf-8")


class TemplateAndCombinedTests(unittest.TestCase):
    """``build_envelope_template`` and full ``parse_package_header``."""

    def test_template_default_is_valid_envelope(self) -> None:
        env = build_envelope_template(
            sender_cert_id="CERT-S",
            recipient_cert_id="CERT-R",
            project_id="PRJ001",
            package_type="TASK_ASSIGNMENT",
            sequence_no=7,
            payload_length=4096,
            nonce_b64="AAAAAAAAAAAAAAAAAAAAAA==",
        )
        self.assertEqual(env.sequence_no, 7)
        self.assertEqual(env.payload_length, 4096)
        text = encode_envelope(env)
        again = decode_envelope(text)
        self.assertEqual(again, env)

    def test_combined_parse_round_trip_header_only(self) -> None:
        env = build_envelope_template(
            sender_cert_id="CERT-S",
            recipient_cert_id="CERT-R",
            project_id="PRJ001",
            package_type="RESULT_SUBMISSION",
            sequence_no=42,
            payload_length=2048,
            nonce_b64="AAAAAAAAAAAAAAAAAAAAAA==",
        )
        envelope_bytes = encode_envelope(env)
        blob = (
            encode_fixed_header(
                header_length=len(envelope_bytes),
                key_block_length=32,
                payload_length=2048,
                flags=(AgentPackageFlags.KEY_BLOCK_PRESENT | AgentPackageFlags.PAYLOAD_PRESENT),
            )
            + envelope_bytes
            + (b"P" * 2048)
            + (b"K" * 32)
        )
        parsed = parse_package_header(blob)
        self.assertEqual(parsed.fixed.major, PROTOCOL_MAJOR)
        self.assertEqual(parsed.fixed.minor, PROTOCOL_MINOR)
        self.assertEqual(parsed.fixed.payload_length, 2048)
        self.assertEqual(parsed.envelope.sequence_no, 42)
        self.assertEqual(parsed.envelope.payload_length, 2048)
        self.assertEqual(parsed.envelope_bytes, envelope_bytes)
        # Total length is fixed header (36) + envelope + key block (32) + payload (2048).
        self.assertEqual(parsed.total_length, 36 + len(envelope_bytes) + 32 + 2048)

    def test_combined_parse_rejects_envelope_mismatch_payload(self) -> None:
        env = build_envelope_template(
            sender_cert_id="CERT-S",
            recipient_cert_id="CERT-R",
            project_id="PRJ001",
            package_type="TASK_ASSIGNMENT",
            sequence_no=1,
            payload_length=2048,
            nonce_b64="AAAAAAAAAAAAAAAAAAAAAA==",
        )
        envelope_bytes = encode_envelope(env)
        blob = (
            encode_fixed_header(header_length=len(envelope_bytes),
                                key_block_length=0, payload_length=9999,
                                flags=AgentPackageFlags.PAYLOAD_PRESENT)
            + envelope_bytes
        )
        with self.assertRaises(AgentPackageLayoutError):
            parse_package_header(blob)

    def test_combined_parse_rejects_truncated_key_block_and_payload(self) -> None:
        env = build_envelope_template(
            sender_cert_id="CERT-S",
            recipient_cert_id="CERT-R",
            project_id="PRJ001",
            package_type="TASK_ASSIGNMENT",
            sequence_no=1,
            payload_length=3,
            nonce_b64="AAAAAAAAAAAAAAAAAAAAAA==",
        )
        envelope_bytes = encode_envelope(env)
        blob = (
            encode_fixed_header(
                header_length=len(envelope_bytes),
                key_block_length=4,
                payload_length=3,
                flags=(AgentPackageFlags.KEY_BLOCK_PRESENT | AgentPackageFlags.PAYLOAD_PRESENT),
            )
            + envelope_bytes
            + b"KEY"
        )
        with self.assertRaises(AgentPackageLayoutError):
            parse_package_header(blob)

    def test_combined_parse_rejects_truncated_envelope(self) -> None:
        env = build_envelope_template(
            sender_cert_id="CERT-S",
            recipient_cert_id="CERT-R",
            project_id="PRJ001",
            package_type="TASK_ASSIGNMENT",
            sequence_no=1,
            payload_length=0,
        )
        envelope_bytes = encode_envelope(env)
        blob = encode_fixed_header(header_length=len(envelope_bytes) + 5,
                                   key_block_length=0,
                                   payload_length=0) + envelope_bytes
        with self.assertRaises(AgentPackageLayoutError):
            parse_package_header(blob)


class ProtocolEnumTests(unittest.TestCase):
    """Flags and constants never silently regress."""

    def test_flags_intflag_round_trip(self) -> None:
        for value in (0, 1, 5, 0x0F):
            flags = AgentPackageFlags.parse(value)
            self.assertEqual(int(flags), value)

    def test_magic_is_eight_ascii_bytes(self) -> None:
        self.assertEqual(len(MAGIC), 8)
        try:
            MAGIC.decode("ascii")
        except UnicodeDecodeError:
            self.fail("MAGIC contains non-ASCII")
        self.assertEqual(MAGIC, b"AGENTPKG")

    def test_package_types_enum_covers_documented_set(self) -> None:
        self.assertIn("TASK_ASSIGNMENT", PACKAGE_TYPES)
        self.assertIn("RESULT_SUBMISSION", PACKAGE_TYPES)
        self.assertIn("REVOCATION_PACKAGE", PACKAGE_TYPES)
        self.assertEqual(len(PACKAGE_TYPES), 10)


class ReviewFindingRegressionTests(unittest.TestCase):
    """Regression coverage for independent protocol/security review findings."""

    def test_decode_rejects_noncanonical_json_bytes(self) -> None:
        env = EnvelopeHeader.from_mapping(_envelope_dict())
        canonical = encode_envelope(env)
        mapping = json.loads(canonical)
        variants = (
            json.dumps(mapping, sort_keys=False).encode("utf-8"),
            b" " + canonical,
            canonical + b"\n",
            canonical.replace(b'":', b'" :', 1),
        )
        for variant in variants:
            with self.subTest(variant=variant[-20:]):
                with self.assertRaises((AgentPackageCanonicalizationError, AgentPackageEnvelopeError)):
                    decode_envelope(variant)

    def test_payload_and_recipient_key_block_must_be_paired(self) -> None:
        cases = (
            (
                EnvelopeHeader.from_mapping(_envelope_dict(payload_length=1)),
                0, 1, AgentPackageFlags.PAYLOAD_PRESENT, b"P",
            ),
            (
                EnvelopeHeader.from_mapping(_envelope_dict(payload_length=0, nonce="")),
                1, 0, AgentPackageFlags.KEY_BLOCK_PRESENT, b"K",
            ),
        )
        for envelope, key_length, payload_length, flags, suffix in cases:
            envelope_bytes = encode_envelope(envelope)
            blob = (
                encode_fixed_header(
                    header_length=len(envelope_bytes),
                    key_block_length=key_length,
                    payload_length=payload_length,
                    flags=flags,
                )
                + envelope_bytes
                + suffix
            )
            with self.subTest(key_length=key_length, payload_length=payload_length):
                with self.assertRaises(AgentPackageLayoutError):
                    parse_package_header(blob)

    def test_security_critical_envelope_enums_are_closed(self) -> None:
        fields = {
            "schema_version": "9.9",
            "protocol_version": "99.99",
            "cipher_suite": "UNKNOWN-CIPHER",
            "compression": "UNKNOWN-COMPRESSION",
            "key_block_format": "UNKNOWN-KEY-FORMAT",
        }
        for field, value in fields.items():
            with self.subTest(field=field):
                with self.assertRaises(AgentPackageEnvelopeError):
                    EnvelopeHeader.from_mapping(_envelope_dict(**{field: value}))

    def test_nonce_requires_canonical_ascii_base64(self) -> None:
        for nonce in ("\u00e9", "\u4e2d", "abc", "A===", "AA=A", "AAAA===="):
            with self.subTest(nonce=nonce):
                with self.assertRaises(AgentPackageEnvelopeError):
                    EnvelopeHeader.from_mapping(_envelope_dict(nonce=nonce))

    def test_nonzero_payload_rejects_empty_nonce(self) -> None:
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(_envelope_dict(nonce="", payload_length=1))

    def test_time_comparison_uses_instants_not_text_order(self) -> None:
        with self.assertRaises(AgentPackageEnvelopeError):
            EnvelopeHeader.from_mapping(_envelope_dict(
                created_at="2026-01-01T10:00:00+02:00",
                expires_at="2026-01-01T07:30:00Z",
            ))
        valid = EnvelopeHeader.from_mapping(_envelope_dict(
            created_at="2026-01-01T10:00:00+02:00",
            expires_at="2026-01-01T09:00:00Z",
        ))
        self.assertEqual(valid.expires_at, "2026-01-01T09:00:00Z")

    def test_timestamp_text_format_is_single_canonical_form(self) -> None:
        invalid_created = (
            "2026-01-01 10:00:00Z",
            "2026-01-01T10:00:00+0000",
            "2026-01-01T10:00:00+00:00:00",
            "2026-01-01T10:00:00.1234567Z",
        )
        for created_at in invalid_created:
            with self.subTest(created_at=created_at):
                with self.assertRaises(AgentPackageEnvelopeError):
                    EnvelopeHeader.from_mapping(_envelope_dict(created_at=created_at))

    def test_header_length_is_rejected_before_envelope_copy(self) -> None:
        blob = encode_fixed_header(header_length=ENVELOPE_MAX_BYTES + 1)
        with self.assertRaises(AgentPackageLayoutError):
            parse_package_header(blob)

    def test_header_flags_and_lengths_must_agree(self) -> None:
        env = build_envelope_template(
            sender_cert_id="CERT-S", recipient_cert_id="CERT-R",
            project_id="PRJ001", package_type="TASK_ASSIGNMENT",
            sequence_no=1, payload_length=0, compression="NONE",
        )
        envelope_bytes = encode_envelope(env)
        invalid = (
            encode_fixed_header(header_length=len(envelope_bytes), key_block_length=1) + envelope_bytes + b"K",
            encode_fixed_header(header_length=len(envelope_bytes), flags=AgentPackageFlags.KEY_BLOCK_PRESENT) + envelope_bytes,
            encode_fixed_header(header_length=len(envelope_bytes), payload_length=1) + envelope_bytes + b"P",
            encode_fixed_header(header_length=len(envelope_bytes), flags=AgentPackageFlags.PAYLOAD_PRESENT) + envelope_bytes,
            encode_fixed_header(header_length=len(envelope_bytes), flags=AgentPackageFlags.EXTENSION_PRESENT) + envelope_bytes,
        )
        for blob in invalid:
            with self.assertRaises((AgentPackageLayoutError, AgentPackageEnvelopeError)):
                parse_package_header(blob)

    def test_package_rejects_undeclared_trailing_bytes(self) -> None:
        env = build_envelope_template(
            sender_cert_id="CERT-S", recipient_cert_id="CERT-R",
            project_id="PRJ001", package_type="TASK_ASSIGNMENT",
            sequence_no=1, payload_length=0, compression="NONE",
        )
        envelope_bytes = encode_envelope(env)
        blob = encode_fixed_header(header_length=len(envelope_bytes)) + envelope_bytes + b"JUNK"
        with self.assertRaises(AgentPackageLayoutError):
            parse_package_header(blob)

    def test_fixed_header_integer_fields_reject_bool(self) -> None:
        for field in ("header_length", "key_block_length", "payload_length", "major", "minor"):
            kwargs = {"header_length": 0, field: True}
            with self.subTest(field=field):
                with self.assertRaises(AgentPackageLayoutError):
                    encode_fixed_header(**kwargs)


if __name__ == "__main__":
    unittest.main()
