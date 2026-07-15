from __future__ import annotations

import copy
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from coevo.identity.certificates import CertificateError, inspect_certificate
from coevo.identity.validation import CertificateStatusError, SensitiveInputError, ValidationError, assert_certificate_usable, validate_bundle
from support_identity import CERTIFICATE_DER, identity_payload


class IdentityValidationTests(unittest.TestCase):
    def test_real_der_certificate_metadata_and_spki_are_derived(self) -> None:
        inspected = inspect_certificate(CERTIFICATE_DER)
        bundle = validate_bundle(identity_payload())
        self.assertEqual(bundle.certificate.fingerprint_sha256, inspected.fingerprint_sha256)
        self.assertEqual(bundle.certificate.public_key_spki_der, inspected.public_key_spki_der)
        self.assertEqual(bundle.certificate.serial_number, inspected.serial_number)
        self.assertEqual(bundle.payload_digest, validate_bundle(copy.deepcopy(identity_payload())).payload_digest)

    def test_random_truncated_trailing_and_private_der_are_rejected(self) -> None:
        private_pkcs8 = bytes.fromhex("3016020100300d06092a864886f70d010101050004023000")
        for candidate in (b"certificate-der", CERTIFICATE_DER[:80], CERTIFICATE_DER + b"tail", private_pkcs8):
            value = identity_payload()
            value["certificate"]["certificate_der"] = candidate
            with self.subTest(length=len(candidate)), self.assertRaises(ValidationError):
                validate_bundle(value)

    def test_helper_unavailability_fails_closed(self) -> None:
        with patch("coevo.identity.certificates.HELPER", ROOT / "missing-helper.ps1"):
            with self.assertRaises(CertificateError):
                inspect_certificate(CERTIFICATE_DER)

    def test_private_key_fields_unknown_fields_and_controls_are_rejected(self) -> None:
        value = identity_payload()
        value["certificate"]["private_key"] = "-----BEGIN PRIVATE KEY-----"
        with self.assertRaises(SensitiveInputError):
            validate_bundle(value)
        value = identity_payload()
        value["certificate"]["public_key_spki_der"] = b"caller-claimed-key"
        with self.assertRaises(ValidationError):
            validate_bundle(value)
        value = identity_payload()
        value["organization"]["name"] = "line1\r\nline2"
        with self.assertRaises(ValidationError):
            validate_bundle(value)

    def test_cyclic_deep_and_oversized_inputs_fail_closed(self) -> None:
        cyclic: dict = {}
        cyclic["child"] = cyclic
        with self.assertRaises(ValidationError):
            validate_bundle(cyclic)
        nested: object = "leaf"
        for _ in range(34):
            nested = [nested]
        with self.assertRaises(ValidationError):
            validate_bundle(nested)
        with self.assertRaises(ValidationError):
            validate_bundle({"data": b"x" * (2 * 1024 * 1024 + 1)})

    def test_cross_references_roles_and_status_check_are_strict(self) -> None:
        value = identity_payload()
        value["client"]["assigned_user_id"] = "user-2"
        with self.assertRaises(ValidationError):
            validate_bundle(value)
        value = identity_payload()
        value["roles"][0]["role_code"] = "administrator"
        with self.assertRaises(ValidationError):
            validate_bundle(value)
        revoked = validate_bundle(identity_payload(revoked=True)).certificate
        with self.assertRaisesRegex(CertificateStatusError, "revoked"):
            assert_certificate_usable(revoked, datetime.now(UTC))
        active = validate_bundle(identity_payload()).certificate
        with self.assertRaisesRegex(CertificateStatusError, "not yet valid"):
            assert_certificate_usable(active, datetime(2020, 1, 1, tzinfo=UTC))
        with self.assertRaisesRegex(CertificateStatusError, "expired"):
            assert_certificate_usable(active, datetime(2035, 1, 1, tzinfo=UTC))


if __name__ == "__main__":
    unittest.main()
