"""ARCH-REVIEW-16: architecture docs registry guard (all docs indexed)."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCH_DIR = ROOT / "docs" / "architecture"
README = ROOT / "docs" / "README.md"


class DocsRegistryTests(unittest.TestCase):
    def test_every_architecture_doc_is_registered_in_readme(self) -> None:
        index = README.read_text(encoding="utf-8")
        missing = sorted(
            path.name
            for path in ARCH_DIR.glob("*.md")
            if path.name not in index
        )
        self.assertEqual(
            missing,
            [],
            "architecture docs not registered in docs/README.md",
        )


if __name__ == "__main__":
    unittest.main()
