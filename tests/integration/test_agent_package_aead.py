"""Integration tests for US-5-AC-2 wire layers.

Coverage matrix (each TestCase class locks one § layer):

  § 7.4  ``TestPayloadBlock``         - SM4-GCM AEAD wire format + fail-closed.
  § 7.3  ``TestKeyTransportBlock``    - SM2 key-transport wire format + fail-closed.
  § 9/12 ``TestSignatureRecord``      - canonical manifest bytes + SM3 digest + fail-closed.
  § 17   ``TestReplayDetector``       - duplicate / replay / revoked checks.
  § 7+13 ``TestPackageBuilder``       - end-to-end wire round-trip.

All cryptographic operations are FAIL-CLOSED in P1; tests assert
that they raise :class:`*AgentPackageCryptoUnavailableError`
without leaking any key material.
"""
from __future__ import annotations

import base64
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.protocol import (
    AgentPackageCryptoUnavailableError,
    AgentPackageCryptoVerifyError,
    AgentPackageError,
    AgentPackageFlags,
    AgentPackageKeywrapCryptoUnavailableError,
    AgentPackagePayloadCryptoUnavailableError,
    AgentPackageSignCryptoUnavailableError,
    BuiltPackage,
    KDF_ITERATIONS_DEFAULT,
    KDF_NAME,
    KEY_BLOCK_FORMAT,
    PAYLOAD_HEADER_MAGIC,
    PAYLOAD_HEADER_SIZE,
    PAYLOAD_NONCE_SIZE,
    PAYLOAD_TAG_SIZE,
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    PayloadBlock,
    ProcessedPackage,
    ReplayDecision,
    ReplayOutcome,
    SESSION_KEY_SIZE,
    SIGNATURE_ALGORITHM,
    SIGNED_OBJECT_NAME,
    SignatureRecord,
    KeyTransportBlock,
    assemble_payload_block,
    build_envelope_template,
    build_key_transport_block,
    build_signature_record,
    build_unsigned_package,
    canonical_manifest_bytes,
    check_reference_target,
    check_replay,
    compute_sm3_digest,
    decode_envelope,
    decode_key_transport_bytes,
    decode_payload_header,
    decode_signature_record,
    encrypt_payload,
    encode_key_transport_bytes,
    generate_payload_nonce,
    generate_session_key,
    parse_package_bytes,
    sign_manifest,
    unwrap_session_key,
    verify_signature,
    wrap_session_key,
)


# ----------------------- § 7.4 PayloadBlock -----------------------


class TestPayloadBlock(unittest.TestCase):
    def test_encode_payload_header_is_8_bytes(self):
        from src.coevo.protocol.agent_payload import encode_payload_header
        h = encode_payload_header()
        self.assertEqual(PAYLOAD_HEADER_SIZE, len(h))
        self.assertEqual(b"SM4GCM", h[:6])

    def test_decode_payload_header_rejects_unknown_magic(self):
        bad = b"XXXXXX" + b"\x01" + b"\x00"
        from src.coevo.protocol.agent_payload import decode_payload_header as dph
        from src.coevo.protocol.agent_payload import AgentPackageCryptoDecryptError
        with self.assertRaises(AgentPackageCryptoDecryptError):
            dph(bad)

    def test_decode_payload_header_rejects_non_zero_reserved(self):
        bad = PAYLOAD_HEADER_MAGIC + b"\x01" + b"\x42"
        from src.coevo.protocol.agent_payload import decode_payload_header as dph
        from src.coevo.protocol.agent_payload import AgentPackageCryptoDecryptError
        with self.assertRaises(AgentPackageCryptoDecryptError):
            dph(bad)

    def test_generate_payload_nonce_length(self):
        n = generate_payload_nonce()
        self.assertEqual(PAYLOAD_NONCE_SIZE, len(n))

    def test_generate_session_key_length(self):
        k = generate_session_key()
        self.assertEqual(SESSION_KEY_SIZE, len(k))

    def test_assemble_payload_block(self):
        block = assemble_payload_block(b"\x42" * 32)
        self.assertEqual(PAYLOAD_HEADER_SIZE, len(block.header))
        self.assertEqual(PAYLOAD_NONCE_SIZE, len(block.nonce))
        self.assertEqual(32, len(block.ciphertext))
        self.assertEqual(PAYLOAD_TAG_SIZE, len(block.tag))

    def test_encrypt_payload_is_fail_closed(self):
        with self.assertRaises(AgentPackagePayloadCryptoUnavailableError):
            encrypt_payload(b"plaintext", associated_data=b"")

    def test_decrypt_payload_is_fail_closed(self):
        from src.coevo.protocol import decrypt_payload
        block = assemble_payload_block(b"x" * 16)
        with self.assertRaises(AgentPackagePayloadCryptoUnavailableError):
            decrypt_payload(block, associated_data=b"")


