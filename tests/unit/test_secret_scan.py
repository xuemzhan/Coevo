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

    def test_tests_pem_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "fixture.py").write_text(_fake_pem(), encoding="utf-8")
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
