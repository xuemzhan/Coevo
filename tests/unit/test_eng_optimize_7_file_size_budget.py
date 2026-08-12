"""ENG-OPTIMIZE-7: source file size budget guard (architecture review P2-1)."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MAX_FILE_LINES = 1133
LARGE_FILE_THRESHOLD = 600
KNOWN_LARGE_FILES: dict[str, int] = {
    "src/coevo/merge/engine.py": 1133,
    "src/coevo/cockpit/server.py": 1105,
    "src/coevo/cockpit/facade.py": 604,
    "src/coevo/orchestrator/real_chain_store.py": 771,
    "src/coevo/orchestrator/_real_chain.py": 720,
    "src/coevo/talent/store.py": 709,
    "src/coevo/merge/receipt.py": 708,
    "src/coevo/protocol/agent_package.py": 692,
    "src/coevo/identity/private_keys.py": 637,
    "src/coevo/merge/repository.py": 624,
    "src/coevo/app/pipeline.py": 723,
}


def _tracked_python_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().startswith("src/coevo/") and line.strip().endswith(".py")
    ]


def _line_count(rel: str) -> int:
    return len((ROOT / rel).read_text(encoding="utf-8").splitlines())


class FileSizeBudgetTests(unittest.TestCase):
    def test_no_file_exceeds_budget(self) -> None:
        over = sorted(
            rel for rel in _tracked_python_files() if _line_count(rel) > MAX_FILE_LINES
        )
        self.assertEqual(over, [], f"files exceed budget {MAX_FILE_LINES}: {over}")

    def test_large_file_set_is_pinned(self) -> None:
        over_threshold = sorted(
            rel
            for rel in _tracked_python_files()
            if _line_count(rel) > LARGE_FILE_THRESHOLD
        )
        self.assertEqual(
            over_threshold,
            sorted(KNOWN_LARGE_FILES),
            "large-file set drifted; update contract + whitelist together",
        )

    def test_known_large_files_do_not_grow(self) -> None:
        grown = sorted(
            rel
            for rel, budget in KNOWN_LARGE_FILES.items()
            if (ROOT / rel).exists() and _line_count(rel) > budget
        )
        self.assertEqual(grown, [], f"known large files grew past recorded budget: {grown}")

    def test_contract_doc_exists_and_registered(self) -> None:
        doc = ROOT / "docs" / "architecture" / "file-size-budget.md"
        self.assertTrue(doc.is_file(), "file-size-budget contract missing")
        text = doc.read_text(encoding="utf-8")
        self.assertIn("MAX_FILE_LINES", text)
        index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("file-size-budget.md", index)
        self.assertIn("源码文件规模预算契约", index)


if __name__ == "__main__":
    unittest.main()
