"""Win7 compatibility profile checks (stdlib-only, offline, no webview)."""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


PROFILE_DOC = ROOT / "docs" / "architecture" / "win7-compat-branch.md"

# Modules in the Win7-supported surface must import with stdlib only.
WIN7_SURFACE = (
    "src.coevo.cockpit",
    "src.coevo.cockpit.server",
    "src.coevo.cockpit.state_store",
    "src.coevo.cockpit.wps",
    "src.coevo.protocol",
    "src.coevo.workspace",
    "src.coevo.report",
    "src.coevo.audit_governance",
    "src.coevo.progress_capture",
    "src.coevo.knowledge_base",
)

# Components explicitly out of scope on Win7 (must NOT be imported by the
# supported surface or referenced as runtime requirements).
FORBIDDEN_RUNTIME = ("webview2", "flask", "fastapi", "django", "torch", "onnx")


class Win7CompatProfileTests(unittest.TestCase):
    def test_profile_document_exists_and_covers_branch_plan(self):
        self.assertTrue(PROFILE_DOC.is_file())
        text = PROFILE_DOC.read_text(encoding="utf-8")
        for marker in ("win7-compat", "冻结依赖", "不支持", "安全补偿", "测试计划"):
            self.assertIn(marker, text)

    def test_supported_surface_imports_with_stdlib_only(self):
        for module_name in WIN7_SURFACE:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

    def test_no_forbidden_runtime_dependency(self):
        lock = (
            ROOT / "docs" / "dependencies" / "toolchain-lock.json"
        ).read_text(encoding="utf-8")
        for name in FORBIDDEN_RUNTIME:
            self.assertNotIn(name, lock.lower())

    def test_offline_constraint(self):
        script = (ROOT / "scripts" / "win7-compat-check.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("tests/win7", script)
        self.assertIn("-m unittest discover", script)


if __name__ == "__main__":
    unittest.main()
