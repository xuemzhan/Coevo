"""ARCH-REVIEW-11: state-persistence matrix guard tests."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = ROOT / "src" / "coevo"
MATRIX = ROOT / "docs" / "architecture" / "state-persistence.md"

# Components that carry state: classes whose name ends with a stateful suffix.
_STATEFUL_CLASS = re.compile(
    r"^class\s+[A-Za-z_][A-Za-z0-9_]*(?:Store|Repository|Registry|Hub|Watcher)\b",
    re.MULTILINE,
)


def _stateful_modules() -> list[str]:
    found: list[str] = []
    for path in sorted(PKG_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if _STATEFUL_CLASS.search(text):
            found.append(path.relative_to(ROOT).as_posix())
    return found


class StatePersistenceMatrixTests(unittest.TestCase):
    def test_matrix_exists_and_covers_every_stateful_module(self) -> None:
        self.assertTrue(MATRIX.is_file(), "state-persistence matrix missing")
        text = MATRIX.read_text(encoding="utf-8")
        documented = set(re.findall(r"`(src/coevo/[^`]+\.py)`", text))
        missing = sorted(set(_stateful_modules()) - documented)
        self.assertEqual(missing, [], f"stateful modules not in matrix: {missing}")

    def test_matrix_declares_restart_semantics(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")
        self.assertIn("重启保留", text)
        self.assertIn("重启丢失", text)
        self.assertIn("内存态", text)
        self.assertIn("持久态", text)

    def test_matrix_registered_in_docs_index(self) -> None:
        index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("state-persistence.md", index)
        self.assertIn("状态持久化矩阵", index)


if __name__ == "__main__":
    unittest.main()
