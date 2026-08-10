"""REVIEW2-3: `.agent` signature carrier closure tests.

Contract (docs/architecture/agent-signature-carrier.md):

* the deliverable path embeds ``sender.sig`` inside the
  authenticated-encrypted payload, so the wire bytes are
  self-contained: parse + open recover and verify the signature
  with no external/detached signature object;
* the P1 unsigned surface is a fail-closed pre-signature carrier
  (placeholder signature; verification always raises);
* envelope is AEAD-bound (tampering fails open), ciphertext
  tampering fails, truncated/trailing/cross-version wires are
  rejected.

Uses a deterministic fake crypto provider so the tests run in the
unit stage without GmSSL helpers; the real-protocol e2e proof lives
in tests/e2e/test_return_chain.py.
"""

from __future__ import annotations

import hashlib
import unittest
from types import SimpleNamespace

from src.coevo.crypto import SealedPayload
from src.coevo.protocol import (
    AgentPackageError,
    build_envelope_template,
    build_encrypted_package,
    build_unsigned_package,
    open_encrypted_package,
    parse_package_bytes,
)
from src.coevo.protocol.sm2_sign import (
    AgentPackageCryptoVerifyError,
    verify_signature,
)

SIGNED_AT = "2026-08-10T00:00:00Z"


class _FakeCrypto:
    """Deterministic stand-in implementing the CryptoProvider surface."""

    def sm3(self, data: bytes) -> bytes:
        return hashlib.sha256(data).digest()

    def sign(self, handle: object, data: bytes) -> bytes:
        return b"sig:" + data

    def verify(self, handle: object, data: bytes, signature: bytes) -> bool:
        return signature == b"sig:" + data

    def seal(
        self,
        handle: object,
        plaintext: bytes,
        *,
        associated_data: bytes,
        nonce: bytes | None = None,
    ) -> SealedPayload:
        tag = hashlib.sha256(plaintext + associated_data).digest()[:16]
        return SealedPayload(
            wrapped_key=b"wrapped",
            nonce=nonce or b"n" * 12,
            ciphertext=plaintext,
            tag=tag,
        )

    def open(self, handle: object, sealed: SealedPayload, *, associated_data: bytes) -> bytes:
        expected = hashlib.sha256(sealed.ciphertext + associated_data).digest()[:16]
        if sealed.tag != expected:
            raise AgentPackageError("payload authentication tag mismatch")
        return sealed.ciphertext


def _handles():
    sender = SimpleNamespace(certificate_id="CERT-SENDER-001")
    recipient = SimpleNamespace(certificate_id="CERT-RECIPIENT-021")
    return sender, recipient


def _manifest() -> dict[str, object]:
    return {
        "protocol_version": "1.0",
        "schema_version": "1.0",
        "package_id": "pkg-review2-3",
        "package_type": "TASK_ASSIGNMENT",
        "project_id": "PRJ001",
        "task_ids": ["TASK-001"],
        "sender": {"user_id": "USR001", "cert_id": "CERT-SENDER-001"},
        "recipient": {"user_id": "USR021", "cert_id": "CERT-RECIPIENT-021"},
        "created_at": SIGNED_AT,
        "base_revision": "PRJ001-R0001",
        "classification": "INTERNAL",
    }


def _build():
    sender, recipient = _handles()
    envelope = build_envelope_template(
        sender_cert_id="CERT-SENDER-001",
        recipient_cert_id="CERT-RECIPIENT-021",
        project_id="PRJ001",
        package_type="TASK_ASSIGNMENT",
        sequence_no=1,
        payload_length=0,
        created_at=SIGNED_AT,
        expires_at="2027-08-10T00:00:00Z",
    )
    package = build_encrypted_package(
        envelope=envelope,
        manifest=_manifest(),
        content=b"payload-bytes",
        provider=_FakeCrypto(),
        sender_handle=sender,
        recipient_handle=recipient,
        signed_at=SIGNED_AT,
    )
    return package, sender, recipient