# ----------------------- § 7.3 KeyTransportBlock -----------------------


class TestKeyTransportBlock(unittest.TestCase):
    def test_build_block_has_required_fields(self):
        b = build_key_transport_block(
            recipient_cert_id="CERT-RECIPIENT-021",
            ephemeral_public_key_b64="AAA=",
            wrapped_key_b64="BBB=",
        )
        m = b.to_mapping()
        self.assertEqual(KEY_BLOCK_FORMAT, m["format"])
        self.assertEqual("CERT-RECIPIENT-021", m["recipient_cert_id"])
        self.assertEqual(KDF_NAME, m["kdf_params"]["kdf"])
        self.assertEqual(KDF_ITERATIONS_DEFAULT, m["kdf_params"]["iterations"])

    def test_encode_decode_round_trip(self):
        b = build_key_transport_block(
            recipient_cert_id="CERT-X",
            ephemeral_public_key_b64="abc",
            wrapped_key_b64="def",
        )
        encoded = encode_key_transport_bytes(b)
        decoded = decode_key_transport_bytes(encoded)
        self.assertEqual(b.format, decoded.format)
        self.assertEqual(b.recipient_cert_id, decoded.recipient_cert_id)
        self.assertEqual(b.ephemeral_public_key, decoded.ephemeral_public_key)
        self.assertEqual(b.wrapped_key, decoded.wrapped_key)

    def test_decode_rejects_unknown_format(self):
        text = json.dumps({
            "format": "UNKNOWN",
            "recipient_cert_id": "x",
            "ephemeral_public_key": "",
            "wrapped_key": "",
            "kdf_params": {"kdf": KDF_NAME, "salt": "", "iterations": 1},
            "wrapped_at": "2026-01-01T00:00:00Z",
        }, separators=(",", ":"))
        with self.assertRaises(AgentPackageKeywrapCryptoUnavailableError):
            decode_key_transport_bytes(text.encode("utf-8"))

    def test_decode_rejects_bom(self):
        text = "\ufeff{}".format(json.dumps({
            "format": KEY_BLOCK_FORMAT,
            "recipient_cert_id": "x",
            "ephemeral_public_key": "",
            "wrapped_key": "",
            "kdf_params": {"kdf": KDF_NAME, "salt": "", "iterations": 1},
            "wrapped_at": "2026-01-01T00:00:00Z",
        }, separators=(",", ":")))
        with self.assertRaises(AgentPackageKeywrapCryptoUnavailableError):
            decode_key_transport_bytes(text.encode("utf-8"))

    def test_wrap_session_key_is_fail_closed(self):
        with self.assertRaises(AgentPackageKeywrapCryptoUnavailableError):
            wrap_session_key(generate_session_key(), recipient_cert_id="CERT-X")

    def test_unwrap_session_key_is_fail_closed(self):
        b = build_key_transport_block(recipient_cert_id="CERT-X")
        with self.assertRaises(AgentPackageKeywrapCryptoUnavailableError):
            unwrap_session_key(b, recipient_cert_id="CERT-X")

    def test_unwrap_session_key_rejects_recipient_mismatch(self):
        b = build_key_transport_block(recipient_cert_id="CERT-A")
        with self.assertRaises(AgentPackageKeywrapCryptoUnavailableError):
            unwrap_session_key(b, recipient_cert_id="CERT-B")


# ----------------------- § 9 / § 12 SignatureRecord -----------------------


