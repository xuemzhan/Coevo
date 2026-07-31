"""Security tests for the offline private-key storage interface (US-0-AC-2).

The interface MUST guarantee that plaintext private-key material never
escapes the local Windows CNG storage. Tests assert:

* :class:`PrivateKeyReference` only carries safe metadata (key handle,
  public digest, validity range, revocation flag). It MUST refuse to
  absorb raw bytes; ``__repr__`` / ``__str__`` / pickle / JSON
  serialisation MUST NOT leak private bytes; ``hash()``/equality MUST
  be stable across rotations while excluding anything an attacker could
  replay.

* :class:`PrivateKeyStore` is a ``Protocol`` so test code can swap in
  a fully in-memory fake without ever invoking PowerShell. The
  Protocol's surface is locked: ``store`` / ``use`` / ``destroy`` /
  ``verify_handle``. Private-key bytes never leave the helper process;
  the only output is a cryptographic result (signature / decrypted
  session key).

* :class:`PrivateKeyService` enforces checks AC-wise:
    - key id format and presence of ``key_public_sha256``;
    - ``valid_from`` < ``valid_to``;
    - ``trusted_time`` falls inside the validity window;
    - revocation blocks ``use``;
    - destroyed handles block ``use`` even if a caller has a stale id;
    - overwrite of an existing handle is rejected.

* :func:`coevo.identity.validation.validate_bundle` rejects any
  payload whose keys contain a ``privatekey`` token (defense-in-depth
  alongside the explicit ``PrivateKeyReference`` boundary).
"""

from __future__ import annotations

import copy
import base64
import hashlib
import hmac
import os
import json
import pickle
import sys
import unittest
import tempfile
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from coevo.identity.private_keys import (
    PrivateKeyHandleError,
    PrivateKeyHandleUnavailableError,
    PrivateKeyReference,
    PrivateKeyRevokedError,
    PrivateKeyService,
    WindowsPrivateKeyStore,
    PrivateKeyUsageError,
    PrivateKeyValidationError,
    format_handle,
    validate_handle_payload,
)
from coevo.identity.validation import SensitiveInputError, validate_bundle
from support_identity import identity_payload

PINNED_THUMBPRINT = "f6de13a4adf56b9d66902b8e3055dcca8b702d86"
CANONICAL_TRUSTED = PINNED_THUMBPRINT.lower()


def _canonical_id(key_id: str) -> str:
    """Reduce any handle form (prefixed or bare UUID) to the same 32-char hex."""
    suffix = key_id[len("CoevoPrivateKey-"):] if key_id.startswith("CoevoPrivateKey-") else key_id
    return suffix.replace("-", "").lower()


