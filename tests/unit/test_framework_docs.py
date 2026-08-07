"""FRAMEWORK-DOCS-1: framework-layer documentation governance guard."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FrameworkDocsTests(unittest.TestCase):
    def test_readme_covers_framework_layer(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in (
            "US-16",
            "CTAF",
            "src/coevo/framework/",
            "timefmt.py",
            "docs/framework/",
            "docs/plans/distributed-agent-framework/",
        ):
            self.assertIn(marker, text, marker)

    def test_docs_index_covers_framework(self) -> None:
        text = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("`framework/`", text)

    def test_code_guide_covers_framework(self) -> None:
        text = (ROOT / "docs" / "code-guide.md").read_text(encoding="utf-8")
        self.assertIn("### 2.18 `framework/`", text)
        self.assertIn("### 2.19 `timefmt.py`", text)
        self.assertIn("manifest_checker.py", text)
        self.assertIn("app/pipeline.py", text)

    def test_framework_docs_exist(self) -> None:
        for name in (
            "capability-closedset.md",
            "memory-interface.md",
            "tool-registry.md",
            "a2a-protocol.md",
            "plan-lsp.md",
            "hybrid-orchestrator.md",
            "integration.md",
            "k8s-crd-listing.md",
        ):
            self.assertTrue((ROOT / "docs" / "framework" / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
