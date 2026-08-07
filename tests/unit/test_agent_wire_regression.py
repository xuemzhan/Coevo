"""T6 (US-16-AC-1 AC-1.10): `.agent` v1.0 wire byte-level regression.

Pins the canonical serialization of the Fixed Header and Envelope Header so
any drift in the wire format is caught by hard byte-level assertions.  These
values change only when the wire format is deliberately version-bumped.
"""

from __future__ import annotations

import hashlib
import unittest

from src.coevo.protocol.agent_package import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    AgentPackageFlags,
    EnvelopeHeader,
    FIXED_HEADER_SIZE,
    encode_envelope,
    encode_fixed_header,
)

PINNED_FIXED_HEADER_HEX = (
    "4147454e54504b4700010000000007d0000000c000000000000100010000000100000000"
)
PINNED_FIXED_HEADER_DIGEST = (
    "03bdbb147ab7c1067e37c6c4c4854481335285a65d26699c91d4fb8044114687"
)
PINNED_ENVELOPE_DIGEST = (
    "c635cafe889a5b0c20bb1435277d72407449f5fb68cef1db9498eb4abcc3b846"
)


def _fixed_envelope_mapping() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "protocol_version": f"{PROTOCOL_MAJOR}.{PROTOCOL_MINOR}",
        "package_id": "11111111-2222-4333-8444-555555555555",
        "package_type": "TASK_ASSIGNMENT",
        "sender_cert_id": "CERT-SENDER-001",
        "recipient_cert_id": "CERT-RECIPIENT-021",
        "project_id": "PRJ001",
        "created_at": "2026-07-15T10:20:30Z",
        "expires_at": "2026-08-15T23:59:59Z",
        "sequence_no": 12,
        "cipher_suite": "CS-SM2-SM4-AEAD-SM3-01",
        "compression": "NONE",
        "nonce": "AAAAAAAAAAAAAAAAAAAAAA==",
        "key_block_format": "SM2-KEY-TRANSPORT-V1",
        "payload_length": 2048,
        "required_client_version": "1.0.0",
    }


class AgentWireRegressionTests(unittest.TestCase):
    def test_fixed_header_wire_unchanged(self) -> None:
        blob = encode_fixed_header(
            header_length=2000,
            key_block_length=192,
            payload_length=65537,
            flags=AgentPackageFlags.COMPRESSION_ZIP_DEFLATE,
        )
        self.assertEqual(len(blob), FIXED_HEADER_SIZE)
        self.assertEqual(blob.hex(), PINNED_FIXED_HEADER_HEX)
        self.assertEqual(hashlib.sha256(blob).hexdigest(), PINNED_FIXED_HEADER_DIGEST)

    def test_envelope_canonical_wire_unchanged(self) -> None:
        envelope = EnvelopeHeader.from_mapping(_fixed_envelope_mapping())
        blob = encode_envelope(envelope)
        self.assertEqual(hashlib.sha256(blob).hexdigest(), PINNED_ENVELOPE_DIGEST)
        self.assertFalse(blob.startswith(b"\xef\xbb\xbf"))
        self.assertTrue(all(byte < 128 for byte in blob))


if __name__ == "__main__":
    unittest.main()