class InMemoryPrivateKeyStore:
    """Test double for :class:`PrivateKeyStore`.

    Keys are stored under a canonical 32-char hex id (UUID with
    hyphens stripped, optionally with the ``CoevoPrivateKey-`` prefix).
    """

    __test__ = False

    def __init__(self) -> None:
        self.handles: dict[str, dict] = {}
        self.usage_log: list[tuple[str, bytes, bytes]] = []
        self.fail_use_with: Exception | None = None

    def store(self, certificate_id: str, payload: dict, *, parent_pinned_thumbprint: str | None = None) -> PrivateKeyReference:
        canonical = _canonical_id(payload["key_id"])
        if canonical in self.handles:
            raise PrivateKeyHandleError("private-key handle already exists; refusing to overwrite")
        if parent_pinned_thumbprint and parent_pinned_thumbprint.lower() != CANONICAL_TRUSTED:
            raise PrivateKeyHandleError("parent attestation certificate thumbprint is not trusted")
        self.handles[canonical] = {
            "secret": hashlib.sha256(canonical.encode("utf-8")).digest(),
            "metadata": {
                "certificate_id": certificate_id,
                "algorithm_oid": payload["algorithm_oid"],
                "key_public_sha256": payload["key_public_sha256"],
                "valid_from": payload["valid_from"],
                "valid_to": payload["valid_to"],
                "creation_audit_id": payload["creation_audit_id"],
            },
            "revoked": False,
        }
        return PrivateKeyReference(
            key_id="CoevoPrivateKey-" + canonical,
            algorithm_oid=payload["algorithm_oid"],
            key_public_sha256=payload["key_public_sha256"],
            valid_from=datetime.fromisoformat(payload["valid_from"].replace("Z", "+00:00")).astimezone(UTC),
            valid_to=datetime.fromisoformat(payload["valid_to"].replace("Z", "+00:00")).astimezone(UTC),
            bound_certificate_id=certificate_id,
            revoked=False,
            handle_token_hint=canonical[:16],
        )

    def use(self, reference: PrivateKeyReference, payload: bytes) -> bytes:
        if self.fail_use_with is not None:
            failure = self.fail_use_with
            self.fail_use_with = None
            raise failure
        canonical = _canonical_id(reference.key_id)
        record = self.handles.get(canonical)
        if record is None:
            raise PrivateKeyHandleUnavailableError("private-key handle is missing from local store")
        if record["revoked"]:
            raise PrivateKeyRevokedError("private-key handle has been revoked")
        signature = hmac.new(record["secret"], payload, hashlib.sha256).digest()
        self.usage_log.append((reference.key_id, payload, signature))
        return signature

    def verify(
        self, reference: PrivateKeyReference, payload: bytes, signature: bytes,
        *, parent_pinned_thumbprint: str,
    ) -> bool:
        if parent_pinned_thumbprint.lower() != CANONICAL_TRUSTED:
            raise PrivateKeyHandleError("parent attestation certificate thumbprint is not trusted")
        canonical = _canonical_id(reference.key_id)
        record = self.handles.get(canonical)
        if record is None:
            raise PrivateKeyHandleUnavailableError("private-key handle is missing from local store")
        if record["revoked"]:
            raise PrivateKeyRevokedError("private-key handle has been revoked")
        expected = hmac.new(record["secret"], payload, hashlib.sha256).digest()
        return hmac.compare_digest(expected, signature)

    def destroy(self, reference: PrivateKeyReference) -> None:
        canonical = _canonical_id(reference.key_id)
        if canonical not in self.handles:
            raise PrivateKeyHandleUnavailableError("private-key handle has already been destroyed")
        del self.handles[canonical]

    def revoke(self, reference: PrivateKeyReference, *, reason: str) -> None:
        canonical = _canonical_id(reference.key_id)
        if canonical not in self.handles:
            raise PrivateKeyHandleUnavailableError("private-key handle is missing from local store")
        self.handles[canonical]["revoked"] = True

    def verify_handle(self, reference: PrivateKeyReference) -> None:
        canonical = _canonical_id(reference.key_id)
        record = self.handles.get(canonical)
        if record is None:
            raise PrivateKeyHandleUnavailableError("private-key handle is missing from local store")
        if record["metadata"]["key_public_sha256"] != reference.key_public_sha256:
            raise PrivateKeyValidationError("private-key reference does not match stored public digest")


def _payload(*, certificate_id: str = "cert-1", revoked: bool = False) -> dict:
    return {
        "certificate_id": certificate_id,
        "key_id": "11111111-1111-1111-1111-111111111111",
        "algorithm_oid": "1.2.840.113549.1.1.1",
        "key_public_sha256": hashlib.sha256(b"public-digest").hexdigest(),
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_to": "2030-01-01T00:00:00Z",
        "creation_audit_id": "11111111-1111-1111-1111-111111111112",
        "revoked": revoked,
    }


def _build_reference() -> PrivateKeyReference:
    payload = _payload()
    return PrivateKeyReference(
        key_id=format_handle(payload["key_id"]),
        algorithm_oid=payload["algorithm_oid"],
        key_public_sha256=payload["key_public_sha256"],
        valid_from=datetime.fromisoformat(payload["valid_from"].replace("Z", "+00:00")).astimezone(UTC),
        valid_to=datetime.fromisoformat(payload["valid_to"].replace("Z", "+00:00")).astimezone(UTC),
        bound_certificate_id=payload["certificate_id"],
        revoked=False,
        handle_token_hint=payload["key_id"].replace("-", "")[:16],
    )


