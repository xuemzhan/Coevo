"""Pin the local-runtime policy for loop/private-key-handles-F6DE...json.

These tests are deliberately read-only:
  - DO NOT mutate git, .gitignore, or the file itself.
  - DO record the current binding state as ground truth so future
    "harmonization" passes cannot silently flip the policy without
    updating this test AND loop/DECISIONS.md (AGENTS.md §3 第 6 条
    audit-binding discipline).

Policy rationale:
  - DECISIONS §2026-07-22 path-3 阶段二 §"untracked runtime" claimed the
    file is untracked — empirically incorrect. git ls-files shows it
    was added in commit cbeab97 ("Harden key handling and agent envelope
    validation") with 206 metadata-only handle entries (all
    destroyed_at-set, no key material).
  - The file content itself is non-sensitive: only public_digest
    (SHA-256), parent_thumbprint, audit UUID, validity window, and
    destroyed_at timestamp. No key bytes, no cng_key_id literals, no
    PIN or secrets.
  - The risk is bloat (every CNG integration test adds ~1.5KB and one
    destroyed entry), NOT exposure.
  - On 2026-07-25 the business owner approved policy (a+b): ignore all
    loop/private-key-handles-*.json receipts and remove the existing
    receipt from the Git index while preserving the local runtime file.

These tests assert the CURRENT state. If the policy is intentionally
changed, update both tests and DECISIONS.md in one commit.

2026-08-02 update: the business owner approved scrubbing the receipts from
git history (ENG-HISTORY-SCRUB-1). The DECISIONS pin below therefore now
expects "historical git blobs were scrubbed" instead of "historical git
blobs remain"; the new invariant is enforced by
tests/security/test_private_key_handles_bindings.py.
"""
from __future__ import annotations
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDLE_FILE = ROOT / "loop" / "private-key-handles-F6DE13A4ADF56B9D66902B8E3055DCCA8B702D86.json"
GITIGNORE = ROOT / ".gitignore"

# Sensitive patterns that would invalidate the "metadata only" claim.
SENSITIVE = [
    re.compile(r"BEGIN (?:RSA |EC |ENCRYPTED |PRIVATE )?PRIVATE KEY", re.I),
    re.compile(r"PRIVATE KEY", re.I),
    re.compile(r"-----BEGIN", re.I),
    re.compile(r"MI[A-Za-z0-9+/]{40,}"),  # high-entropy BASE64 MI-prefixed
    re.compile(r"AAAA[0-9a-zA-Z+/]{40,}"),  # high-entropy BASE64 AAAA-prefixed
]


def _git_ls_files_for(path: Path) -> str:
    res = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--stage", "--", str(path.relative_to(ROOT))],
        capture_output=True, text=True, encoding="utf-8",
    )
    return res.stdout.strip()


class PrivateKeyHandlesBindingsTests(unittest.TestCase):
    """Ground-truth pin for local-only receipts and metadata-only payloads."""

    def test_file_is_not_tracked_in_repository(self):
        """Pin: runtime receipts must not be present in the Git index."""
        listing = _git_ls_files_for(HANDLE_FILE)
        self.assertEqual(
            "",
            listing,
            f"runtime receipt is tracked unexpectedly: {listing!r}",
        )

    def test_gitignore_blocks_future_receipts(self):
        """Pin: future per-certificate receipts remain local runtime state."""
        ignore_text = GITIGNORE.read_text(encoding="utf-8", errors="replace")
        self.assertIn(
            "loop/private-key-handles-*.json",
            ignore_text,
            "missing ignore policy for private-key handle receipts",
        )
        result = subprocess.run(
            [
                "git", "-C", str(ROOT), "check-ignore", "--no-index", "--quiet",
                "--", str(HANDLE_FILE.relative_to(ROOT)),
            ],
            capture_output=True,
        )
        self.assertEqual(
            0,
            result.returncode,
            "Git does not apply the private-key handle receipt ignore rule",
        )

    def test_handle_payload_is_metadata_only(self):
        """Pin: no key material ever enters the file (only digests + thumbprints).

        Runtime invariant enforced by audit. If a future commit accidentally
        inlines a private key blob into the file, this test fails closed.
        """
        if not HANDLE_FILE.exists():
            self.skipTest(f"handle file absent: {HANDLE_FILE}")
        text = HANDLE_FILE.read_text(encoding="utf-8-sig")
        for pat in SENSITIVE:
            self.assertNotRegex(
                text, pat,
                f"sensitive pattern {pat.pattern!r} found in handle file; "
                f"this is a security regression",
            )

    def test_handle_payload_schema_is_stable(self):
        """Pin: each handle entry has the expected metadata-only key set.

        Locks the schema so a future helper that starts writing extra
        fields (e.g. raw_cng_blob) breaks this test loudly.
        """
        if not HANDLE_FILE.exists():
            self.skipTest(f"handle file absent: {HANDLE_FILE}")
        obj = json.loads(HANDLE_FILE.read_text(encoding="utf-8-sig"))
        handles = obj.get("handles", {})
        self.assertIsInstance(handles, dict)
        self.assertGreaterEqual(len(handles), 1)
        allowed_keys = {
            "valid_from", "valid_to", "parent_subject", "parent_thumbprint",
            "certificate_id", "public_digest", "created_at",
            "creation_audit_id", "algorithm_oid", "destroyed_at",
            "revoked_at", "revocation_reason",
        }
        # revoked_at and revocation_reason are optional; still NOT allowed beyond this set
        for k, handle in handles.items():
            self.assertIsInstance(handle, dict, f"handle {k!r} not a dict")
            extras = set(handle.keys()) - allowed_keys
            self.assertEqual(
                set(), extras,
                f"handle {k!r} has unexpected keys: {sorted(extras)!r}; "
                f"regression in schema",
            )

    def test_decisions_records_the_audit_corpus_status(self):
        """Pin: latest DECISIONS entry acknowledges the receipt policy.

        Self-correction discipline per AGENTS.md §3 第 6 条: DECISIONS is the
        source of truth for the current binding state, not an aspirational
        description. If this test fails, the most recent DECISIONS entry is
        stale and must be updated.
        """
        text = (ROOT / "loop" / "DECISIONS.md").read_text(encoding="utf-8", errors="replace")
        # Pull the most recent entry (between last two '## ' headings)
        sections = re.split(r"(?m)^## ", text)
        last_section = "## " + sections[-1]
        # The latest section must mention the runtime receipt policy; not silent.
        latest = last_section.lower()
        for marker in (
            "decision status: approved a+b",
            ".gitignore",
            "git rm --cached",
            "local runtime file preserved",
            "historical git blobs were scrubbed",
        ):
            self.assertIn(
                marker,
                latest,
                f"latest DECISIONS.md section lacks approved governance marker: {marker}",
            )
        self.assertNotIn(
            "awaiting",
            latest,
            "latest DECISIONS.md section still describes the approved policy as awaiting",
        )


if __name__ == "__main__":
    unittest.main()
