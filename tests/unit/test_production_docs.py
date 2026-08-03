"""DOCS-COMMENT-1: documentation ↔ code consistency guards.

These tests keep the production documentation honest:

1. every ``COEVO_*`` runtime variable read by ``src/coevo/config.py``
   must be registered in ``docs/operations/configuration-reference.md``;
2. every variable registered in the reference must actually be used in
   ``src/coevo`` or ``scripts`` (no dead documentation);
3. source comments must not describe completed slices as deferred /
   future (no stale "deferred to US-x-AC-y" / "future slice" in the
   modules whose slices have since landed).
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_SOURCE = (ROOT / "src" / "coevo" / "config.py").read_text(encoding="utf-8")
REFERENCE = (
    ROOT / "docs" / "operations" / "configuration-reference.md"
).read_text(encoding="utf-8")
_CODE_PATTERNS = (
    (ROOT / "src" / "coevo").rglob("*.py"),
    (ROOT / "scripts").rglob("*.py"),
    (ROOT / "scripts").rglob("*.ps1"),
    (ROOT / "scripts").rglob("*.cs"),
)
CODE_TEXT = "\n".join(
    path.read_text(encoding="utf-8", errors="replace")
    for pattern in _CODE_PATTERNS
    for path in pattern
)
_VAR_RE = re.compile(r"COEVO_[A-Z0-9_]+")

# Modules whose documented slices have landed; they must not describe
# themselves as deferred / future.
_LANDED_MODULES = (
    ROOT / "src" / "coevo" / "knowledge_base" / "__init__.py",
    ROOT / "src" / "coevo" / "cockpit" / "__init__.py",
    ROOT / "src" / "coevo" / "talent" / "__init__.py",
    ROOT / "src" / "coevo" / "talent" / "service.py",
    ROOT / "src" / "coevo" / "task_decomposition" / "__init__.py",
    ROOT / "src" / "coevo" / "task_decomposition" / "service.py",
)


class ConfigurationReferenceTests(unittest.TestCase):
    def test_runtime_env_vars_are_documented(self):
        documented = set(_VAR_RE.findall(REFERENCE))
        missing = sorted(set(_VAR_RE.findall(CONFIG_SOURCE)) - documented)
        self.assertEqual([], missing, "config.py vars missing from configuration-reference.md")

    def test_documented_vars_exist_in_code(self):
        documented = set(_VAR_RE.findall(REFERENCE))
        unused = sorted(documented - set(_VAR_RE.findall(CODE_TEXT)))
        self.assertEqual(
            [], unused, "documented vars not used anywhere in src/coevo or scripts"
        )


class CommentFreshnessTests(unittest.TestCase):
    def test_landed_modules_have_no_stale_deferred_references(self):
        offenders = []
        for path in _LANDED_MODULES:
            text = path.read_text(encoding="utf-8")
            if "deferred to US-" in text or "future slice" in text:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
