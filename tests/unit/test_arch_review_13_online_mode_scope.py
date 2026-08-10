"""ARCH-REVIEW-13: online-mode implementation scope declaration guard."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCOPE = ROOT / "docs" / "architecture" / "online-mode-scope.md"


class OnlineModeScopeTests(unittest.TestCase):
    def test_scope_doc_exists_and_declares_mvp_boundary(self) -> None:
        self.assertTrue(SCOPE.is_file(), "online-mode-scope contract missing")
        text = SCOPE.read_text(encoding="utf-8")
        for marker in (
            "离线闭环",
            "受控网络协同模式",
            "设计态",
            "后续版本范围",
            "DESIGNED",
            "MODELED",
        ):
            self.assertIn(marker, text, marker)

    def test_scope_doc_forbids_overclaim(self) -> None:
        text = SCOPE.read_text(encoding="utf-8")
        for marker in ("不得声称", "在线协同为后续版本范围"):
            self.assertIn(marker, text, marker)

    def test_registered_in_docs_index(self) -> None:
        index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("online-mode-scope.md", index)
        self.assertIn("在线协同实现范围", index)


if __name__ == "__main__":
    unittest.main()
