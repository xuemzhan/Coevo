"""Domain skills must stay single-sourced across both execution surfaces."""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / ".agents" / "skills"
OPENCODE = ROOT / ".opencode" / "skills"
DOMAIN_SKILLS = ("mvp-requirements", "agent-package", "acceptance-testing")
REQUIRED_MARKERS = ("## 权威文件",)


class SkillConsistencyTests(unittest.TestCase):
    def test_canonical_domain_skills_exist_with_required_markers(self):
        for name in DOMAIN_SKILLS:
            path = CANONICAL / name / "SKILL.md"
            self.assertTrue(path.is_file(), f"missing canonical skill {name}")
            text = path.read_text(encoding="utf-8")
            for marker in REQUIRED_MARKERS:
                self.assertIn(marker, text, f"{name} is missing {marker!r}")

    def test_opencode_skills_are_thin_pointers_to_canonical_source(self):
        for name in DOMAIN_SKILLS:
            path = OPENCODE / name / "SKILL.md"
            self.assertTrue(path.is_file(), f"missing opencode pointer {name}")
            text = path.read_text(encoding="utf-8")
            self.assertIn(f".agents/skills/{name}/SKILL.md", text)
            self.assertNotIn("## 权威文件", text, f"{name} duplicates canonical body")


if __name__ == "__main__":
    unittest.main()