class PrivateKeyReferenceSafetyTests(unittest.TestCase):
    """A reference must be safe to log, cache, pickle, and serialise."""

    def test_reference_accepts_only_safe_metadata(self) -> None:
        token = format_handle("11111111-1111-1111-1111-111111111111")
        reference = PrivateKeyReference(
            key_id=token,
            algorithm_oid="1.2.840.113549.1.1.1",
            key_public_sha256="a" * 64,
            valid_from=datetime(2026, 1, 1, tzinfo=UTC),
            valid_to=datetime(2030, 1, 1, tzinfo=UTC),
            bound_certificate_id="cert-1",
            revoked=False,
            handle_token_hint="1111111111111111",
        )
        self.assertEqual(reference.bound_certificate_id, "cert-1")
        self.assertTrue(reference.handle_token_hint.endswith("1111"))

    def test_reference_rejects_malformed_handle_and_digest(self) -> None:
        with self.assertRaises(PrivateKeyValidationError):
            PrivateKeyReference(
                key_id="coevo-wrong",
                algorithm_oid="1.2.840.113549.1.1.1",
                key_public_sha256="a" * 64,
                valid_from=datetime(2026, 1, 1, tzinfo=UTC),
                valid_to=datetime(2030, 1, 1, tzinfo=UTC),
                bound_certificate_id="cert-1",
                revoked=False,
                handle_token_hint="a" * 16,
            )
        with self.assertRaises(PrivateKeyValidationError):
            PrivateKeyReference(
                key_id=format_handle("11111111-1111-1111-1111-111111111111"),
                algorithm_oid="not-an-oid",
                key_public_sha256="a" * 64,
                valid_from=datetime(2026, 1, 1, tzinfo=UTC),
                valid_to=datetime(2030, 1, 1, tzinfo=UTC),
                bound_certificate_id="cert-1",
                revoked=False,
                handle_token_hint="a" * 16,
            )

    def test_reference_rejects_inverted_validity(self) -> None:
        with self.assertRaises(PrivateKeyValidationError):
            PrivateKeyReference(
                key_id=format_handle("11111111-1111-1111-1111-111111111111"),
                algorithm_oid="1.2.840.113549.1.1.1",
                key_public_sha256="a" * 64,
                valid_from=datetime(2030, 1, 1, tzinfo=UTC),
                valid_to=datetime(2026, 1, 1, tzinfo=UTC),
                bound_certificate_id="cert-1",
                revoked=False,
                handle_token_hint="a" * 16,
            )

    def test_repr_and_pickle_never_expose_secret_token(self) -> None:
        reference = _build_reference()
        renders = (repr(reference), str(reference),
                   pickle.dumps(reference), json.dumps(reference.__safe_dict__()))
        for render in renders:
            text = render.decode("utf-8", errors="replace") if isinstance(render, (bytes, bytearray)) else render
            self.assertNotIn("PRIVATE KEY", text.upper())
            self.assertNotIn("BEGIN ENCRYPTED", text.upper())
            self.assertNotIn("BEGIN EC PRIVATE", text.upper())
        self.assertLessEqual(len(reference.handle_token_hint), 16)

    def test_reference_is_frozen_and_hash_stable_across_rotations(self) -> None:
        reference_a = _build_reference()
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            reference_a.revoked = True  # type: ignore[misc]
        same = _build_reference()
        self.assertEqual(hash(reference_a), hash(same))
        self.assertEqual(reference_a, same)

    def test_validate_handle_payload_rejects_unknown_or_sensitive_fields(self) -> None:
        payload = _payload()
        validate_handle_payload(payload)
        for sensitive in (
            {"private_key_pkcs8": "blob"},
            {"private_key_pem": "blob"},
            {"passphrase": "x"},
            {"unknown_field": "x"},
        ):
            tampered = dict(payload); tampered.update(sensitive)
            with self.assertRaises(PrivateKeyValidationError):
                validate_handle_payload(tampered)

    def test_validate_handle_payload_rejects_private_key_blob_strings(self) -> None:
        payload = _payload()
        tampered = dict(payload); tampered["certificate_id"] = "-----BEGIN PRIVATE KEY-----"
        with self.assertRaises(PrivateKeyValidationError):
            validate_handle_payload(tampered)


