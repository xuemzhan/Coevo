"""FRAMEWORK-GAPS-6: shared ISO validator consolidation."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

from src.coevo.framework.validation import is_iso_utc_z as framework_iso
from src.coevo.timefmt import is_iso_utc_z

ROOT = Path(__file__).resolve().parents[2]

PRODUCT_MODULES = (
    "src/coevo/cockpit/models.py",
    "src/coevo/cockpit/sessions.py",
    "src/coevo/crypto/cng_handle.py",
    "src/coevo/knowledge_base/models.py",
    "src/coevo/audit_governance/models.py",
    "src/coevo/orchestrator/models.py",
    "src/coevo/progress_capture/models.py",
    "src/coevo/progress_capture/watcher.py",
    "src/coevo/talent/models.py",
    "src/coevo/task_decomposition/agent.py",
    "src/coevo/task_decomposition/baseline.py",
)


class SharedIsoConsolidationTests(unittest.TestCase):
    def test_framework_reexports_shared_validator(self) -> None:
        self.assertIs(framework_iso, is_iso_utc_z)

    def test_product_modules_have_no_iso_regex_duplicates(self) -> None:
        for rel in PRODUCT_MODULES:
            source = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("_ISO_UTC_Z = re.compile", source, rel)
            self.assertNotIn("_ISO_Z = re.compile", source, rel)
            self.assertNotIn("_ISO_RE: Final[re.Pattern", source, rel)
            self.assertIn("is_iso_utc_z", source, rel)

    def test_shared_validator_bounds(self) -> None:
        self.assertTrue(is_iso_utc_z("2026-08-08T08:00:00Z"))
        self.assertTrue(is_iso_utc_z("2026-08-08T08:00:00.123456Z"))
        self.assertFalse(is_iso_utc_z("2026-08-08T08:00:00Z\n"))
        self.assertFalse(is_iso_utc_z("2026-02-30T00:00:00Z"))
        self.assertFalse(is_iso_utc_z(123))

    def test_timefmt_imports_stdlib_only(self) -> None:
        source = (ROOT / "src" / "coevo" / "timefmt.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        allowed = set(sys.stdlib_module_names)
        bad: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] not in allowed:
                        bad.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] not in allowed:
                    bad.append(node.module)
        self.assertEqual([], bad, "third-party imports found in timefmt.py")


if __name__ == "__main__":
    unittest.main()
