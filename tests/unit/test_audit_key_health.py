"""AUDIT-KEY-1: pure diagnostics logic for the audit-signing key health tool."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "audit_key_health", ROOT / "scripts" / "audit_key_health.py"
)
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)


def _valid_config(*, thumbprint: str = "F6DE13A4ADF56B9D66902B8E3055DCCA8B702D86") -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "prototype": True,
        "store": "CurrentUser/My",
        "thumbprint": thumbprint,
        "public_certificate": "loop/audit-signing-public.cer",
        "public_certificate_sha256": "b" * 64,
        "signature_algorithm": "RSA-PKCS1-v1_5",
        "digest_algorithm": "SHA-256",
        "formal_replacement": "approved SM2 product required",
    }


class LoadConfigTests(unittest.TestCase):
    def test_missing_config_raises(self):
        with self.assertRaises(health.KeyHealthError):
            health.load_config(Path("C:/definitely/not/here.json"))

    def test_invalid_json_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(health.KeyHealthError):
                health.load_config(path)

    def test_non_object_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text("[1,2]", encoding="utf-8")
            with self.assertRaises(health.KeyHealthError):
                health.load_config(path)


class ValidateConfigTests(unittest.TestCase):
    def test_valid_config_has_no_problems(self):
        self.assertEqual([], health.validate_config(_valid_config()))

    def test_missing_fields_reported(self):
        problems = health.validate_config({})
        self.assertTrue(any("missing config fields" in p for p in problems))

    def test_bad_thumbprint_reported(self):
        config = _valid_config(thumbprint="not-a-thumbprint")
        self.assertTrue(any("thumbprint" in p for p in health.validate_config(config)))

    def test_bad_cert_sha_reported(self):
        config = _valid_config()
        config["public_certificate_sha256"] = "xyz"
        self.assertTrue(
            any("public_certificate_sha256" in p for p in health.validate_config(config))
        )

    def test_wrong_store_reported(self):
        config = _valid_config()
        config["store"] = "LocalMachine/My"
        self.assertTrue(any("store" in p for p in health.validate_config(config)))


class PublicCertTests(unittest.TestCase):
    def test_missing_file_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _valid_config()
            problems = health.public_cert_problems(root, config)
            self.assertTrue(any("missing" in p for p in problems))

    def test_hash_mismatch_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cert = root / "audit-signing-public.cer"
            cert.parent.mkdir(parents=True, exist_ok=True)
            cert.write_bytes(b"fake cert bytes")
            config = _valid_config()
            config["public_certificate"] = "audit-signing-public.cer"
            problems = health.public_cert_problems(root, config)
            self.assertTrue(any("hash mismatch" in p for p in problems))

    def test_matching_file_is_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cert = root / "audit-signing-public.cer"
            cert.parent.mkdir(parents=True, exist_ok=True)
            cert.write_bytes(b"fake cert bytes")
            config = _valid_config()
            config["public_certificate"] = "audit-signing-public.cer"
            config["public_certificate_sha256"] = hashlib.sha256(b"fake cert bytes").hexdigest()
            self.assertEqual([], health.public_cert_problems(root, config))

    def test_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _valid_config()
            config["public_certificate"] = "../outside.cer"
            self.assertTrue(any("escapes" in p for p in health.public_cert_problems(root, config)))


class HeadSignerTests(unittest.TestCase):
    def _repo(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "loop").mkdir(parents=True, exist_ok=True)
        return root

    def test_no_head_is_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual([], health.head_signer_problems(self._repo(tmp), _valid_config()))

    def test_matching_head_is_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            thumb = "F6DE13A4ADF56B9D66902B8E3055DCCA8B702D86"
            (root / "loop" / "audit-head.json").write_text(
                json.dumps({"signer_thumbprint": thumb}), encoding="utf-8"
            )
            self.assertEqual([], health.head_signer_problems(root, _valid_config(thumbprint=thumb)))

    def test_mismatch_without_archive_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "loop" / "audit-head.json").write_text(
                json.dumps({"signer_thumbprint": "A" * 40}), encoding="utf-8"
            )
            problems = health.head_signer_problems(root, _valid_config())
            self.assertTrue(any("historical archive" in p for p in problems))

    def test_mismatch_with_matching_archive_is_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            head_thumb = "A" * 40
            (root / "loop" / "audit-head.json").write_text(
                json.dumps({"signer_thumbprint": head_thumb}), encoding="utf-8"
            )
            archive = root / "loop" / f"audit-signing-{head_thumb.upper()}.json"
            archive.write_text(
                json.dumps({"thumbprint": head_thumb, "public_certificate_sha256": "b" * 64}),
                encoding="utf-8",
            )
            self.assertEqual([], health.head_signer_problems(root, _valid_config()))

    def test_archive_with_wrong_signer_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            head_thumb = "A" * 40
            (root / "loop" / "audit-head.json").write_text(
                json.dumps({"signer_thumbprint": head_thumb}), encoding="utf-8"
            )
            archive = root / "loop" / f"audit-signing-{head_thumb.upper()}.json"
            archive.write_text(
                json.dumps({"thumbprint": "B" * 40}), encoding="utf-8"
            )
            problems = health.head_signer_problems(root, _valid_config())
            self.assertTrue(any("does not match its signer" in p for p in problems))


class RemediationTests(unittest.TestCase):
    def test_public_cert_problem_yields_hint(self):
        hints = health.remediations(["public certificate file hash mismatch"])
        self.assertTrue(any("audit-signing-public" in h.lower() for h in hints))

    def test_cert_store_problem_yields_hint(self):
        hints = health.remediations(
            ["pinned certificate has no private key", "pinned certificate private key is exportable"]
        )
        self.assertTrue(any("currentuser" in h.lower() for h in hints))

    def test_archive_problem_yields_hint(self):
        hints = health.remediations(["no historical archive audit-signing-ABC.json exists"])
        self.assertTrue(any("audit-signing-" in h.lower() for h in hints))


class BuildReportTests(unittest.TestCase):
    def test_missing_config_report_is_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = health.build_report(
                Path(tmp), Path(tmp) / "missing.json", inspect=False
            )
            self.assertFalse(report["ok"])
            self.assertTrue(report["remediations"])

    def test_valid_config_report_is_ok_without_inspect(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "loop").mkdir(parents=True, exist_ok=True)
            cert = root / "audit-signing-public.cer"
            cert.write_bytes(b"fake cert bytes")
            config = _valid_config()
            config["public_certificate"] = "audit-signing-public.cer"
            config["public_certificate_sha256"] = hashlib.sha256(b"fake cert bytes").hexdigest()
            config_path = root / "loop" / "audit-signing.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            report = health.build_report(root, config_path, inspect=False)
            self.assertTrue(report["ok"], report)


if __name__ == "__main__":
    unittest.main()