class TestSignatureRecord(unittest.TestCase):
    def test_canonical_manifest_bytes_sorted_keys(self):
        a = canonical_manifest_bytes({"b": 2, "a": 1})
        b = canonical_manifest_bytes({"a": 1, "b": 2})
        self.assertEqual(a, b)
        self.assertEqual(b'{"a":1,"b":2}', a)

    def test_canonical_manifest_bytes_no_trailing_whitespace(self):
        b = canonical_manifest_bytes({"a": 1})
        self.assertFalse(b.endswith(b" "))
        self.assertFalse(b.endswith(b"\n"))
        self.assertFalse(b.endswith(b"\r"))

    def test_canonical_manifest_bytes_no_bom(self):
        b = canonical_manifest_bytes({"a": 1})
        self.assertFalse(b.startswith(b"\xef\xbb\xbf"))

    def test_compute_sm3_digest_is_64_lowercase_hex(self):
        d = compute_sm3_digest(b"hello")
        self.assertEqual(64, len(d))
        self.assertTrue(all(c in "0123456789abcdef" for c in d))

    def test_compute_sm3_digest_deterministic(self):
        self.assertEqual(compute_sm3_digest(b"x"), compute_sm3_digest(b"x"))

    def test_build_signature_record_uses_digest(self):
        record = build_signature_record(
            {"a": 1}, signer_cert_id="CERT-X",
            signed_at="2026-07-25T00:00:00Z",
        )
        self.assertEqual(SIGNATURE_ALGORITHM, record.algorithm)
        self.assertEqual(SIGNED_OBJECT_NAME, record.signed_object)
        self.assertEqual("CERT-X", record.signer_cert_id)
        self.assertEqual("", record.signature)  # P1: empty
        self.assertEqual(64, len(record.manifest_sm3))

    def test_decode_signature_record_strict_field_set(self):
        record = build_signature_record(
            {"a": 1}, signer_cert_id="CERT-X",
            signed_at="2026-07-25T00:00:00Z",
        )
        decoded = decode_signature_record(record.to_mapping())
        self.assertEqual(record, decoded)
        with self.assertRaises(AgentPackageError):
            decode_signature_record({**record.to_mapping(), "extra": "field"})

    def test_sign_manifest_is_fail_closed(self):
        with self.assertRaises(AgentPackageSignCryptoUnavailableError):
            sign_manifest({"a": 1}, signer_cert_id="CERT-X")

    def test_verify_signature_rejects_empty_signature(self):
        record = build_signature_record(
            {"a": 1}, signer_cert_id="CERT-X",
            signed_at="2026-07-25T00:00:00Z",
        )
        with self.assertRaises(AgentPackageCryptoVerifyError):
            verify_signature(record, manifest={"a": 1})

    def test_verify_signature_rejects_digest_mismatch(self):
        record = build_signature_record(
            {"a": 1}, signer_cert_id="CERT-X",
            signed_at="2026-07-25T00:00:00Z",
        )
        bad = SignatureRecord(
            algorithm=record.algorithm,
            signer_cert_id=record.signer_cert_id,
            signed_object=record.signed_object,
            manifest_sm3=record.manifest_sm3,
            signature="MEUCIQDummy",
            signed_at=record.signed_at,
        )
        with self.assertRaises(AgentPackageCryptoVerifyError):
            verify_signature(bad, manifest={"a": 1})


# ----------------------- § 17 ReplayDetector -----------------------


class TestReplayDetector(unittest.TestCase):
    def test_accept_first_package(self):
        cand = ProcessedPackage(
            package_id="p.1", package_digest="d.1",
            sender_cert_id="S", recipient_cert_id="R",
            project_id="PRJ", sequence_no=1,
        )
        d = check_replay(candidate=cand)
        self.assertEqual(ReplayOutcome.ACCEPT, d.outcome)
        self.assertIsNone(d.previous_sequence_no)

    def test_duplicate_package_id_rejected(self):
        cand = ProcessedPackage(
            package_id="p.1", package_digest="d.1",
            sender_cert_id="S", recipient_cert_id="R",
            project_id="PRJ", sequence_no=1,
        )
        d = check_replay(candidate=cand, registry=[cand])
        self.assertEqual(ReplayOutcome.DUPLICATE_PACKAGE_ID, d.outcome)

    def test_duplicate_digest_rejected(self):
        cand = ProcessedPackage(
            package_id="p.2", package_digest="d.1",
            sender_cert_id="S", recipient_cert_id="R",
            project_id="PRJ", sequence_no=2,
        )
        prior = ProcessedPackage(
            package_id="p.1", package_digest="d.1",
            sender_cert_id="S", recipient_cert_id="R",
            project_id="PRJ", sequence_no=1,
        )
        d = check_replay(candidate=cand, registry=[prior])
        self.assertEqual(ReplayOutcome.DUPLICATE_DIGEST, d.outcome)

    def test_replay_sequence_rejected(self):
        prior = ProcessedPackage(
            package_id="p.1", package_digest="d.1",
            sender_cert_id="S", recipient_cert_id="R",
            project_id="PRJ", sequence_no=10,
        )
        cand = ProcessedPackage(
            package_id="p.2", package_digest="d.2",
            sender_cert_id="S", recipient_cert_id="R",
            project_id="PRJ", sequence_no=5,
        )
        d = check_replay(candidate=cand, registry=[prior])
        self.assertEqual(ReplayOutcome.REPLAY_SEQUENCE, d.outcome)

    def test_revoked_package_id_rejected(self):
        cand = ProcessedPackage(
            package_id="p.1", package_digest="d.1",
            sender_cert_id="S", recipient_cert_id="R",
            project_id="PRJ", sequence_no=1,
        )
        d = check_replay(candidate=cand, revoked_package_ids=["p.1"])
        self.assertEqual(ReplayOutcome.REVOKED_PACKAGE, d.outcome)

    def test_reference_target_requires_existing_package(self):
        d = check_reference_target(
            package_type="CORRECTION_PACKAGE",
            referenced_package_id="p.unknown",
            registry=[],
        )
        self.assertEqual(ReplayOutcome.INVALID_REFERENCE, d.outcome)

    def test_reference_target_accepts_known_package(self):
        prior = ProcessedPackage(
            package_id="p.known", package_digest="d.known",
            sender_cert_id="S", recipient_cert_id="R",
            project_id="PRJ", sequence_no=1,
        )
        d = check_reference_target(
            package_type="REVOCATION_PACKAGE",
            referenced_package_id="p.known",
            registry=[prior],
        )
        self.assertEqual(ReplayOutcome.ACCEPT, d.outcome)


