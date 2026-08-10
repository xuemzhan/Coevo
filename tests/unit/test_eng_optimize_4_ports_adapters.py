"""ENG-OPTIMIZE-4: Ports & Adapters layering contract guard tests."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = ROOT / "src" / "coevo"


class PortsAdaptersTests(unittest.TestCase):
    def test_doc_defines_all_four_layers(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "ports-adapters.md"
        ).read_text(encoding="utf-8")
        for layer in ("Domain Core", "Application", "Ports", "Adapters"):
            self.assertIn(layer, text, layer)
        for marker in ("无 IO", "注入", "厂商", "DraftSuggestion"):
            self.assertIn(marker, text, marker)

    def test_doc_covers_every_src_coevo_package(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "ports-adapters.md"
        ).read_text(encoding="utf-8")
        missing = sorted(
            path.name
            for path in PKG_ROOT.iterdir()
            if path.is_dir() and (path / "__init__.py").is_file()
            and path.name not in text
        )
        self.assertEqual([], missing, "packages missing from layer mapping")

    def test_doc_states_change_discipline(self) -> None:
        text = (
            ROOT / "docs" / "architecture" / "ports-adapters.md"
        ).read_text(encoding="utf-8")
        self.assertIn("变更纪律", text)
        self.assertIn("DECISIONS", text)


if __name__ == "__main__":
    unittest.main()
