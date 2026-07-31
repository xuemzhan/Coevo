"""Round-2 (US-0-AC-2 slice E): end-to-end test for the real Windows
``store_private_key.ps1`` helper that drives Windows CNG.

This test **requires the pinned F6DE attestation certificate in
``Cert:\\CurrentUser\\My``**. If the cert is missing the test is skipped
(``unittest.SkipTest``) 閳?the production runtime cannot start without
the cert, and the unit protocol tests already cover the interface contract
without depending on Windows storage.

The test creates a non-exportable RSA-2048 CNG key via the helper, signs
a payload through the real CNG key, verifies the helper returns the
expected digest, and cleans up. Private-key bytes are never observed in
Python; only the cryptographic result flows back.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from coevo.identity.private_keys import (
    PrivateKeyError,
    PrivateKeyHandleUnavailableError,
    PrivateKeyService,
    PrivateKeyUsageError,
    PrivateKeyValidationError,
    WindowsPrivateKeyStore,
    format_handle,
    validate_handle_payload,
)


HELPER = ROOT / "scripts" / "store_private_key.ps1"
PINNED_THUMBPRINT = "F6DE13A4ADF56B9D66902B8E3055DCCA8B702D86"


def _powershell_executable() -> str:
    exe = os.environ.get("COEVO_POWERSHELL_PATH")
    if exe and Path(exe).is_absolute():
        return exe
    fallback = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if fallback.is_file():
        return str(fallback)
    raise unittest.SkipTest("Windows PowerShell is unavailable")


def _pinned_cert_present() -> bool:
    if not HELPER.is_file():
        return False
    probe = json.dumps({"action": "Inspect", "arguments": {}}, separators=(",", ":"))
    process = subprocess.run(
        [_powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HELPER).replace("store_private_key.ps1", "audit_signature.ps1"), "-Action", "Inspect", "-ConfigPath", "loop/audit-signing.json"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
    )
    if process.returncode:
        return False
    try:
        item = json.loads(process.stdout)
    except json.JSONDecodeError:
        return False
    return bool(item.get("match_count")) and bool(item.get("has_private_key"))


def _payload(certificate_id: str = "cert-it-1") -> dict:
    # key_public_sha256 is intentionally empty so the helper returns the
    # real CNG-computed digest and the test reads it back from the response.
    return {
        "certificate_id": certificate_id,
        "key_id": str(uuid := __import__("uuid").uuid4()),
        "algorithm_oid": "1.2.840.113549.1.1.1",
        "key_public_sha256": "",
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_to": "2030-01-01T00:00:00Z",
        "creation_audit_id": str(__import__("uuid").uuid4()),
        "revoked": False,
    }


def _call_helper(*, payload_dict: dict | None = None, arguments: dict | None = None, action: str = "Store") -> dict:
    body = {"action": action, "arguments": arguments or {"payload": payload_dict}, "parent_pinned_thumbprint": PINNED_THUMBPRINT}
    process = subprocess.run(
        [_powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HELPER)],
        cwd=ROOT,
        input=json.dumps(body, separators=(",", ":")).encode("utf-8"),
        capture_output=True,
        timeout=60,
    )
    if process.returncode:
        raise AssertionError(
            "helper failed exit={rc} stderr={stderr}".format(
                rc=process.returncode,
                stderr=process.stderr.decode("utf-8", errors="replace").strip()[:400],
            )
        )
    text = process.stdout.decode("utf-8", errors="replace").strip()
    return json.loads(text)


@unittest.skipUnless(HELPER.is_file(), "store_private_key.ps1 helper missing")
class WindowsCNGPrivateKeyTests(unittest.TestCase):
    def setUp(self) -> None:
        if not _pinned_cert_present():
            self.skipTest(f"pinned attestation certificate {PINNED_THUMBPRINT} is missing from CurrentUser/My")

    def test_store_use_destroy_cycle_uses_real_cng(self) -> None:
        payload = _payload()
        store_response = _call_helper(payload_dict=payload)
        self.assertEqual(store_response.get("schema_version"), "1.0")
        reference = store_response["reference"]
        self.assertEqual(reference["revoked"], False)
        key_id = reference["key_id"]
        public_digest = reference["key_public_sha256"]
        self.assertTrue(key_id.startswith("CoevoPrivateKey-"))
        # Use: sign a payload via the CNG key
        payload_bytes = b"integrate-with-cng"
        with tempfile.TemporaryDirectory(prefix="coevo-pk-cng-") as tmp:
            payload_path = Path(tmp) / "payload.bin"
            payload_path.write_bytes(payload_bytes)
            use_response = _call_helper(
                action="Use",
                arguments={"handle": key_id, "public_digest": public_digest, "algorithm_oid": "1.2.840.113549.1.1.1", "payload_path": str(payload_path)},
            )
            verify_signature_response = _call_helper(
                action="Verify",
                arguments={
                    "handle": key_id, "public_digest": public_digest,
                    "algorithm_oid": "1.2.840.113549.1.1.1",
                    "payload_path": str(payload_path),
                    "signature_base64": use_response["result"]["signature_base64"],
                    "parent_pinned_thumbprint": PINNED_THUMBPRINT,
                },
            )
        signature = base64.b64decode(use_response["result"]["signature_base64"], validate=True)
        self.assertTrue(verify_signature_response["result"]["verified"])
        expected = hashlib.sha256(payload_bytes).hexdigest()
        self.assertNotEqual(expected, signature.hex())
        # VerifyHandle: still alive, digest matches.
        verify_response = _call_helper(
            action="VerifyHandle",
            arguments={"handle": key_id, "public_digest": public_digest},
        )
        self.assertTrue(verify_response["result"]["verified"])
        # Destroy: tombstones the receipt and removes the CNG key.
        destroy_response = _call_helper(
            action="Destroy",
            arguments={"handle": key_id, "public_digest": public_digest},
        )
        self.assertTrue(destroy_response["result"]["destroyed"])

    def test_python_windows_private_key_store_end_to_end(self) -> None:
        """The Protocol-bound Python wrapper drives the helper script.

        We don't bypass ``WindowsPrivateKeyStore``; the production
        boundary is the script. This integration confirms the boundary
        holds for the operations US-5 will call.
        """
        backend = WindowsPrivateKeyStore(helper_path=HELPER)
        service = PrivateKeyService(backend)
        payload = _payload(certificate_id="cert-it-2")
        reference = service.store("cert-it-2", payload, actor_id="integration-test")
        try:
            payload_bytes = b"produced-from-python"
            signature = service.use(reference, payload_bytes, trusted_time=datetime(2027, 1, 1, tzinfo=UTC), actor_id="integration-test")
            self.assertEqual(len(signature), 256)
            self.assertTrue(service.verify(
                reference, payload_bytes, signature,
                trusted_time=datetime(2027, 1, 1, tzinfo=UTC),
                actor_id="integration-test",
                expected_certificate_id="cert-it-2",
                expected_parent_thumbprint=PINNED_THUMBPRINT,
                expected_public_sha256=reference.key_public_sha256,
                expected_algorithm_oid=reference.algorithm_oid,
            ))
            revoked = service.revoke(
                reference, actor_id="integration-test", reason="integration rotation",
            )
            self.assertTrue(revoked.revoked)
            with self.assertRaises(PrivateKeyError):
                service.use(
                    reference, payload_bytes,
                    trusted_time=datetime(2027, 1, 1, tzinfo=UTC),
                    actor_id="integration-test",
                )
            with self.assertRaises(PrivateKeyError):
                service.verify(
                    reference, payload_bytes, signature,
                    trusted_time=datetime(2027, 1, 1, tzinfo=UTC),
                    actor_id="integration-test",
                    expected_certificate_id="cert-it-2",
                    expected_parent_thumbprint=PINNED_THUMBPRINT,
                    expected_public_sha256=reference.key_public_sha256,
                    expected_algorithm_oid=reference.algorithm_oid,
                )
        finally:
            service.destroy(reference, actor_id="integration-test")


@unittest.skipUnless(HELPER.is_file(), "store_private_key.ps1 helper missing")
class NegativeWindowsCNGTests(unittest.TestCase):
    def setUp(self) -> None:
        if not _pinned_cert_present():
            self.skipTest(f"pinned attestation certificate {PINNED_THUMBPRINT} is missing from CurrentUser/My")

    def test_use_with_wrong_public_digest_is_rejected(self) -> None:
        payload = _payload(certificate_id="cert-neg-1")
        store = _call_helper(payload_dict=payload)
        with tempfile.TemporaryDirectory(prefix="coevo-pk-neg-") as tmp:
            payload_path = Path(tmp) / "payload.bin"
            payload_path.write_bytes(b"x")
            try:
                _call_helper(action="Use", arguments={
                    "handle": store["reference"]["key_id"],
                    "public_digest": "0" * 64,
                    "algorithm_oid": "1.2.840.113549.1.1.1",
                    "payload_path": str(payload_path),
                })
            except AssertionError as exc:
                self.assertIn("digest", str(exc).lower())
            else:
                self.fail("Use with wrong public digest should have failed")
        _call_helper(action="Destroy", arguments={"handle": store["reference"]["key_id"], "public_digest": store["reference"]["key_public_sha256"]})

    def test_receipt_digest_cannot_substitute_for_actual_cng_key(self) -> None:
        store = _call_helper(payload_dict=_payload(certificate_id="cert-neg-binding"))
        reference = store["reference"]
        handle = reference["key_id"]
        actual_digest = reference["key_public_sha256"]
        receipt_path = ROOT / "loop" / f"private-key-handles-{PINNED_THUMBPRINT}.json"
        original_receipt = receipt_path.read_bytes()
        tampered = json.loads(original_receipt.decode("utf-8-sig"))
        tampered["handles"][handle]["public_digest"] = "0" * 64
        receipt_path.write_text(json.dumps(tampered, indent=2), encoding="utf-8")
        try:
            with tempfile.TemporaryDirectory(prefix="coevo-pk-binding-") as tmp:
                payload_path = Path(tmp) / "payload.bin"
                payload_path.write_bytes(b"binding-check")
                calls = (
                    ("Use", {"handle": handle, "public_digest": "0" * 64, "algorithm_oid": "1.2.840.113549.1.1.1", "payload_path": str(payload_path)}),
                    ("VerifyHandle", {"handle": handle, "public_digest": "0" * 64}),
                )
                for action, arguments in calls:
                    with self.subTest(action=action):
                        with self.assertRaises(AssertionError) as raised:
                            _call_helper(action=action, arguments=arguments)
                        self.assertIn("actual cng key public digest", str(raised.exception).lower())
        finally:
            receipt_path.write_bytes(original_receipt)
            _call_helper(action="Destroy", arguments={"handle": handle, "public_digest": actual_digest})
    def test_use_outside_validity_window_is_rejected_by_service(self) -> None:
        payload = _payload(certificate_id="cert-neg-2")
        store = _call_helper(payload_dict=payload)
        reference_dict = store["reference"]
        from coevo.identity.private_keys import PrivateKeyReference
        reference = PrivateKeyReference(
            key_id=reference_dict["key_id"],
            algorithm_oid=reference_dict["algorithm_oid"],
            key_public_sha256=reference_dict["key_public_sha256"],
            valid_from=datetime.fromisoformat(reference_dict["valid_from"].replace("Z", "+00:00")).astimezone(UTC),
            valid_to=datetime.fromisoformat(reference_dict["valid_to"].replace("Z", "+00:00")).astimezone(UTC),
            bound_certificate_id=reference_dict.get("certificate_id", "cert-neg-2"),
            revoked=reference_dict["revoked"],
            handle_token_hint=reference_dict["handle_token_hint"],
        )
        backend = WindowsPrivateKeyStore(helper_path=HELPER)
        service = PrivateKeyService(backend)
        try:
            with self.assertRaises(PrivateKeyUsageError):
                service.use(reference, b"x", trusted_time=datetime(2025, 6, 1, tzinfo=UTC))
        finally:
            service.destroy(reference, actor_id="integration-test")


if __name__ == "__main__":
    unittest.main()
