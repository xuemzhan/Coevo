"""SECSCAN-1: secret scanner logic + real-repo cleanliness tests."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "secret_scan", ROOT / "scripts" / "secret_scan.py"
)
secret_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(secret_scan)


def _fake_token() -> str:
    return "ghp_" + "A" * 36


def _fake_pem() -> str:
    return (
        "-----BEGIN PRIVATE KEY-----\n"
        + "A" * 64
        + "\n-----END PRIVATE KEY-----\n"
    )


def _fake_sm2_pem() -> str:
    return (
        "-----BEGIN SM2 PRIVATE KEY-----\n"
        + "B" * 64
        + "\n-----END SM2 PRIVATE KEY-----\n"
    )


class SecretScanTests(unittest.TestCase):
    def test_repo_is_clean(self):
        # The tracked repository must contain no high-confidence secrets.
        findings = secret_scan.scan(ROOT)
        self.assertEqual([], findings)

    def test_finds_pem_private_key_outside_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "bad.py").write_text(_fake_pem(), encoding="utf-8")
            findings = secret_scan.scan(root)
            self.assertEqual(1, len(findings))
            self.assertEqual("pem_private_key", findings[0]["pattern"])

    def test_finds_sm2_private_key_outside_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "bad.py").write_text(_fake_sm2_pem(), encoding="utf-8")
            findings = secret_scan.scan(root)
            self.assertEqual(1, len(findings))
            self.assertEqual("pem_private_key", findings[0]["pattern"])

    def test_tests_pem_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "fixture.py").write_text(_fake_pem(), encoding="utf-8")
            findings = secret_scan.scan(root)
            self.assertEqual([], findings)

    def test_tests_sm2_pem_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "fixture.py").write_text(
                _fake_sm2_pem(), encoding="utf-8"
            )
            findings = secret_scan.scan(root)
            self.assertEqual([], findings)

    def test_token_pattern_applies_everywhere_including_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "x.py").write_text(
                "token = " + repr(_fake_token()) + "\n", encoding="utf-8"
            )
            findings = secret_scan.scan(root)
            self.assertTrue(
                any(item["pattern"] == "github_pat" for item in findings),
                findings,
            )

    def test_github_token_family_detected(self):
        prefixes = ("ghp_", "gho_", "ghu_", "ghs_", "ghr_", "github_pat_")
        for prefix in prefixes:
            with self.subTest(prefix=prefix):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    suffix = "A" * 36 if prefix != "github_pat_" else (
                        "A" * 22 + "_" + "B" * 59
                    )
                    (root / "conf.py").write_text(
                        "token = " + repr(prefix + suffix) + "\n",
                        encoding="utf-8",
                    )
                    findings = secret_scan.scan(root)
                    self.assertTrue(
                        any(item["pattern"] == "github_pat" for item in findings),
                        (prefix, findings),
                    )

    def test_google_api_key_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "conf.py").write_text(
                "key = 'AIza" + "A" * 35 + "'\n", encoding="utf-8"
            )
            findings = secret_scan.scan(root)
            self.assertTrue(
                any(item["pattern"] == "google_api_key" for item in findings),
                findings,
            )

    def test_npm_token_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "npmrc.txt").write_text(
                "//registry.npmjs.org/:_authToken=npm_" + "A" * 36 + "\n",
                encoding="utf-8",
            )
            findings = secret_scan.scan(root)
            self.assertTrue(
                any(item["pattern"] == "npm_token" for item in findings),
                findings,
            )

    def test_stripe_key_detected(self):
        for prefix in ("sk_live_", "sk_test_", "rk_live_"):
            with self.subTest(prefix=prefix):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / "conf.py").write_text(
                        "key = '" + prefix + "A" * 24 + "'\n",
                        encoding="utf-8",
                    )
                    findings = secret_scan.scan(root)
                    self.assertTrue(
                        any(item["pattern"] == "stripe_key" for item in findings),
                        (prefix, findings),
                    )

    def test_sendgrid_key_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "conf.py").write_text(
                "key = 'SG." + "A" * 22 + "." + "B" * 20 + "'\n",
                encoding="utf-8",
            )
            findings = secret_scan.scan(root)
            self.assertTrue(
                any(item["pattern"] == "sendgrid_key" for item in findings),
                findings,
            )

    def test_pgp_private_key_outside_tests_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "bad.txt").write_text(
                "-----BEGIN PGP PRIVATE KEY BLOCK-----\n"
                + "C" * 64
                + "\n-----END PGP PRIVATE KEY BLOCK-----\n",
                encoding="utf-8",
            )
            findings = secret_scan.scan(root)
            self.assertEqual(1, len(findings))
            self.assertEqual("pgp_private_key", findings[0]["pattern"])

    def test_pgp_private_key_in_tests_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "fixture.txt").write_text(
                "-----BEGIN PGP PRIVATE KEY BLOCK-----\n"
                + "D" * 64
                + "\n-----END PGP PRIVATE KEY BLOCK-----\n",
                encoding="utf-8",
            )
            findings = secret_scan.scan(root)
            self.assertEqual([], findings)

    def test_pgp_private_key_in_loop_records_allowed(self):
        # REVIEW-FIX-3: loop/ records quote gate output that legitimately
        # contains PGP fixture text; it must not fail the real-repo scan.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loop = root / "loop"
            loop.mkdir()
            (loop / "VERIFICATION.md").write_text(
                "SECRET pgp_private_key: loop/DECISIONS.md:4091 "
                "(-----BEGIN PGP PRIVATE KEY BLOCK-----)\n",
                encoding="utf-8",
            )
            findings = secret_scan.scan_file(root, "loop/VERIFICATION.md")
            self.assertEqual([], findings)

    def test_pem_private_key_in_loop_records_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loop = root / "loop"
            loop.mkdir()
            (loop / "DECISIONS.md").write_text(_fake_pem(), encoding="utf-8")
            findings = secret_scan.scan_file(root, "loop/DECISIONS.md")
            self.assertEqual([], findings)

    def test_token_pattern_still_applies_in_loop_records(self):
        # Token-style secrets are never exempt, even inside loop/ records.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loop = root / "loop"
            loop.mkdir()
            (loop / "VERIFICATION.md").write_text(
                "quoted output token = " + repr(_fake_token()) + "\n",
                encoding="utf-8",
            )
            findings = secret_scan.scan_file(root, "loop/VERIFICATION.md")
            self.assertTrue(
                any(item["pattern"] == "github_pat" for item in findings),
                findings,
            )

    def test_key_assignment_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_value = "AbC" + "1" * 17
            (root / "config.py").write_text(
                'api_key = "' + fake_value + '"', encoding="utf-8"
            )
            findings = secret_scan.scan(root)
            self.assertEqual(1, len(findings))
            self.assertEqual("key_assignment", findings[0]["pattern"])

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = secret_scan.main(["--root", str(root), "--json"])
            self.assertEqual(0, code)
            (root / "bad.py").write_text(_fake_pem(), encoding="utf-8")
            code = secret_scan.main(["--root", str(root), "--json"])
            self.assertEqual(1, code)


if __name__ == "__main__":
    unittest.main()
