import importlib.util, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("validator",ROOT/"scripts/validate_opencode.py")
validator=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(validator)

class BaselineTests(unittest.TestCase):
    def test_jsonc_comments_are_removed_without_damaging_urls(self):
        value=validator.strip_jsonc('{"url":"https://example.invalid",// note\n"ok":true}')
        self.assertIn("https://example.invalid",value); self.assertNotIn("note",value)
    def test_baseline_validation_passes_without_optional_tool_installation(self):
        self.assertEqual([],validator.validate(False))
    def test_quality_gate_covers_product_source_and_preseals_audit(self):
        source=(ROOT/"scripts/quality_gate.py").read_text(encoding="utf-8")
        self.assertIn('"scripts","src","tests"',source)
        self.assertIn('"-p","*test*.py"',source)
        self.assertLess(source.index("seal()"),source.index("for argv in argvs"))
