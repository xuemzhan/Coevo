import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class LoopGuardStaticTests(unittest.TestCase):
    def test_apply_patch_and_windows_download_aliases_are_guarded(self):
        text=(ROOT/".opencode/plugins/loop-guard.ts").read_text(encoding="utf-8")
        self.assertIn('input.tool==="apply_patch"',text); self.assertIn("iwr|irm",text); self.assertIn("python\\s+-m\\s+pip",text)