class PrivateKeyServicePolicyTests(unittest.TestCase):
    """``PrivateKeyService`` enforces validity, revocation, and atomic destruction."""

    def setUp(self) -> None:
        self.backend = InMemoryPrivateKeyStore()
        self.service = PrivateKeyService(self.backend)
        self.payload = _payload()

    def test_stored_reference_round_trips_use_and_returns_signature(self) -> None:
        reference = self.service.store("cert-1", self.payload, actor_id="admin-1")
        signature = self.service.use(reference, b"payload", trusted_time=datetime(2027, 1, 1, tzinfo=UTC), actor_id="signer-1")
        self.assertEqual(len(signature), 32)
        self.assertEqual(len(self.backend.usage_log), 1)
        # Public digest seen by tests; secret bytes never appear.
        self.assertNotIn(self.backend.handles[_canonical_id(reference.key_id)]["secret"], (signature,))

    def test_verify_binds_certificate_pin_digest_algorithm_and_audits_digest_only(self) -> None:
        reference = self.service.store("cert-1", self.payload, actor_id="admin-1")
        payload = b"receipt-payload"
        signature = self.service.use(
            reference, payload, trusted_time=datetime(2027, 1, 1, tzinfo=UTC),
        )
        verified = self.service.verify(
            reference, payload, signature,
            trusted_time=datetime(2027, 1, 1, tzinfo=UTC),
            expected_certificate_id="cert-1",
            expected_parent_thumbprint=PINNED_THUMBPRINT,
            expected_public_sha256=reference.key_public_sha256,
            expected_algorithm_oid=reference.algorithm_oid,
        )
        self.assertTrue(verified)
        event = self.service.audit_trail[-1]
        encoded = json.dumps(event, sort_keys=True)
        self.assertEqual("private_key_verify", event["action"])
        self.assertIn(hashlib.sha256(signature).hexdigest(), encoded)
        self.assertNotIn(payload.decode(), encoded)
        self.assertNotIn(base64.b64encode(signature).decode(), encoded)

    def test_verify_rejects_wrong_pin_revoked_destroyed_and_bad_signature(self) -> None:
        reference = self.service.store("cert-1", self.payload)
        signature = self.service.use(
            reference, b"x", trusted_time=datetime(2027, 1, 1, tzinfo=UTC),
        )
        common = dict(
            trusted_time=datetime(2027, 1, 1, tzinfo=UTC),
            expected_certificate_id="cert-1",
            expected_public_sha256=reference.key_public_sha256,
            expected_algorithm_oid=reference.algorithm_oid,
        )
        with self.assertRaises(PrivateKeyHandleError):
            self.service.verify(
                reference, b"x", signature,
                expected_parent_thumbprint="0" * 40, **common,
            )
        self.assertFalse(self.service.verify(
            reference, b"x", b"bad",
            expected_parent_thumbprint=PINNED_THUMBPRINT, **common,
        ))
        revoked = self.service.revoke(reference, actor_id="admin", reason="test")
        with self.assertRaises(PrivateKeyUsageError):
            self.service.verify(
                revoked, b"x", signature,
                expected_parent_thumbprint=PINNED_THUMBPRINT, **common,
            )
        self.service.destroy(reference, actor_id="admin")
        with self.assertRaises(PrivateKeyHandleUnavailableError):
            self.service.verify(
                reference, b"x", signature,
                expected_parent_thumbprint=PINNED_THUMBPRINT, **common,
            )

    def test_use_outside_validity_window_is_rejected(self) -> None:
        reference = self.service.store("cert-1", self.payload)
        with self.assertRaises(PrivateKeyUsageError):
            self.service.use(reference, b"x", trusted_time=datetime(2025, 1, 1, tzinfo=UTC))
        with self.assertRaises(PrivateKeyUsageError):
            self.service.use(reference, b"x", trusted_time=datetime(2031, 1, 1, tzinfo=UTC))

    def test_use_with_naive_datetime_is_rejected(self) -> None:
        reference = self.service.store("cert-1", self.payload)
        with self.assertRaises(PrivateKeyUsageError):
            self.service.use(reference, b"x", trusted_time=datetime(2027, 1, 1))

    def test_revoked_reference_blocks_use_and_audits_rejection(self) -> None:
        reference = self.service.store("cert-1", self.payload)
        revoked = self.service.revoke(reference, actor_id="admin-1", reason="key compromise")
        self.assertTrue(revoked.revoked)
        self.assertFalse(reference.revoked, "original reference remains usable until caller adopts the revoked instance")
        with self.assertRaises(PrivateKeyUsageError):
            self.service.use(revoked, b"x", trusted_time=datetime(2027, 1, 1, tzinfo=UTC))
        with self.assertRaises(PrivateKeyUsageError):
            self.service.use(reference, b"x", trusted_time=datetime(2027, 1, 1, tzinfo=UTC))

    def test_revoke_without_reason_is_rejected(self) -> None:
        reference = self.service.store("cert-1", self.payload)
        with self.assertRaises(PrivateKeyValidationError):
            self.service.revoke(reference, actor_id="admin-1", reason="")

    def test_destroyed_handle_blocks_use_with_stale_reference(self) -> None:
        reference = self.service.store("cert-1", self.payload)
        self.service.destroy(reference, actor_id="admin-1")
        with self.assertRaises(PrivateKeyHandleUnavailableError):
            self.service.use(reference, b"x", trusted_time=datetime(2027, 1, 1, tzinfo=UTC))

    def test_overwrite_store_is_rejected(self) -> None:
        self.service.store("cert-1", self.payload)
        with self.assertRaises(PrivateKeyHandleError):
            self.service.store("cert-1", self.payload)

    def test_audit_chain_records_store_use_revoke_and_destroy(self) -> None:
        reference = self.service.store("cert-1", self.payload, actor_id="admin-1")
        self.service.use(reference, b"x", trusted_time=datetime(2027, 1, 1, tzinfo=UTC), actor_id="signer-1")
        revoked = self.service.revoke(reference, actor_id="admin-1", reason="rotation")
        self.service.destroy(revoked, actor_id="admin-1")
        actions = [event["action"] for event in self.service.audit_trail]
        self.assertEqual(actions, ["private_key_store", "private_key_use", "private_key_revoke", "private_key_destroy"])
        self.assertTrue(self.service.verify_audit_chain())
        for event in self.service.audit_trail:
            entry = json.dumps(event)
            self.assertNotIn("PRIVATE KEY", entry.upper())
            self.assertNotIn("BEGIN EC PRIVATE", entry.upper())

    def test_audit_chain_detects_event_tampering(self) -> None:
        self.service.store("cert-1", self.payload, actor_id="admin-1")
        self.service.audit_trail[0]["actor_id"] = "forged"
        self.assertFalse(self.service.verify_audit_chain())

    def test_untrusted_parent_thumbprint_is_rejected(self) -> None:
        with self.assertRaises(PrivateKeyHandleError):
            self.backend.store("cert-1", self.payload, parent_pinned_thumbprint="0000000000000000000000000000000000000000")


