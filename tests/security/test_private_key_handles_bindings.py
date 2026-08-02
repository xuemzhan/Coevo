"""Security test: private-key-handle receipts must never be tracked in git.

ENG-HISTORY-SCRUB-1 acceptance test. Guards the invariant restored by the
2026-08-02 history scrub (business-owner approved):

* no tracked path matches ``loop/private-key-handles-*``;
* no reachable git blob has such a path under any ref;
* the pre-scrub HEAD no longer resolves in the object store;
* ``.gitignore`` permanently excludes the receipt pattern.
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECEIPT_PATTERN = "loop/private-key-handles-"
OLD_PRE_SCRUB_HEAD = "85d07b738ffb32294d342c6f5584fd50330a2ca8"


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class PrivateKeyHandleGitBindingTests(unittest.TestCase):
    def test_no_tracked_receipt_paths(self):
        tracked = git("ls-files").stdout.splitlines()
        offenders = [line for line in tracked if RECEIPT_PATTERN in line.replace("\\", "/")]
        self.assertEqual([], offenders)

    def test_no_reachable_receipt_blobs_across_all_refs(self):
        objects = git("rev-list", "--objects", "--all").stdout.splitlines()
        offenders = [
            line for line in objects if RECEIPT_PATTERN in line.split(" ", 1)[-1].replace("\\", "/")
        ]
        self.assertEqual([], offenders)

    def test_pre_scrub_head_is_no_longer_reachable(self):
        probe = git("cat-file", "-e", OLD_PRE_SCRUB_HEAD)
        self.assertNotEqual(
            0,
            probe.returncode,
            "pre-scrub HEAD must not resolve after the history scrub",
        )

    def test_gitignore_excludes_receipt_pattern(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("loop/private-key-handles-*.json", ignore)


if __name__ == "__main__":
    unittest.main()
