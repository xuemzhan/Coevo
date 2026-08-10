import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class LoopGuardStaticTests(unittest.TestCase):
    def test_apply_patch_and_windows_download_aliases_are_guarded(self):
        text=(ROOT/".opencode/plugins/loop-guard.ts").read_text(encoding="utf-8")
        self.assertIn('input.tool==="apply_patch"',text); self.assertIn("iwr|irm",text); self.assertIn("python\\s+-m\\s+pip",text)

    def test_codex_guard_mirrors_opencode_blocklist_and_path_policy(self):
        # ARCH-REVIEW-17: the Codex mirror (.codex/hooks/loop-guard.mjs) must
        # stay aligned with the OpenCode guard; drift would let one runtime
        # silently allow prohibited commands.
        codex=(ROOT/".codex/hooks/loop-guard.mjs").read_text(encoding="utf-8")
        opencode=(ROOT/".opencode/plugins/loop-guard.ts").read_text(encoding="utf-8")
        needles=(
            "git\\s+push",
            "git\\s+reset\\s+--hard",
            "rm\\s+-rf",
            "\\bcurl\\b",
            "\\bwget\\b",
            "npm|bun|pip|pip3",
            "python\\s+-m\\s+pip",
            "go\\s+get",
            "path-policy",
        )
        for needle in needles:
            self.assertIn(needle,codex,f"codex guard missing: {needle}")
            self.assertIn(needle,opencode,f"opencode guard missing: {needle}")
        self.assertIn("deny",codex)