# ----------------------- End-to-end builder -----------------------


class TestPackageBuilder(unittest.TestCase):
    def test_unsigned_package_round_trip(self):
        nonce_b64 = base64.b64encode(b"\x00" * 12).decode("ascii")
        env = build_envelope_template(
            sender_cert_id="CERT-SENDER-001",
            recipient_cert_id="CERT-RECIPIENT-021",
            project_id="PRJ001",
            package_type="TASK_ASSIGNMENT",
            sequence_no=1,
            payload_length=42,
            nonce_b64=nonce_b64,
        )
        key_block = build_key_transport_block(
            recipient_cert_id="CERT-RECIPIENT-021",
        )
        payload_block = assemble_payload_block(b"\x42" * 42)
        pkg = build_unsigned_package(
            envelope=env, key_block=key_block, payload_block=payload_block,
        )
        data = pkg.to_bytes()
        self.assertGreater(len(data), 36)
        self.assertEqual(pkg.expected_total_length(), len(data))
        rebuilt = parse_package_bytes(data)
        self.assertEqual(pkg.fixed_header.major, rebuilt.fixed_header.major)
        self.assertEqual(pkg.fixed_header.minor, rebuilt.fixed_header.minor)
        self.assertEqual(env.package_id, rebuilt.envelope.package_id)
        self.assertEqual(key_block.format, rebuilt.key_block.format)
        self.assertEqual(len(payload_block.ciphertext), len(rebuilt.payload_block.ciphertext))

    def test_unsigned_package_rejects_trailing_bytes(self):
        env = build_envelope_template(
            sender_cert_id="S",
            recipient_cert_id="R",
            project_id="PRJ",
            package_type="TASK_ASSIGNMENT",
            sequence_no=1,
            payload_length=0,
        )
        key_block = build_key_transport_block(recipient_cert_id="R")
        payload_block = assemble_payload_block(b"")
        pkg = build_unsigned_package(
            envelope=env, key_block=key_block, payload_block=payload_block,
        )
        data = pkg.to_bytes() + b"\x00\x00"
        with self.assertRaises(AgentPackageError):
            parse_package_bytes(data)

    def test_payload_block_header_is_valid(self):
        nonce_b64 = base64.b64encode(b"\x00" * 12).decode("ascii")
        env = build_envelope_template(
            sender_cert_id="S",
            recipient_cert_id="R",
            project_id="PRJ",
            package_type="TASK_ASSIGNMENT",
            sequence_no=1,
            payload_length=16,
            nonce_b64=nonce_b64,
        )
        key_block = build_key_transport_block(recipient_cert_id="R")
        payload_block = assemble_payload_block(b"\x00" * 16)
        pkg = build_unsigned_package(
            envelope=env, key_block=key_block, payload_block=payload_block,
        )
        data = pkg.to_bytes()
        rebuilt = parse_package_bytes(data)
        decode_payload_header(rebuilt.payload_block.header)


if __name__ == "__main__":
    unittest.main()