class WindowsPrivateKeyLaunchPolicyTests(unittest.TestCase):
    """The production CNG bridge must not execute caller-selected code."""

    def test_rejects_uncontrolled_helper_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="coevo-helper-policy-") as tmp:
            fake_helper = Path(tmp) / "fake.ps1"
            fake_helper.write_text("Write-Output '{}';", encoding="utf-8")
            with self.assertRaises(PrivateKeyHandleError):
                WindowsPrivateKeyStore(helper_path=fake_helper)

    def test_poisoned_powershell_path_is_rejected_before_execution(self) -> None:
        backend = WindowsPrivateKeyStore()
        with tempfile.TemporaryDirectory(prefix="coevo-powershell-policy-") as tmp:
            fake_exe = Path(tmp) / "powershell.exe"
            fake_exe.write_bytes(b"not the locked Windows PowerShell executable")
            with patch.dict(os.environ, {"COEVO_POWERSHELL_PATH": str(fake_exe)}):
                with patch("coevo.identity.private_keys.subprocess.run") as runner:
                    with self.assertRaises(PrivateKeyHandleError):
                        backend._run("VerifyHandle", handle="CoevoPrivateKey-" + "0" * 32, public_digest="0" * 64)
                    runner.assert_not_called()
class IdentityBundlePrivateKeyRejectionTests(unittest.TestCase):
    """Identity-bundle input MUST NOT carry private-key material (defense in depth)."""

    def test_validate_bundle_rejects_private_key_handle_field(self) -> None:
        value = identity_payload()
        value["certificate"]["private_key_handle"] = {"key_id": "x"}
        with self.assertRaises(SensitiveInputError):
            validate_bundle(copy.deepcopy(value))

    def test_validate_bundle_rejects_private_key_pkcs8_bytes(self) -> None:
        value = identity_payload()
        value["certificate"]["private_key_pkcs8"] = b"raw-bytes"
        with self.assertRaises(SensitiveInputError):
            validate_bundle(copy.deepcopy(value))


if __name__ == "__main__":
    unittest.main()