class SignatureCarrierTests(unittest.TestCase):
    def test_deliverable_path_is_self_contained_and_verifies(self) -> None:
        package, sender, recipient = _build()
        data = package.to_bytes()
        self.assertEqual(len(data), package.expected_total_length())
        parsed = parse_package_bytes(data)
        opened = open_encrypted_package(
            parsed,
            provider=_FakeCrypto(),
            recipient_handle=recipient,
            sender_handle=sender,
        )
        self.assertEqual(opened.content, b"payload-bytes")
        self.assertEqual(opened.manifest["package_id"], "pkg-review2-3")
        self.assertEqual(opened.signature.signer_cert_id, "CERT-SENDER-001")
        self.assertNotEqual(opened.signature.signature, "")
        self.assertEqual(opened.signature.signed_object, "manifest.json")

    def test_ciphertext_tamper_fails_open(self) -> None:
        package, sender, recipient = _build()
        data = package.to_bytes()
        parsed = parse_package_bytes(data)
        ciphertext_start = (
            36
            + parsed.fixed_header.header_length
            + parsed.fixed_header.key_block_length
            + len(parsed.payload_block.header)
            + len(parsed.payload_block.nonce)
        )
        flipped = bytearray(data)
        flipped[ciphertext_start] ^= 0xFF
        tampered = parse_package_bytes(bytes(flipped))
        with self.assertRaises(AgentPackageError):
            open_encrypted_package(
                tampered,
                provider=_FakeCrypto(),
                recipient_handle=recipient,
                sender_handle=sender,
            )

    def test_envelope_is_aead_bound(self) -> None:
        package, sender, recipient = _build()
        parsed = parse_package_bytes(package.to_bytes())
        import dataclasses

        forged = dataclasses.replace(parsed.envelope, package_id="forged-package")
        forged_package = dataclasses.replace(parsed, envelope=forged)
        with self.assertRaises(AgentPackageError):
            open_encrypted_package(
                forged_package,
                provider=_FakeCrypto(),
                recipient_handle=recipient,
                sender_handle=sender,
            )

    def test_manifest_signature_mismatch_fails_closed(self) -> None:
        package, sender, _ = _build()
        parsed = parse_package_bytes(package.to_bytes())
        tampered_manifest = dict(_manifest())
        tampered_manifest["task_ids"] = ["TASK-999"]
        with self.assertRaises(AgentPackageCryptoVerifyError):
            verify_signature(
                parsed.signature,
                manifest=tampered_manifest,
                expected_signer_cert_id="CERT-SENDER-001",
                provider=_FakeCrypto(),
                signer_handle=sender,
            )

    def test_unsigned_carrier_fails_closed(self) -> None:
        sender, recipient = _handles()
        envelope = build_envelope_template(
            sender_cert_id="CERT-SENDER-001",
            recipient_cert_id="CERT-RECIPIENT-021",
            project_id="PRJ001",
            package_type="TASK_ASSIGNMENT",
            sequence_no=1,
            payload_length=0,
            created_at=SIGNED_AT,
            expires_at="2027-08-10T00:00:00Z",
        )
        from src.coevo.protocol.sm2_keywrap import build_key_transport_block
        from src.coevo.protocol.agent_payload import PayloadBlock

        carrier = build_unsigned_package(
            envelope=envelope,
            key_block=build_key_transport_block(
                recipient_cert_id="CERT-RECIPIENT-021",
                wrapped_key_b64="d3JhcHBlZA==",
                ephemeral_public_key_b64="",
            ),
            payload_block=PayloadBlock(header=b"", nonce=b"", ciphertext=b"", tag=b""),
        )
        self.assertEqual(carrier.signature.signature, "")
        parsed = parse_package_bytes(carrier.to_bytes())
        with self.assertRaises(AgentPackageCryptoVerifyError):
            verify_signature(
                parsed.signature,
                manifest=_manifest(),
                expected_signer_cert_id="CERT-SENDER-001",
                provider=_FakeCrypto(),
                signer_handle=sender,
            )

    def test_truncation_trailing_and_cross_version_rejected(self) -> None:
        package, _, _ = _build()
        data = package.to_bytes()
        with self.assertRaises(AgentPackageError):
            parse_package_bytes(data[:-1])
        with self.assertRaises(AgentPackageError):
            parse_package_bytes(data + b"x")
        parsed = parse_package_bytes(data)
        from src.coevo.protocol.agent_package import encode_fixed_header

        cross_version = (
            encode_fixed_header(
                major=2,
                minor=parsed.fixed_header.minor,
                header_length=parsed.fixed_header.header_length,
                key_block_length=parsed.fixed_header.key_block_length,
                payload_length=parsed.fixed_header.payload_length,
                flags=parsed.fixed_header.flags,
            )
            + data[36:]
        )
        with self.assertRaises(AgentPackageError):
            parse_package_bytes(cross_version)


if __name__ == "__main__":
    unittest.main()
